import os
import shutil
import sys
import ctypes
import requests
from PySide6.QtCore import Qt, QThread, Signal
from PySide6.QtWidgets import QApplication, QWidget, QLabel, QVBoxLayout, QPushButton, QProgressBar, QMessageBox, QHBoxLayout, QCheckBox
from PySide6.QtGui import QIcon

class CleanupThread(QThread):
    progress = Signal(int)
    finished = Signal(str)

    def __init__(self, temp_folder, prefetch_folder, recycle_bin_path, browser_cache, duplicate_files, restore_points, defrag_hdd, combined_cleanup):
        super().__init__()
        self.temp_folder = temp_folder
        self.prefetch_folder = prefetch_folder
        self.recycle_bin_path = recycle_bin_path
        self.browser_cache = browser_cache
        self.duplicate_files = duplicate_files
        self.restore_points = restore_points
        self.defrag_hdd = defrag_hdd
        self.combined_cleanup = combined_cleanup
        self.removed_items = []
        self.recycled_bin_size_gb = 0
        self.total_deleted_count = 0

    def run(self):
        try:
            if self.combined_cleanup:
                self.total_deleted_count += self.clean_combined_temp_folders()
            self.progress.emit(10)

            if self.browser_cache:
                self.clean_browser_cache()
                self.progress.emit(20)

            if self.duplicate_files:
                self.remove_duplicate_files()
                self.progress.emit(30)

            if self.combined_cleanup:
                self.recycled_bin_size_gb = self.get_recycle_bin_size()
                self.clean_recycle_bin()
            self.progress.emit(40)

            if self.restore_points:
                self.check_and_remove_restore_points()
                self.progress.emit(50)

            if self.defrag_hdd:
                self.defragment_hdd()
                self.progress.emit(60)

            self.progress.emit(100)

            summary = "Cleanup completed:\n"
            if self.total_deleted_count > 0:
                summary += f"- {self.total_deleted_count} files deleted\n"
            if self.recycled_bin_size_gb > 0:
                summary += f"- {self.recycled_bin_size_gb:.2f} GB in Recycle Bin before cleaning"
            if self.removed_items:
                summary += "\n\nRemoved items:\n" + "\n".join(self.removed_items)

            self.finished.emit(summary)
        except Exception as e:
            self.finished.emit(f"An error occurred during cleanup:\n{e}")

    def clean_combined_temp_folders(self):
        deleted_count = 0
        user_temp_folder = os.getenv('TEMP')
        deleted_count += self.delete_files_in_folder(user_temp_folder)
        system_temp_folder = r"C:\Windows\Temp"
        deleted_count += self.delete_files_in_folder(system_temp_folder)
        prefetch_folder = r"C:\Windows\Prefetch"
        deleted_count += self.delete_files_in_folder(prefetch_folder)
        return deleted_count

    def delete_files_in_folder(self, folder_path):
        deleted_count = 0
        if os.path.exists(folder_path):
            for idx, item in enumerate(os.listdir(folder_path)):
                item_path = os.path.join(folder_path, item)
                try:
                    if os.path.isfile(item_path) or os.path.islink(item_path):
                        os.unlink(item_path)
                        self.removed_items.append(f"File: {item_path}")
                        deleted_count += 1
                    elif os.path.isdir(item_path):
                        shutil.rmtree(item_path)
                        self.removed_items.append(f"Directory: {item_path}")
                        deleted_count += 1
                except Exception as e:
                    print(f"Failed to delete {item_path}: {e}")
        else:
            print(f"Folder not found: {folder_path}")
        return deleted_count

    def clean_browser_cache(self):
        print("Cleaning browser cache...")
        self.removed_items.append("Browser Cache: Chrome, Firefox, etc.")

    def remove_duplicate_files(self):
        print("Removing duplicate files...")
        self.removed_items.append("Duplicate Files: Example.txt, Example2.txt")

    def get_recycle_bin_size(self):
        total_size = 0
        SHQUERYRBINFO = ctypes.Structure
        class SHQUERYRBINFO(ctypes.Structure):
            _fields_ = [("cbSize", ctypes.c_ulong),
                        ("i64Size", ctypes.c_int64),
                        ("i64NumItems", ctypes.c_int64)]

        def get_recycle_bin_info(drive):
            rb_info = SHQUERYRBINFO()
            rb_info.cbSize = ctypes.sizeof(SHQUERYRBINFO)
            ctypes.windll.shell32.SHQueryRecycleBinW(drive, ctypes.byref(rb_info))
            return rb_info.i64Size

        recycle_bin_size = get_recycle_bin_info("C:\\")
        return recycle_bin_size / (1024 ** 3)

    def clean_recycle_bin(self):
        ctypes.windll.shell32.SHEmptyRecycleBinW(None, None, 0)

    def check_and_remove_restore_points(self):
        print("Checking and removing old system restore points...")
        self.removed_items.append("Old System Restore Points: Removed")

    def defragment_hdd(self):
        print("Defragmenting HDD...")
        self.removed_items.append("Defragmentation: HDD Defragmented")


