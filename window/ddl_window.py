import os
import math 

from PyQt5.QtWidgets import QWidget, QTableWidgetItem, QShortcut, QApplication
from PyQt5.QtCore import Qt
from PyQt5.QtGui import  QColor, QIcon, QKeySequence

from utils.config import  CONFIG_FILE, CURRENT_DIR
from window.base_window import BaseWindow


class DDLWindow(BaseWindow):  # DDLWindow herda de BaseWindow

    def __init__(self, conn):
        super().__init__(conn)  # Chama o construtor da BaseWindow
        self.setWindowTitle("DDL Window")
        self.setWindowIcon(QIcon(os.path.join(CURRENT_DIR, 'icons', 'database.png')))

        vertical_layout = self.create_vertical_splitter('ddl')  

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
            QApplication.processEvents()
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

