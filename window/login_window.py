import os
from PyQt5.QtWidgets import ( QMainWindow, QLabel, QLineEdit, QPushButton,
                            QVBoxLayout, QWidget, QMessageBox,
                            QAction, QHBoxLayout,
                             QRadioButton, QComboBox)
from PyQt5.QtCore import Qt
from PyQt5.QtGui import  QIcon
from utils.database import Conexao
from utils.utils import save_login_data, load_login_data, create_login_folder
from utils.config import  CURRENT_DIR, GEOMETRY_LOGIN
from window.ddl_window import DDLWindow
from window.query_window import DQLWindow


class LoginWindow(QMainWindow):
    def __init__(self):
        try:
            super().__init__()

            create_login_folder()

            # definindo a janela principal
            self.setWindowTitle("Tela de Login")
            self.setWindowIcon(QIcon(os.path.join(CURRENT_DIR, 'icons', 'user-interface.png')))
            self.setGeometry(GEOMETRY_LOGIN)  # aumentando a altura para caber os radio buttons
            
            # criando os widgets da tela de login
            self.edit_username = QLineEdit()
            self.edit_password = QLineEdit()
            self.edit_password.setEchoMode(QLineEdit.Password)
            self.edit_server = QLineEdit()
            self.combo_server = QComboBox()
            self.button_login = QPushButton("Login")
            self.toggle_button = QPushButton()
            
            self.toggle_button.setIcon(QIcon("./icons/refresh.png"))
            self.toggle_button.clicked.connect(self.toggle_text_combo)


            # criando os radio buttons
            self.radio_ddl_dml = QRadioButton("DDL/DML")
            self.radio_dql = QRadioButton("Query (DQL)")
            self.radio_ddl_dml.setChecked(True)  # deixando o DDL/DML selecionado por padrão
            
            # preenchendo os campos com os dados salvos (se existirem)
            try:
                servers, username = load_login_data()
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

            combo_text_layout = QHBoxLayout()
            combo_text_layout.addWidget(self.edit_server)
            combo_text_layout.addWidget(self.combo_server)
            combo_text_layout.addWidget(self.toggle_button)
            combo_text_layout.setAlignment(Qt.AlignTop) # alinha o layout ao topo
            combo_text_layout.setContentsMargins(0, 0, 0, 0) # remove as margens
            combo_text_layout.setSpacing(0) # remove o espaçamento
                
            layout.addLayout(combo_text_layout)
            self.edit_server.setVisible(False)
            self.combo_server.addItems(servers)

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
        
        except Exception as e:
            QMessageBox.warning(self, 'Erro', str(e))
        
    def toggle_text_combo(self):
        if self.edit_server.isVisible():
            self.edit_server.setVisible(False)
            self.combo_server.setVisible(True)
        else:
            self.edit_server.setVisible(True)
            self.combo_server.setVisible(False)

    def test_connection(self):

        # lendo os dados inseridos na tela de login
        if self.combo_server.isVisible():  # Verifica se a ComboBox está visível
            server = self.combo_server.currentText()
        else:
            server = self.edit_server.text()
        username = self.edit_username.text()
        password = self.edit_password.text()

        # testando a conexão com o banco de dados
        conn = Conexao(server, user=username, password=password)


        try:
            conn_result = conn.test_azure_connection()
            if conn_result:
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
        
        except NameError as e:
            QMessageBox.warning(self, "Erro de Conexão" ,str(e))      
