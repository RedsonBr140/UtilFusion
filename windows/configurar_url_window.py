from PySide6.QtWidgets import (
    QDialog,
    QMessageBox
)
from PySide6.QtCore import Qt
from database.connection import Database
from ui.ui_configurar_url import Ui_ConfigurarURLDialog


class ConfigurarURLWindow(QDialog):

    def __init__(self, context, settings):
        super().__init__()

        self.context = context
        self.settings = settings

        self.ui = Ui_ConfigurarURLDialog()
        self.ui.setupUi(self)

        self.ui.CancelButton.clicked.connect(self.reject)
        self.ui.ApplyButton.clicked.connect(self.apply)
        self.ui.RemoveButton.clicked.connect(self.remove)
        self.load_settings()
        
    def load_settings(self):
        self.ui.UsuarioLineEdit.setText(
                self.settings.settings.value("database/user", "")
        )

        self.ui.SenhaLineEdit.setText(
                self.settings.settings.value("database/password", "")
        )

        self.ui.IPServidorLineEdit.setText(
                self.settings.settings.value("database/host", "")
            )

        self.ui.PortaLineEdit.setText(
                self.settings.settings.value("database/port", "5432")
        )

        self.ui.NomeBancoLineEdit.setText(
                self.settings.settings.value("database/name", "")
        )
    def apply(self):
        host = self.ui.IPServidorLineEdit.text().strip()
        port = self.ui.PortaLineEdit.text().strip()
        database = self.ui.NomeBancoLineEdit.text().strip()
        username = self.ui.UsuarioLineEdit.text().strip()
        password = self.ui.SenhaLineEdit.text()

        if not all([host, port, database, username]):
            QMessageBox.warning(
            self,
            "Configuração",
            "Preencha todos os campos."
            )
            return

        try:
            Database.test_connection(
                host=host,
                port=port,
                database=database,
                username=username,
                password=password
                )

        except Exception as e:
                QMessageBox.critical(
                self,
                "Erro",
                f"Não foi possível conectar ao banco.\n\n{e}"
                )
                return

        self.settings.settings.setValue("database/host", host)
        self.settings.settings.setValue("database/port", port)
        self.settings.settings.setValue("database/name", database)
        self.settings.settings.setValue("database/user", username)
        self.settings.settings.setValue("database/password", password)

        self.settings.settings.sync()

        QMessageBox.information(
                self,
                "Configuração",
                "Configuração salva com sucesso."
        )

        self.accept()
    def remove(self):
        reply = QMessageBox.question(
        self,
        "Remover configuração",
        "Deseja remover esta configuração?"
        )

        if reply != QMessageBox.StandardButton.Yes:
                return

        self.settings.settings.remove("database")

        self.settings.settings.sync()

        self.load_settings()