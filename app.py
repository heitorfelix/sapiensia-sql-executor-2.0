import sys
from PyQt5.QtWidgets import QApplication, QMainWindow, QLabel, QLineEdit, QPushButton, QVBoxLayout, QWidget,\
 QMessageBox, QTextEdit,QTableWidget, QListWidget, QAbstractItemView, QAction, QHBoxLayout, QTableWidgetItem
from PyQt5.QtGui import QFont, QColor, QIcon

import pickle
from database import Conexao

# salvar os dados de login em um arquivo
def save_login_data(server, username):
    with open("login_data.pkl", "wb") as f:
        login_data = {"server": server, "username": username}
        pickle.dump(login_data, f)

# carregar os dados de login de um arquivo
def load_login_data():
    try:
        with open("login_data.pkl", "rb") as f:
            login_data = pickle.load(f)
            return login_data["server"], login_data["username"]
    except FileNotFoundError:
        return "", "", ""
    

class LoginWindow(QMainWindow):
    def __init__(self):
        super().__init__()
    
        # definindo a janela principal
        self.setWindowTitle("Tela de Login")
        self.setGeometry(100, 100, 300, 200)
        
        # criando os widgets da tela de login
        self.label_username = QLabel("Username:")
        self.edit_username = QLineEdit()
        self.label_password = QLabel("Password:")
        self.edit_password = QLineEdit()
        self.edit_password.setEchoMode(QLineEdit.Password)
        self.label_server = QLabel("Server:")
        self.edit_server = QLineEdit()
        self.button_login = QPushButton("Login")

        # preenchendo os campos com os dados salvos (se existirem)
        server, username = load_login_data()
        self.edit_server.setText(server)
        self.edit_username.setText(username)


        # criando o layout da tela de login
        layout = QVBoxLayout()
        layout.addWidget(self.label_username)
        layout.addWidget(self.edit_username)
        layout.addWidget(self.label_password)
        layout.addWidget(self.edit_password)
        layout.addWidget(self.label_server)
        layout.addWidget(self.edit_server)
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
        print(server)
        print(username)
        print(password)
        # testando a conexão com o banco de dados
        conn = Conexao(server, user=username, password=password)
        if conn.test_azure_connection():
            # salvando os dados de login para a próxima vez
            save_login_data(server, username)
            
            # abrindo a janela de consulta
            self.query_window = QueryWindow(conn)
            self.query_window.show()
            self.close()
        else:
            # exibindo mensagem de erro
            QMessageBox.warning(self, "Erro de Conexão", "Não foi possível conectar ao servidor.")

class QueryWindow(QMainWindow):



    def menu_bar(self):
        # criando o menu de login
        menubar = self.menuBar()
        login_menu = menubar.addMenu('User')

        # criando a ação de logout
        logout_action = QAction('Logout', self)
        logout_action.triggered.connect(self.logout)

        # adicionando a ação de logout ao menu de login
        login_menu.addAction(logout_action)

        refresh_action = QAction(QIcon('.icons/refresh.png'), 'Refresh', self)
        refresh_action.triggered.connect(self.refresh_database_list)
        login_menu.addAction(refresh_action)

    def refresh_database_list(self):
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
        ddl_layout.addWidget(QLabel("Escreva um comando DDL para executar"))
        ddl_layout.addWidget(self.text_query)
        ddl_layout.setStretchFactor(self.text_query, 2)
        ddl_height = self.geometry().height() // 4
        self.text_query.setFixedHeight(ddl_height )
        font = QFont("Arial", 10)  # cria uma fonte com tamanho 10 e tipo Arial
        self.text_query.setFont(font)  # aplica a fonte ao widget QTextEdit
        ddl_layout.addWidget(self.button_run_query)
        vertical_layout.addLayout(ddl_layout)

        # Criando a tabela de resultados
        self.table_results = QTableWidget()
        self.table_results.setColumnCount(2)
        self.table_results.setHorizontalHeaderLabels(["Banco de dados", "Resultados"])
        vertical_layout.addWidget(self.table_results)
        layout.addLayout(vertical_layout)

        # criando o widget central
        widget = QWidget()
        widget.setLayout(layout)
        self.setCentralWidget(widget)

        # conectando o botão de executar query ao método correspondente
        results = self.button_run_query.clicked.connect(self.on_button_run_query_clicked)
        print(results)
        # armazenando a conexão com o banco de dados
        self.conn = conn

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

        results = self.sort_results(results)
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

        # if num_sucessos == len(selected_databases):
        #     QMessageBox.information(self, "Query Executada com Sucesso", "A query foi executada com sucesso para todos os bancos selecionados.")
        # elif num_sucessos > 0:
        #     error_message = ("\n".join([f"Erro no banco {result[0]}: {result[1]}" for result in results if result[1] == 'Executado com sucesso']).
        #                      join([f"Erro no banco {result[0]}: {result[1]}" for result in results if not result[1] == 'Executado com sucesso'])+'\n')
        #     QMessageBox.warning(self, "Algumas Execuções Falharam", error_message)
        # else:
        #     error_message = ("\n".join([f"Erro no banco {result[0]}: {result[1]}" for result in results]))
        #     QMessageBox.critical(self, "Todas Execuções Falharam", error_message)
        
        return results
        
    def sort_results(self, results):
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