import sys
import csv
import os
from PyQt5.QtWidgets import QApplication, QMainWindow, QLabel, QLineEdit, QPushButton, QVBoxLayout, QWidget,\
 QMessageBox, QTextEdit,QTableWidget, QListWidget, QAbstractItemView, QAction, QHBoxLayout, QTableWidgetItem,\
 QComboBox, QRadioButton 
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QFont, QColor, QIcon
from pyodbc import ProgrammingError
from datetime import datetime
import pickle
import pandas as pd
from database import Conexao

CURRENT_DIR = current_dir = os.path.dirname(os.path.abspath(__file__))

# salvar os dados de login em um arquivo
def save_login_data(server, username):

    if not os.path.exists("./login"):
        os.mkdir('./login')

    with open("./login/login_data.pkl", "wb") as f:
        login_data = {"server": server, "username": username}
        pickle.dump(login_data, f)

# carregar os dados de login de um arquivo
def load_login_data():
    try:
        with open("./login/login_data.pkl", "rb") as f:
            login_data = pickle.load(f)
            return login_data["server"], login_data["username"]
    except FileNotFoundError:
        return "", "", ""
    

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
        
        # conectando os radio buttons ao slot de seleção


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
                self.query_window = QueryWindow(conn)
                
            self.query_window.show()
            self.close()
        else:
            # exibindo mensagem de erro
            QMessageBox.warning(self, "Erro de Conexão", "Não foi possível conectar ao servidor.")


