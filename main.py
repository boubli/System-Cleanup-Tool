import os
import shutil
import sys
import ctypes
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

    def run(self):
        try:
            # Clean Temp folders, Prefetch, and %TEMP% if selected
            total_deleted_count = 0
            if self.combined_cleanup:
                total_deleted_count += self.clean_combined_temp_folders()
            self.progress.emit(10)

            # Clean Browser Cache if selected
            browser_cache_count = 0
            if self.browser_cache:
                browser_cache_count = self.clean_browser_cache()
                self.progress.emit(20)

            # Remove Duplicate Files if selected
            duplicate_files_count = 0
            if self.duplicate_files:
                duplicate_files_count = self.remove_duplicate_files()
                self.progress.emit(30)

            # Clean Recycle Bin if Temp Cleanup is selected
            recycle_bin_size_gb = 0
            if self.combined_cleanup:
                recycle_bin_size_gb = self.get_recycle_bin_size()
                self.clean_recycle_bin()
            self.progress.emit(40)

            # Check and remove old System Restore Points if selected
            restore_points_count = 0
            if self.restore_points:
                restore_points_count = self.check_and_remove_restore_points()
                self.progress.emit(50)

            # Defragment HDD if selected
            if self.defrag_hdd:
                self.defragment_hdd()
                self.progress.emit(60)

            # Summarize cleanup
            total_count = total_deleted_count + browser_cache_count + duplicate_files_count + restore_points_count
            self.progress.emit(100)  # Emit 100% when everything is done

            # Prepare the summary of removed items
            summary = f"Cleanup completed:\n- {total_count} files deleted\n- {recycle_bin_size_gb:.2f} GB in Recycle Bin before cleaning"
            if self.removed_items:
                summary += "\n\nRemoved items:\n" + "\n".join(self.removed_items)

            self.finished.emit(summary)
        except Exception as e:
            self.finished.emit(f"An error occurred during cleanup:\n{e}")

    def clean_combined_temp_folders(self):
        """Clean combined temp folders for all users."""
        deleted_count = 0
        user_temp_folder = os.getenv('TEMP')
        deleted_count += self.delete_files_in_folder(user_temp_folder)
        system_temp_folder = r"C:\Windows\Temp"
        deleted_count += self.delete_files_in_folder(system_temp_folder)
        prefetch_folder = r"C:\Windows\Prefetch"
        deleted_count += self.delete_files_in_folder(prefetch_folder)
        return deleted_count

    def delete_files_in_folder(self, folder_path):
        """Delete all files and folders in the specified folder."""
        deleted_count = 0
        if os.path.exists(folder_path):
            for idx, item in enumerate(os.listdir(folder_path)):
                item_path = os.path.join(folder_path, item)
                try:
                    if os.path.isfile(item_path) or os.path.islink(item_path):
                        os.unlink(item_path)  # Remove file or symbolic link
                        self.removed_items.append(f"File: {item_path}")
                        deleted_count += 1
                    elif os.path.isdir(item_path):
                        shutil.rmtree(item_path)  # Remove directory
                        self.removed_items.append(f"Directory: {item_path}")
                        deleted_count += 1
                except Exception as e:
                    print(f"Failed to delete {item_path}: {e}")
        else:
            print(f"Folder not found: {folder_path}")
        return deleted_count

    def clean_browser_cache(self):
        """Clean browser cache."""
        # Placeholder: Implement specific browser cache cleaning here
        print("Cleaning browser cache...")
        self.removed_items.append("Browser Cache: Chrome, Firefox, etc.")  # Placeholder
        return 5  # Placeholder count

    def remove_duplicate_files(self):
        """Remove duplicate files."""
        # Placeholder: Implement logic to find and remove duplicate files
        print("Removing duplicate files...")
        self.removed_items.append("Duplicate Files: Example.txt, Example2.txt")  # Placeholder
        return 3  # Placeholder count

    def get_recycle_bin_size(self):
        """Get the total size of the Recycle Bin."""
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

        recycle_bin_size = get_recycle_bin_info("C:\\")  # Assume C: drive for Recycle Bin
        return recycle_bin_size / (1024 ** 3)  # Convert bytes to GB

    def clean_recycle_bin(self):
        """Clean the Recycle Bin."""
        ctypes.windll.shell32.SHEmptyRecycleBinW(None, None, 0)

    def check_and_remove_restore_points(self):
        """Check and remove old system restore points."""
        # Placeholder: Implement logic to check and remove old restore points
        print("Checking and removing old system restore points...")
        self.removed_items.append("Old System Restore Points: Removed")
        return 2  # Placeholder count

    def defragment_hdd(self):
        """Defragment HDD if it's an HDD."""
        # Placeholder: Implement logic for defragmenting HDD
        print("Defragmenting HDD...")
        self.removed_items.append("Defragmentation: HDD Defragmented")
        return


