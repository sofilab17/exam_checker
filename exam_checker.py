import os # Удалять файлы
import sys # Выход из программы

# Типы UI виджетов, такие как кнопки (QPushButton), текстовые поля (QLineEdit), метки (QLabel), итд
from PySide6.QtWidgets import *

# Загрузить из .ui файла все виджеты
from PySide6.QtUiTools import QUiLoader

# Создать Pixmap объект из изображения и вывести на экран в QLabel виджет
from PySide6.QtGui import QPixmap

# Открывать/закрывать текстовые файлы
from PySide6.QtCore import QFile, QIODevice

# Распознавать текст из картинки
import pytesseract
# Открыть файл с изображением для pytesseract
from PIL import Image

# opencv функции для чтения/записи изображений и работы с ними (например разделение картинки на более мелкие картинки, чтобы распознавать на них текст)
import cv2

# Функция для детектирования баркодов на изображении
from pyzbar.pyzbar import decode

# Некоторые вспомогательные функции для работы с массивами
import numpy as np

# Добавить дату и время в название выходного файла с распознанными ответами
import time

# Чтобы определить путь выбранной папки
from pathlib import Path

# Главный класс, включающий в себя функции загрузки UI, открытии изображений ЕГЭ, чтения информации с бланков и проверки с правильными ответами
class ExamChecker(QMainWindow):
    # Конструктор класса. Запускается при создании объекта класса (exam_checker = ExamChecker())
    def __init__(self, parent=None):
        # Класс унаследован от родительского класса QMainWindow, поэтому необходимо запустить сначала родительский конструктор
        super().__init__(parent)
        # Загружаем UI!
        self.load_ui()
        # Привязываем функции на клик кнопок
        self.connect_functions_to_buttons()

        # Инициализируем некоторые поля класса и константы
        # Шаги 1 и 2 еще не выполнены, присвоим переменным false
        self.step_1 = False
        self.step_2 = False
        # Может использоваться 2 режима: работа с одним изображением или с целой папкой
        self.file_mode = False
        self.folder_mode = False
        # Константы для конфигурации pytesseract для различных видов текста
        self.REGION_CONFIG = "-c tessedit_char_whitelist=1234567890 --psm 7"
        self.REGION_LANG = "rus"
        self.SUBJECT_CODE_CONFIG = "-c tessedit_char_whitelist=1234567890 --psm 7"
        self.SUBJECT_CODE_LANG = "rus"
        self.SUBJECT_NAME_CONFIG = "-c tessedit_char_whitelist=АБВГДЕЖЗИЙКЛМНОПРСТУФХЦЧШЩЭЮЯ --psm 7"
        self.SUBJECT_NAME_LANG = "rus"
        self.FIXED_NUM_CONFIG = "-c tessedit_char_whitelist=1234567890 --psm 7"
        self.FIXED_NUM_LANG = "rus"

        self.ANSWERS_NUMBERS_CONFIG = "-c tessedit_char_whitelist=,-1234567890 --psm 7"
        self.ANSWERS_RUS_AND_NUMBERS_CONFIG = "-c tessedit_char_whitelist=,-АБВГДЕЁЖЗИЙКЛМНОПРСТУФХЦЧШЩЪЫЬЭЮЯ --psm 7"
        self.ANSWERS_ENG_AND_NUMBERS_CONFIG = "-c tessedit_char_whitelist=,-ABCDEFGHIJKLMNOPQRSTUVWXYZ --psm 7"
        self.ANSWERS_RUS_LANG = "rus"
        self.ANSWERS_ENG_LANG = "eng"
        self.ANSWERS_OTHER_LANG_CONFIG = ""
        self.ANSWERS_GERMAN_LANG = "deu"
        self.ANSWERS_FRENCH_LANG = "fra"
        self.ANSWERS_SPANISH_LANG = "spa"
        self.ANSWERS_CHINESE_LANG = "chi_sim"

        # Константы кодов предметов
        self.RUS_CODE = "01"
        self.MAT_PROF_CODE = "02"
        self.FIZ_CODE = "03"
        self.HIM_CODE = "04"
        self.INF_PROF_CODE = "05"
        self.BIO_CODE = "06"
        self.IST_CODE = "07"
        self.GEO_CODE = "08"
        self.ANG_CODE = "09"
        self.NEM_CODE = "10"
        self.FRA_CODE = "11"
        self.OBH_CODE = "12"
        self.ISP_CODE = "13"
        self.KIT_CODE = "14"
        self.LIT_CODE = "18"
        self.MAT_BAS_CODE = "22"
        self.INF_BAS_CODE = "25"

    # Функция загрузки UI
    def load_ui(self):
        # UI спроектирован в файле form.ui, запишем название файла в переменую ui_path
        ui_path = "form.ui"
        # Создадим объект типа Файл, передав параметром имя UI файла
        ui_file = QFile(ui_path)
        # Попробуем открыть файл. Если произошла ошибка, выведем ее в поле статуса выполнения программы
        if not ui_file.open(QIODevice.ReadOnly):
            self.show_status(f"Не получилось открыть файл {ui_path}: {ui_file.errorString()}", True)
            # Завершим программу, так как не получилось загрузить UI
            sys.exit(-1)
        # Создаем объект типа QUiLoader
        loader = QUiLoader()
        # Загружаем UI из файла в поле класса ui
        self.ui = loader.load(ui_file)
        # Файл больше не нужен, закрываем его
        ui_file.close()
        # Если в ui переменную ничего не считалось, то мы не можем загрузить UI, поэтому выведем сообщение об ошибке и закроем программу
        if not self.ui:
            self.show_status(f"UI не получен из файла {ui_path}: {loader.errorString()}", True)
            sys.exit(-1)
        self.ui.show()

    # Функция вывода ошибок или положительного статуса выполнения программы в специально отведенное поле
    def show_status(self, status, error):
        # Параметр status имеет тип string, поэтому мы можем вывести статус как текст в текстовое поле нашего UI errors_output
        self.ui.errors_output.setPlainText(status)
        if error:
            # Если тип сообщения был ошибка (error), то сделаем текст красным
            self.ui.errors_output.setStyleSheet("color: red;")
        else:
            # В остальных случаях текст будет зеленым
            self.ui.errors_output.setStyleSheet("color: green;")

    # Функция соединения кнопок и событий по клику
    def connect_functions_to_buttons(self):
        # По клику на кнопку open_file_btn выполняется функция open_exam_image (открытие файла с изображением экзамена и вывод картинки на экран)
        self.ui.open_file_btn.clicked.connect(self.open_exam_image)
        # По клику на кнопку open_folder_btn выполняется функция open_exam_folder (чтение изображенией экзамена из папки и вывод первой картинки на экран)
        self.ui.open_folder_btn.clicked.connect(self.open_exam_folder)
        # По клику на кнопку get_answers_btn выполняется функция read_correct_answers (чтение текстового файла с правильными ответами и вывод ответов на экран)
        self.ui.get_answers_btn.clicked.connect(self.read_correct_answers)
        # По клику на кнопку check_btn выполняется функция check_exams
        # (проверка экзаменационного бланка, которая включает в себя считывание баркода, региона, кода предмета и название, а также ответы на вопросы ЕГЭ)
        self.ui.check_btn.clicked.connect(self.check_exams)
        # По клику на кнопку clear_btn выполняется функция clear_form (все текстовые поля и поле вывода экзамена очищаются)
        self.ui.clear_btn.clicked.connect(self.clear_form)
        # Закрытие программы на Action "Закрыть" в меню
        self.ui.actionClose.triggered.connect(self.close_program)

    def close_program(self):
        sys.exit(0)

    # Открыть файл экзамена и вывести его на экран
    def open_exam_image(self):
        try:
            # TODO: Проверить, что это был файл типа картинки
            # Открыть диалоговое окно, чтобы выбрать файл, и записать имя выбранного файла в переменную
            self.exam_path = QFileDialog.getOpenFileName(self, "Выберите отсканированное изображение ЕГЭ")[0]
            # Вывести имя выбранного файла в текстовое поле
            self.ui.exam_path_ouput.setText(self.exam_path)
            # Вывести изображение экзамена на экран
            self.show_exam_image(self.exam_path)
            # Шаг 1 завершен без ошибок, присвоим переменной true
            self.step_1 = True
            # Режим работы с файлом активирован
            self.file_mode = True
            self.show_status("Файл с экзаменом открыт", False)
        except:
            self.show_status("Не удалось открыть файл с экзаменом, попробуйте еще раз", True)

   # Вывести изображение экзамена на в поле scroll area
    def show_exam_image(self, path):
        # Создать объект Pixmap, чтобы вывести на экран
        pixmap = QPixmap(path)
        # Изменить масштаб изображения, чтобы подошло под размер выходного поля scroll area
        pixmap = pixmap.scaledToWidth(self.ui.scroll_area_content.width())
        # Назначить пиксели в выходной виджет image_output
        self.ui.image_output.setPixmap(pixmap)
        # Отобразить пиксели
        self.ui.image_output.show()

    # Открыть папку с экзаменасм и вывести первое изображение из папки на экран
    def open_exam_folder(self):
        try:
            # Открыть диалоговое окно, чтобы выбрать папку, и записать имя выбранной папки в переменную
            folder_name = QFileDialog.getExistingDirectory(self, "Выберите папку с отсканированными изображениями ЕГЭ")
            self.exam_folder = Path(folder_name)
            # Вывести имя выбранной папки в текстовое поле
            self.ui.exam_path_ouput.setText(str(self.exam_folder))
            # Массив, чтобы хранить пути до всех файлов ЕГЭ из папки
            self.exam_paths = []
            # Итерируемся через все файлы в папке
            for path in os.listdir(self.exam_folder):
                # Проверяем если текущий путь это файл
                full_path = os.path.join(self.exam_folder, path)
                if os.path.isfile(full_path):
                   # Добавляем в массив
                    self.exam_paths.append(full_path)
            # Если есть хотя бы один файл
            if (len(self.exam_paths) > 0):
                # Выводим первое изображение на экран
                self.show_exam_image(self.exam_paths[0])
                self.show_status("Папка с экзаменами открыта\n,первый файл выведен на экран.", False)
            else:
                self.show_status("Открытая папка пуста\n, нечего проверять.", True)
                # Завершаем работу функции здесь, т.к. нет файлов для дальнейшей работы
                return

            # Шаг 1 завершен без ошибок, присвоим переменной true
            self.step_1 = True
            # Режим работы с папкой активирован
            self.folder_mode = True
        except:
            self.show_status("Не удалось открыть\nпапку с экзаменами,\nпопробуйте еще раз", True)

    # Считать файл с правильными ответами и вывести их на экран
    def read_correct_answers(self):
        try:
            # Открыть диалоговое окно, чтобы выбрать файл, и записать имя выбранного файла в переменную
            self.answers_path = QFileDialog.getOpenFileName()[0]
            # Вывести имя выбранного файла в текстовое поле
            self.ui.answers_path_ouput.setText(self.answers_path)
            # Создать переменную для массива правильных ответов
            self.answers = []
            # Считываем строки из файла одну за другой в цикле и убираем лишние пробелы с помощью rstrip функции
            with open(self.answers_path, encoding='utf-8') as file:
                self.answers = [line.rstrip() for line in file]
            # Объединяем все значения массива с помощью функции join, разделяя ответы новой строкой "\n". Выводим результат в текстовое поле ответов.
            self.ui.answers_output.setPlainText('\n'.join(self.answers))
            # Присваиваем переменной максимальное возможное значение правильных ответов, определяя длину массива правильных ответов
            self.max_possible_result = len(self.answers)
            # Шаг 1 завершен без ошибок, присвоим переменной true
            self.step_2 = True
            self.show_status("Файл с правильными ответами открыт", False)
        except:
            self.show_status("Не удалось открыть файл\nс правильными ответами,\nпопробуйте еще раз", True)

    # Проверить бланки экзаменов
    def check_exams(self):
        # Очистить форму результатов перед началом обработки
        self.clear_results()

        # Если шаг 1 или 2 еще не выполнен - мы не можем начать проверку, выводим сообщение с напоминанием и завершаем выполнение этой функции
        if not self.step_1:
            self.show_status("Шаг 1 еще не выполнен.\nСначала откройте файл экзамена,\nпотом повторите попытку проверки.", True)
            return
        if not self.step_2:
            self.show_status("Шаг 2 еще не выполнен.\nСначала откройте файл ответов,\nпотом повторите попытку проверки.", True)
            return

        if (self.file_mode):
            self.check_exam(self.exam_path, True)
        elif (self.folder_mode):
            if (len(self.exam_paths) > 0):
                self.check_exam(self.exam_paths[0], True)
            for i in range(1, len(self.exam_paths)):
                path = self.exam_paths[i]
                self.check_exam(path, False)
        else:
            self.show_status("Ни один файл для проверки не выбран.\nПовторите попытку.", True)

    def check_exam(self, path, show_results):
        # По умолчанию проверка успешна. При появлении ошибок, статус заменяется на сообщение об ошибке
        self.show_status("Проверка прошла успешно", False)

        # Читаем изображение экзамена
        try:
            gray_exam_img = cv2.imread(path, 0)
            # Применяем threshold фильтр, чтобы сделать изображение бинарным (черно-белым, без серых оттенков)
            self.exam_img = cv2.threshold(gray_exam_img, 250, 255, cv2.THRESH_BINARY | cv2.THRESH_OTSU)[1]
            # Убрать шум с изображения (убрать мелкие точки вокруг текста)
            self.exam_img = cv2.fastNlMeansDenoising(self.exam_img, None, 60, 7, 21)

            # Обрабатываем шапку бланка ЕГЭ, а затем часть с ответами
            self.process_header(show_results)
            self.process_answers(show_results)
        except:
            self.show_status("Не удалось проверить экзамен, попробуйте другой файл", True)

    # Функция получения пикселя изображения экзамена по оси Y в соответствии с указанной пропорцией (процентом)
    def get_y(self, proportion):
        return int(self.exam_img.shape[0]*proportion)

    # Функция получения пикселя изображения экзамена по оси X в соответствии с указанной пропорцией (процентом)
    def get_x(self, proportion):
        return int(self.exam_img.shape[1]*proportion)

    # Обработать шапку экзамена
    def process_header(self, show_results):
        # Считать баркод
        self.read_barcode(show_results)

        # Задать начальное и конечное значение Y для распознавания региона, кода предмета и названия предмета
        header_y_start = self.get_y(0.088)
        header_y_end = self.get_y(0.12)
        # Распознать текст региона
        self.recognize_region(header_y_start, header_y_end, show_results)
        # Распознать текст кода предмета
        self.recognize_subject_code(header_y_start, header_y_end, show_results)
        # Распознать текст названия предмета
        self.recognize_subject_name(header_y_start, header_y_end, show_results)
        # TODO: Сравнить код предмета и название, и вывести ошибку, если не соответствуют

    # Функция считывания баркода
    def read_barcode(self, show_results):
        # Обрезаем начало X, чтобы исключить попадания QRcode (не несет важной информации?)
        barcodes_image = self.exam_img[self.get_y(0.12):self.get_y(0.2), self.get_x(0.07):self.get_x(0.4)]
        # TODO: Убрать вызов функции imwrite, используемый для тестирования
        #cv2.imwrite("barcodes.png", self.exam_img[self.get_y(0.12):self.get_y(0.2), self.get_x(0.07):self.get_x(0.4)])

        self.barcode = ''
        # Из обрезанного изображения распознаем баркоды
        detectedBarcodes = decode(barcodes_image)
        if not detectedBarcodes and show_results:
            self.show_status("Баркод не найден или испорчен", True)
        else:
            # Итерируемся по найденным баркодам (по факту должен быть один)
            for barcode in detectedBarcodes:
                # Декодировать данные баркода в строку по кодирующему формату UTF-8
                self.barcode = barcode.data.decode('UTF-8')
                # Вывести значение баркода в текстовое поле, если переменная show_results True
                if (show_results):
                    self.ui.student_code_output.setText(self.barcode)
        if self.barcode == '' and show_results:
            self.show_status("Баркод не найден", True)

    # Распознать текст региона
    def recognize_region(self, y_start, y_end, show_results):
        self.region = self.recognize_text(y_start, y_end, self.get_x(0.22), self.get_x(0.3), self.REGION_CONFIG, self.REGION_LANG)
        self.region = self.filter_recognized_text(self.region)
        # TODO: Убрать вызов функции imwrite, используемый для тестирования
        #cv2.imwrite("region.png", self.exam_img[y_start:y_end, self.get_x(0.22):self.get_x(0.3)])
        # Вывести текст региона на экран, если переменная show_results True, или ошибку, если нет результата
        if len(self.region) > 0 and show_results:
            self.ui.region_code_output.setText(self.region)
        else:
            if (show_results):
                self.show_status("Не удалось распознать регион", True)

    # Распознать текст кода предмета
    def recognize_subject_code(self, y_start, y_end, show_results):
        self.subject_code = self.recognize_text(y_start, y_end, self.get_x(0.3), self.get_x(0.38), self.SUBJECT_CODE_CONFIG, self.SUBJECT_CODE_LANG)
        self.subject_code = self.filter_recognized_text(self.subject_code)
        # TODO: Убрать вызов функции imwrite, используемый для тестирования
        #cv2.imwrite("subject_code.png", self.exam_img[y_start:y_end, self.get_x(0.3):self.get_x(0.38)])
        # Вывести текст кода предмета на экран, если переменная show_results True, или ошибку, если нет результата
        if len(self.subject_code) > 0 and show_results:
            self.ui.subject_code_output.setText(self.subject_code)
        else:
            if (show_results):
                self.show_status("Не удалось распознать код предмета", False)

    # Распознать текст названия предмета
    def recognize_subject_name(self, y_start, y_end, show_results):
        self.subject_name = self.recognize_text(y_start, y_end, self.get_x(0.38), self.get_x(0.48), self.SUBJECT_NAME_CONFIG, self.SUBJECT_NAME_LANG)
        self.subject_name = self.filter_recognized_text(self.subject_name)
        # TODO: Убрать вызов функции imwrite, используемый для тестирования
        cv2.imwrite("subject_name.png", self.exam_img[y_start:y_end, self.get_x(0.38):self.get_x(0.48)])
        # Вывести текст названия предмета, если переменная show_results True, на экран или ошибку, если нет результата
        if len(self.subject_name) > 0 and show_results:
            self.ui.subject_name_output.setText(self.subject_name)
        else:
            if (show_results):
                self.show_status("Не удалось распознать название предмета", True)

    # Общая функция распознавания текста из картинки
    def recognize_text(self, y_start, y_end, x_start, x_end, config, language):
        # Создаем временный файл с обрезанным изображением, чтобы считать его для библиотеки pytesseract
        filename = "tmp.png";
        cv2.imwrite(f"{filename}", self.exam_img[y_start:y_end, x_start:x_end])

        # Детектируем текст с изображения и возвращаем его из функции
        text = pytesseract.image_to_string(Image.open(filename), config=f"{config}", lang=f"{language}")
        try:
            # Удаляем временно созданный файл
            os.remove(filename)
        except: pass
        return text

    # Обрабатываем ответы на бланке ЕГЭ
    def process_answers(self, show_results):
        # Запишем распознанные ответы в файл,
        # создадим уникальное название с текущим временем
        current_day_time = time.strftime("%Y%m%d_%H%M%S")
        filename = "results_" + self.barcode + "_time_" + current_day_time + ".txt"
        file = open(filename, "a")  # append mode
        # Запишем баркод, код и название предмета в файл
        file.write("Баркод: " + self.barcode + ", код предмета: " + self.subject_code\
                   + ", название предмета: " + self.subject_name + "\n\n")
        file.write("Ответы:" + "\n")
        # Изначально набранный балл 0
        self.received_result = 0

        start_x_1 = 0.06
        end_x_1 = 0.5
        start_x_2 = 0.53
        end_x_2 = 0.97

        # Создадим массив для хранения распознанных ответов
        self.recognized_answers = []

        # Если ответов меньше чем 20, то не нужно идти до конца бланка в первой колонке
        if len(self.answers) < 20:
            self.process_answers_column(0, len(self.answers), start_x_1, end_x_1)
        else:
            self.process_answers_column(0, 20, start_x_1, end_x_1)
            # Если ответов меньше чем 40, то не нужно идти до конца бланка во второй колонке
            if len(self.answers) < 40:
                self.process_answers_column(20, len(self.answers), start_x_2, end_x_2)
            else:
                self.process_answers_column(20, 40, start_x_2, end_x_2)

        self.process_extra_answers()

        # Запишем результаты в файл
        self.output_answers(file)
        file.write("\nРезультат: " + str(self.received_result)+ " из " + str(self.max_possible_result) + "\n")
        # Закрыть файл с распознанными ответами
        file.close()
        # Вывести в текстовое поле результат распознанных ответов из максимального количества возможных, если переменная show_results True
        if (show_results):
            self.ui.result_num_output.setText(str(self.received_result) + " из " + str(self.max_possible_result))
        # Если найдено 0 правильных ответов, выводим сообщение о возможной проблеме
        if self.received_result == 0:
            self.show_status("Не найден ни один правильный ответ.\nВозможно файл экзамена имеет неверные\nпропорции ширины и высоты, или файл\nс правильными ответами пуст/неверно заполнен.", True)
        # TODO: Дополнительно обработать исправленные ответы (6 отдельных полей в самом низу бланка)
        # TODO: Подсветить несовпадения ответов на бланке

    # Обработать 6 полей для ввода исправленных ответов
    def process_extra_answers(self):
        # Массив, который хранит номер исправленного ответа и исправленное значение
        self.fixed_answers = []
        config_answer = self.define_config_for_answers()
        lang_answer = self.define_language_for_answers()

        # Обработаем первые три ответа в колонке
        x_start_num = self.get_x(0.05)
        x_end_num = self.get_x(0.1)
        x_start_answer = self.get_x(0.11)
        x_end_answer = self.get_x(0.5)
        y_prev = self.get_y(0.831)
        y_inc = self.get_y(0.0263)
        for i in range(0, 3):
            fixed_num = self.recognize_text(y_prev, y_prev + y_inc, x_start_num, x_end_num, self.FIXED_NUM_CONFIG, self.FIXED_NUM_LANG)
            fixed_num = self.filter_recognized_text(fixed_num)
            fixed_answer = self.recognize_text(y_prev, y_prev + y_inc, x_start_answer, x_end_answer, config_answer, lang_answer)
            fixed_answer = self.filter_recognized_text(fixed_answer)
            self.fixed_answers.append((fixed_num, fixed_answer))
            print("fixed", self.fixed_answers)
            # TODO: Убрать вызов функции imwrite, используемый для тестирования
            #cv2.imwrite(f"fixed_num_img_{i + 1}.png", self.exam_img[y_prev:(y_prev + y_inc), x_start_num:x_end_num])
            #cv2.imwrite(f"fixed_answer_img_{i + 1}.png", self.exam_img[y_prev:(y_prev + y_inc), x_start_answer:x_end_answer])
            y_prev += y_inc

        # Обработаем следующие три ответа во второй колонке
        x_start_num = self.get_x(0.52)
        x_end_num = self.get_x(0.57)
        x_start_answer = self.get_x(0.58)
        x_end_answer = self.get_x(0.97)
        y_prev = self.get_y(0.831)
        for i in range(0, 3):
            fixed_num = self.recognize_text(y_prev, y_prev + y_inc, x_start_num, x_end_num, self.FIXED_NUM_CONFIG, self.FIXED_NUM_LANG)
            fixed_num = self.filter_recognized_text(fixed_num)
            fixed_answer = self.recognize_text(y_prev, y_prev + y_inc, x_start_answer, x_end_answer, config_answer, lang_answer)
            fixed_answer = self.filter_recognized_text(fixed_answer)
            self.fixed_answers.append((fixed_num, fixed_answer))
            # TODO: Убрать вызов функции imwrite, используемый для тестирования
            #cv2.imwrite(f"fixed_num_img_{i + 4}.png", self.exam_img[y_prev:(y_prev + y_inc), x_start_num:x_end_num])
            #cv2.imwrite(f"fixed_answer_img_{i + 4}.png", self.exam_img[y_prev:(y_prev + y_inc), x_start_answer:x_end_answer])
            y_prev += y_inc

        # Пройдемся по каждому исправленному ответу и подставим его значение в массив найденных ранее ответов
        for fixed in self.fixed_answers:
            try:
                # Попробуем перевести номер вопроса в string и потом в int
                index = int(str(fixed[0])) - 1
                # Если номер ответа корректный (в диапазоне допустимых значений), то перезапишем ответ
                if index >= 0 and index < len(self.recognized_answers):
                    self.recognized_answers[index] = fixed[1]
            except: pass

    # Вывести правильные ответы в файл
    def output_answers(self, file):
        # Создадим переменную для того, чтобы итерироваться по массиву правильных ответов и выводить номер ответа в файл
        i = 0
        for recognized_answer in self.recognized_answers:
            # Создадим переменную, чтобы отобразить статус ответа в файле
            summary = "[Неверно]"
            # Если распознанный ответ сходится с правильным ответом, то инкрементируем значение с определенными правильными ответами
            if recognized_answer == self.answers[i]:
                self.received_result += 1
                # Изменим сообщение о статусе ответа, потому что он правильный
                summary = "[Верно]"
            # Записать строку с результатом в файл, переданный аргументом в функцию
            file.write(str(i + 1) + ": " + recognized_answer + "    " + summary + "\n")
            i += 1

    # Обработать ответы из одной колонки бланка ЕГЭ
    def process_answers_column(self, i_start, i_end, x_start, x_end):
        # Назначить инкремент по оси Y, и предыдущее значение Y
        y_inc = 0.0263
        y_prev = 0.2375
        # Итерируемся по каждому ответу
        for i in range(i_start, i_end):
            # После пятого ответа инкремент по оси Y чуть больше, поэтому добавляем большее значение
            if i % 5 == 0:
                y_prev += 0.008
            recognized_answer = self.recognize_text(self.get_y(y_prev), self.get_y(y_prev + y_inc), self.get_x(x_start), self.get_x(x_end), self.define_config_for_answers(), self.define_language_for_answers())
            recognized_answer = self.filter_recognized_text(recognized_answer)
            self.recognized_answers.append(recognized_answer)
            # TODO: Убрать вызов функции imwrite, используемый для тестирования
            #cv2.imwrite(f"img_{i+1}.png", self.exam_img[self.get_y(y_prev):self.get_y(y_prev + y_inc), self.get_x(x_start):self.get_x(x_end)])
            # Обновим последнее значение Y для следующей итерации
            y_prev += y_inc

    # Отфильтровать распознанный текст: убрать ненужные символы
    def filter_recognized_text(self, text):
        # Уберем из результата символ конца строки и другой non-ascii символ, и вернем обработанный результат
        filtered_text = text.replace("\n", "")
        return filtered_text.replace("\x0c", "")

    # Подобрать соответствующую конфигурацию букв/чисел для распознавания текста в зависимости от предмета
    def define_config_for_answers(self):
        if self.subject_code == self.MAT_PROF_CODE or self.subject_code == self.FIZ_CODE or self.subject_code == self.HIM_CODE or self.subject_code == self.MAT_BAS_CODE:
            return self.ANSWERS_NUMBERS_CONFIG
        elif self.subject_code == self.INF_PROF_CODE or self.subject_code == self.INF_BAS_CODE or self.subject_code == self.ANG_CODE:
            return self.ANSWERS_ENG_AND_NUMBERS_CONFIG
        elif self.subject_code == self.NEM_CODE or self.subject_code == self.FRA_CODE or self.subject_code == self.ISP_CODE or self.subject_code == self.KIT_CODE:
            return self.ANSWERS_OTHER_LANG_CONFIG
        else:
            return self.ANSWERS_RUS_AND_NUMBERS_CONFIG


    # Подобрать соответствующий язык для распознавания текста в зависимости от предмета
    def define_language_for_answers(self):
        if self.subject_code == self.NEM_CODE:
            return self.ANSWERS_GERMAN_LANG
        if self.subject_code == self.FRA_CODE:
            return self.ANSWERS_FRENCH_LANG
        if self.subject_code == self.ISP_CODE:
            return self.ANSWERS_SPANISH_LANG
        if self.subject_code == self.KIT_CODE:
            return self.ANSWERS_CHINESE_LANG
        elif self.subject_code == self.MAT_PROF_CODE or self.subject_code == self.FIZ_CODE or self.subject_code == self.HIM_CODE or self.subject_code == self.INF_PROF_CODE or self.subject_code == self.ANG_CODE or self.subject_code == self.MAT_BAS_CODE or self.subject_code == self.INF_BAS_CODE:
            return self.ANSWERS_ENG_LANG
        else:
            return self.ANSWERS_RUS_LANG

    # Очистить все поля UI
    def clear_form(self):
        # Очищаем поля с названием файлов
        self.ui.exam_path_ouput.clear()
        self.ui.answers_path_ouput.clear()
        # Очищаем форму результатов
        self.clear_results()
        # Очищаем поле с выводом правильных ответов
        self.ui.answers_output.clear()
        # Очищаем поле с выводом картинки экзамена
        self.ui.image_output.clear()
        # Поля очищены, поэтому шаги 1 и 2 тоже очищаются, присвоим переменным false
        self.step_1 = False
        self.step_2 = False
        # Файловый режим и режим папки тоже сбрасываются
        self.file_mode = False
        self.folder_mode = False

    def clear_results(self):
        self.ui.student_code_output.clear()
        self.ui.region_code_output.clear()
        self.ui.subject_code_output.clear()
        self.ui.subject_name_output.clear()
        self.ui.result_num_output.clear()
        # Очищаем поле ошибок
        self.ui.errors_output.clear()

# Старт программы
if __name__ == "__main__":
    # Создаем приложение
    app = QApplication(sys.argv)
    # Создаем объект класса ExamChecker
    exam_checker = ExamChecker()
    # При завершении работы приложения app (нажатие на крестик), работа программы тоже завершается
    sys.exit(app.exec())