class QueryWindow(QMainWindow):

    def menu_bar(self):
        # criando o menu de user e pages
        menubar = self.menuBar()
        user_menu = menubar.addMenu('User')
        page_menu = menubar.addMenu('Pages')

        # criando a ação de logout e refresh + adicionando no menu
        logout_action = QAction(QIcon(os.path.join(CURRENT_DIR, 'icons', 'logout_icon.png')), 'Logout', self)
        logout_action.triggered.connect(self.logout)
        user_menu.addAction(logout_action)
        refresh_action = QAction(QIcon(os.path.join(CURRENT_DIR, 'icons', 'refresh.png')), 'Refresh', self)
        refresh_action.triggered.connect(self._refresh_database_list)
        user_menu.addAction(refresh_action)

        # criando a ação de mudança de pagina ddl e query e adicionando no menu
        ddl_action = QAction('DDL', self)
        ddl_action.triggered.connect(self._ddl_page)
        query_action = QAction('Query', self)
        query_action.triggered.connect(self._query_page)
        page_menu.addAction(ddl_action)
        page_menu.addAction(query_action)

    def _ddl_page(self):
        self.close()
        self.ddl_window = DDLWindow(self.conn)
        self.ddl_window.show()

    def _query_page(self):
        self.close()
        self.query_window = QueryWindow(self.conn)
        self.query_window.show()

    def _refresh_database_list(self):
        # limpa a lista atual de bancos de dados
        self.list_select_db.clear()

        # atualiza a lista de bancos de dados
        self.list_select_db.addItems(self.conn.list_databases())

    def __init__(self, conn):
        super().__init__()

        self.menu_bar()

        # definindo a janela principal
        self.setWindowTitle("Query Window")
        self.setGeometry(100, 100, 800, 600)

        # criando os widgets da tela de query
        self.label_select_db = QLabel("Selecionar banco(s) de dados:")
        self.label_select_db.setFont(QFont("Arial", 10)) 
        self.list_select_db = QListWidget()
        self.list_select_db.setSelectionMode(QAbstractItemView.MultiSelection)
        self.list_select_db.addItems(conn.list_databases())
        self.text_query = QTextEdit()
        self.button_run_query = QPushButton("Executar")

        # criando o layout da tela de query
        layout = QHBoxLayout()
        menu_layout = QVBoxLayout()
        menu_layout.addWidget(self.label_select_db)
        menu_layout.addWidget(self.list_select_db)
        layout.addLayout(menu_layout)

        vertical_layout = QVBoxLayout()

        # CAIXA DE DDL
        query_layout = QVBoxLayout()
        label = QLabel("Escreva uma query (DQL) para executar")
        label.setFont(QFont("Arial", 10)) #define a nova fonte com tamanho 12 no QLabel
        query_layout.addWidget(label)

        query_layout.addWidget(self.text_query)
        self.text_query.setFont(QFont("Consolas", 10))  # aplica a fonte ao widget QTextEdit
        query_layout.addWidget(self.button_run_query)
        query_layout.setAlignment(Qt.AlignTop) # alinha os widgets ao topo
        query_layout.setContentsMargins(0, 0, 0, 0) # remove as margens
        query_layout.setSpacing(0) # remove o espaçamento
        vertical_layout.addLayout(query_layout)

        # Criando a tabela de resultados
        results_layout = QVBoxLayout()
        self.table_results = QTableWidget()
        results_layout.addWidget(self.table_results)
        results_layout.setAlignment(Qt.AlignTop) # alinha o layout ao topo
        results_layout.setContentsMargins(0, 0, 0, 0) # remove as margens
        results_layout.setSpacing(0) # remove o espaçamento
        vertical_layout.addLayout(results_layout, stretch=1) # expande verticalmente
        

        # criando o botão
        self.button_export_csv = QPushButton("Exportar resultados em csv")
        self.button_export_csv.setEnabled(False) # desabilita o botão inicialmente
        vertical_layout.addWidget(self.button_export_csv)
        self.button_export_xlsx = QPushButton("Exportar resultados em xlsx")
        self.button_export_xlsx.setEnabled(False) # desabilita o botão inicialmente
        vertical_layout.addWidget(self.button_export_xlsx)
        vertical_layout.setAlignment(Qt.AlignTop) # alinha o layout ao topo
        vertical_layout.setContentsMargins(0, 0, 0, 0) # remove as margens
        vertical_layout.setSpacing(0) # remove o espaçamento
        layout.addLayout(vertical_layout, stretch=1) # expande verticalmente

        # criando o widget central
        widget = QWidget()
        widget.setLayout(layout)
        self.setCentralWidget(widget)

        # conectando o botão de executar query ao método correspondente
        self.button_run_query.clicked.connect(self.on_button_run_query_clicked)

        # configura botão oculto para salvar csv
        self.table_results.itemChanged.connect(self.on_table_results_changed)
        self.button_export_csv.clicked.connect(self._save_csv)
        self.button_export_xlsx.clicked.connect(self._save_xlsx)

        # armazenando a conexão com o banco de dados
        self.conn = conn
        
        # adicionando widget de status para exibir informações de usuário e servidor
        status_label = QLabel(f"Usuário: {self.conn.user} - Servidor: {self.conn.server}")
        self.statusBar().addWidget(status_label)

    def on_table_results_changed(self):
        if self.table_results.rowCount() > 0:
            self.button_export_csv.setEnabled(True)
            self.button_export_xlsx.setEnabled(True)
        else:
            self.button_export_csv.setEnabled(False)
            self.button_export_xlsx.setEnabled(False)

    def logout(self):
        # fechando a janela atual
        self.close()

        # abrindo uma nova instância da janela de login
        self.login_window = LoginWindow()
        self.login_window.show()

    def on_button_run_query_clicked(self):
        # obtendo a query a ser executada
        query = self.text_query.toPlainText()

        # obtendo os bancos selecionados
        selected_databases = [self.list_select_db.item(i).text() for i in range(self.list_select_db.count()) if self.list_select_db.item(i).isSelected()]

        if not selected_databases: 
            QMessageBox.warning(self, f"Erro", "Selecione algum database ")
            return None

        results = []
        columns = ['DatabaseName']
        for db_name in selected_databases:
            try:
                find_columns_test = self.conn.execute_query(db_name, query)
            except Exception as e:
                # erro de conexão com o banco de dados
                QMessageBox.warning(self, f"Erro de conexão em {db_name}", f"Houve um problema de conexão com o banco de dados {db_name}. Verifique se as credenciais de acesso são válidas e se o banco de dados está em funcionamento.")
                return None
            
            if "Error: " in find_columns_test: # armazenando a mensagem de erro
                QMessageBox.warning(self, f"Erro em {db_name}", find_columns_test)
                continue

            # o banco de dados foi acessado com sucesso
            db_columns = []
            try:
                db_columns = self.conn.get_columns(db_name, query)
            except ProgrammingError as e:
                # erro ao obter as colunas da consulta
                QMessageBox.warning(self, f"Erro em {db_name}", str(e))

            
            result = self.conn.execute_query(db_name, query)
            results += result
        columns += db_columns
        
        if not results:
            QMessageBox.critical(self, f"Erro", "A tabela não existe em nenhum database.")

        # preenchendo a tabela com os resultados
        self.table_results.setRowCount(len(results))
        self.table_results.setColumnCount(len(columns))
        self.table_results.setHorizontalHeaderLabels(columns)
        for row, result in enumerate(results):
            for column, item in enumerate(result):
                self.table_results.setItem(row, column, QTableWidgetItem(str(item)))
        # ajustando o tamanho das colunas para exibir os dados completos
        self.table_results.resizeColumnToContents(0)
        self.table_results.resizeRowsToContents()
        self.table_results.horizontalHeader().setStretchLastSection(True) # estica a ultima coluna para preencher o espaço disponível

        # armazenando em memória
        self.results = results
        self.columns = columns
        return results

        

    def _save_csv(self):

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




    def _save_xlsx(self):
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



