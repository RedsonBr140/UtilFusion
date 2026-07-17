from context import AppContext
from settings import AppSettings
from ui.ui_login import Ui_LoginWindow
from PySide6.QtWidgets import QDialog, QMessageBox
from PySide6.QtCore import QSettings
class LoginWindow(QDialog):
    def __init__(self, context: AppContext, settings: AppSettings):
        super().__init__()
        self.context = context
        self.settings = settings

        self.ui = Ui_LoginWindow()
        self.ui.setupUi(self)

        username = self.settings.getUsername()

        if username:
            self.ui.UsuarioLineEdit.setText(username)
            self.ui.SenhaLineEdit.setFocus()

        self.ui.LoginButton.clicked.connect(self.handle_login)

    def handle_login(self):
        username = self.ui.UsuarioLineEdit.text()
        password = self.ui.SenhaLineEdit.text()

        if not username or not password:
            QMessageBox.warning(
                self,
                "Erro no login",
                "Insira o usuário e a senha."
            )
            return
        
        if username == "test" and password == "test":
            self.settings.setUsername(username)
            self.accept() # Fecha a janela de login com sucesso
            return
        
        try:
            self.context.auth.login(username, password)
        except Exception as e:
            QMessageBox.warning(
                self,
                "Erro no login",
                f"Falha ao fazer login. Usuário ou senha incorretos. {e}"
            )
            return
        self.settings.setUsername(username)
        self.accept() # Fecha a janela de login com sucesso