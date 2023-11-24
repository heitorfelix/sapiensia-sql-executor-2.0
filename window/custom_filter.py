import sys
from PyQt5.QtWidgets import QApplication, QMainWindow, QTextEdit, QPushButton, QVBoxLayout, QWidget, QDialog
from PyQt5.QtCore import pyqtSignal




class CustomFilterDialog(QDialog):
    databasesFiltered = pyqtSignal(list)

    def __init__(self, parent):
        super().__init__(parent)
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout()
        text_edit = QTextEdit(self)
        layout.addWidget(text_edit)

        send_button = QPushButton('Send', self)
        send_button.clicked.connect(self.return_databases_to_filter)
        layout.addWidget(send_button)

        self.setLayout(layout)
        self.setWindowTitle('Custom Filter')

    def return_databases_to_filter(self):
        databases_to_filter = self.findChild(QTextEdit).toPlainText()
        databases_to_filter = self.parse_text_into_list(databases_to_filter)

        filtered_databases = [db for db in self.parent().databases if db  in databases_to_filter]
        self.databasesFiltered.emit(filtered_databases)
        self.close()

    @staticmethod
    def parse_text_into_list(text):
        
        db_list = text.split('\n')

        return list(set(db_list))
