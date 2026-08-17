from argon2 import PasswordHasher
from PySide6.QtCore import Qt, Signal
from PySide6.QtWidgets import (
    QCheckBox,
    QDialog,
    QDialogButtonBox,
    QFormLayout,
    QGridLayout,
    QGroupBox,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QMessageBox,
    QPushButton,
    QTableWidget,
    QTableWidgetItem,
    QVBoxLayout,
    QWidget,
)

from services.permissions import ROUTINES, all_denied
from windows.app_behaviors import AppSubWindow, apply_standard_behaviors


class UsuarioFormDialog(QDialog):
    def __init__(self, parent=None, user=None, permissions: dict[str, bool] | None = None):
        super().__init__(parent)
        self.user = user
        self.setWindowTitle("Editar Usuário" if user else "Novo Usuário")
        self.setModal(True)
        self.setMinimumWidth(400)

        layout = QVBoxLayout(self)
        form = QFormLayout()

        self.username_input = QLineEdit()
        self.username_input.setPlaceholderText("Usuário")
        form.addRow("Usuário:", self.username_input)

        self.password_input = QLineEdit()
        self.password_input.setEchoMode(QLineEdit.Password)
        if user:
            self.password_input.setPlaceholderText("Em branco = manter a senha")
        form.addRow("Senha:", self.password_input)

        self.active_check = QCheckBox("Ativo")
        self.active_check.setChecked(True)
        form.addRow("", self.active_check)

        layout.addLayout(form)

        perm_group = QGroupBox("Permissões")
        perm_layout = QGridLayout(perm_group)
        self.permission_boxes: dict[str, QCheckBox] = {}
        for col, (key, label) in enumerate(ROUTINES.items()):
            box = QCheckBox(label)
            box.setChecked(bool((permissions or {}).get(key, False)))
            self.permission_boxes[key] = box
            perm_layout.addWidget(box, col // 2, col % 2)
        layout.addWidget(perm_group)

        buttons = QDialogButtonBox(QDialogButtonBox.Save | QDialogButtonBox.Cancel)
        buttons.accepted.connect(self.accept)
        buttons.rejected.connect(self.reject)
        layout.addWidget(buttons)

        if user:
            self.username_input.setText(user.username)
            self.active_check.setChecked(user.active)

        apply_standard_behaviors(self)

    def get_data(self) -> tuple[str, str, bool, dict[str, bool]] | None:
        username = self.username_input.text().strip()
        password = self.password_input.text()
        active = self.active_check.isChecked()

        if not username:
            QMessageBox.warning(self, "Usuário", "Informe o usuário.")
            return None
        if not self.user and not password:
            QMessageBox.warning(self, "Usuário", "Informe a senha.")
            return None

        permissions = {
            key: box.isChecked() for key, box in self.permission_boxes.items()
        }
        return username, password, active, permissions


class UsuariosWindow(AppSubWindow):
    permissions_changed = Signal()

    def __init__(self, context):
        super().__init__()
        self.context = context
        self.setWindowTitle("Usuários")
        self.setMinimumSize(720, 420)

        widget = QWidget()
        self.setWidget(widget)
        layout = QVBoxLayout(widget)
        layout.setContentsMargins(12, 12, 12, 12)
        layout.setSpacing(8)

        top = QHBoxLayout()
        top.addWidget(QLabel("Buscar:"))
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("Digite para buscar...")
        self.search_input.returnPressed.connect(self._search)
        top.addWidget(self.search_input)

        search_btn = QPushButton("OK")
        search_btn.clicked.connect(self._search)
        top.addWidget(search_btn)
        top.addStretch()

        self.add_btn = QPushButton("Novo")
        self.add_btn.clicked.connect(self._add)
        top.addWidget(self.add_btn)

        self.edit_btn = QPushButton("Editar")
        self.edit_btn.clicked.connect(self._edit)
        top.addWidget(self.edit_btn)

        self.delete_btn = QPushButton("Excluir")
        self.delete_btn.clicked.connect(self._delete)
        top.addWidget(self.delete_btn)

        layout.addLayout(top)

        self.table = QTableWidget(0, 4)
        self.table.setHorizontalHeaderLabels(["ID", "Usuário", "Ativo", "Criado em"])
        self.table.setEditTriggers(QTableWidget.NoEditTriggers)
        self.table.setSelectionBehavior(QTableWidget.SelectRows)
        self.table.setSelectionMode(QTableWidget.SingleSelection)
        self.table.setAlternatingRowColors(True)
        self.table.verticalHeader().setVisible(False)
        self.table.doubleClicked.connect(self._edit)
        layout.addWidget(self.table)

        self._load()

    @staticmethod
    def _hash_password(password: str) -> str:
        return PasswordHasher().hash(password)

    def _load(self, term: str | None = None):
        repo = self.context.users
        items = repo.search(term) if term else repo.find_all()

        self.table.setRowCount(0)
        for item in items:
            row = self.table.rowCount()
            self.table.insertRow(row)
            created = (
                item.created_at.strftime("%d/%m/%Y %H:%M")
                if item.created_at is not None
                else ""
            )
            values = [
                str(item.id),
                item.username,
                "Sim" if item.active else "Não",
                created,
            ]
            for col, value in enumerate(values):
                cell = QTableWidgetItem(value)
                cell.setTextAlignment(Qt.AlignCenter)
                if col == 0:
                    cell.setData(Qt.UserRole, item.id)
                self.table.setItem(row, col, cell)

    def _search(self):
        term = self.search_input.text().strip()
        self._load(term if term else None)

    def _selected_id(self) -> int | None:
        rows = self.table.selectionModel().selectedRows()
        if not rows:
            return None
        item = self.table.item(rows[0].row(), 0)
        return int(item.data(Qt.UserRole)) if item else None

    def _add(self):
        dlg = UsuarioFormDialog(self, permissions=all_denied())
        if dlg.exec() != QDialog.Accepted:
            return
        data = dlg.get_data()
        if not data:
            return
        username, password, active, permissions = data

        if self.context.users.find_by_username(username):
            QMessageBox.warning(self, "Usuário", f"Já existe um usuário '{username}'.")
            return

        try:
            user = self.context.users.create(username, self._hash_password(password), active)
            self.context.user_permissions.set_all(user.id, permissions)
            self._load()
            self.permissions_changed.emit()
        except Exception as e:
            QMessageBox.critical(self, "Usuário", f"Erro ao salvar:\n{e}")

    def _edit(self):
        user_id = self._selected_id()
        if user_id is None:
            QMessageBox.warning(self, "Usuário", "Selecione um usuário.")
            return

        atual = self.context.users.find_by_id(user_id)
        if not atual:
            QMessageBox.warning(self, "Usuário", "Registro não encontrado.")
            return

        permissions = self.context.user_permissions.get(user_id)
        dlg = UsuarioFormDialog(self, atual, permissions)
        if dlg.exec() != QDialog.Accepted:
            return
        data = dlg.get_data()
        if not data:
            return
        username, password, active, permissions = data

        if not active and atual.username == self.context.current_username:
            QMessageBox.warning(self, "Usuário", "Não é possível desativar o próprio usuário.")
            return

        if username != atual.username and self.context.users.find_by_username(username):
            QMessageBox.warning(self, "Usuário", f"Já existe um usuário '{username}'.")
            return

        try:
            self.context.users.update(user_id, username, active)
            if password:
                self.context.users.update_password(user_id, self._hash_password(password))
            self.context.user_permissions.set_all(user_id, permissions)
            self._load()
            self.permissions_changed.emit()
        except Exception as e:
            QMessageBox.critical(self, "Usuário", f"Erro ao atualizar:\n{e}")

    def _delete(self):
        user_id = self._selected_id()
        if user_id is None:
            QMessageBox.warning(self, "Usuário", "Selecione um usuário.")
            return

        atual = self.context.users.find_by_id(user_id)
        if not atual:
            QMessageBox.warning(self, "Usuário", "Registro não encontrado.")
            return

        if atual.username == self.context.current_username:
            QMessageBox.warning(self, "Usuário", "Não é possível excluir o usuário logado.")
            return

        reply = QMessageBox.question(
            self,
            "Excluir",
            f"Deseja excluir o usuário '{atual.username}'?",
            QMessageBox.Yes | QMessageBox.No,
        )
        if reply != QMessageBox.Yes:
            return

        try:
            self.context.user_permissions.delete_all(user_id)
            self.context.users.delete(user_id)
            self._load()
            self.permissions_changed.emit()
        except Exception as e:
            QMessageBox.critical(self, "Usuário", f"Erro ao excluir:\n{e}")