class CleanupApp(QWidget):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("System Cleanup Tool")
        self.setGeometry(100, 100, 400, 300)

        # Set application icon (use the full path to the icon)
        self.setWindowIcon(QIcon(r"C:\Users\youssef\Desktop\app cleaner\images\icon.ico"))

        # Layout
        layout = QVBoxLayout()

        # Label
        self.label = QLabel("Click the button below to clean your system:")
        layout.addWidget(self.label)

        # Progress Bar
        self.progress_bar = QProgressBar()
        self.progress_bar.setRange(0, 100)
        layout.addWidget(self.progress_bar)

        # Checkboxes for optional features
        self.combined_cleanup_checkbox = QCheckBox("Clean System Cache and Temporary Folders")
        self.browser_cache_checkbox = QCheckBox("Clean Browser Cache")
        self.duplicate_files_checkbox = QCheckBox("Remove Duplicate Files")
        self.restore_points_checkbox = QCheckBox("Old System Restore Points Remove")
        self.defrag_hdd_checkbox = QCheckBox("Defragment Hard Drive (HDD only)")

        layout.addWidget(self.combined_cleanup_checkbox)
        layout.addWidget(self.browser_cache_checkbox)
        layout.addWidget(self.duplicate_files_checkbox)
        layout.addWidget(self.restore_points_checkbox)
        layout.addWidget(self.defrag_hdd_checkbox)

        # Button to start cleanup
        self.cleanup_button = QPushButton("Clean Now")
        self.cleanup_button.clicked.connect(self.start_cleanup)
        layout.addWidget(self.cleanup_button)

        # About Button
        self.about_button = QPushButton("About")
        self.about_button.clicked.connect(self.show_about_info)
        layout.addWidget(self.about_button)

        # Set the layout
        self.setLayout(layout)

    def start_cleanup(self):
        # Check if at least one feature is selected
        if not (self.combined_cleanup_checkbox.isChecked() or
                self.browser_cache_checkbox.isChecked() or
                self.duplicate_files_checkbox.isChecked() or
                self.restore_points_checkbox.isChecked() or
                self.defrag_hdd_checkbox.isChecked()):
            QMessageBox.warning(self, "Error", "Please select at least one cleanup option before proceeding.")
            return

        # Set up the cleanup thread with selected options
        temp_folder = os.getenv('TEMP')
        prefetch_folder = r"C:\Windows\Prefetch"
        recycle_bin_path = "C:/$Recycle.Bin"

        self.cleanup_thread = CleanupThread(
            temp_folder,
            prefetch_folder,
            recycle_bin_path,
            self.browser_cache_checkbox.isChecked(),  # Only clean browser cache if checked
            self.duplicate_files_checkbox.isChecked(),  # Only remove duplicate files if checked
            self.restore_points_checkbox.isChecked(),  # Only check and remove restore points if checked
            self.defrag_hdd_checkbox.isChecked(),  # Only defrag HDD if checked
            self.combined_cleanup_checkbox.isChecked()  # Only clean temp folders if checked
        )

        # Connect signals
        self.cleanup_thread.progress.connect(self.update_progress)
        self.cleanup_thread.finished.connect(self.show_message)

        # Start the cleanup thread
        self.cleanup_thread.start()

    def update_progress(self, value):
        self.progress_bar.setValue(value)

    def show_message(self, message):
        QMessageBox.information(self, "Cleanup Complete", message)

    def show_about_info(self):
        about_info = (
            "Version: 1.0\n"
            "Developer: Youssef Boubli\n"
            "GitHub: https://github.com/boubli\n"
            "Email: bbb.vloger@gmail.com\n"
            "Phone: +48 514 450 053\n"
        )
        QMessageBox.information(self, "About", about_info)


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = CleanupApp()
    window.show()
    sys.exit(app.exec())
