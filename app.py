import sys
import csv
import os

from PyQt5.QtWidgets import (QApplication, QMainWindow, QLabel, QLineEdit, QPushButton,
                            QVBoxLayout, QWidget, QMessageBox, QTextEdit, QTableWidget,
                            QListWidget, QAbstractItemView, QAction, QHBoxLayout,
                            QTableWidgetItem, QRadioButton, QSplitter)
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QFont, QColor, QIcon

from pyodbc import ProgrammingError
from datetime import datetime
import pandas as pd
from utils.database import Conexao
from utils.utils import save_login_data, load_login_data


CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))


class BaseWindow(QMainWindow):
    def __init__(self, conn):
        super().__init__()
        self.conn = conn
        self.create_menu_bar()
        self.setGeometry(100, 100, 800, 600)

        self.create_widgets()
        self.create_database_list_widget()
        self.create_search_bar()
        self.create_query_layout()

        self.create_status_bar()        
        
    def create_status_bar(self):
        """ Rodapé da página """
        # adicionando widget de status para exibir informações de usuário e servidor
        status_label = QLabel(f"Usuário: {self.conn.user} - Servidor: {self.conn.server}")
        self.statusBar().addWidget(status_label)

    def create_menu_bar(self):
        menubar = self.menuBar()
        user_menu = menubar.addMenu('User')
        page_menu = menubar.addMenu('Pages')

        logout_action = QAction(QIcon(os.path.join(CURRENT_DIR, 'icons', 'logout_icon.png')), 'Logout', self)
        logout_action.triggered.connect(self.logout)
        user_menu.addAction(logout_action)

        refresh_action = QAction(QIcon(os.path.join(CURRENT_DIR, 'icons', 'refresh.png')), 'Refresh', self)
        refresh_action.triggered.connect(self._refresh_database_list)
        user_menu.addAction(refresh_action)

        ddl_action = QAction('DDL', self)
        ddl_action.triggered.connect(self.switch_to_ddl_page)
        page_menu.addAction(ddl_action)

        query_action = QAction('Query', self)
        query_action.triggered.connect(self.switch_to_query_page)
        page_menu.addAction(query_action)

    def logout(self):
        # fechando a janela atual
        self.close()

        # abrindo uma nova instância da janela de login
        self.login_window = LoginWindow()
        self.login_window.show()

    def _refresh_database_list(self):
        # limpa a lista atual de bancos de dados
        self.list_select_db.clear()

        # atualiza a lista de bancos de dados
        self.list_select_db.addItems(self.conn.list_databases())

    def switch_to_ddl_page(self):
        self.close()
        self.ddl_window = DDLWindow(self.conn)
        self.ddl_window.show()

    def switch_to_query_page(self):
        self.close()
        self.query_window = DQLWindow(self.conn)
        self.query_window.show()

    def create_widgets(self):
        self.text_query = QTextEdit()
        self.button_run_query = QPushButton("Executar")

    def create_search_bar(self):
        self.search_bar = QLineEdit()
        self.search_bar.setPlaceholderText("Pesquisar bancos de dados...")
        self.search_bar.textChanged.connect(self.filter_databases)
       
    def create_database_list_widget(self):
        self.label_select_db = self.create_label("Selecionar banco(s) de dados:")
        self.list_select_db = QListWidget()
        self.list_select_db.setSelectionMode(QAbstractItemView.MultiSelection)
        self.list_select_db.addItems(self.conn.list_databases())
        
    def create_label(self, text):
        label = QLabel(text)
        label.setFont(QFont("Arial", 10))
        return label
    
    def create_query_layout(self):
        # criando o layout da tela de query
        self.layout = QHBoxLayout()
        menu_layout = QVBoxLayout()
        menu_layout.addWidget(self.search_bar)

        menu_layout.addWidget(self.label_select_db)
        menu_layout.addWidget(self.list_select_db)
        self.layout.addLayout(menu_layout)

    def filter_databases(self):
        # Obtendo o texto da barra de pesquisa
        search_text = self.search_bar.text().strip().lower()

        # Obtendo todos os bancos de dados disponíveis
        all_databases = self.conn.list_databases()

        # Filtrando os bancos de dados que correspondem ao texto da pesquisa
        filtered_databases = [db for db in all_databases if search_text in db.lower()]

        # Limpando a lista de seleção
        self.list_select_db.clear()

        # Adicionando os bancos de dados filtrados à lista de seleção
        self.list_select_db.addItems(filtered_databases)


