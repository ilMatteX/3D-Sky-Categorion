import os
import sys
import json
import webbrowser
import psutil
from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QVBoxLayout, QWidget, QPushButton, QLineEdit, QLabel, QFileDialog, QTextEdit,
    QProgressBar
)
from PyQt5.QtCore import Qt, QThread, pyqtSignal
from PyQt5.QtGui import QIcon
import multiprocessing
from process_files import process_files

CONFIG_FILE = "config.json"


class WorkerThread(QThread):
    progress = pyqtSignal(int)
    log = pyqtSignal(str)

    def __init__(self, chromedriver_path, categories_folder, image_folder, polygon_id):
        super().__init__()
        self.chromedriver_path = chromedriver_path
        self.categories_folder = categories_folder
        self.image_folder = image_folder
        self.polygon_id = polygon_id

    def run(self):
        self.log.emit("Starting file processing...")
        try:
            process_files(
                self.chromedriver_path,
                self.categories_folder,
                self.image_folder,
                self.polygon_id,
                log_signal=self.log,
                progress_signal=self.progress
            )
            self.log.emit("Processing completed successfully!")
        except Exception as e:
            self.log.emit(f"An error occurred: {str(e)}")


class FileManagerApp(QMainWindow):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("3D Sky Categorion")
        self.setWindowIcon(QIcon("icon.ico"))
        self.setGeometry(100, 100, 600, 400)

        layout = QVBoxLayout()

        self.chrome_path_input = self.create_input_field(
            r"Set ChromeDriver Path, including the file: (e.g., C:\\chromedriver-win64\\chromedriver.exe)", layout)
        self.download_chromedriver_button = QPushButton("Download ChromeDriver Stable Version")
        self.download_chromedriver_button.clicked.connect(self.download_chromedriver)
        layout.addWidget(self.download_chromedriver_button)
        self.categories_path_input = self.create_input_field(
            r"Set Categories Folder where you extracted all the empty folders: (e.g., C:\\3dsky\\categories)", layout)
        self.image_path_input = self.create_input_field(
            r"Set Image Folder with all the files that need to be organized: (e.g., C:\\3dsky\\images)", layout)
        self.polygon_id_input = self.create_input_field("Change Polygon Expert ID:", layout, show_select=False)

        self.open_3dsky_button = QPushButton(
            "Click here to open 3dsky.org, scroll to the bottom of the page, and click on 'Polygon Expert'. Then copy the model ID from the URL (e.g., for 'https://3dsky.org/3dmodels/show/nabor_proektorov_epson_1', the ID is 'nabor_proektorov_epson_1')."
        )
        self.open_3dsky_button.clicked.connect(self.open_3dsky)
        layout.addWidget(self.open_3dsky_button)

        self.log_output = QTextEdit()
        self.log_output.setReadOnly(True)
        layout.addWidget(self.log_output)

        self.progress_bar = QProgressBar()
        layout.addWidget(self.progress_bar)

        self.start_button = QPushButton("Start")
        self.start_button.clicked.connect(self.start_processing)
        layout.addWidget(self.start_button)

        self.stop_button = QPushButton("Stop")
        self.stop_button.clicked.connect(self.stop_processing)
        layout.addWidget(self.stop_button)

        container = QWidget()
        container.setLayout(layout)
        self.setCentralWidget(container)

        self.load_config()

    def create_input_field(self, label_text, layout, show_select=True):
        label = QLabel(label_text)
        path_input = QLineEdit()
        path_input.setPlaceholderText("Select" if show_select else "")

        input_layout = QVBoxLayout()
        input_layout.addWidget(label)
        input_layout.addWidget(path_input)

        if show_select:
            select_button = QPushButton("Select")

            def open_file_dialog():
                if "Folder" in label_text:
                    selected_path = QFileDialog.getExistingDirectory(self, "Select Folder")
                else:
                    selected_path, _ = QFileDialog.getOpenFileName(self, "Select File")
                if selected_path:
                    path_input.setText(os.path.normpath(selected_path))

            select_button.clicked.connect(open_file_dialog)
            input_layout.addWidget(select_button)

        layout.addLayout(input_layout)
        return path_input

    def download_chromedriver(self):
        webbrowser.open("https://googlechromelabs.github.io/chrome-for-testing/#stable")

    def open_3dsky(self):
        webbrowser.open("https://3dsky.org/")

    def start_processing(self):
        chromedriver_path = os.path.normpath(self.chrome_path_input.text())
        categories_folder = os.path.normpath(self.categories_path_input.text())
        image_folder = os.path.normpath(self.image_path_input.text())
        polygon_id = self.polygon_id_input.text().strip().strip('\'"')  # Clean up quotes and apostrophes

        if not os.path.isfile(chromedriver_path):
            self.show_error("Invalid ChromeDriver path. Please select a valid file.")
            return

        if not os.path.isdir(categories_folder):
            self.show_error("Invalid Categories folder. Please select a valid directory.")
            return

        if not os.path.isdir(image_folder):
            self.show_error("Invalid Image folder. Please select a valid directory.")
            return

        self.save_config(chromedriver_path, categories_folder, image_folder, polygon_id)

        self.thread = WorkerThread(chromedriver_path, categories_folder, image_folder, polygon_id)

        self.thread.progress.connect(self.update_progress)
        self.thread.log.connect(self.update_log)

        self.thread.start()

    def stop_processing(self):
        if self.thread.isRunning():
            self.thread.terminate()
            self.terminate_chromedriver_and_chrome_processes()

    def terminate_chromedriver_and_chrome_processes(self):
        for process in psutil.process_iter(['pid', 'name']):
            if 'chromedriver' in process.info['name'].lower() or 'chrome' in process.info['name'].lower():
                try:
                    psutil.Process(process.info['pid']).terminate()
                    self.log_output.append(f"Terminated process {process.info['pid']}")
                except psutil.NoSuchProcess:
                    pass

    def update_progress(self, value):
        self.progress_bar.setValue(value)

    def update_log(self, message):
        self.log_output.append(message)

    def show_error(self, message):
        self.log_output.append(f"Error: {message}")

    def load_config(self):
        if os.path.exists(CONFIG_FILE):
            with open(CONFIG_FILE, 'r') as f:
                config = json.load(f)
                self.chrome_path_input.setText(config.get("chromedriver_path", ""))
                self.categories_path_input.setText(config.get("categories_folder", ""))
                self.image_path_input.setText(config.get("image_folder", ""))
                self.polygon_id_input.setText(config.get("polygon_id", ""))

    def save_config(self, chromedriver_path, categories_folder, image_folder, polygon_id):
        config = {
            "chromedriver_path": chromedriver_path,
            "categories_folder": categories_folder,
            "image_folder": image_folder,
            "polygon_id": polygon_id
        }
        with open(CONFIG_FILE, 'w') as f:
            json.dump(config, f)


if __name__ == "__main__":
    multiprocessing.freeze_support()
    app = QApplication(sys.argv)
    window = FileManagerApp()
    window.show()
    sys.exit(app.exec_())
