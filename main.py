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

class DrawFigure(FigureCanvas):
    def __init__(self, parent=None, width=4, height=4, dpi=100, settings = default_settings):
        self._fig = plt.figure(figsize=(width,  height), dpi=dpi)
        super(DrawFigure, self).__init__(self._fig)
        self.setParent(parent)

        FigureCanvas.setSizePolicy(self, QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Expanding)
        FigureCanvas.updateGeometry(self)
        self._ax = self._fig.add_subplot(111)
        self._settings = settings
    def draw_plot(self, data, settings):

        # Строим график
        self._settings = settings
        self._ax.plot(data[0,:], data[1,:],
                      color=self._settings["color"], linewidth=self._settings["width"])

        plt.axis("off")
        # Нужно, чтобы все элементы не выходили за пределы холста
        #plt.tight_layout()

        #self.resize(300, 300)
        self.draw()


#class LissajousWindow(QMainWindow):
class LissajousWindow(QWidget):
    def __init__(self,  parent = None):
        super(LissajousWindow, self).__init__(parent)



        self.thread = QThread()
        self._lj = LJ()
        self._lj.moveToThread(self.thread)
        self._lj.signalData.connect(self.plot_lj_fig)
        self.thread.start()

        self.stopSpinner = QtCore.pyqtSignal(np.ndarray)

        self.initUI()

    def signalExample(self, data):
        print(data)

    def initUI(self):

        # Ставим версию и иконку
        with open("version.txt", "r") as f:
            version = f.readline()
        self.setWindowTitle("Генератор фигур Лиссажу. Версия {}. CC BY-SA 4.0 Ivanov".format(
            version
        ))
        scriptDir = os.path.dirname(os.path.realpath(__file__))
        self.setWindowIcon(QtGui.QIcon(scriptDir + os.path.sep + "icon.bmp"))

        self._settings = {}


        self._layout = QHBoxLayout(self)
        self.setLayout(self._layout)



        self._drw_fig= DrawFigure(self, 5, 5, 150, default_settings)
        self._drw_fig.draw_plot(self._lj.doCalc(default_settings["freq_x"],
                                                         default_settings["freq_y"]), default_settings)

        self._layout.addWidget(self._drw_fig)


        self._ctrl_layout = QVBoxLayout(self)

        self._x_layout = QHBoxLayout(self)

        self._x_freq_lb = QLabel("Частота X:")
        self._x_layout.addWidget(self._x_freq_lb)
        self._x_layout.setAlignment(self._x_freq_lb, Qt.AlignRight)

        self._x_freq_ln_edt = QLineEdit("%d"%default_settings["freq_x"])
        self._x_freq_ln_edt.setFixedSize(30, 30)
        self._x_layout.addWidget(self._x_freq_ln_edt)
        self._x_layout.setAlignment(self._x_freq_ln_edt, Qt.AlignRight)
        self._ctrl_layout.addLayout(self._x_layout)

        self._y_layout = QHBoxLayout(self)

        self._y_freq_lb = QLabel("Частота Y:")
        self._y_layout.addWidget(self._y_freq_lb)
        self._y_layout.setAlignment(self._y_freq_lb, Qt.AlignRight)

        self._y_freq_ln_edt = QLineEdit("%d"%default_settings["freq_y"])
        self._y_freq_ln_edt.setFixedSize(30, 30)
        self._y_layout.addWidget(self._y_freq_ln_edt)
        self._y_layout.setAlignment(self._y_freq_ln_edt, Qt.AlignRight)

        self._ctrl_layout.addLayout(self._y_layout)

        self._clr_layout = QHBoxLayout(self)

        self._clr_blb = QLabel("Цвет:")
        self._clr_layout.addWidget(self._clr_blb)
        self._clr_layout.setAlignment(self._clr_blb, Qt.AlignRight)

        self._clr_combo = QComboBox()
        self._clr_combo.addItems(["Синий","Зелёный","Красный", "Жёлтый"])
        self._clr_combo.setFixedSize(80, 30)
        self._clr_layout.addWidget(self._clr_combo)

        self._ctrl_layout.addLayout(self._clr_layout)

        self._thnk_layout = QHBoxLayout(self)

        self._thnk_blb = QLabel("Толщина \n линии:")
        self._thnk_layout.addWidget(self._thnk_blb)
        self._thnk_layout.setAlignment(self._thnk_blb, Qt.AlignRight)

        self._thnk_combo = QComboBox()
        self._thnk_combo.addItems(["1", "2", "3", "4"])
        self._thnk_combo.setFixedSize(50, 30)
        self._thnk_layout.addWidget(self._thnk_combo)

        self._ctrl_layout.addLayout(self._thnk_layout)

        self._update_btn = QPushButton("Обновить фигуру")
        self._update_btn.setFixedSize(120, 30)
        self._ctrl_layout.addWidget(self._update_btn)
        self._ctrl_layout.setAlignment(self._update_btn, Qt.AlignRight)
        self._save_btn = QPushButton("Сохранить фигуру")
        self._save_btn.setFixedSize(120, 30)

        self._ctrl_layout.addWidget(self._save_btn)
        self._ctrl_layout.setAlignment(self._save_btn, Qt.AlignRight)
        self._ctrl_layout.addStretch()

        self._layout.addLayout(self._ctrl_layout)

        self._spinner = QtWaitingSpinner(self)

        self._update_btn.clicked.connect(self.plot_button_click_handler)
        self._update_btn.clicked.connect(self._spinner.start)
        self._lj.signalData.connect(self._spinner.stop)

        self._save_btn.clicked.connect(self.save_button_click_handler)
        #self._save_btn.clicked.connect(self._spinner.stop)

        self.resize(400, 300)
        self.move(300, 150)
        self.show()



    def plot_button_click_handler(self):
        """
        Обработчик нажатия на кнопку применения настроек
        """
        # Получаем данные из текстовых полей

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

    # def resizeEvent(self, event):
    #     self._overlay.resize(event.size())
    #     event.accept()


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