class DDLWindow(BaseWindow):  # DDLWindow herda de BaseWindow

    def __init__(self, conn):
        super().__init__(conn)  # Chama o construtor da BaseWindow
        self.setWindowTitle("DDL Window")

        vertical_layout = self.create_vertical_ddl_layout()

        self.layout.addWidget(vertical_layout, stretch=1) # expande verticalmente

        # criando o widget central
        widget = QWidget()
        widget.setLayout(self.layout)
        self.setCentralWidget(widget)

        # conectando o botão de executar query ao método correspondente
        self.button_run_query.clicked.connect(self.on_button_run_query_clicked)
 
    def create_vertical_ddl_layout(self):

        # Cria um QSplitter vertical
        splitter = QSplitter()
        splitter.setOrientation(0)  #0: Vertical

        # CAIXA DE DDL
        ddl_layout = QVBoxLayout()
        
        label = self.create_label("Escreva um comando DDL/DML para executar")
        ddl_layout.addWidget(label)

        ddl_layout.addWidget(self.text_query)
        self.text_query.setFont(QFont("Consolas", 10))  # aplica a fonte ao widget QTextEdit
        ddl_layout.addWidget(self.button_run_query)
        ddl_layout.setAlignment(Qt.AlignTop)
        ddl_layout.setContentsMargins(0,0,0,0)
        ddl_layout.setSpacing(0)
        ddl_widget = QWidget()
        ddl_widget.setLayout(ddl_layout)
        splitter.addWidget(ddl_widget)

        # Criando a tabela de resultados
        results_layout = QVBoxLayout()
        self.table_results = QTableWidget()
        results_layout.addWidget(self.table_results)
        results_layout.setAlignment(Qt.AlignTop) # alinha o layout ao topo
        results_layout.setContentsMargins(0, 0, 0, 0) # remove as margens
        results_layout.setSpacing(0) # remove o espaçamento
        
        self.table_results.setColumnCount(2)
        self.table_results.setHorizontalHeaderLabels(["Banco de dados", "Resultados"])
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
        results = []

        for db_name in selected_databases:
            try:
                # executando a query
                result = self.conn.execute_ddl(db_name, query)
                results.append(result)
            except Exception as e:
                # armazenando a mensagem de erro
                results.append((db_name, str(e)))

        results = self._sort_results(results)
        # preenchendo a tabela com os resultados
        self.table_results.setRowCount(len(results))
        for row, result in enumerate(results):
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

        sucessos = [result[1] == 'Executado com sucesso' for result in results]
        
        return results
        
    def _sort_results(self, results):
        sucesso = []
        fail = []

        for item in results:

            db_name = item[0]
            result = item[1]

            if result == 'Executado com sucesso':
                sucesso.append((db_name, result))
            else:
                fail.append((db_name, result))

        results = fail + sucesso
        return results

class DQLWindow(BaseWindow):  # DQLWindow herda de BaseWindow

    def __init__(self, conn):
        super().__init__(conn)  # Chama o construtor da BaseWindow
        self.setWindowTitle("DQL Window")

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
        vertical_layout = QVBoxLayout()

        # Cria um QSplitter vertical
        splitter = QSplitter()
        splitter.setOrientation(0)  #0: Vertical

        # CAIXA DE DDL
        query_layout = QVBoxLayout()
        label = self.create_label("Escreva uma query (DQL) para executar")
        query_layout.addWidget(label)

        query_layout.addWidget(self.text_query)
        self.text_query.setFont(QFont("Consolas", 10))  # aplica a fonte ao widget QTextEdit
        query_layout.addWidget(self.button_run_query)
        query_layout.setAlignment(Qt.AlignTop) # alinha os widgets ao topo
        query_layout.setContentsMargins(0, 0, 0, 0) # remove as margens
        query_layout.setSpacing(0) # remove o espaçamento
        query_widget = QWidget()
        query_widget.setLayout(query_layout)

        splitter.addWidget(query_widget)

        # Criando a tabela de resultados
        results_layout = QVBoxLayout()
        self.table_results = QTableWidget()
        results_layout.addWidget(self.table_results)
        results_layout.setAlignment(Qt.AlignTop) # alinha o layout ao topo
        results_layout.setContentsMargins(0, 0, 0, 0) # remove as margens
        results_layout.setSpacing(0) # remove o espaçamento


        # criando o botão
        self.button_export_csv = QPushButton("Exportar resultados em csv")
        self.button_export_csv.setEnabled(False) # desabilita o botão inicialmente
        results_layout.addWidget(self.button_export_csv)
        ##splitter.addWidget(self.button_export_csv)

        self.button_export_xlsx = QPushButton("Exportar resultados em xlsx")
        self.button_export_xlsx.setEnabled(False) # desabilita o botão inicialmente
        results_layout.addWidget(self.button_export_xlsx)
        #splitter.addWidget(self.button_export_xlsx)

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

        for db_name in selected_databases:
            try:
                find_columns_test = self.conn.execute_query(db_name, query)
            except Exception as e:
                # Erro de conexão com o banco de dados
                QMessageBox.warning(self, f"Erro de conexão em {db_name}", f"Houve um problema de conexão com o banco de dados {db_name}. Verifique se as credenciais de acesso são válidas e se o banco de dados está em funcionamento.")
                return None
            
            if "Error: " in find_columns_test:  # Armazenando a mensagem de erro
                QMessageBox.warning(self, f"Erro em {db_name}", find_columns_test)
                continue

            try:
                db_columns = self.conn.get_columns(db_name, query)
            except ProgrammingError as e:
                # Erro ao obter as colunas da consulta
                QMessageBox.warning(self, f"Erro em {db_name}", str(e))

            result = self.conn.execute_query(db_name, query)
            results += result
            
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

    def configure_export_buttons(self):
            # configura botão oculto para salvar csv
        self.table_results.itemChanged.connect(self.on_table_results_changed)
        self.button_export_csv.clicked.connect(self.save_csv)
        self.button_export_xlsx.clicked.connect(self.save_xlsx)

    def save_csv(self):

        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

        if not os.path.exists("./dados"):
            os.mkdir('./dados')

        try:
            with open(f"dados/csv_{timestamp}.csv", "w", newline="") as arquivo_csv:

                escritor = csv.writer(arquivo_csv)
                escritor.writerow(self.columns)
                for tupla in self.results:
                    escritor.writerow(tupla)
            QMessageBox.information(self, "Sucesso", "Arquivo exportado")
            self.close()
            self.show()
        except Exception as e:
            QMessageBox.warning(self, "Erro", str(e))

    def save_xlsx(self):
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

        if not os.path.exists("./dados"):
            os.mkdir('./dados')

        try:
            df = pd.DataFrame(self.results, columns=self.columns)
            df.to_excel(f"dados/xlsx_{timestamp}.xlsx", index=False)

            QMessageBox.information(self, "Sucesso", "Arquivo exportado")
            self.close()
            self.show()

        except Exception as e:
            QMessageBox.warning(self, "Erro", str(e))

    def on_table_results_changed(self):
        if self.table_results.rowCount() > 0:
            self.button_export_csv.setEnabled(True)
            self.button_export_xlsx.setEnabled(True)
        else:
            self.button_export_csv.setEnabled(False)
            self.button_export_xlsx.setEnabled(False)

