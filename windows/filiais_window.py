from PySide6.QtWidgets import (
    QWidget,
    QTableWidgetItem,
)
from ui.ui_filiais import Ui_FiliaisWindow
from windows.app_behaviors import AppSubWindow


class FiliaisWindow(AppSubWindow):
    def __init__(self, context):
        super().__init__()
        self.context = context
        self.setWindowTitle("Filiais")

        widget = QWidget()
        self.ui = Ui_FiliaisWindow()
        self.ui.setupUi(widget)
        self.setWidget(widget)

        self.ui.OkButton.clicked.connect(self._search)
        self.ui.SearchLineEdit.returnPressed.connect(self._search)

        self._load_data()

    def _load_data(self, term: str | None = None):
        repo = self.context.filiais

        if term:
            filiais = repo.search(term)
        else:
            filiais = repo.find_all()

        table = self.ui.FiliaisTable
        table.setRowCount(0)

        for filial in filiais:
            row = table.rowCount()
            table.insertRow(row)
            table.setItem(row, 0, QTableWidgetItem(str(filial.id)))
            table.setItem(row, 1, QTableWidgetItem(filial.nome_fantasia))
            table.setItem(row, 2, QTableWidgetItem(filial.endereco))
            table.setItem(row, 3, QTableWidgetItem(filial.cidade))
            table.setItem(row, 4, QTableWidgetItem(filial.estado))
            table.setItem(row, 5, QTableWidgetItem(filial.telefone))

    def _search(self):
        term = self.ui.SearchLineEdit.text().strip()
        self._load_data(term if term else None)