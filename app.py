import sys
from PyQt5.QtWidgets import QApplication, QMainWindow, QLabel, QLineEdit, QPushButton, QVBoxLayout, QWidget,\
 QMessageBox, QTextEdit, QListWidget, QAbstractItemView, QAction, QHBoxLayout, QGridLayout
import pickle
from Conexao import Conexao

# salvar os dados de login em um arquivo
def save_login_data(server, username, password):
    with open("login_data.pkl", "wb") as f:
        login_data = {"server": server, "username": username, "password": password}
        pickle.dump(login_data, f)

# carregar os dados de login de um arquivo
def load_login_data():
    try:
        with open("login_data.pkl", "rb") as f:
            login_data = pickle.load(f)
            return login_data["server"], login_data["username"], login_data["password"]
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
        server, username, password = load_login_data()
        self.edit_server.setText(server)
        self.edit_username.setText(username)
        self.edit_password.setText(password)

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
            save_login_data(server, username, password)
            
            # abrindo a janela de consulta
            self.query_window = QueryWindow(conn)
            self.query_window.show()
            self.close()
        else:
            # exibindo mensagem de erro
            QMessageBox.warning(self, "Erro de Conexão", "Não foi possível conectar ao servidor.")

class QueryWindow(QMainWindow):
    def __init__(self, conn):
        super().__init__()

        # criando o menu de login
        menubar = self.menuBar()
        login_menu = menubar.addMenu('User')

        # criando a ação de logout
        logout_action = QAction('Logout', self)
        logout_action.triggered.connect(self.logout)

        # adicionando a ação de logout ao menu de login
        login_menu.addAction(logout_action)

        # definindo a janela principal
        self.setWindowTitle("Query Window")
        self.setGeometry(100, 100, 800, 600)

        # criando os widgets da tela de query
        self.label_select_db = QLabel("Selecionar banco(s) de dados:")
        self.list_select_db = QListWidget()
        self.list_select_db.setSelectionMode(QAbstractItemView.MultiSelection)
        self.list_select_db.addItems(conn.list_databases())
        self.text_query = QTextEdit()
        self.button_run_query = QPushButton("Executar Query")

        # criando widgets para exibir a entrada e a saída da consulta
        self.input_output = QTextEdit()
        self.input_output.setReadOnly(True)
        self.result_output = QTextEdit()
        self.result_output.setReadOnly(True)


        # criando o layout da tela de query
        layout = QHBoxLayout()
        menu_layout = QVBoxLayout()
        menu_layout.addWidget(self.label_select_db)
        menu_layout.addWidget(self.list_select_db)
        layout.addLayout(menu_layout)
        layout.addWidget(self.text_query)
        layout.addWidget(self.button_run_query)

        # adicionando widgets de entrada e saída da consulta ao layout
        layout.addWidget(self.input_output)
        layout.addWidget(self.result_output)

        # criando o widget central
        widget = QWidget()
        widget.setLayout(layout)
        self.setCentralWidget(widget)

        # conectando o botão de executar query ao método correspondente
        self.button_run_query.clicked.connect(self.on_button_run_query_clicked)

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
                result = self.conn.execute_query(db_name, query)
                results.append(result)
            except Exception as e:
                # armazenando a mensagem de erro
                results.append((db_name, str(e)))

        sucessos = [result[1] == 'Consulta realizada' for result in results]
        num_sucessos = sum(sucessos)

        if num_sucessos == len(selected_databases):
            QMessageBox.information(self, "Query Executada com Sucesso", "A query foi executada com sucesso para todos os bancos selecionados.")
        elif num_sucessos > 0:
            error_message = ("\n".join([f"Erro no banco {result[0]}: {result[1]}" for result in results if result[1] == 'Consulta realizada']).
                             join([f"Erro no banco {result[0]}: {result[1]}" for result in results if not result[1] == 'Consulta realizada'])+'\n')
            QMessageBox.warning(self, "Algumas Execuções Falharam", error_message)
        else:
            error_message = ("\n".join([f"Erro no banco {result[0]}: {result[1]}" for result in results]))
            QMessageBox.critical(self, "Todas Execuções Falharam", error_message)
            

if __name__ == '__main__':
    app = QApplication(sys.argv)
    login_window = LoginWindow()
    login_window.show()
    sys.exit(app.exec_())
