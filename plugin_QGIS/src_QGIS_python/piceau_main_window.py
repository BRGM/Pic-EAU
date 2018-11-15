# coding=utf-8
import os.path
import os
from PyQt5.QtCore import QObject, Qt
from PyQt5.QtWidgets import QAction, QWidget, QLineEdit, QPushButton, QVBoxLayout, QDockWidget
from PyQt5.QtGui import QIcon
#from PyQt5.uic import  loadUi
from PyQt5 import  uic

def ui_path(ui):
    return os.path.join(os.path.dirname(os.path.abspath(__file__)),'ui',ui)

class PicoDialog(QtWidgets.QDockWidget):
    def __init__(self):
        QDockWidget.__init__(self)
        self.ui=uic.loadUi(ui_path('pic_eau.ui'))
        self.ui.setupUi(self)
