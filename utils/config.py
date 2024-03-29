
import os
import json
from PyQt5.QtCore import QRect, Qt
from PyQt5.QtWidgets import (QApplication, QLineEdit, QPushButton,
                            QListWidget, QAbstractItemView, 
                            QCheckBox, QFormLayout, QFileDialog, QDialog)

from json.decoder import JSONDecodeError

CONFIG_FILE = 'config.json'
CURRENT_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), os.pardir))


app = QApplication([])
screen_geometry = app.screens()[1].geometry() if len(app.screens()) > 1 else app.screens()[0].geometry()
GEOMETRY_LOGIN = QRect(screen_geometry.x() + 100, screen_geometry.y() + 100, 300, 250)
GEOMETRY_BASE_WINDOW = QRect(screen_geometry.x() + 100, screen_geometry.y() + 100, 800, 600)
DEFAULT_DATA_DIR = os.path.join(CURRENT_DIR, 'dados')
print(DEFAULT_DATA_DIR)


class ConfigDialog(QDialog):
    def __init__(self, server, databases, parent=None):
        super(ConfigDialog, self).__init__(parent)

        self.server = server
        self.databases = databases
        self.initUI()

    def initUI(self):
        layout = QFormLayout()
        path = DEFAULT_DATA_DIR
        blacklist = []
        always_use_blacklist = False

        if os.path.exists(CONFIG_FILE):
            try:
                with open(CONFIG_FILE, 'r') as f:
                    existing_config = json.load(f)
                    if self.server in existing_config:
                        existing_config = existing_config[self.server] 
                        path = existing_config.get('path', DEFAULT_DATA_DIR)
                        blacklist = existing_config.get('black_list', [])
                        always_use_blacklist = existing_config.get('always_use_blacklist_filter', False)
            except JSONDecodeError:
                pass 

        self.use_blacklist_checkbox = QCheckBox('Always Use BlackList')
        self.use_blacklist_checkbox.setChecked(always_use_blacklist)  # Set default value

        self.path_lineedit = QLineEdit()
        self.path_lineedit.setText(path)

        self.path_button = QPushButton('Select Path')
        self.save_button = QPushButton('Save Config')
        self.clear_button = QPushButton('Clear Config')

        # Adicione um QListWidget para exibir os bancos de dados
        self.blacklist_select = QListWidget()
        self.blacklist_select.setSelectionMode(QAbstractItemView.MultiSelection)
        self.blacklist_select.addItems(self.databases)
        
        # Set default values and pre-select items
        for item_text in blacklist:
            items = self.blacklist_select.findItems(item_text, Qt.MatchExactly)
            if items:
                item = items[0]
                item.setSelected(True)

        layout.addRow('Use BlackList:', self.use_blacklist_checkbox)
        layout.addRow('BlackList:', self.blacklist_select)
        layout.addRow('Path to save files:', self.path_lineedit)
        layout.addRow('', self.path_button)
        
        layout.addRow('', self.save_button)
        layout.addRow('', self.clear_button)
        
        self.path_button.clicked.connect(self.select_path)
        self.save_button.clicked.connect(self.save_settings)
        self.clear_button.clicked.connect(self.clear_settings)

        self.setLayout(layout)
        self.setWindowTitle('Configuration')

    def select_path(self):
        path = QFileDialog.getExistingDirectory(self, 'Select Directory')
        if path:
            self.path_lineedit.setText(path)

    def save_settings(self):
        server_name = self.server
        selected_databases = [self.blacklist_select.item(i).text() for i in range(self.blacklist_select.count()) if self.blacklist_select.item(i).isSelected()]
        path = self.path_lineedit.text()
        use_blacklist = self.use_blacklist_checkbox.isChecked()
        print(selected_databases)
        existing_config = {}

        # Verificar se o arquivo de configuração existe
        if os.path.exists(CONFIG_FILE):
            try:
                with open(CONFIG_FILE, 'r') as f:
                    existing_config = json.load(f)

                # Atualizar o dicionário existente com as novas configurações
            except JSONDecodeError:
                pass
        existing_config[server_name] = {"black_list": selected_databases, "path" : path, "always_use_blacklist_filter":use_blacklist} 

        # Salvar o dicionário atualizado no arquivo JSON
        with open(CONFIG_FILE, 'w') as f:
            json.dump(existing_config, f)

        print("Configurações salvas:", existing_config)
        self.close()




    def clear_settings(self):
        config_file = 'config.json'
        if os.path.exists(config_file):
            with open(config_file, 'r') as f:
                existing_config = json.load(f)
            
            # Remova a entrada correspondente ao servidor do dicionário
            if self.server in existing_config:
                del existing_config[self.server]

                # Salve o dicionário atualizado no arquivo JSON
                with open(config_file, 'w') as f:
                    json.dump(existing_config, f)

                print(f"Configurações para o servidor {self.server} foram removidas.")
                self.config = None
                
            else:
                print(f"Não há configurações para o servidor {self.server}.")
                
            self.close()