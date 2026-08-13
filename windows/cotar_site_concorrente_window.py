from PySide6.QtCore import Qt
from PySide6.QtGui import QAction, QColor
from PySide6.QtWidgets import (
    QApplication,
    QComboBox,
    QGroupBox,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QMessageBox,
    QPushButton,
    QSizePolicy,
    QSpacerItem,
    QTableWidget,
    QTableWidgetItem,
    QToolBar,
    QVBoxLayout,
    QWidget,
)

from services.concorrente_site import get_fetcher
from windows.app_behaviors import AppSubWindow


class CotarSiteConcorrenteWindow(AppSubWindow):
    def __init__(self, context):
        super().__init__()
        self.context = context
        self.setWindowTitle("Cotar no site do concorrente")
        self.setMinimumSize(900, 450)
        self._rows = []

        widget = QWidget()
        self.setWidget(widget)
        main = QVBoxLayout(widget)
        main.setContentsMargins(12, 12, 12, 12)
        main.setSpacing(10)

        toolbar = QToolBar()
        toolbar.setMovable(False)
        self.gravar_action = QAction("Gravar", self)
        self.gravar_action.setEnabled(False)
        self.gravar_action.triggered.connect(self._gravar)
        toolbar.addAction(self.gravar_action)

        self.buscar_site_action = QAction("Buscar preços no site", self)
        self.buscar_site_action.setEnabled(False)
        self.buscar_site_action.triggered.connect(self._buscar_precos_site)
        toolbar.addAction(self.buscar_site_action)
        main.addWidget(toolbar)

        filtros = QGroupBox("Filtros")
        filtro_layout = QHBoxLayout(filtros)
        filtro_layout.setSpacing(8)
        filtro_layout.setContentsMargins(12, 10, 12, 10)

        filtro_layout.addWidget(QLabel("ID Cotação:"))
        self.idcotacao_input = QLineEdit()
        self.idcotacao_input.setMaximumWidth(80)
        filtro_layout.addWidget(self.idcotacao_input)

        filtro_layout.addWidget(QLabel("Concorrente:"))
        self.concorrente_combo = QComboBox()
        self.concorrente_combo.setMinimumWidth(220)
        filtro_layout.addWidget(self.concorrente_combo)

        self.search_btn = QPushButton("Pesquisar")
        self.search_btn.clicked.connect(self._carregar)
        filtro_layout.addWidget(self.search_btn)

        filtro_layout.addItem(
            QSpacerItem(40, 20, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)
        )
        main.addWidget(filtros)

        self.table = QTableWidget(0, 5)
        self.table.setHorizontalHeaderLabels(
            [
                "ID",
                "Descrição",
                "Preço Varejo Atual",
                "Preço Site",
                "Fonte",
            ]
        )
        self.table.setEditTriggers(QTableWidget.NoEditTriggers)
        self.table.setSelectionBehavior(QTableWidget.SelectRows)
        self.table.setSortingEnabled(True)
        main.addWidget(self.table)

        self.idcotacao_input.returnPressed.connect(self._carregar)
        self._load_concorrentes()

    def _load_concorrentes(self):
        self.concorrente_combo.clear()
        items = self.context.concorrentes.find_all(only_active=True)
        for item in items:
            label = f"{item.nome} (ERP {item.id_erp}) [{item.tipo}]"
            self.concorrente_combo.addItem(label, item)

        if self.concorrente_combo.count() == 0:
            self.concorrente_combo.addItem("Nenhum concorrente cadastrado", None)

    def _selected_concorrente(self):
        return self.concorrente_combo.currentData()

    def _format_preco(self, value) -> str:
        if value is None:
            return "—"
        try:
            num = float(str(value).replace(",", "."))
        except (TypeError, ValueError):
            return "—"
        if num <= 0:
            return "—"
        return f"R$ {num:.2f}".replace(".", ",")

    def _parse_preco(self, value):
        if value is None:
            return None
        try:
            num = float(str(value).replace(",", "."))
        except (TypeError, ValueError):
            return None
        return num if num > 0 else None

    @staticmethod
    def _as_str(value) -> str:
        if value is None:
            return ""
        if isinstance(value, bytes):
            for enc in ("utf-8", "latin-1", "cp1252", "cp850"):
                try:
                    return value.decode(enc).strip()
                except UnicodeDecodeError:
                    continue
            return value.decode("latin-1", errors="replace").strip()
        return str(value).strip()

    def _carregar(self):
        idcotacao = self.idcotacao_input.text().strip()
        concorrente = self._selected_concorrente()

        if not idcotacao:
            QMessageBox.warning(self, "Cotação", "Informe o ID da cotação.")
            return
        if concorrente is None:
            QMessageBox.warning(
                self,
                "Cotação",
                "Cadastre um concorrente em Cadastros > Concorrentes.",
            )
            return

        cisspoder = self.context.cisspoder_config.get()
        if (
            not cisspoder
            or not cisspoder.host
            or not cisspoder.database_name
            or not cisspoder.username
        ):
            QMessageBox.warning(
                self,
                "Cotação",
                "Credenciais do CISSPoder (DB2) não configuradas.\n"
                "Acesse Arquivo > Configurações.",
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
                    self, "Erro de conexão", f"Falha ao conectar ao DB2:\n{error}"
                )
                return

            sql = (
                "SELECT "
                "pg.IDPRODUTO, "
                "ccp.IDSUBPRODUTO, "
                "pg.CODBAR, "
                "ccp.VALPRECOVAREJOCONCORRENTE, "
                "CAST(pg.DESCRRESPRODUTO AS VARCHAR(254)) "
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
            ibm_db.bind_param(stmt, 2, str(concorrente.id_erp))
            ibm_db.execute(stmt)

            self._rows.clear()
            self.table.setSortingEnabled(False)
            self.table.setRowCount(0)

            row_data = ibm_db.fetch_tuple(stmt)
            while row_data:
                idproduto = int(row_data[0]) if row_data[0] is not None else 0
                idsubproduto = int(row_data[1]) if row_data[1] is not None else 0
                item_id = self._as_str(row_data[0])
                codbar = self._as_str(row_data[2])
                preco_varejo_val = self._parse_preco(row_data[3])
                preco_varejo = self._format_preco(preco_varejo_val)
                descricao = self._as_str(row_data[4]) or "—"

                self._rows.append(
                    {
                        "idproduto": idproduto,
                        "idsubproduto": idsubproduto,
                        "item_id": item_id,
                        "codbar": codbar,
                        "descricao": descricao,
                        "preco_varejo": preco_varejo_val,
                        "preco_site": None,
                        "fonte": "",
                    }
                )
                self._add_row(item_id, descricao, preco_varejo, "—", "—")
                QApplication.processEvents()
                row_data = ibm_db.fetch_tuple(stmt)

            ibm_db.close(conn)
            self.table.setSortingEnabled(True)
            self._update_actions()

            if not self._rows:
                QMessageBox.information(
                    self,
                    "Cotação",
                    "Nenhum produto encontrado para esta cotação/concorrente.",
                )
        except Exception as e:
            QMessageBox.critical(self, "Erro", f"Erro ao consultar:\n{e}")

    def _buscar_precos_site(self):
        concorrente = self._selected_concorrente()
        if concorrente is None:
            QMessageBox.warning(self, "Cotação", "Selecione um concorrente.")
            return
        if not self._rows:
            QMessageBox.warning(self, "Cotação", "Pesquise a cotação primeiro.")
            return

        try:
            fetcher = get_fetcher(concorrente.tipo)
        except ValueError as e:
            QMessageBox.warning(self, "Cotação", str(e))
            return

        self.table.setSortingEnabled(False)
        for idx, row in enumerate(self._rows):
            codbar = row["codbar"]
            result = fetcher.fetch_by_gtin(codbar) if codbar else None
            if result and result.preco is not None and result.preco > 0:
                row["preco_site"] = result.preco
                row["fonte"] = result.fonte or concorrente.nome
            else:
                row["preco_site"] = None
                row["fonte"] = ""

            self._update_table_row(
                idx,
                row["item_id"],
                row["descricao"],
                self._format_preco(row["preco_varejo"]),
                self._format_preco(row["preco_site"]),
                row["fonte"] or "—",
            )
            QApplication.processEvents()

        self.table.setSortingEnabled(True)
        self._update_actions()

    def _gravar(self):
        idcotacao = self.idcotacao_input.text().strip()
        concorrente = self._selected_concorrente()

        if not idcotacao or concorrente is None:
            QMessageBox.warning(
                self, "Gravar", "Informe ID Cotação e Concorrente."
            )
            return

        if not self._rows:
            QMessageBox.warning(self, "Gravar", "Pesquise a cotação primeiro.")
            return

        por_produto = {}
        for row in self._rows:
            preco_val = row["preco_site"]
            if preco_val is None or preco_val <= 0:
                continue
            chave = (row["idproduto"], row["idsubproduto"])
            if chave not in por_produto or preco_val < por_produto[chave]:
                por_produto[chave] = preco_val

        if not por_produto:
            QMessageBox.warning(
                self, "Gravar", "Nenhum produto com preço de site para gravar."
            )
            return

        reply = QMessageBox.question(
            self,
            "Confirmar",
            f"Gravar {len(por_produto)} produtos no ERP?\n\n"
            f"ID Cotação: {idcotacao}\n"
            f"Concorrente: {concorrente.nome} (ERP {concorrente.id_erp})",
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
                    self, "Erro de conexão", f"Falha ao conectar ao DB2:\n{error}"
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
            for (idproduto, idsubproduto), preco in por_produto.items():
                try:
                    ibm_db.bind_param(stmt, 1, str(preco).replace(".", ","))
                    ibm_db.bind_param(stmt, 2, idcotacao)
                    ibm_db.bind_param(stmt, 3, str(concorrente.id_erp))
                    ibm_db.bind_param(stmt, 4, str(idproduto))
                    ibm_db.bind_param(stmt, 5, str(idsubproduto))
                    ibm_db.execute(stmt)
                    atualizados += 1
                except Exception as e:
                    print(f"[UPDATE] erro IDPRODUTO={idproduto}: {e}")
                    erros += 1

            ibm_db.close(conn)

            for row in self._rows:
                if row["preco_site"] is not None and row["preco_site"] > 0:
                    row["preco_varejo"] = row["preco_site"]

            self.table.setSortingEnabled(False)
            for idx, row in enumerate(self._rows):
                self._update_table_row(
                    idx,
                    row["item_id"],
                    row["descricao"],
                    self._format_preco(row["preco_varejo"]),
                    self._format_preco(row["preco_site"]),
                    row["fonte"] or "—",
                )
            self.table.setSortingEnabled(True)

            QMessageBox.information(
                self,
                "Gravar",
                f"{atualizados} produtos gravados.\n"
                + (f"{erros} erros." if erros else ""),
            )
        except Exception as e:
            QMessageBox.critical(self, "Erro", f"Erro ao gravar:\n{e}")

    def _update_actions(self):
        has_rows = bool(self._rows)
        has_site = any(
            row["preco_site"] is not None and row["preco_site"] > 0
            for row in self._rows
        )
        self.buscar_site_action.setEnabled(has_rows)
        self.gravar_action.setEnabled(has_site)

    def _add_row(self, item_id, descricao, preco_varejo, preco_site, fonte):
        row = self.table.rowCount()
        self.table.insertRow(row)
        self._update_table_row(row, item_id, descricao, preco_varejo, preco_site, fonte)

    def _update_table_row(self, row, item_id, descricao, preco_varejo, preco_site, fonte):
        values = [item_id, descricao, preco_varejo, preco_site, fonte]
        for col, value in enumerate(values):
            cell = QTableWidgetItem(value)
            cell.setTextAlignment(Qt.AlignCenter if col != 1 else Qt.AlignLeft | Qt.AlignVCenter)
            if col == 3 and value != "—":
                cell.setForeground(QColor("green"))
            self.table.setItem(row, col, cell)
