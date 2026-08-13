import json
import time
import requests

from PySide6.QtWidgets import (
    QWidget,
    QTableWidgetItem,
    QMessageBox,
    QApplication,
    QLabel,
    QComboBox,
)
from PySide6.QtCore import Qt
from PySide6.QtGui import QColor

from ui.ui_relatorio_concorrencia import Ui_RelatorioConcorrenciaWindow
from windows.app_behaviors import AppSubWindow


class RelatorioConcorrenciaWindow(AppSubWindow):
    BASE_URL = "https://menorpreco.notaparana.pr.gov.br/api/v1/produtos"
    LOCATIONS = {
        "Triunfo, PE": ("7nsgky426yt", "26395"),
        "Serra Talhada, PE": ("7nsf8dmv2q1", "26395"),
    }

    def __init__(self, context):
        super().__init__()
        self.context = context
        self.setWindowTitle("Relatorio de Concorrencia")
        self.setMinimumSize(1000, 500)

        widget = QWidget()
        self.ui = Ui_RelatorioConcorrenciaWindow()
        self.ui.setupUi(widget)
        self.setWidget(widget)

        self.ui.resultadoTable.setSortingEnabled(True)

        self.ui.filtroLayout.insertWidget(0, QLabel("Local:"))
        self.local_combo = QComboBox()
        self.local_combo.addItems(list(self.LOCATIONS.keys()))
        self.ui.filtroLayout.insertWidget(1, self.local_combo)

        self.ui.gerarButton.clicked.connect(self._carregar)

    def _carregar(self):
        idcotacao = self.ui.idcotacaoInput.text().strip()
        idempresa = self.ui.idempresaInput.text().strip()

        if not all([idcotacao, idempresa]):
            QMessageBox.warning(
                self, "Relatorio",
                "Preencha ID Cotacao e ID Empresa."
            )
            return

        cisspoder = self.context.cisspoder_config.get()
        if not cisspoder or not cisspoder.host or not cisspoder.database_name or not cisspoder.username:
            QMessageBox.warning(
                self, "Relatorio",
                "Credenciais do CISSPoder (DB2) nao configuradas.\n"
                "Acesse Arquivo > Configuracoes."
            )
            return

        try:
            import ibm_db

            conn_str = (
                f"DATABASE={cisspoder.database_name};"
                f"HOSTNAME={cisspoder.host};"
                f"PORT={cisspoder.port};"
                f"PROTOCOL=TCPIP;"
                f"UID={cisspoder.username};"
                f"PWD={cisspoder.password};"
            )
            conn = ibm_db.connect(conn_str, "", "")
            if not conn:
                error = ibm_db.conn_errormsg()
                QMessageBox.critical(
                    self, "Erro de conexao",
                    f"Falha ao conectar ao DB2:\n{error}"
                )
                return

            sql = (
                "SELECT DISTINCT "
                "pg.CODBAR, "
                "POLITICA_PRECO_PRODUTO.CUSTOGERENCIAL, "
                "POLITICA_PRECO_PRODUTO.VALPRECOVAREJO, "
                "POLITICA_PRECO_PRODUTO.VALPRECOATACADO "
                "FROM "
                "COTACAO_CONCORRENCIA, "
                "PRODUTOS_VIEW "
                "LEFT OUTER JOIN POLITICA_PRECO_PRODUTO "
                "ON PRODUTOS_VIEW.IDPRODUTO = POLITICA_PRECO_PRODUTO.IDPRODUTO "
                "AND PRODUTOS_VIEW.IDSUBPRODUTO = POLITICA_PRECO_PRODUTO.IDSUBPRODUTO, "
                "COTACAO_CONCORRENCIA_PROD "
                "LEFT OUTER JOIN PRODUTO_GRADE pg "
                "ON pg.IDPRODUTO = COTACAO_CONCORRENCIA_PROD.IDPRODUTO "
                "AND pg.IDSUBPRODUTO = COTACAO_CONCORRENCIA_PROD.IDSUBPRODUTO "
                "WHERE "
                "COTACAO_CONCORRENCIA_PROD.IDCOTACAO = COTACAO_CONCORRENCIA.IDCOTACAO "
                "AND PRODUTOS_VIEW.IDPRODUTO = COTACAO_CONCORRENCIA_PROD.IDPRODUTO "
                "AND PRODUTOS_VIEW.IDSUBPRODUTO = COTACAO_CONCORRENCIA_PROD.IDSUBPRODUTO "
                "AND COTACAO_CONCORRENCIA.IDCOTACAO IN (?) "
                "AND POLITICA_PRECO_PRODUTO.IDEMPRESA IN (?) "
                "AND LENGTH(pg.CODBAR) = 13"
            )

            stmt = ibm_db.prepare(conn, sql)
            ibm_db.bind_param(stmt, 1, idcotacao)
            ibm_db.bind_param(stmt, 2, idempresa)
            ibm_db.execute(stmt)

            self.ui.resultadoTable.setRowCount(0)
            preco_cache = {}
            row_data = ibm_db.fetch_tuple(stmt)

            while row_data:
                codbar = str(row_data[0]) if row_data[0] is not None else ""
                custo = self._to_float(row_data[1])
                varejo_nosso = self._to_float(row_data[2])
                atacado_nosso = self._to_float(row_data[3])

                if codbar not in preco_cache:
                    preco_cache[codbar] = self._buscar_precos(codbar)

                for desc, concorrente, preco_conc in preco_cache[codbar]:
                    self._add_row(
                        desc, custo, varejo_nosso, atacado_nosso,
                        concorrente, preco_conc,
                    )

                QApplication.processEvents()
                row_data = ibm_db.fetch_tuple(stmt)

            ibm_db.close(conn)

        except Exception as e:
            QMessageBox.critical(self, "Erro", f"Erro ao consultar:\n{e}")

    def _buscar_precos(self, gtin: str) -> list:
        if not gtin:
            return [("\u2014", "\u2014", "\u2014")]
        local_key = self.local_combo.currentText()
        local, mun = self.LOCATIONS.get(local_key, ("7nsgky426yt", "26395"))
        params = {
            "local": local,
            "raio": "20",
            "data": "1",
            "ordem": "0",
            "gtin": gtin,
            "mun": mun,
        }
        try:
            time.sleep(3)
            resp = requests.get(
                self.BASE_URL, params=params,
                headers={
                    "Accept": "application/json",
                    "User-Agent": (
                        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                        "AppleWebKit/537.36 (KHTML, like Gecko) "
                        "Chrome/148.0.0.0 Safari/537.36"
                    ),
                },
                timeout=15,
            )
            resp.raise_for_status()
            data = json.loads(resp.content)
            produtos = data.get("produtos", [])

            if not produtos:
                return [("\u2014", "\u2014", "\u2014")]

            results = []
            for p in produtos:
                desc = p.get("desc", "")
                valor = p.get("valor", "")
                est = p.get("estabelecimento", {})
                nome = est.get("nm_fan", "") or est.get("nm_emp", "")
                if nome and valor:
                    preco = self._to_float(valor)
                    if preco > 0:
                        results.append((desc, nome, preco))
            return results
        except Exception:
            return [("\u2014", "\u2014", "\u2014")]

    def _add_row(self, desc, custo, varejo_nosso, atacado_nosso,
                 concorrente, preco_conc):
        table = self.ui.resultadoTable
        row = table.rowCount()
        table.insertRow(row)

        self._set_cell(row, 0, desc, Qt.AlignLeft | Qt.AlignVCenter)
        self._set_cell(row, 1, f"R$ {custo:,.2f}" if custo else "\u2014",
                       Qt.AlignCenter)
        self._set_cell(row, 2, f"R$ {varejo_nosso:,.2f}" if varejo_nosso else "\u2014",
                       Qt.AlignCenter)
        self._set_cell(row, 3, f"R$ {atacado_nosso:,.2f}" if atacado_nosso else "\u2014",
                       Qt.AlignCenter)
        self._set_cell(row, 4, concorrente, Qt.AlignLeft | Qt.AlignVCenter)

        cor = self._comparar_cor(varejo_nosso, preco_conc)
        self._set_cell(row, 5, f"R$ {preco_conc:,.2f}" if preco_conc else "\u2014",
                       Qt.AlignCenter, cor)

    def _set_cell(self, row, col, text, alignment, color=None):
        item = QTableWidgetItem(text)
        item.setTextAlignment(alignment)
        if color:
            item.setForeground(color)
            item.setBackground(QColor(color).lighter(190))
        self.ui.resultadoTable.setItem(row, col, item)

    def _comparar_cor(self, nosso, conc):
        if not nosso or not conc:
            return None
        if conc < nosso:
            return QColor("red")
        if nosso < conc:
            return QColor("green")
        return None

    @staticmethod
    def _to_float(val):
        if val is None:
            return 0.0
        s = str(val).replace(",", ".")
        try:
            return float(s)
        except ValueError:
            return 0.0
