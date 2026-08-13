from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QCheckBox,
    QComboBox,
    QDialog,
    QDialogButtonBox,
    QFormLayout,
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

from database.repositories.concorrente_repository import CONCORRENTE_TIPOS
from services.concorrente_site.registry import available_tipos
from windows.app_behaviors import AppSubWindow, apply_standard_behaviors


class ConcorrenteFormDialog(QDialog):
    def __init__(self, parent=None, concorrente=None):
        super().__init__(parent)
        self.concorrente = concorrente
        self.setWindowTitle("Editar Concorrente" if concorrente else "Novo Concorrente")
        self.setModal(True)
        self.setMinimumWidth(360)

        layout = QVBoxLayout(self)
        form = QFormLayout()

        self.nome_input = QLineEdit()
        self.nome_input.setPlaceholderText("Nome do concorrente")
        form.addRow("Nome:", self.nome_input)

        self.id_erp_input = QLineEdit()
        self.id_erp_input.setPlaceholderText("ID no CISSPoder")
        form.addRow("ID ERP:", self.id_erp_input)

        self.tipo_combo = QComboBox()
        tipos = available_tipos() or list(CONCORRENTE_TIPOS)
        self.tipo_combo.addItems(tipos)
        form.addRow("Tipo:", self.tipo_combo)

        self.active_check = QCheckBox("Ativo")
        self.active_check.setChecked(True)
        form.addRow("", self.active_check)

        layout.addLayout(form)

        buttons = QDialogButtonBox(QDialogButtonBox.Save | QDialogButtonBox.Cancel)
        buttons.accepted.connect(self.accept)
        buttons.rejected.connect(self.reject)
        layout.addWidget(buttons)

        if concorrente:
            self.nome_input.setText(concorrente.nome)
            self.id_erp_input.setText(str(concorrente.id_erp))
            idx = self.tipo_combo.findText(concorrente.tipo)
            if idx >= 0:
                self.tipo_combo.setCurrentIndex(idx)
            self.active_check.setChecked(concorrente.active)

        apply_standard_behaviors(self)

    def get_data(self) -> tuple[str, int, str, bool] | None:
        nome = self.nome_input.text().strip()
        id_erp_raw = self.id_erp_input.text().strip()
        tipo = self.tipo_combo.currentText().strip()
        active = self.active_check.isChecked()

        if not nome:
            QMessageBox.warning(self, "Concorrente", "Informe o nome.")
            return None
        if not id_erp_raw.isdigit():
            QMessageBox.warning(self, "Concorrente", "ID ERP deve ser numérico.")
            return None
        if not tipo:
            QMessageBox.warning(self, "Concorrente", "Selecione o tipo.")
            return None

        return nome, int(id_erp_raw), tipo, active


class ConcorrentesWindow(AppSubWindow):
    def __init__(self, context):
        super().__init__()
        self.context = context
        self.setWindowTitle("Concorrentes")
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

        self.table = QTableWidget(0, 5)
        self.table.setHorizontalHeaderLabels(
            ["ID", "Nome", "ID ERP", "Tipo", "Ativo"]
        )
        self.table.setEditTriggers(QTableWidget.NoEditTriggers)
        self.table.setSelectionBehavior(QTableWidget.SelectRows)
        self.table.setSelectionMode(QTableWidget.SingleSelection)
        self.table.setAlternatingRowColors(True)
        self.table.verticalHeader().setVisible(False)
        self.table.doubleClicked.connect(self._edit)
        layout.addWidget(self.table)

        self._load()

    def _load(self, term: str | None = None):
        repo = self.context.concorrentes
        items = repo.search(term) if term else repo.find_all()

        self.table.setRowCount(0)
        for item in items:
            row = self.table.rowCount()
            self.table.insertRow(row)
            values = [
                str(item.id),
                item.nome,
                str(item.id_erp),
                item.tipo,
                "Sim" if item.active else "Não",
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
        dlg = ConcorrenteFormDialog(self)
        if dlg.exec() != QDialog.Accepted:
            return
        data = dlg.get_data()
        if not data:
            return
        nome, id_erp, tipo, active = data
        try:
            self.context.concorrentes.create(nome, id_erp, tipo, active)
            self._load()
        except Exception as e:
            QMessageBox.critical(self, "Concorrente", f"Erro ao salvar:\n{e}")

    def _edit(self):
        concorrente_id = self._selected_id()
        if concorrente_id is None:
            QMessageBox.warning(self, "Concorrente", "Selecione um concorrente.")
            return

        atual = self.context.concorrentes.find_by_id(concorrente_id)
        if not atual:
            QMessageBox.warning(self, "Concorrente", "Registro não encontrado.")
            return

        dlg = ConcorrenteFormDialog(self, atual)
        if dlg.exec() != QDialog.Accepted:
            return
        data = dlg.get_data()
        if not data:
            return
        nome, id_erp, tipo, active = data
        try:
            self.context.concorrentes.update(concorrente_id, nome, id_erp, tipo, active)
            self._load()
        except Exception as e:
            QMessageBox.critical(self, "Concorrente", f"Erro ao atualizar:\n{e}")

    def _delete(self):
        concorrente_id = self._selected_id()
        if concorrente_id is None:
            QMessageBox.warning(self, "Concorrente", "Selecione um concorrente.")
            return

        reply = QMessageBox.question(
            self,
            "Excluir",
            "Deseja excluir o concorrente selecionado?",
            QMessageBox.Yes | QMessageBox.No,
        )
        if reply != QMessageBox.Yes:
            return

        try:
            self.context.concorrentes.delete(concorrente_id)
            self._load()
        except Exception as e:
            QMessageBox.critical(self, "Concorrente", f"Erro ao excluir:\n{e}")
