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
from window.base_window import BaseWindow

class DDLWindow(BaseWindow):  # DDLWindow herda de BaseWindow

    def __init__(self, conn):
        super().__init__(conn)  # Chama o construtor da BaseWindow
        self.setWindowTitle("DDL Window")
        self.setWindowIcon(QIcon(os.path.join(CURRENT_DIR, 'icons', 'database.png')))


        vertical_layout = self.create_ddl_vertical_splitter()

        self.layout.addWidget(vertical_layout, stretch=1) # expande verticalmente

        # criando o widget central
        widget = QWidget()
        widget.setLayout(self.layout)
        self.setCentralWidget(widget)

        # conectando o botão de executar query ao método correspondente
        self.button_run_query.clicked.connect(self.on_button_run_query_clicked)
        self.configure_export_buttons()
 
    def create_ddl_vertical_splitter(self)->QSplitter:

        # Cria um QSplitter vertical
        splitter = QSplitter()
        splitter.setOrientation(0)  #0: Vertical

        ddl_widget = self.create_command_write_widget('DDL/DML')
        splitter.addWidget(ddl_widget)

        self.progress_bar = QProgressBar(self)
        self.progress_bar.setEnabled(False)

        # Criando a tabela de resultados
        results_layout = QVBoxLayout()
        self.table_results = QTableWidget()
        results_layout.addWidget(self.table_results)
        results_layout.addWidget(self.progress_bar)
        results_layout.addWidget(self.button_export_csv)
        results_layout.addWidget(self.button_export_xlsx)

        results_layout.setAlignment(Qt.AlignTop) # alinha o layout ao topo
        results_layout.setContentsMargins(0, 0, 0, 0) # remove as margens
        results_layout.setSpacing(0) # remove o espaçamento
        
        self.table_results.setColumnCount(2)
        self.columns = ["Banco de dados", "Resultados"]
        self.table_results.setHorizontalHeaderLabels(self.columns)
        results_widget = QWidget()
        results_widget.setLayout(results_layout)
        splitter.addWidget(results_widget)

        return splitter
    
    def on_button_run_query_clicked(self):
        # obtendo a query a ser executada
        query = self.text_query.toPlainText()

        # obtendo os bancos selecionados
        selected_databases = [self.list_select_db.item(i).text() for i in range(self.list_select_db.count()) if self.list_select_db.item(i).isSelected()]

        # executando a query para cada banco selecionado
        self.results = []

        self.progress_bar.setEnabled(True)

        number_of_dbs = len(selected_databases)
        for i ,db_name in enumerate(selected_databases):
            step = math.ceil((i+1)/number_of_dbs * 100)
            self.update_status_bar(db_name)
            
            try:
                # executando a query
                result = self.conn.execute_ddl(db_name, query)
                self.results.append(result)
            except Exception as e:
                # armazenando a mensagem de erro
                self.results.append((db_name, str(e)))
            self.progress_bar.setValue(step)
        self._sort_results()
        # preenchendo a tabela com os resultados
        self.table_results.setRowCount(len(self.results))
        for row, result in enumerate(self.results):
            self.table_results.setItem(row, 0, QTableWidgetItem(result[0]))
            item = QTableWidgetItem(str(result[1]))
            if result[1] == 'Executado com sucesso':
                item.setBackground(QColor(152, 251, 152)) # Define a cor de fundo da célula para verde
            else:
                item.setBackground(QColor(255, 255, 224)) # Define a cor de fundo da célula para verde
            self.table_results.setItem(row, 1, item)
        # ajustando o tamanho das colunas para exibir os dados completos

        self.table_results.resizeColumnToContents(0)
        self.table_results.resizeRowsToContents()
        self.table_results.horizontalHeader().setStretchLastSection(True) # estica a ultima coluna para preencher o espaço disponível
        sucessos = [result[1] == 'Executado com sucesso' for result in self.results]
        
    def _sort_results(self):
        sucesso = []
        fail = []

        for item in self.results:

            db_name = item[0]
            result = item[1]

            if result == 'Executado com sucesso':
                sucesso.append((db_name, result))
            else:
                fail.append((db_name, result))

        self.results = fail + sucesso

