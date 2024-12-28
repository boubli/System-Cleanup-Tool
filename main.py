import os
import shutil
import sys
import ctypes
from PySide6.QtCore import Qt, QThread, Signal
from PySide6.QtWidgets import QApplication, QWidget, QLabel, QVBoxLayout, QPushButton, QProgressBar, QMessageBox, QHBoxLayout
from PySide6.QtGui import QIcon

class CleanupThread(QThread):
    progress = Signal(int)
    finished = Signal(str)

    def __init__(self, temp_folder, prefetch_folder, recycle_bin_path):
        super().__init__()
        self.temp_folder = temp_folder
        self.prefetch_folder = prefetch_folder
        self.recycle_bin_path = recycle_bin_path

    def run(self):
        try:
            # Clean Temp folders
            temp_count = self.clean_temp_folders()
            self.progress.emit(25)

            # Clean Prefetch folder
            prefetch_count = self.delete_files_in_folder(self.prefetch_folder)
            self.progress.emit(50)

            # Get Recycle Bin size before cleaning
            recycle_bin_size_gb = self.get_recycle_bin_size()

            # Clean Recycle Bin
            self.clean_recycle_bin()
            self.progress.emit(75)

            # Summarize cleanup
            total_count = temp_count + prefetch_count
            self.progress.emit(100)  # Emit 100% when everything is done
            self.finished.emit(f"Cleanup completed:\n- {total_count} files deleted\n- {recycle_bin_size_gb:.2f} GB in Recycle Bin before cleaning")
        except Exception as e:
            self.finished.emit(f"An error occurred during cleanup:\n{e}")

    def clean_temp_folders(self):
        """Clean temp folders for all users."""
        total_deleted_count = 0

        # User temp folder
        user_temp_folder = os.getenv('TEMP')
        total_deleted_count += self.delete_files_in_folder(user_temp_folder)

        # System temp folder (usually under C:\Windows\Temp)
        system_temp_folder = r"C:\Windows\Temp"
        total_deleted_count += self.delete_files_in_folder(system_temp_folder)

        return total_deleted_count

    def delete_files_in_folder(self, folder_path):
        """Delete all files and folders in the specified folder."""
        deleted_count = 0
        if os.path.exists(folder_path):
            for idx, item in enumerate(os.listdir(folder_path)):
                item_path = os.path.join(folder_path, item)
                try:
                    if os.path.isfile(item_path) or os.path.islink(item_path):
                        os.unlink(item_path)  # Remove file or symbolic link
                        deleted_count += 1
                    elif os.path.isdir(item_path):
                        shutil.rmtree(item_path)  # Remove directory
                        deleted_count += 1
                except Exception as e:
                    print(f"Failed to delete {item_path}: {e}")
        else:
            print(f"Folder not found: {folder_path}")
        return deleted_count

    def get_recycle_bin_size(self):
        """Get the total size of the Recycle Bin."""
        total_size = 0
        # Use ctypes to access Recycle Bin
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
        # Simulate cleaning the Recycle Bin (this is just a placeholder)
        ctypes.windll.shell32.SHEmptyRecycleBinW(None, None, 0)


class CleanupApp(QWidget):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("System Cleanup Tool")
        self.setGeometry(100, 100, 400, 200)

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

        # Button
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
        # Set up the cleanup thread
        temp_folder = os.getenv('TEMP')
        prefetch_folder = r"C:\Windows\Prefetch"
        recycle_bin_path = "C:/$Recycle.Bin"

        self.cleanup_thread = CleanupThread(temp_folder, prefetch_folder, recycle_bin_path)
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
