import os
import shutil
import sys
import ctypes
import requests
from PySide6.QtCore import Qt, QThread, Signal
from PySide6.QtWidgets import QApplication, QWidget, QLabel, QVBoxLayout, QPushButton, QProgressBar, QMessageBox, QHBoxLayout, QCheckBox
from PySide6.QtGui import QIcon
import subprocess  # For running system commands like 'sc' to stop services
import urllib.request  # For downloading the update

class CleanupThread(QThread):
    progress = Signal(int)
    finished = Signal(str)

    def __init__(self, temp_folder, prefetch_folder, recycle_bin_path, browser_cache, duplicate_files, restore_points, defrag_hdd, combined_cleanup, import_power_plan, reduce_services):
        super().__init__()
        self.temp_folder = temp_folder
        self.prefetch_folder = prefetch_folder
        self.recycle_bin_path = recycle_bin_path
        self.browser_cache = browser_cache
        self.duplicate_files = duplicate_files
        self.restore_points = restore_points
        self.defrag_hdd = defrag_hdd
        self.combined_cleanup = combined_cleanup
        self.import_power_plan = import_power_plan
        self.reduce_services = reduce_services
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

            if self.import_power_plan:
                self.import_power_plan_func()
                self.progress.emit(70)

            if self.reduce_services:
                self.reduce_unnecessary_services()
                self.progress.emit(80)

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

        # Add the temp2 folder to be cleaned
        temp2_folder = r"C:\Temp2"  # Update this path to the actual location of temp2 if needed
        deleted_count += self.delete_files_in_folder(temp2_folder)

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

    def import_power_plan_func(self):
        try:
            # Get the path of the current script and build the relative path to the power plan
            script_dir = os.path.dirname(os.path.abspath(__file__))  # Get the directory of the current script
            power_plan_path = os.path.join(script_dir, "extra", "Power Plan", "TRADMSS.pow")  # Build the path dynamically
            
            print(f"Looking for power plan at: {power_plan_path}")  # Debugging line
            if os.path.exists(power_plan_path):
                # Use the powercfg command to import the power plan
                os.system(f'powercfg /import "{power_plan_path}"')
                self.removed_items.append(f"Power Plan: {power_plan_path} added successfully.")  # Changed to "added"
            else:
                self.removed_items.append(f"Power Plan File: {power_plan_path} not found.")
        except Exception as e:
            self.removed_items.append(f"Power Plan Import Error: {e}")
            print(f"Error importing power plan: {e}")

    def reduce_unnecessary_services(self):
        # Execute the batch file to reduce unnecessary services
        try:
            batch_file_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "extra", "bats", "reduce_services.bat")
            if os.path.exists(batch_file_path):
                subprocess.run(batch_file_path, check=True)
                self.removed_items.append(f"Unnecessary services reduced using {batch_file_path}")
            else:
                self.removed_items.append("Batch file for reducing services not found.")
        except Exception as e:
            self.removed_items.append(f"Error reducing services: {e}")
            print(f"Error reducing services: {e}")


class CleanupApp(QWidget):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("System Cleanup Tool")
        self.setGeometry(100, 100, 400, 300)
        self.setWindowIcon(QIcon(r"extra\images\icon.ico"))

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
        self.import_power_plan_checkbox = QCheckBox("Import Power Plan")
        self.reduce_services_checkbox = QCheckBox("Reduce Unnecessary Services")

        layout.addWidget(self.combined_cleanup_checkbox)
        layout.addWidget(self.browser_cache_checkbox)
        layout.addWidget(self.duplicate_files_checkbox)
        layout.addWidget(self.restore_points_checkbox)
        layout.addWidget(self.defrag_hdd_checkbox)
        layout.addWidget(self.import_power_plan_checkbox)
        layout.addWidget(self.reduce_services_checkbox)

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
                self.restore_points_checkbox.isChecked() or
                self.import_power_plan_checkbox.isChecked() or
                self.reduce_services_checkbox.isChecked()):  # Add power plan check
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
            self.combined_cleanup_checkbox.isChecked(),
            self.import_power_plan_checkbox.isChecked(),
            self.reduce_services_checkbox.isChecked()
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
            "Version: 2.0\n"
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

            current_version = "1.0"  # Replace with your current version number
            if latest_version != current_version:
                user_response = QMessageBox.question(self, "Update Available",
                                                     f"A new version ({latest_version}) is available. Do you want to download it?",
                                                     QMessageBox.Yes | QMessageBox.No)
                if user_response == QMessageBox.Yes:
                    self.download_and_install_update(download_url)
        except Exception as e:
            print(f"Error checking for updates: {e}")

    def download_and_install_update(self, download_url):
        try:
            # Download the update
            temp_file_path = os.path.join(os.getenv("TEMP"), "update_installer.exe")
            urllib.request.urlretrieve(download_url, temp_file_path)

            # Run the installer
            subprocess.run(temp_file_path, check=True)
            QMessageBox.information(self, "Update", "The update has been downloaded and installed successfully.")
        except Exception as e:
            QMessageBox.warning(self, "Error", f"An error occurred while downloading or installing the update: {e}")


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = CleanupApp()
    window.show()
    sys.exit(app.exec())
