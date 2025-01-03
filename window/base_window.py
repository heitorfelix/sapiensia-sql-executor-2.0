import csv
import os
import json
from json.decoder import JSONDecodeError

from PyQt5.QtWidgets import ( QMainWindow, QLabel, QLineEdit, QPushButton,
                            QVBoxLayout, QWidget, QMessageBox, QTextEdit, 
                            QListWidget, QAbstractItemView, QAction, QHBoxLayout
                            ,QSplitter, QProgressBar, QTableWidget, QApplication, QShortcut)
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QFont, QIcon, QKeySequence

from window.custom_filter import CustomFilterDialog

from datetime import datetime
import pandas as pd
from utils.config import ConfigDialog, CONFIG_FILE, CURRENT_DIR, GEOMETRY_BASE_WINDOW, DEFAULT_DATA_DIR



class BaseWindow(QMainWindow):

    def __init__(self, conn):
        super().__init__()
        self.conn = conn
        self.databases = self.conn.list_databases()
        self.create_menu_bar()
        self.setGeometry(GEOMETRY_BASE_WINDOW)

        self.create_widgets()
        self.create_database_list_widget()
        self.create_search_bar()
        self.create_query_layout()

        self.create_status_bar()        
        self.create_export_button()

        self.canceled = False

        self.config = self.get_config()
        if self.config:
            if self.config['always_use_blacklist_filter']:
                self.filter_databases_blacklist()

        # Atalho para copiar apenas linhas (Ctrl+C)
        self.shortcut_copy = QShortcut(QKeySequence("Ctrl+C"), self)
        self.shortcut_copy.activated.connect(lambda: self.copy_table_selection(include_headers=False))

        # Atalho para copiar colunas e linhas (Ctrl+Shift+C)
        self.shortcut_copy_with_headers = QShortcut(QKeySequence("Ctrl+Shift+C"), self)
        self.shortcut_copy_with_headers.activated.connect(lambda: self.copy_table_selection(include_headers=True))

    def _cancel_queries(self):
        self.canceled = True

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
        config_dialog.exec_()

    def create_menu_bar(self):
        menubar = self.menuBar()
        new = menubar.addMenu('New')
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

        custom_database_filter = QAction('Copy Paste Databases', self)
        custom_database_filter.triggered.connect(self.open_custom_filter)
        options_menu.addAction(custom_database_filter)

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

        new_action = QAction(QIcon(os.path.join(CURRENT_DIR, 'icons', 'plug.png')),'Connection', self)
        new_action.triggered.connect(self.new_connection)
        new.addAction(new_action)

    def new_connection(self):
        from window.login_window import LoginWindow

        # abrindo uma nova instância da janela de login
        self.login_window = LoginWindow()
        self.login_window.show()

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
        self.databases = self.conn.list_databases()
        # atualiza a lista de bancos de dados
        self.list_select_db.addItems(self.databases)

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
        self.button_cancel_query = QPushButton("Cancel")
        self.button_cancel_query.setEnabled(False)

    def create_search_bar(self):
        self.search_bar = QLineEdit()
        self.search_bar.setPlaceholderText("Pesquisar bancos de dados...")
        self.search_bar.textChanged.connect(self.filter_databases)
       
    def create_database_list_widget(self):
        self.label_select_db = self.create_label("Selecionar banco(s) de dados:")
        self.list_select_db = QListWidget()
        self.list_select_db.setSelectionMode(QAbstractItemView.MultiSelection)
        self.list_select_db.addItems(self.databases)
        
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
        query_layout.addWidget(self.button_cancel_query)
 
        query_layout.setAlignment(Qt.AlignTop)
        query_layout.setContentsMargins(0,0,0,0)
        query_layout.setSpacing(0)
        query_widget = QWidget()
        query_widget.setLayout(query_layout)
 
        return query_widget

    def create_vertical_splitter(self, page):
            # Cria um QSplitter vertical
            splitter = QSplitter()
            splitter.setOrientation(0)  # 0: Vertical

            command_widget = self.create_command_write_widget('DDL/DML' if page == 'ddl' else 'Query (DQL)')
            splitter.addWidget(command_widget)

            self.progress_bar = QProgressBar(self)
            self.progress_bar.setEnabled(False)

            # Criando a tabela de resultados
            results_layout = QVBoxLayout()
            self.table_results = QTableWidget()
            results_layout.addWidget(self.table_results)
            results_layout.addWidget(self.progress_bar)

            # criando o botão
            results_layout.addWidget(self.button_export_csv)
            results_layout.addWidget(self.button_export_xlsx)

            results_layout.setAlignment(Qt.AlignTop)  # alinha o layout ao topo
            results_layout.setContentsMargins(0, 0, 0, 0)  # remove as margens
            results_layout.setSpacing(0)  # remove o espaçamento

            if page == 'ddl':
                self.table_results.setColumnCount(2)
                self.columns = ["Banco de dados", "Resultados"]
                self.table_results.setHorizontalHeaderLabels(self.columns)

            results_widget = QWidget()
            results_widget.setLayout(results_layout)
            splitter.addWidget(results_widget)

            return splitter

    def filter_databases(self):
        # Obtendo o texto da barra de pesquisa
        search_text = self.search_bar.text().strip().lower()

        # Obtendo todos os bancos de dados disponíveis
        all_databases = self.databases

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
            all_databases = self.databases
            filtered_databases = [db for db in all_databases if db not in blacklist]
            self.list_select_db.clear()
            self.list_select_db.addItems(filtered_databases)

    def filter_databases_custom(self, databases: list):

        self.list_select_db.clear()

        self.list_select_db.addItems(databases)

    def open_custom_filter(self):
        custom_filter_dialog = CustomFilterDialog( self)
        custom_filter_dialog.databasesFiltered.connect(self.filter_databases_custom)
        custom_filter_dialog.exec_()

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
            with open(f"{path}/csv_{timestamp}.csv", "w", newline="", encoding = 'utf-8') as arquivo_csv:

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

    def copy_table_selection(self, include_headers=False):
        selection = self.table_results.selectedRanges()
        if selection:
            selected_text = ""

            # Se for para incluir os cabeçalhos (Ctrl+Shift+C)
            if include_headers:
                headers = []
                for col in range(selection[0].leftColumn(), selection[0].rightColumn() + 1):
                    headers.append(self.table_results.horizontalHeaderItem(col).text())
                selected_text += "\t".join(headers) + "\n"


            for selected_range in selection:
                for row in range(selected_range.topRow(), selected_range.bottomRow() + 1):
                    row_data = []
                    for col in range(selected_range.leftColumn(), selected_range.rightColumn() + 1):
                        item = self.table_results.item(row, col)
                        if item is not None:
                            row_data.append(item.text())
                        else:
                            row_data.append('')
                    selected_text += "\t".join(row_data) + "\n"
            # Copiando para a área de transferência
            clipboard = QApplication.clipboard()
            clipboard.setText(selected_text)
