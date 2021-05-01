import numpy as np
import time

from PyQt5 import QtCore


from PyQt5.QtCore import *

doDelay = False

class LJ(QObject):
    """
    Генерирует фигуры Лиссажу с заданными параметрами
    """
    signalData = pyqtSignal(np.ndarray)

    def __init__(self, resolution=20):
        super(LJ, self).__init__()
        self.set_resolution(resolution)
        
        # Эта задержка эмулирует процедуру инициализации следующей версии генератора.
        # Задержка будет убрана после обновления.
        # Пока не трогать.
        # P.S. В новом генераторе задержка будет только при инициализации.
        # Фигуры будут генерироваться так же быстро, как и сейчас.
        time.sleep(1)
    @QtCore.pyqtSlot(int,int)
    def callCalc(self, x_freq, y_freq):
        if doDelay:
            time.sleep(5)
        t = np.linspace(0, 2 * np.pi, self._resolution)
        x = np.sin(x_freq * t)
        y = np.cos(y_freq * t)
        self.signalData.emit(self.doCalc( x_freq, y_freq))

    def doCalc(self, x_freq, y_freq):
        t = np.linspace(0, 2 * np.pi, self._resolution)
        x = np.sin(x_freq * t)
        y = np.cos(y_freq * t)
        return np.vstack((x, y))

    def run(self):
        pass #time.sleep(10)

    def set_resolution(self, resolution):
        """
        resolution определяет количество точек в кривой
        """
        self._resolution = resolution



