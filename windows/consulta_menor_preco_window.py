import json
import time
import requests

from PySide6.QtWidgets import (
    QWidget,
    QTableWidgetItem,
    QMessageBox,
    QApplication,
    QLineEdit,
    QLabel,
    QComboBox,
)
from PySide6.QtCore import Qt
from PySide6.QtGui import QColor

from ui.ui_consulta_menor_preco_window import Ui_ConsultaMenorPrecoWindow
from windows.app_behaviors import AppSubWindow


class ConsultaMenorPrecoWindow(AppSubWindow):
    BASE_URL = "https://menorpreco.notaparana.pr.gov.br/api/v1/produtos"
    LOCATIONS = {
        "Triunfo, PE": ("7nsgky426yt", "26395"),
        "Serra Talhada, PE": ("7nsf8dmv2q1", "26395"),
    }

    def __init__(self, context):
        super().__init__()
        self.context = context
        self.setWindowTitle("Consulta Menor Preco")
        self.setMinimumSize(900, 450)
        self._rows = []

        widget = QWidget()
        self.ui = Ui_ConsultaMenorPrecoWindow()
        self.ui.setupUi(widget)
        self.setWidget(widget)

        self.ui.resultadoTable.setSortingEnabled(True)

        self.ui.filtroLayout.insertWidget(0, QLabel("Local:"))
        self.local_combo = QComboBox()
        self.local_combo.addItems(list(self.LOCATIONS.keys()))
        self.ui.filtroLayout.insertWidget(1, self.local_combo)

        self.ui.filtroLayout.insertWidget(6, QLabel("Filtrar Concorrente:"))
        self.concorrente_filter = QLineEdit()
        self.concorrente_filter.setPlaceholderText("Digite parte do nome...")
        self.concorrente_filter.setMaximumSize(180, 16777215)
        self.concorrente_filter.textChanged.connect(self._aplicar_filtro)
        self.ui.filtroLayout.insertWidget(7, self.concorrente_filter)

        self.ui.searchButton.clicked.connect(self._carregar)
        self.ui.atualizarButton.clicked.connect(self._atualizar_cotacao)
        self.ui.idconcorrenteInput.returnPressed.connect(self._carregar)

    def _carregar(self):
        idcotacao = self.ui.idcotacaoInput.text().strip()
        idconcorrente = self.ui.idconcorrenteInput.text().strip()

        if not idcotacao or not idconcorrente:
            QMessageBox.warning(
                self, "Consulta Menor Preco",
                "Informe ID Cotacao e ID Concorrente."
            )
            return

        cisspoder = self.context.cisspoder_config.get()
        if not cisspoder or not cisspoder.host or not cisspoder.database_name or not cisspoder.username:
            QMessageBox.warning(
                self, "Consulta Menor Preco",
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
                "SELECT "
                "pg.IDPRODUTO, "
                "ccp.IDSUBPRODUTO, "
                "pg.CODBAR, "
                "ccp.* "
                "FROM COTACAO_CONCORRENCIA_PROD ccp "
                "LEFT JOIN PRODUTO_GRADE pg "
                "ON pg.IDPRODUTO = ccp.IDPRODUTO "
                "AND pg.IDSUBPRODUTO = ccp.IDSUBPRODUTO "
                "WHERE IDCOTACAO = ? "
                "AND IDCONCORRENTE = ? "
                "AND LENGTH(pg.CODBAR) = 13"
            )
            stmt = ibm_db.prepare(conn, sql)
            ibm_db.bind_param(stmt, 1, idcotacao)
            ibm_db.bind_param(stmt, 2, idconcorrente)
            ibm_db.execute(stmt)

            print(f"[DB2] IDCOTACAO={idcotacao}, IDCONCORRENTE={idconcorrente}")

            self._rows.clear()
            self.ui.resultadoTable.setRowCount(0)
            preco_cache = {}
            row_data = ibm_db.fetch_tuple(stmt)

            while row_data:
                idproduto = int(row_data[0]) if row_data[0] is not None else 0
                idsubproduto = int(row_data[1]) if row_data[1] is not None else 0
                item_id = str(row_data[0]) if row_data[0] is not None else ""
                codbar = str(row_data[2]) if row_data[2] is not None else ""

                print(f"[DB2] row: ID={item_id}, CODBAR={codbar}")

                if codbar not in preco_cache:
                    preco_cache[codbar] = self._buscar_precos(codbar)

                for desc, preco, concorrente in preco_cache[codbar]:
                    self._rows.append(
                        (idproduto, idsubproduto, item_id, codbar,
                         desc, preco, concorrente)
                    )

                row_data = ibm_db.fetch_tuple(stmt)

            ibm_db.close(conn)
            self._aplicar_filtro()

        except Exception as e:
            QMessageBox.critical(self, "Erro", f"Erro ao consultar:\n{e}")

    def _atualizar_cotacao(self):
        idcotacao = self.ui.idcotacaoInput.text().strip()
        idconcorrente = self.ui.idconcorrenteInput.text().strip()

        if not idcotacao or not idconcorrente:
            QMessageBox.warning(
                self, "Atualizar Cotacao",
                "Preencha ID Cotacao e ID Concorrente."
            )
            return

        if not self._rows:
            QMessageBox.warning(
                self, "Atualizar Cotacao",
                "Gere a consulta primeiro."
            )
            return

        min_por_produto = {}
        filtro = self.concorrente_filter.text().strip().lower()

        for idproduto, idsubproduto, _, _, _, preco_str, concorrente in self._rows:
            if filtro and filtro not in concorrente.lower():
                continue
            chave = (idproduto, idsubproduto)
            preco = self._to_float(preco_str.replace("R$ ", ""))
            if preco <= 0:
                continue
            if chave not in min_por_produto or preco < min_por_produto[chave]:
                min_por_produto[chave] = preco

        if not min_por_produto:
            QMessageBox.warning(
                self, "Atualizar Cotacao",
                "Nenhum produto para atualizar."
            )
            return

        reply = QMessageBox.question(
            self, "Confirmar",
            f"Atualizar {len(min_por_produto)} produtos "
            f"com o menor preco da API?\n\n"
            f"ID Cotacao: {idcotacao}\n"
            f"ID Concorrente: {idconcorrente}",
            QMessageBox.Yes | QMessageBox.No,
        )
        if reply != QMessageBox.Yes:
            return

        cisspoder = self.context.cisspoder_config.get()
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
                "UPDATE COTACAO_CONCORRENCIA_PROD "
                "SET VALPRECOVAREJOCONCORRENTE = ? "
                "WHERE IDCOTACAO = ? "
                "AND IDCONCORRENTE = ? "
                "AND IDPRODUTO = ? "
                "AND IDSUBPRODUTO = ?"
            )
            stmt = ibm_db.prepare(conn, sql)

            atualizados = 0
            erros = 0

            for (idproduto, idsubproduto), preco in min_por_produto.items():
                try:
                    ibm_db.bind_param(stmt, 1, str(preco).replace(".", ","))
                    ibm_db.bind_param(stmt, 2, idcotacao)
                    ibm_db.bind_param(stmt, 3, idconcorrente)
                    ibm_db.bind_param(stmt, 4, str(idproduto))
                    ibm_db.bind_param(stmt, 5, str(idsubproduto))
                    ibm_db.execute(stmt)
                    atualizados += 1
                except Exception as e:
                    print(f"[UPDATE] erro IDPRODUTO={idproduto}: {e}")
                    erros += 1

            ibm_db.close(conn)

            QMessageBox.information(
                self, "Atualizar Cotacao",
                f"{atualizados} produtos atualizados.\n"
                + (f"{erros} erros." if erros else "")
            )
        except Exception as e:
            QMessageBox.critical(self, "Erro", f"Erro ao atualizar:\n{e}")

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
        print(f"[API] GET {self.BASE_URL} {params}")
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
            print(f"[API] status={resp.status_code}")
            resp.raise_for_status()
            data = json.loads(resp.content)
            produtos = data.get("produtos", [])
            print(f"[API] response: total={len(produtos)} produtos")

            if not produtos:
                return [("\u2014", "\u2014", "\u2014")]

            results = []
            for p in produtos:
                desc = p.get("desc", "")
                valor = p.get("valor", "")
                est = p.get("estabelecimento", {})
                nome = est.get("nm_fan", "") or est.get("nm_emp", "") or "\u2014"
                print(f"[API]   R$ {valor} - {nome}")
                results.append((desc, f"R$ {valor}", nome))
            return results
        except Exception as e:
            print(f"[API] ERROR: {e}")
            return [("\u2014", "\u2014", "\u2014")]

    def _aplicar_filtro(self):
        filtro = self.concorrente_filter.text().strip().lower()
        self.ui.resultadoTable.setSortingEnabled(False)
        self.ui.resultadoTable.setRowCount(0)

        for _, _, item_id, codbar, desc, preco, concorrente in self._rows:
            if filtro and filtro not in concorrente.lower():
                continue
            self._add_row(item_id, codbar, desc, preco, concorrente)

        self.ui.resultadoTable.setSortingEnabled(True)
        QApplication.processEvents()

    def _add_row(self, item_id, codbar, desc, preco, concorrente):
        table = self.ui.resultadoTable
        row = table.rowCount()
        table.insertRow(row)

        id_item = QTableWidgetItem(item_id)
        id_item.setTextAlignment(Qt.AlignCenter)
        table.setItem(row, 0, id_item)

        codbar_item = QTableWidgetItem(codbar)
        codbar_item.setTextAlignment(Qt.AlignCenter)
        table.setItem(row, 1, codbar_item)

        desc_item = QTableWidgetItem(desc)
        desc_item.setTextAlignment(Qt.AlignCenter)
        table.setItem(row, 2, desc_item)

        preco_item = QTableWidgetItem(preco)
        preco_item.setTextAlignment(Qt.AlignCenter)
        if preco != "\u2014":
            preco_item.setForeground(QColor("green"))
        table.setItem(row, 3, preco_item)

        conc_item = QTableWidgetItem(concorrente)
        conc_item.setTextAlignment(Qt.AlignCenter)
        table.setItem(row, 4, conc_item)

    @staticmethod
    def _to_float(val):
        if val is None:
            return 0.0
        s = str(val).replace(",", ".")
        try:
            return float(s)
        except ValueError:
            return 0.0
