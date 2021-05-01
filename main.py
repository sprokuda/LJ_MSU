import sys
import os
import time
from PyQt5 import QtCore, QtWidgets, QtGui
from PyQt5.QtWidgets import *

from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5.QtCore import Q_ARG

from matplotlib.backends.backend_qt5agg import FigureCanvasQTAggBase as FigureCanvas
import matplotlib.pyplot as plt
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure
import numpy as np
import json


from lissajousgen import LJ
from waitspinner import QtWaitingSpinner

# Настройки фигуры по умолчанию
default_settings = {
    "freq_x": 2,
    "freq_y": 3,
    "color": "midnightblue",
    "width": 2
}



# Цвета для matplotlib
with open("mpl.json", mode="r", encoding="utf-8") as f:
    mpl_color_dict = json.load(f)

# класс для отрисовки изображений, будет востребован количестве графиков более одного.
class DrawFigure(FigureCanvas):
    def __init__(self, parent=None, width=4, height=4, dpi=100, settings = default_settings):
        self._fig = plt.figure(figsize=(width,  height), dpi=dpi)
        super(DrawFigure, self).__init__(self._fig)
        self.setParent(parent)
# отрисовывается в "растягиваемом" = Expanding режиме. но возможно нужна
# реализация с фиксированным размером задаваемом пользователем
        FigureCanvas.setSizePolicy(self, QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Expanding)
        FigureCanvas.updateGeometry(self)
        self._ax = self._fig.add_subplot(111)
        self._settings = settings
# отрисовка графика
    def draw_plot(self, data, settings):

        # Строим график
        self._settings = settings
        self._ax.plot(data[0,:], data[1,:],
                      color=self._settings["color"], linewidth=self._settings["width"])

        plt.axis("off")
        self.draw()

# базовый класс изменен на QWidget для облегчения масштабирования виджета с графиком
#class LissajousWindow(QMainWindow):
class LissajousWindow(QWidget):
    def __init__(self,  parent = None):
        super(LissajousWindow, self).__init__(parent)


# контроллер потока для выполнения расчетов
        self.thread = QThread()
        self._lj = LJ()
# передача класса в контроллер
        self._lj.moveToThread(self.thread)
# соединение сигнала окончания расчетов с отрисовкой графика
        self._lj.signalData.connect(self.plot_lj_fig)
# запуск метода run контроллера потока
        self.thread.start()

# инифилизация GUI
        self.initUI()

    def initUI(self):

        # Ставим версию и иконку
        with open("version.txt", "r") as f:
            version = f.readline()
        self.setWindowTitle("Генератор фигур Лиссажу. Версия {}. CC BY-SA 4.0 Ivanov".format(
            version
        ))
        scriptDir = os.path.dirname(os.path.realpath(__file__))
        self.setWindowIcon(QtGui.QIcon(scriptDir + os.path.sep + "icon.bmp"))
# инициализация словаря настроек
        self._settings = {}

# создание главного слоя элементов интерфейса, горизонтальное построение
        self._layout = QHBoxLayout(self)
        self.setLayout(self._layout)

# создания экземпляра класса-рисовальщика графика DrawFigure
        self._drw_fig= DrawFigure(self, 5, 5, 150, default_settings)
        self._drw_fig.draw_plot(self._lj.doCalc(default_settings["freq_x"],
                                                         default_settings["freq_y"]), default_settings)
# добавление экземпляра класса-рисовальщика графика DrawFigure
        self._layout.addWidget(self._drw_fig)

# создание слоя элементов управления, вертикальное построение
        self._ctrl_layout = QVBoxLayout(self)

# создание слоя элементов установки частоты X, горизонтальное построение
        self._x_layout = QHBoxLayout(self)

# создание пояснения для установки частоты X, добавление ее в слой, установка выравнивания
        self._x_freq_lb = QLabel("Частота X:")
        self._x_layout.addWidget(self._x_freq_lb)
        self._x_layout.setAlignment(self._x_freq_lb, Qt.AlignRight)

# создание элемента текстового ввода для установки частоты X, добавление его в слой, установка выравнивания
        self._x_freq_ln_edt = QLineEdit("%d"%default_settings["freq_x"])
        self._x_freq_ln_edt.setFixedSize(30, 30)
        self._x_layout.addWidget(self._x_freq_ln_edt)
        self._x_layout.setAlignment(self._x_freq_ln_edt, Qt.AlignRight)

# добавление слоя установки частоты X в слой элементов управления
        self._ctrl_layout.addLayout(self._x_layout)

# создание слоя элементов установки частоты Y, горизонтальное построение
        self._y_layout = QHBoxLayout(self)

# создание пояснения для установки частоты Y, добавление ее в слой, установка выравнивания
        self._y_freq_lb = QLabel("Частота Y:")
        self._y_layout.addWidget(self._y_freq_lb)
        self._y_layout.setAlignment(self._y_freq_lb, Qt.AlignRight)

# создание элемента текстового ввода для установки частоты Y, добавление его в слой, установка выравнивания
        self._y_freq_ln_edt = QLineEdit("%d"%default_settings["freq_y"])
        self._y_freq_ln_edt.setFixedSize(30, 30)
        self._y_layout.addWidget(self._y_freq_ln_edt)
        self._y_layout.setAlignment(self._y_freq_ln_edt, Qt.AlignRight)

