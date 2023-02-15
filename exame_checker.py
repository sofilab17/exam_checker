import os
from pathlib import Path
import sys

from PySide6.QtWidgets import *
from PySide6.QtCore import QFile, QIODevice
from PySide6.QtUiTools import QUiLoader
from PySide6.QtGui import QPixmap

import pytesseract
from PIL import Image
import cv2
from pyzbar.pyzbar import decode

class ExamChecker(QMainWindow):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.load_ui()
        self.connect_functions_to_buttons()

    def load_ui(self):
        ui_path = "form.ui"
        ui_file = QFile(ui_path)
        if not ui_file.open(QIODevice.ReadOnly):
            self.show_status(f"Не получилось открыть файл {ui_file_name}: {ui_file.errorString()}", True)
            sys.exit(-1)
        loader = QUiLoader()
        self.ui = loader.load(ui_file)
        ui_file.close()
        if not self.ui:
            selfshow_status(loader.errorString(), True)
            sys.exit(-1)
        self.ui.show()

    def show_status(self, status, error):
        self.ui.errors_output.setPlainText(status)
        if error:
            self.ui.errors_output.setStyleSheet("color: red;")
        else:
            self.ui.errors_output.setStyleSheet("color: green;")

    def connect_functions_to_buttons(self):
        self.ui.open_btn.clicked.connect(self.open_exam_image)
        self.ui.check_btn.clicked.connect(self.check_exam)
        self.ui.get_answers_btn.clicked.connect(self.read_answers)

    def open_exam_image(self):
        # todo: try/catch and resize according to canvas size
        self.exam_path = QFileDialog.getOpenFileName()[0]
        self.ui.exam_path_ouput.setText(self.exam_path)

        pixmap = QPixmap(self.exam_path)
        self.ui.image_output.setPixmap(pixmap)
        self.ui.image_output.show()

    def read_answers(self):
        self.answers_path = QFileDialog.getOpenFileName()[0]
        self.ui.answers_path_ouput.setText(self.answers_path)
        with open(self.answers_path) as file:
            answers = [line.rstrip() for line in file]
        self.ui.answers_output.setPlainText('\n'.join(answers))

    def check_exam(self):
        self.show_status("Проверка прошла успешно", False)
        # todo: try/except + outpur error
        self.exam_img = cv2.imread(self.exam_path, cv2.IMREAD_COLOR)
        self.process_header()

        # todo:
        # read answers in container
        # column 1 loop
        # column 2 loop
        # compare with reference answers
        # write results to the file and in the output text


        # TODO: process answers
        #for r in range(0,img.shape[0],30):
        #    for c in range(0,img.shape[1],30):
        #        cv2.imwrite(f"img{r}_{c}.png",img[r:r+30, c:c+30,:])

        # TODO: Output header and answers also to the file

    def get_y(self, proportion):
        return int(self.exam_img.shape[0]*proportion)

    def get_x(self, proportion):
        return int(self.exam_img.shape[1]*proportion)

    def process_header(self):
        self.read_barcode()

        header_y_start = self.get_y(0.083)
        header_y_end = self.get_y(0.11)
        self.recognize_region(header_y_start, header_y_end)
        self.recognize_subject_code(header_y_start, header_y_end)
        self.recognize_subject_name(header_y_start, header_y_end)

    def read_barcode(self):
        # cut to exclude QRcode
        barcodes_image = self.exam_img[self.get_y(0.0):self.get_y(0.2), self.get_x(0.07):self.get_x(1.0)]

        detectedBarcodes = decode(barcodes_image)
        if not detectedBarcodes:
            self.show_status("Баркод не найден или испорчен", True)
        else:
            prev_barcode = ''
            for barcode in detectedBarcodes:
                print("detected")
                #(x, y, w, h) = barcode.rect
                #cv2.rectangle(img, (x-10, y-10), (x + w+10, y + h+10), (255, 0, 0), 2)
                if prev_barcode and prev_barcode != barcode.data:
                    self.show_status("Баркоды на бланке должны быть одинаковы", True)
                prev_barcode = barcode.data
                self.ui.student_code_output.setText(barcode.data.decode('UTF-8'))

    def recognize_region(self, y_start, y_end):
        self.region = self.recognize_text(y_start, y_end, self.get_x(0.18), self.get_x(0.3), "eng")
        self.ui.region_code_output.setText(self.region)

    def recognize_subject_code(self, y_start, y_end):
        self.subject_code = self.recognize_text(y_start, y_end, self.get_x(0.3), self.get_x(0.36), "eng")
        self.ui.subject_code_output.setText(self.subject_code)

    def recognize_subject_name(self, y_start, y_end):
        self.subject_name = self.recognize_text(y_start, y_end, self.get_x(0.36), self.get_x(0.5), "rus")
        self.ui.subject_name_output.setText(self.subject_name)

    def recognize_text(self, y_start, y_end, x_start, x_end, language):
        filename = "exam1_region.png";
        cv2.imwrite(f"{filename}", self.exam_img[y_start:y_end, x_start:x_end])
        text = pytesseract.image_to_string(Image.open(filename), lang=f"{language}")
        try:
            os.remove(filename)
        except: pass
        return text

if __name__ == "__main__":
    app = QApplication(sys.argv)
    exam_checker = ExamChecker()
    sys.exit(app.exec())