class DDLWindow(QMainWindow):

    def menu_bar(self):
        # criando o menu de user e pages
        menubar = self.menuBar()
        user_menu = menubar.addMenu('User')
        page_menu = menubar.addMenu('Pages')

        # criando a ação de logout e refresh + adicionando no menu
        logout_action = QAction(QIcon(os.path.join(CURRENT_DIR, 'icons', 'logout_icon.png')), 'Logout', self)
        logout_action.triggered.connect(self.logout)
        user_menu.addAction(logout_action)
        refresh_action = QAction(QIcon(os.path.join(CURRENT_DIR, 'icons', 'refresh.png')), 'Refresh', self)
        refresh_action.triggered.connect(self._refresh_database_list)
        user_menu.addAction(refresh_action)

        # criando a ação de mudança de pagina ddl e query e adicionando no menu
        ddl_action = QAction('DDL', self)
        ddl_action.triggered.connect(self._ddl_page)
        query_action = QAction('Query', self)
        query_action.triggered.connect(self._query_page)
        page_menu.addAction(ddl_action)
        page_menu.addAction(query_action)
        
    def _ddl_page(self):
        self.close()
        self.ddl_window = DDLWindow(self.conn)
        self.ddl_window.show()

    def _query_page(self):
        self.close()
        self.query_window = QueryWindow(self.conn)
        self.query_window.show()


    def _refresh_database_list(self):
        # limpa a lista atual de bancos de dados
        self.list_select_db.clear()

        # atualiza a lista de bancos de dados
        self.list_select_db.addItems(self.conn.list_databases())

    def __init__(self, conn):
        super().__init__()

        self.menu_bar()

        # definindo a janela principal
        self.setWindowTitle("DDL Window")
        self.setGeometry(100, 100, 800, 600)

        # criando os widgets da tela de query
        self.label_select_db = QLabel("Selecionar banco(s) de dados:")
        self.label_select_db.setFont(QFont("Arial", 10)) 
        self.list_select_db = QListWidget()
        self.list_select_db.setSelectionMode(QAbstractItemView.MultiSelection)
        self.list_select_db.addItems(conn.list_databases())
        self.text_query = QTextEdit()
        self.button_run_query = QPushButton("Executar")

        # criando o layout da tela de query
        layout = QHBoxLayout()
        menu_layout = QVBoxLayout()
        menu_layout.addWidget(self.label_select_db)
        menu_layout.addWidget(self.list_select_db)
        layout.addLayout(menu_layout)

        vertical_layout = QVBoxLayout()

        # CAIXA DE DDL
        ddl_layout = QVBoxLayout()
        label = QLabel("Escreva um comando DDL/DML para executar")
        label.setFont(QFont("Arial", 10)) #define a nova fonte com tamanho 12 no QLabel
        ddl_layout.addWidget(label)

        ddl_layout.addWidget(self.text_query)
        self.text_query.setFont(QFont("Consolas", 10))  # aplica a fonte ao widget QTextEdit
        ddl_layout.addWidget(self.button_run_query)
        ddl_layout.setAlignment(Qt.AlignTop)
        ddl_layout.setContentsMargins(0,0,0,0)
        ddl_layout.setSpacing(0)
        vertical_layout.addLayout(ddl_layout)

        # Criando a tabela de resultados
        results_layout = QVBoxLayout()
        self.table_results = QTableWidget()
        results_layout.addWidget(self.table_results)
        results_layout.setAlignment(Qt.AlignTop) # alinha o layout ao topo
        results_layout.setContentsMargins(0, 0, 0, 0) # remove as margens
        results_layout.setSpacing(0) # remove o espaçamento
        vertical_layout.addLayout(results_layout, stretch=1) # expande verticalmente

        self.table_results.setColumnCount(2)
        self.table_results.setHorizontalHeaderLabels(["Banco de dados", "Resultados"])
        vertical_layout.setAlignment(Qt.AlignTop) # alinha o layout ao topo
        vertical_layout.setContentsMargins(0, 0, 0, 0) # remove as margens
        vertical_layout.setSpacing(0) # remove o espaçamento
        layout.addLayout(vertical_layout, stretch=1) # expande verticalmente

        # criando o widget central
        widget = QWidget()
        widget.setLayout(layout)
        self.setCentralWidget(widget)

        # conectando o botão de executar query ao método correspondente
        self.button_run_query.clicked.connect(self.on_button_run_query_clicked)

        # armazenando a conexão com o banco de dados
        self.conn = conn
        
        # adicionando widget de status para exibir informações de usuário e servidor
        status_label = QLabel(f"Usuário: {self.conn.user} - Servidor: {self.conn.server}")
        self.statusBar().addWidget(status_label)

    def logout(self):
        # fechando a janela atual
        self.close()

        # abrindo uma nova instância da janela de login
        self.login_window = LoginWindow()
        self.login_window.show()

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
        num_sucessos = sum(sucessos)
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

if __name__ == '__main__':
    app = QApplication(sys.argv)
    login_window = LoginWindow()
    login_window.show()
    sys.exit(app.exec_())