# добавление слоя установки частоты Y в слой элементов управления
        self._ctrl_layout.addLayout(self._y_layout)

# создание слоя элементов установки цвета, горизонтальное построение
        self._clr_layout = QHBoxLayout(self)

# создание пояснения для установки цвета, добавление ее в слой, установка выравнивания
        self._clr_blb = QLabel("Цвет:")
        self._clr_layout.addWidget(self._clr_blb)
        self._clr_layout.setAlignment(self._clr_blb, Qt.AlignRight)

# создание экземпляра комбо-бокс для установки цвета, добавление элементов комбо-бокс,
# добавление ее в слой, установка размеров
        self._clr_combo = QComboBox()
        self._clr_combo.addItems(["Синий","Зелёный","Красный", "Жёлтый"])
        self._clr_combo.setFixedSize(80, 30)
        self._clr_layout.addWidget(self._clr_combo)

# добавление слоя установки цвета в слой элементов управления
        self._ctrl_layout.addLayout(self._clr_layout)

# создание слоя элементов установки толщины линии, горизонтальное построение
        self._thnk_layout = QHBoxLayout(self)

# создание пояснения для установки толщины линии, добавление ее в слой, установка выравнивания
        self._thnk_blb = QLabel("Толщина \n линии:")
        self._thnk_layout.addWidget(self._thnk_blb)
        self._thnk_layout.setAlignment(self._thnk_blb, Qt.AlignRight)

# создание экземпляра комбо-бокс для установки толщины линии, добавление элементов комбо-бокс,
# добавление ее в слой, установка размеров
        self._thnk_combo = QComboBox()
        self._thnk_combo.addItems(["1", "2", "3", "4"])
        self._thnk_combo.setFixedSize(50, 30)
        self._thnk_layout.addWidget(self._thnk_combo)

# добавление слоя установки толшины линии в слой элементов управления
        self._ctrl_layout.addLayout(self._thnk_layout)

# добавление кнопки "Обновить фигуру", установка ее размеров и выравнивания
        self._update_btn = QPushButton("Обновить фигуру")
        self._update_btn.setFixedSize(120, 30)
        self._ctrl_layout.addWidget(self._update_btn)
        self._ctrl_layout.setAlignment(self._update_btn, Qt.AlignRight)

# добавление кнопки "Сохранить фигуру", установка ее размеров и выравнивания
        self._save_btn = QPushButton("Сохранить фигуру")
        self._save_btn.setFixedSize(120, 30)
        self._ctrl_layout.addWidget(self._save_btn)
        self._ctrl_layout.setAlignment(self._save_btn, Qt.AlignRight)

# создание экземпляра элемента заполнения
        self._ctrl_layout.addStretch()

# добавление элемента заполнения
        self._layout.addLayout(self._ctrl_layout)

# создание экземпляра элемента индикиции ожидания
        self._spinner = QtWaitingSpinner(self)

# соединение сигнала нажатия кнопки  с методом-обработчиком
        self._update_btn.clicked.connect(self.plot_button_click_handler)

# соединение сигнала нажатия кнопки с запуском индикации ожидания
        self._update_btn.clicked.connect(self._spinner.start)

# соединение сигнала окончания расчета с остановкой индикации ожидания
        self._lj.signalData.connect(self._spinner.stop)

# соединение сигнала нажатия кнопки  с методом-обработчиком
        self._save_btn.clicked.connect(self.save_button_click_handler)

# установка начального размера окна
        self.resize(400, 300)

# установка начального положения окна
        self.move(300, 150)

# отрисовка окна
        self.show()


# функция обработки нажатия кнопки "Обновить фигуру"
    def plot_button_click_handler(self):
        """
        Обработчик нажатия на кнопку применения настроек
        """
        # Получаем данные из текстовых полей и обновляем словарь
        self._settings["freq_x"] = float(self._x_freq_ln_edt.text())
        self._settings["freq_y"] = float(self._y_freq_ln_edt.text())
        self._settings["color"] = mpl_color_dict[self._clr_combo.currentText()]
        self._settings["width"] = int(self._thnk_combo.currentText())

# Вызываем метод потока вычислений
        QMetaObject.invokeMethod(self._lj, 'callCalc', Qt.QueuedConnection,
                                 Q_ARG(int, self._settings["freq_x"]),
                                 Q_ARG(int, self._settings["freq_y"]))



    def plot_lj_fig(self, data):
        """
        Обновление фигуры
        """
        self._drw_fig._ax.cla()
        self._drw_fig.draw_plot(data, self._settings)

    def save_button_click_handler(self):
        """
        Обработчик нажатия на кнопку сохранения настроек
        """
        file_path, _ = QFileDialog.getSaveFileName(self, "Сохранение изображения", "C:/",
                                                            "PNG(*.png);;JPEG(*.jpg *.jpeg);;All Files(*.*) ")

        if file_path == "":
            return

#запись изображения в файл
        plt.savefig(file_path)



if __name__ == "__main__":
    # Инициализируем приложение Qt
    app = QApplication(sys.argv)

    # Создаём и настраиваем главное окно
    main_window = LissajousWindow()

    # Показываем окно
    main_window.show()

    # Запуск приложения
    # На этой строке выполнение основной программы блокируется
    # до тех пор, пока пользователь не закроет окно.
    # Вся дальнейшая работа должна вестись либо в отдельных потоках,
    # либо в обработчиках событий Qt.
    sys.exit(app.exec_())
