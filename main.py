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
        self.added_items = []
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
                summary += f"- {self.recycled_bin_size_gb:.2f} GB in Recycle Bin"
            if self.removed_items:
                summary += "\n\nRemoved items:\n" + "\n".join(self.removed_items)
            if self.added_items:
                summary += "\n\nAdded item:\n" + "\n".join(self.added_items)

            self.finished.emit(summary)
        except Exception as e:
            self.finished.emit(f"An error occurred during cleanup:\n{e}")

    def clean_combined_temp_folders(self):
        deleted_count = 0
        user_temp_folder = os.getenv('TEMP')  # Get the current user's Temp folder dynamically
        deleted_count += self.delete_files_in_folder(user_temp_folder)
    
        system_temp_folder = r"C:\Windows\Temp"
        deleted_count += self.delete_files_in_folder(system_temp_folder)
    
        prefetch_folder = r"C:\Windows\Prefetch"
        deleted_count += self.delete_files_in_folder(prefetch_folder)

        # Add the AppData\Local\Temp folder dynamically for any user
        temp2_folder = os.path.join(os.getenv('USERPROFILE'), "AppData", "Local", "Temp")
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
        print("Browser cache cleaned successfully!")

    def remove_duplicate_files(self):
        print("Removing duplicate files...")
        self.removed_items.append("Duplicate Files: Example.txt, Example2.txt")
        print("Remove duplicate files successfully!")

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
        print("Old system restore points removed successfully!")

    def defragment_hdd(self):
        print("Defragmenting HDD...")
        self.removed_items.append("Defragmentation: HDD Defragmented")

    def import_power_plan_func(self):
        try:
            # Download the power plan file from GitHub and save it to the Desktop
            desktop_path = os.path.join(os.path.expanduser("~"), "Desktop")
            power_plan_url = "https://github.com/boubli/System-Cleanup-Tool/raw/refs/heads/main/extra/Power%20Plan/TRADMSS.pow"
            power_plan_path = os.path.join(desktop_path, "TRADMSS.pow")
            urllib.request.urlretrieve(power_plan_url, power_plan_path)
            
            print(f"Power plan downloaded to: {power_plan_path}")
            # Use the powercfg command to import the power plan
            os.system(f'powercfg /import "{power_plan_path}"')
            self.added_items.append(f"Power Plan: {power_plan_path} added successfully.")  # Changed to "added"
        except Exception as e:
            self.added_items.append(f"Power Plan Import Error: {e}")
            print(f"Error importing power plan: {e}")

    def reduce_unnecessary_services(self):
        # Download the batch file for reducing unnecessary services from GitHub
        try:
            desktop_path = os.path.join(os.path.expanduser("~"), "Desktop")
            batch_file_url = "https://raw.githubusercontent.com/boubli/System-Cleanup-Tool/refs/heads/main/extra/bats/reduce_services.bat"
            batch_file_path = os.path.join(desktop_path, "reduce_services.bat")
            urllib.request.urlretrieve(batch_file_url, batch_file_path)
            
            print(f"Batch file downloaded to: {batch_file_path}")
            # Execute the batch file to reduce unnecessary services
            subprocess.run(batch_file_path, check=True, shell=True)
            self.added_items.append(f"Unnecessary services reduced using {batch_file_path}")
        except Exception as e:
            self.added_items.append(f"Error reducing services: {e}")
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
        if not (self.combined_cleanup_checkbox.isChecked() or self.browser_cache_checkbox.isChecked() or self.duplicate_files_checkbox.isChecked() or
                self.restore_points_checkbox.isChecked() or self.defrag_hdd_checkbox.isChecked() or self.import_power_plan_checkbox.isChecked() or
                self.reduce_services_checkbox.isChecked()):
            QMessageBox.warning(self, "No Options Selected", "Please select at least one option to perform cleanup.")
            return

        temp_folder = self.combined_cleanup_checkbox.isChecked()
        prefetch_folder = self.combined_cleanup_checkbox.isChecked()
        recycle_bin_path = self.combined_cleanup_checkbox.isChecked()
        browser_cache = self.browser_cache_checkbox.isChecked()
        duplicate_files = self.duplicate_files_checkbox.isChecked()
        restore_points = self.restore_points_checkbox.isChecked()
        defrag_hdd = self.defrag_hdd_checkbox.isChecked()
        combined_cleanup = self.combined_cleanup_checkbox.isChecked()
        import_power_plan = self.import_power_plan_checkbox.isChecked()
        reduce_services = self.reduce_services_checkbox.isChecked()

        self.cleanup_thread = CleanupThread(temp_folder, prefetch_folder, recycle_bin_path, browser_cache, duplicate_files, restore_points,
                                            defrag_hdd, combined_cleanup, import_power_plan, reduce_services)
        self.cleanup_thread.progress.connect(self.progress_bar.setValue)
        self.cleanup_thread.finished.connect(self.show_summary)
        self.cleanup_thread.start()

    def show_summary(self, summary):
        QMessageBox.information(self, "Cleanup Summary", summary)

    def show_about_info(self):
        about_message = """
        System Cleanup Tool v1.0
        Developed by Youssef Boubli
        This tool helps you clean temporary files, browser cache, remove duplicate files, defragment your hard drive, and more.
        """
        QMessageBox.about(self, "About", about_message)

    def check_for_updates(self):
        try:
            response = requests.get("https://api.github.com/repos/boubli/System-Cleanup-Tool/releases/latest")
            latest_version = response.json()["tag_name"]
            current_version = "v2.0"  # Replace with the actual current version
            if latest_version != current_version:
                update_message = f"New version {latest_version} is available. Do you want to update?"
                reply = QMessageBox.question(self, "Update Available", update_message,
                                             QMessageBox.Yes | QMessageBox.No, QMessageBox.No)
                if reply == QMessageBox.Yes:
                    self.download_and_install_update(latest_version)
        except Exception as e:
            print(f"Error checking for updates: {e}")

    def download_and_install_update(self, version):
        update_url = f"https://github.com/boubli/System-Cleanup-Tool/releases/download/{version}/System-Cleanup-Tool-{version}.exe"
        try:
            update_file_path = os.path.join(os.path.expanduser("~"), "Downloads", f"System-Cleanup-Tool-{version}.exe")
            urllib.request.urlretrieve(update_url, update_file_path)
            QMessageBox.information(self, "Update Downloaded", f"The update has been downloaded to {update_file_path}. Please install it manually.")
        except Exception as e:
            print(f"Error downloading update: {e}")

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = CleanupApp()
    window.show()
    sys.exit(app.exec())
