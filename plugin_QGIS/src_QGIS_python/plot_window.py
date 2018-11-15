# coding='utf8'

import os

from PyQt5 import QtWidgets
from PyQt5.uic import *


FORM_CLASS, _ = uic.loadUiType(os.path.join(
    os.path.dirname(__file__), 'ui/pic_eau.ui'))


class PlotWindow(QtWidgets.QDockWidget,FORM_CLASS):
    def __init__(self, parent=None):
        super(PlotWindow, self).__init__(parent)
        self.setupUi(self)
        self.setWindowTitle("My Form")
        self.pushButton.setTest("Grettings")
        self.pushButton.clicked.connect(self.greetings)


    def showPlot(self):
        #self.XX.load(QUrl(''))
        pass


    def greetings(self):
        print("Hello {}")