class LoginWindow(QMainWindow):
    def __init__(self):
        super().__init__()
    
        # definindo a janela principal
        self.setWindowTitle("Tela de Login")
        self.setGeometry(100, 100, 300, 250)  # aumentando a altura para caber os radio buttons
        
        # criando os widgets da tela de login
        self.edit_username = QLineEdit()
        self.edit_password = QLineEdit()
        self.edit_password.setEchoMode(QLineEdit.Password)
        self.edit_server = QLineEdit()
        self.button_login = QPushButton("Login")
        
        # criando os radio buttons
        self.radio_ddl_dml = QRadioButton("DDL/DML")
        self.radio_dql = QRadioButton("Query (DQL)")
        self.radio_ddl_dml.setChecked(True)  # deixando o DDL/DML selecionado por padrão
        
        # preenchendo os campos com os dados salvos (se existirem)
        try:
            server, username = load_login_data()
            self.edit_server.setText(server)
            self.edit_username.setText(username)
        except:
            pass

        # criando o layout da tela de login
        layout = QVBoxLayout()
        layout.addWidget(QLabel("Username:"))
        layout.addWidget(self.edit_username)
        layout.addWidget(QLabel("Password:"))
        layout.addWidget(self.edit_password)
        layout.addWidget(QLabel("Server:"))
        layout.addWidget(self.edit_server)
        
        # adicionando os radio buttons ao layout
        layout.addWidget(self.radio_ddl_dml)
        layout.addWidget(self.radio_dql)
        layout.addWidget(self.button_login)

        # criando o widget central
        widget = QWidget()
        widget.setLayout(layout)
        self.setCentralWidget(widget)

        # conectando o botão de login à função de teste de conexão
        self.button_login.clicked.connect(self.test_connection)
        


    def test_connection(self):
        # lendo os dados inseridos na tela de login
        server = self.edit_server.text()
        username = self.edit_username.text()
        password = self.edit_password.text()

        # testando a conexão com o banco de dados
        conn = Conexao(server, user=username, password=password)
        if conn.test_azure_connection():
            # salvando os dados de login para a próxima vez
            save_login_data(server, username)

            # abrindo a janela correspondente ao tipo de consulta selecionado
            if self.radio_ddl_dml.isChecked():
                self.query_window = DDLWindow(conn)
            elif self.radio_dql.isChecked():
                self.query_window = DQLWindow(conn)
                
            self.query_window.show()
            self.close()
        else:
            # exibindo mensagem de erro
            QMessageBox.warning(self, "Erro de Conexão", "Não foi possível conectar ao servidor.")
  
if __name__ == '__main__':
    app = QApplication(sys.argv)
    login_window = LoginWindow()
    login_window.show()
    sys.exit(app.exec_())
