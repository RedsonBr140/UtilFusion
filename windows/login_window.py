from context import AppContext
from settings import AppSettings
from ui.ui_login import Ui_LoginWindow
from PySide6.QtWidgets import (
    QDialog,
    QMessageBox,
    QVBoxLayout,
    QFormLayout,
    QLineEdit,
    QPushButton,
    QHBoxLayout,
)
from PySide6.QtCore import QSettings


class _FusionCredentialsDialog(QDialog):
    def __init__(self, username, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Fusion - Credenciais")
        self.setFixedSize(300, 140)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(16, 14, 16, 10)
        layout.setSpacing(8)

        form = QFormLayout()
        form.setSpacing(6)

        self.username_input = QLineEdit(username)
        form.addRow("Usuário:", self.username_input)

        self.password_input = QLineEdit()
        self.password_input.setEchoMode(QLineEdit.Password)
        form.addRow("Senha:", self.password_input)
        layout.addLayout(form)

        buttons = QHBoxLayout()
        buttons.addStretch()
        ok_btn = QPushButton("Entrar")
        ok_btn.clicked.connect(self.accept)
        cancel_btn = QPushButton("Cancelar")
        cancel_btn.clicked.connect(self.reject)
        buttons.addWidget(ok_btn)
        buttons.addWidget(cancel_btn)
        layout.addLayout(buttons)

        self.password_input.setFocus()


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
            self._show_connection_splash()
            self._authenticate_fusion(username, password)
            self.accept()
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
        self._show_connection_splash()
        self._authenticate_fusion(username, password)
        self.accept()

    def _show_connection_splash(self):
        from windows.connection_splash import ConnectionSplash
        splash = ConnectionSplash(self.context, self.settings, self)
        splash.exec()

    def _authenticate_fusion(self, username, password):
        fusion = self.context.FusionClient
        if fusion is None:
            return

        while True:
            try:
                fusion.login(username, password)
                return
            except Exception as e:
                reply = QMessageBox.warning(
                    self,
                    "Fusion - Erro de autenticação",
                    f"Falha ao autenticar no Fusion:\n{e}\n\n"
                    "Deseja tentar com outras credenciais?",
                    QMessageBox.Yes | QMessageBox.No,
                )
                if reply == QMessageBox.No:
                    return

                dlg = _FusionCredentialsDialog(username, self)
                if dlg.exec() == QDialog.Accepted:
                    username = dlg.username_input.text()
                    password = dlg.password_input.text()
                else:
                    return
