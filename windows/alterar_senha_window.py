from argon2 import PasswordHasher
from PySide6.QtWidgets import (
    QDialog,
    QDialogButtonBox,
    QFormLayout,
    QLineEdit,
    QMessageBox,
    QVBoxLayout,
)

from windows.app_behaviors import apply_standard_behaviors


class AlterarSenhaDialog(QDialog):
    def __init__(self, context, parent=None):
        super().__init__(parent)
        self.context = context
        self.setWindowTitle("Alterar Senha")
        self.setModal(True)
        self.setMinimumWidth(380)

        layout = QVBoxLayout(self)
        form = QFormLayout()

        self.current_input = QLineEdit()
        self.current_input.setEchoMode(QLineEdit.Password)
        form.addRow("Senha atual:", self.current_input)

        self.new_input = QLineEdit()
        self.new_input.setEchoMode(QLineEdit.Password)
        form.addRow("Nova senha:", self.new_input)

        self.confirm_input = QLineEdit()
        self.confirm_input.setEchoMode(QLineEdit.Password)
        form.addRow("Confirmar nova senha:", self.confirm_input)

        layout.addLayout(form)

        buttons = QDialogButtonBox(QDialogButtonBox.Save | QDialogButtonBox.Cancel)
        buttons.accepted.connect(self._save)
        buttons.rejected.connect(self.reject)
        layout.addWidget(buttons)

        self.current_input.setFocus()
        apply_standard_behaviors(self)

    def _save(self):
        username = self.context.current_username
        if not username or username == "test":
            QMessageBox.warning(
                self, "Alterar Senha", "A conta de teste não permite alterar a senha."
            )
            return

        current = self.current_input.text()
        new = self.new_input.text()
        confirm = self.confirm_input.text()

        if not current or not new:
            QMessageBox.warning(self, "Alterar Senha", "Preencha todos os campos.")
            return
        if new != confirm:
            QMessageBox.warning(self, "Alterar Senha", "A nova senha não confere.")
            return

        try:
            self.context.auth.login(username, current)
        except Exception:
            QMessageBox.warning(self, "Alterar Senha", "Senha atual incorreta.")
            return

        user = self.context.users.find_by_username(username)
        if user is None:
            QMessageBox.warning(self, "Alterar Senha", "Usuário não encontrado.")
            return

        try:
            self.context.users.update_password(user.id, PasswordHasher().hash(new))
        except Exception as e:
            QMessageBox.critical(self, "Alterar Senha", f"Erro ao alterar a senha:\n{e}")
            return

        QMessageBox.information(self, "Alterar Senha", "Senha alterada com sucesso.")
        self.accept()