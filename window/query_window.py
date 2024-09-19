import os
import math 

from PyQt5.QtWidgets import ( QWidget, QMessageBox,
                            QTableWidgetItem,  QShortcut)
from PyQt5.QtCore import Qt
from PyQt5.QtGui import  QIcon, QKeySequence

from pyodbc import ProgrammingError
from utils.config import CURRENT_DIR
from window.base_window import BaseWindow
from PyQt5.QtWidgets import QApplication

class DQLWindow(BaseWindow):  # DQLWindow herda de BaseWindow

    def __init__(self, conn):
        super().__init__(conn)  # Chama o construtor da BaseWindow
        self.ignore_errors = False
        self.setWindowTitle("DQL Window")
        self.setWindowIcon(QIcon(os.path.join(CURRENT_DIR, 'icons', 'sql.png')))
        vertical_layout = self.create_vertical_splitter('dql')

        self.layout.addWidget(vertical_layout, stretch=1) # expande verticalmente

        # criando o widget central
        widget = QWidget()
        widget.setLayout(self.layout)
        self.setCentralWidget(widget)

        # conectando o botão de executar query ao método correspondente
        self.button_run_query.clicked.connect(self.on_button_run_query_clicked)
        self.shortcut_f5 = QShortcut(QKeySequence(Qt.Key_F5), self)
        self.shortcut_f5.activated.connect(self.on_button_run_query_clicked)
        self.configure_export_buttons()


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

            self.button_cancel_query.setEnabled(True)
            self.button_cancel_query.clicked.connect(self._cancel_queries)
            step = math.ceil((i + 1) / number_of_dbs * 100)
            self.update_status_bar(db_name)
            try:
                find_columns_test = self.conn.execute_query(db_name, query)
            except Exception as e:
                if not self.ignore_errors:
                    self.show_error_message(db_name, str(e))
                continue

            if "Error: " in find_columns_test:
                if not self.ignore_errors:
                    self.show_error_message(db_name, find_columns_test)
                continue

            try:
                db_columns = self.conn.columns
            except ProgrammingError as e:
                if not self.ignore_errors:
                    self.show_error_message(db_name, str(e))

            result = self.conn.execute_query(db_name, query)
            if result:
                results += result

            self.progress_bar.setValue(step)
            QApplication.processEvents()

            if self.canceled:
                QMessageBox.warning(self, f"Cancelada", "Comando cancelado, exibindo resultados...")
                break

        self.button_cancel_query.setEnabled(False)

        if not self.canceled:
            self.progress_bar.setValue(100)

        self.canceled = False
        if db_columns:
            for col in db_columns:
                if col not in columns:
                    columns.append(col)

        if not results:
            pass

        self.ignore_errors = False
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
    
    def show_error_message(self, db_name, error_message):
        """Exibe uma mensagem de erro com a opção de ignorar todos os erros futuros."""
        msg_box = QMessageBox(self)
        msg_box.setIcon(QMessageBox.Warning)
        msg_box.setWindowTitle(f"Erro em {db_name}")
        msg_box.setText(error_message)

        ignore_button = msg_box.addButton("Ignorar todos os erros", QMessageBox.ActionRole)
        msg_box.addButton(QMessageBox.Ok)

        msg_box.exec_()

        if msg_box.clickedButton() == ignore_button:
            self.ignore_errors = True