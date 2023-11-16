import sys
import csv
import os
import math 
import json

from PyQt5.QtWidgets import (QApplication, QMainWindow, QLabel, QLineEdit, QPushButton,
                            QVBoxLayout, QWidget, QMessageBox, QTextEdit, QTableWidget,
                            QListWidget, QAbstractItemView, QAction, QHBoxLayout,
                            QTableWidgetItem, QRadioButton, QSplitter, QComboBox, QProgressBar,
                            QCheckBox, QFormLayout, QFileDialog, QDialog)
from PyQt5.QtCore import Qt, QRect
from PyQt5.QtGui import QFont, QColor, QIcon

from pyodbc import ProgrammingError
from datetime import datetime
import pandas as pd
from utils.database import Conexao
from utils.utils import save_login_data, load_login_data, create_login_folder
from utils.config import ConfigDialog, CONFIG_FILE, CURRENT_DIR
from window.login_window import LoginWindow


if __name__ == '__main__':
    app = QApplication(sys.argv)

    screen_geometry = app.screens()[1].geometry() if len(app.screens()) > 1 else app.screens()[0].geometry()
    
    GEOMETRY_LOGIN = QRect(screen_geometry.x() + 100, screen_geometry.y() + 100, 300, 250)
    GEOMETRY_BASE_WINDOW = QRect(screen_geometry.x() + 100, screen_geometry.y() + 100, 800, 600)

    login_window = LoginWindow()
    login_window.show()
    sys.exit(app.exec_())