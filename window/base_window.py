import csv
import os
import json
from json.decoder import JSONDecodeError

from PyQt5.QtWidgets import ( QMainWindow, QLabel, QLineEdit, QPushButton,
                            QVBoxLayout, QWidget, QMessageBox, QTextEdit, 
                            QListWidget, QAbstractItemView, QAction, QHBoxLayout)
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QFont, QIcon


from datetime import datetime
import pandas as pd
from utils.config import ConfigDialog, CONFIG_FILE, CURRENT_DIR, GEOMETRY_BASE_WINDOW, DEFAULT_DATA_DIR



class BaseWindow(QMainWindow):
    def __init__(self, conn):
        super().__init__()
        self.conn = conn
        
        self.create_menu_bar()
        self.setGeometry(GEOMETRY_BASE_WINDOW)

        self.create_widgets()
        self.create_database_list_widget()
        self.create_search_bar()
        self.create_query_layout()

        self.create_status_bar()        
        self.create_export_button()

        self.config = self.get_config()
        if self.config:
            if self.config['always_use_blacklist_filter']:
                self.filter_databases_blacklist()
       
    def get_config(self):
        if os.path.exists(CONFIG_FILE):
            try:
                with open(CONFIG_FILE, 'r') as f:
                    config = json.load(f)

                return config.get(self.conn.server, None)
            except JSONDecodeError as e:
                return None

        return None

    def create_status_bar(self):
        """ Rodapé da página """
        # adicionando widget de status para exibir informações de usuário e servidor
        self.status_label = QLabel(f"Usuário: {self.conn.user} - Servidor: {self.conn.server}")
        self.statusBar().addWidget(self.status_label)

    def update_status_bar(self, db_name):
        """Atualiza o texto na statusBar com o nome do banco de dados."""
        new_text = f"Usuário: {self.conn.user} - Servidor: {self.conn.server} - Database: {db_name}"
        self.status_label.setText(new_text)
        self.statusBar().update()

    def open_options(self):
        config_dialog = ConfigDialog(self.conn.server, self.conn.list_databases(), self)
        print(self.conn.list_databases())
        config_dialog.exec_()

    def create_menu_bar(self):
        menubar = self.menuBar()
        user_menu = menubar.addMenu('User')
        page_menu = menubar.addMenu('Pages')
        options_menu =  menubar.addMenu('Options')

        configuration_action = QAction(QIcon(os.path.join(CURRENT_DIR, 'icons', 'settings.png')), 'Configuration', self)
        configuration_action.triggered.connect(self.open_options)
        options_menu.addAction(configuration_action)

        use_blacklist_action = QAction('Use Blacklist', self)
        use_blacklist_action.triggered.connect(self.filter_databases_blacklist)
        options_menu.addAction(use_blacklist_action)

        not_use_blacklist_action = QAction('Not Use Blacklist', self)
        not_use_blacklist_action.triggered.connect(self._refresh_database_list)
        options_menu.addAction(not_use_blacklist_action)

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
        from window.login_window import LoginWindow
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

        from window.ddl_window import DDLWindow
        self.close()
        self.ddl_window = DDLWindow(self.conn)
        self.ddl_window.show()

    def switch_to_query_page(self):
        from window.query_window import DQLWindow
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

    def create_command_write_widget(self, command : str) -> QWidget:
        """
        command: ['DDL/DML', 'Query (DQL)']
        """
        query_layout = QVBoxLayout()
       
        label = self.create_label(f"Escreva um comando {command} para executar")
        query_layout.addWidget(label)
 
        query_layout.addWidget(self.text_query)
        self.text_query.setFont(QFont("Consolas", 10))  # aplica a fonte ao widget QTextEdit
        query_layout.addWidget(self.button_run_query)
 
        query_layout.setAlignment(Qt.AlignTop)
        query_layout.setContentsMargins(0,0,0,0)
        query_layout.setSpacing(0)
        query_widget = QWidget()
        query_widget.setLayout(query_layout)
 
        return query_widget
    
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


    def filter_databases_blacklist(self):
        
        # update config
        self.config = self.get_config()

        if not self.config:
            QMessageBox.warning(self, 'No config', 'Init the config')

        else:
            
            blacklist = self.config['black_list']
            all_databases = self.conn.list_databases()
            filtered_databases = [db for db in all_databases if db not in blacklist]
            self.list_select_db.clear()
            self.list_select_db.addItems(filtered_databases)

    def create_export_button(self):
        # criando o botão
        self.button_export_csv = QPushButton("Exportar resultados em csv")
        self.button_export_csv.setEnabled(False) # desabilita o botão inicialmente
        self.button_export_xlsx = QPushButton("Exportar resultados em xlsx")
        self.button_export_xlsx.setEnabled(False) # desabilita o botão inicialmente


    def configure_export_buttons(self):
            # configura botão oculto para salvar csv
        self.table_results.itemChanged.connect(self.on_table_results_changed)
        self.button_export_csv.clicked.connect(self.save_csv)
        self.button_export_xlsx.clicked.connect(self.save_xlsx)

    def save_csv(self):

        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        config_path = self.config.get('path', None)

        if not config_path:
            if not os.path.exists(DEFAULT_DATA_DIR):
                os.mkdir(DEFAULT_DATA_DIR)
                path = DEFAULT_DATA_DIR
        else:
            path = config_path

        try:
            with open(f"{path}/csv_{timestamp}.csv", "w", newline="") as arquivo_csv:

                escritor = csv.writer(arquivo_csv)
                escritor.writerow(self.columns)
                for tupla in self.results:
                    escritor.writerow(tupla)
            QMessageBox.information(self, "Sucesso", f"Arquivo exportado em {path}")
            self.close()
            self.show()
        except Exception as e:
            QMessageBox.warning(self, "Erro", str(e))

    def save_xlsx(self):
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        config_path = self.config.get('path', None)

        if not config_path:

            if not os.path.exists(DEFAULT_DATA_DIR):
                os.mkdir(DEFAULT_DATA_DIR)
                path = DEFAULT_DATA_DIR

        else:
            path = config_path

        try:
            df = pd.DataFrame(self.results, columns=self.columns)
            df.to_excel(f"{path}/xlsx_{timestamp}.xlsx", index=False)

            QMessageBox.information(self, "Sucesso", f"Arquivo exportado em {path}")
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