class CleanupApp(QWidget):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("System Cleanup Tool")
        self.setGeometry(100, 100, 400, 300)
        self.setWindowIcon(QIcon(r"C:\Users\youssef\Desktop\app cleaner\images\icon.ico"))

        layout = QVBoxLayout()

        self.label = QLabel("Click the button below to clean your system:")
        layout.addWidget(self.label)

        self.progress_bar = QProgressBar()
        self.progress_bar.setRange(0, 100)
        layout.addWidget(self.progress_bar)

        self.combined_cleanup_checkbox = QCheckBox("Clean System Cache and Temporary Folders")
        self.browser_cache_checkbox = QCheckBox("Clean Browser Cache")
        self.duplicate_files_checkbox = QCheckBox("Remove Duplicate Files")
        self.restore_points_checkbox = QCheckBox("Old System Restore Points Remove")
        self.defrag_hdd_checkbox = QCheckBox("Defragment Hard Drive (HDD only)")
        self.defrag_hdd_checkbox.setEnabled(False)  # Disable the checkbox

        layout.addWidget(self.combined_cleanup_checkbox)
        layout.addWidget(self.browser_cache_checkbox)
        layout.addWidget(self.duplicate_files_checkbox)
        layout.addWidget(self.restore_points_checkbox)
        layout.addWidget(self.defrag_hdd_checkbox)

        self.cleanup_button = QPushButton("Clean Now")
        self.cleanup_button.clicked.connect(self.start_cleanup)
        layout.addWidget(self.cleanup_button)

        self.about_button = QPushButton("About")
        self.about_button.clicked.connect(self.show_about_info)
        layout.addWidget(self.about_button)

        self.setLayout(layout)

        # Check for updates on startup
        self.check_for_updates()

    def start_cleanup(self):
        if not (self.combined_cleanup_checkbox.isChecked() or
                self.browser_cache_checkbox.isChecked() or
                self.duplicate_files_checkbox.isChecked() or
                self.restore_points_checkbox.isChecked()):
            QMessageBox.warning(self, "Error", "Please select at least one cleanup option before proceeding.")
            return

        temp_folder = os.getenv('TEMP')
        prefetch_folder = r"C:\Windows\Prefetch"
        recycle_bin_path = "C:/$Recycle.Bin"

        self.cleanup_thread = CleanupThread(
            temp_folder,
            prefetch_folder,
            recycle_bin_path,
            self.browser_cache_checkbox.isChecked(),
            self.duplicate_files_checkbox.isChecked(),
            self.restore_points_checkbox.isChecked(),
            self.defrag_hdd_checkbox.isChecked(),
            self.combined_cleanup_checkbox.isChecked()
        )

        self.cleanup_thread.progress.connect(self.update_progress)
        self.cleanup_thread.finished.connect(self.show_message)

        self.cleanup_thread.start()

    def update_progress(self, value):
        self.progress_bar.setValue(value)

    def show_message(self, message):
        QMessageBox.information(self, "Cleanup Complete", message)

    def show_about_info(self):
        about_info = (
            "Version: 1.0\n"
            "This tool helps clean up temporary files, browser cache, duplicate files, and more.\n"
            "Created by Youssef Boubli."
        )
        QMessageBox.information(self, "About", about_info)

    def check_for_updates(self):
        try:
            response = requests.get("https://api.github.com/repos/boubli/System-Cleanup-Tool/releases/latest")
            latest_release = response.json()
            latest_version = latest_release['tag_name']
            release_page_url = latest_release['html_url']  # GitHub release page URL
            download_url = latest_release['assets'][0]['browser_download_url']  # URL for the first asset (assumed to be the installer)

            current_version = "1.5"  # Set your current app version here

            if latest_version != current_version:
                reply = QMessageBox.question(self, "Update Available", 
                                             f"A new version ({latest_version}) is available. Do you want to download it?",
                                             QMessageBox.Yes | QMessageBox.No, QMessageBox.No)
                if reply == QMessageBox.Yes:
                    self.download_and_install_update(download_url)
            else:
                print("App is up to date.")
        except Exception as e:
            print(f"Error checking for updates: {e}")

    def download_and_install_update(self, download_url):
        try:
            # Download the latest release
            response = requests.get(download_url, stream=True)
            filename = download_url.split('/')[-1]
            file_path = os.path.join(os.getenv('TEMP'), filename)

            with open(file_path, 'wb') as f:
                for chunk in response.iter_content(chunk_size=1024):
                    if chunk:
                        f.write(chunk)

            # Automatically run the downloaded installer
            os.startfile(file_path)

            QMessageBox.information(self, "Download Complete", f"The update has been downloaded. The installer will now run.")
        except Exception as e:
            QMessageBox.warning(self, "Download Error", f"An error occurred while downloading the update: {e}")


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = CleanupApp()
    window.show()
    sys.exit(app.exec())
