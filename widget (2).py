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

import cv2

class Widget(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.load_ui()
        self.connect_ui_elements()

    def load_ui(self):
        loader = QUiLoader()
        ui_path = "form.ui"
        ui_file = QFile(ui_path)
        ui_file.open(QFile.ReadOnly)
        self.window = loader.load(ui_file, self)
        ui_file.close()

    def connect_ui_elements(self):
        self.window.open_btn.clicked.connect(self.open_image)
        self.window.check_btn.clicked.connect(self.process_document)

    def open_image(self):
        image_path = "exam1.png"
        pixmap = QPixmap(image_path)
        self.window.image_output.setPixmap(pixmap)
        self.window.image_output.show()

    def process_document(self):
        #pytesseract.pytesseract.tesseract_cmd = r'C:\Users\USER\AppData\Local\Tesseract-OCR\tesseract.exe'

        exam_img = cv2.imread("exam1.png", cv2.IMREAD_COLOR)
        header_y_start = int(exam_img.shape[0]*0.083)
        header_y_end = int(exam_img.shape[0]*0.11)

        # TODO: read student code (using some library?)

        self.process_region(exam_img, header_y_start, header_y_end)
        self.process_subject_code(exam_img, header_y_start, header_y_end)
        self.process_subject_name(exam_img, header_y_start, header_y_end)

        # TODO: process answers
        #for r in range(0,img.shape[0],30):
        #    for c in range(0,img.shape[1],30):
        #        cv2.imwrite(f"img{r}_{c}.png",img[r:r+30, c:c+30,:])

        # TODO: Output header and answers also to the file

    def process_region(self, exam_img, header_y_start, header_y_end):
        region_y_start = int(exam_img.shape[1]*0.18)
        region_x_end = int(exam_img.shape[1]*0.3)
        filename = "exam1_region.png";
        cv2.imwrite(f"{filename}",exam_img[header_y_start:header_y_end, region_y_start:region_x_end])
        region_text = pytesseract.image_to_string(Image.open(filename))
        self.window.region_code_output.setText(region_text);
        try:
            os.remove(filename)
        except: pass

    def process_subject_code(self, exam_img, header_y_start, header_y_end):
        subject_code_x_start = int(exam_img.shape[1]*0.3)
        subject_code_x_end = int(exam_img.shape[1]*0.36)
        filename = "exam1_subject_code.png";
        cv2.imwrite(f"{filename}",exam_img[header_y_start:header_y_end, subject_code_x_start:subject_code_x_end])
        subject_code_text = pytesseract.image_to_string(Image.open(filename))
        self.window.subject_code_output.setText(subject_code_text);
        try:
            os.remove(filename)
        except: pass

    def process_subject_name(self, exam_img, header_y_start, header_y_end):
        subject_name_x_start = int(exam_img.shape[1]*0.36)
        subject_name_x_end = int(exam_img.shape[1]*0.5)
        filename = "exam1_subject_name.png";
        cv2.imwrite(f"{filename}",exam_img[header_y_start:header_y_end, subject_name_x_start:subject_name_x_end])
        subject_name_text = pytesseract.image_to_string(Image.open(filename), lang="rus")
        self.window.subject_name_output.setText(subject_name_text);
        try:
            os.remove(filename)
        except: pass

    def print_test_message(self):
        text = pytesseract.image_to_string(Image.open("./exam1.png"))
        self.window.errors_output.setPlainText(text);
        print("hello")
        img = cv2.imread("./exam1.png", cv2.IMREAD_COLOR)
        cv2.imshow("image", img)

if __name__ == "__main__":
    app = QApplication(sys.argv)
    widget = Widget()
    widget.show()

    sys.exit(app.exec())
