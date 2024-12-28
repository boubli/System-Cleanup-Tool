# System Cleanup Tool

## Navigate to the Project Directory

```bash
cd System-Cleanup-Tool
```

## Install the Required Dependencies

```bash
pip install -r requirements.txt
```

## Run the Application

```bash
python main.py
```

---

## Download the Executable

You can download the **System Cleanup Tool** executable directly from the GitHub releases page:

[Download System Cleanup Tool .exe](https://github.com/boubli/System-Cleanup-Tool/releases/latest/download/System%20Cleanup%20Tool.exe)

---

## Executable Usage

The **System Cleanup Tool** can be run as an executable `.exe` file on Windows systems:

1. After downloading the `.exe`, double-click the file to launch the application.
2. Click the **"Clean Now"** button to start the cleanup process.
3. The tool will clean the **Temp** and **Prefetch** folders and empty the **Recycle Bin**.
4. The progress bar will show the real-time status of the cleanup.
5. After completion, a summary message will display the number of deleted files and the amount of space freed up in the Recycle Bin.

---

## Command Line Usage

You can also run the **System Cleanup Tool** from the command line. This is useful for automating the cleanup process or running it without opening the GUI.

### Command Syntax

```bash
SystemCleanupTool.exe --clean-temp --clean-prefetch --empty-recycle-bin
```

### Options

- `--clean-temp`: Cleans the **Temp** folders.
- `--clean-prefetch`: Cleans the **Prefetch** folder.
- `--empty-recycle-bin`: Empties the **Recycle Bin**.

### Example Command

To clean the **Temp** and **Prefetch** folders, and empty the **Recycle Bin**:

```bash
SystemCleanupTool.exe --clean-temp --clean-prefetch --empty-recycle-bin
```

This command will run the cleanup operations without opening the graphical interface.

---


## Technologies Used

- **Python 3.x**: The programming language used to develop the application.
- **PySide6**: A Python library for building graphical user interfaces.
- **ctypes**: Used for interacting with Windows system functions, such as accessing and cleaning the Recycle Bin.

---

## License

This project is licensed under the MIT License - see the LICENSE file for details.

---

## Contributing

Contributions are welcome! If you have suggestions for improvements or have found a bug, feel free to fork the repository and submit a pull request. Please follow these guidelines:

1. Fork the repository.
2. Create a new branch for your feature or bug fix.
3. Commit your changes.
4. Push to the branch.
5. Create a pull request.

---

## Developer Information

- **Developer**: Youssef Boubli
- **Email**: bbb.vloger@gmail.com
- **Phone**: +48 514 450 053
- **GitHub**: [boubli](https://github.com/boubli)

---

## Contact

For any inquiries or support, feel free to reach out via email at bbb.vloger@gmail.com.

---

## Acknowledgements

- Special thanks to the PySide6 library for providing a powerful toolkit for building the GUI.
- Thanks to the Python community for making such an amazing programming language!
