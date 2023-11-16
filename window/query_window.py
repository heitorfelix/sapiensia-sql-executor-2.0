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


class DQLWindow(BaseWindow):  # DQLWindow herda de BaseWindow

    def __init__(self, conn):
        super().__init__(conn)  # Chama o construtor da BaseWindow
        self.setWindowTitle("DQL Window")
        self.setWindowIcon(QIcon(os.path.join(CURRENT_DIR, 'icons', 'sql.png')))
        vertical_layout = self.create_vertical_dql_layout()

        self.layout.addWidget(vertical_layout, stretch=1) # expande verticalmente

        # criando o widget central
        widget = QWidget()
        widget.setLayout(self.layout)
        self.setCentralWidget(widget)

        # conectando o botão de executar query ao método correspondente
        self.button_run_query.clicked.connect(self.on_button_run_query_clicked)
        self.configure_export_buttons()


    def create_vertical_dql_layout(self):

        # Cria um QSplitter vertical
        splitter = QSplitter()
        splitter.setOrientation(0)  #0: Vertical

        # CAIXA DE DDL
        query_widget = self.create_command_write_widget('Query (DQL)')
        splitter.addWidget(query_widget)
        self.progress_bar = QProgressBar(self)
        self.progress_bar.setEnabled(False)

        # Criando a tabela de resultados
        results_layout = QVBoxLayout()
        self.table_results = QTableWidget()
        results_layout.addWidget(self.table_results)
        results_layout.addWidget(self.progress_bar)
        results_layout.setAlignment(Qt.AlignTop) # alinha o layout ao topo
        results_layout.setContentsMargins(0, 0, 0, 0) # remove as margens
        results_layout.setSpacing(0) # remove o espaçamento

        # criando o botão
        results_layout.addWidget(self.button_export_csv)
        results_layout.addWidget(self.button_export_xlsx)
        
        results_widget = QWidget()
        results_widget.setLayout(results_layout)
        splitter.addWidget(results_widget)
        return splitter
  
    def on_button_run_query_clicked(self):
        # Obtendo a query a ser executada
        query = self.text_query.toPlainText()

        # Obtendo os bancos selecionados
        selected_databases = [self.list_select_db.item(i).text() for i in range(self.list_select_db.count()) if self.list_select_db.item(i).isSelected()]

        if not selected_databases: 
            QMessageBox.warning(self, f"Erro", "Selecione algum database ")
            return None

        results = []
        columns = ['DatabaseName']
        db_columns = []
        
        number_of_dbs = len(selected_databases)
            

        for i, db_name in enumerate(selected_databases):
            step = math.ceil((i+1)/number_of_dbs * 100)
            self.update_status_bar(db_name)
            try:
                find_columns_test = self.conn.execute_query(db_name, query)
            except Exception as e:
                # Erro de conexão com o banco de dados
                QMessageBox.warning(self, f"Erro de conexão em {db_name}", f"Houve um problema de conexão com o banco de dados {db_name}. Verifique se as credenciais de acesso são válidas e se o banco de dados está em funcionamento.")
                continue
            
            if "Error: " in find_columns_test:  # Armazenando a mensagem de erro
                QMessageBox.warning(self, f"Erro em {db_name}", find_columns_test)
                continue

            try:
                db_columns = self.conn.get_columns(db_name, query)
            except ProgrammingError as e:
                # Erro ao obter as colunas da consulta
                QMessageBox.warning(self, f"Erro em {db_name}", str(e))

            result = self.conn.execute_query(db_name, query)
            #print(result)
            if not result:
                pass
            
            else:
                results += result
            self.progress_bar.setValue(step)

        self.progress_bar.setValue(100) # força finalizar a barra
        if db_columns:
            for col in db_columns:
                if col not in columns:
                    columns.append(col)
        
        
        if not results:
            QMessageBox.critical(self, f"Erro", "A tabela não existe em nenhum database ou há algum problema nesta consulta")
        
        # Preenchendo a tabela com os resultados
        self.table_results.setRowCount(len(results))
        self.table_results.setColumnCount(len(columns))
        self.table_results.setHorizontalHeaderLabels(columns)
        
        for row, result in enumerate(results):
            for column, item in enumerate(result):
                self.table_results.setItem(row, column, QTableWidgetItem(str(item)))

        # Ajustando o tamanho das colunas para exibir os dados completos
        self.table_results.resizeColumnToContents(0)
        self.table_results.resizeRowsToContents()
        self.table_results.horizontalHeader().setStretchLastSection(True)  # Estica a última coluna para preencher o espaço disponível

        # Armazenando em memória
        self.results = results
        self.columns = columns
        return results
