# This Python file uses the following encoding: utf-8
import os
from pathlib import Path
import sys

from PySide6.QtWidgets import (
    QApplication,
    QCheckBox,
    QComboBox,
    QDateEdit,
    QDateTimeEdit,
    QDial,
    QDoubleSpinBox,
    QFontComboBox,
    QLabel,
    QLCDNumber,
    QLineEdit,
    QMainWindow,
    QProgressBar,
    QPushButton,
    QRadioButton,
    QSlider,
    QSpinBox,
    QTimeEdit,
    QVBoxLayout,
    QWidget,
)
from PySide6.QtCore import QFile
from PySide6.QtUiTools import QUiLoader
from PySide6.QtGui import QPixmap

import pytesseract
from PIL import Image

class Widget(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.load_ui()

    def print_test_message(self):
        #pytesseract.pytesseract.tesseract_cmd = r'C:\Users\USER\AppData\Local\Tesseract-OCR\tesseract.exe'
        text = pytesseract.image_to_string(Image.open("exam1.png"))
        self.window.errors_output.setPlainText(text);
        print("hello")

    def load_ui(self):
        loader = QUiLoader()
        ui_path = "form.ui"
        ui_file = QFile(ui_path)
        ui_file.open(QFile.ReadOnly)
        self.window = loader.load(ui_file, self)

        self.window.open_btn.clicked.connect(self.print_test_message)

        ui_file.close()

    def load_image(self):
        image_path = "exam1.png"
        pixmap = QPixmap(image_path)
        self.window.image_output.setPixmap(pixmap)
        self.window.image_output.show()

if __name__ == "__main__":
    app = QApplication(sys.argv)

    widget = Widget()
    widget.show()
    widget.load_image()

    sys.exit(app.exec())
