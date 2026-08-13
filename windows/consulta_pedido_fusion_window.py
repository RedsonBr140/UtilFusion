from PySide6.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QLineEdit,
    QPushButton,
    QGroupBox,
    QTableWidget,
    QTableWidgetItem,
    QMessageBox,
    QApplication,
)
from PySide6.QtCore import Qt
from PySide6.QtGui import QColor

from windows.app_behaviors import AppSubWindow


class ConsultaPedidoFusionWindow(AppSubWindow):
    def __init__(self, context):
        super().__init__()
        self.context = context
        self.setWindowTitle("Consulta Pedido Fusion")
        self.setMinimumSize(700, 280)

        widget = QWidget()
        self.setWidget(widget)

        main_layout = QVBoxLayout(widget)
        main_layout.setContentsMargins(16, 16, 16, 16)
        main_layout.setSpacing(12)

        input_group = QGroupBox("Nota/Cupom")
        input_layout = QHBoxLayout(input_group)
        input_layout.setContentsMargins(12, 12, 12, 12)
        input_layout.setSpacing(8)

        self.nota_input = QLineEdit()
        self.nota_input.setPlaceholderText("Ex: 588227,522345,123456")
        self.nota_input.returnPressed.connect(self._pesquisar)
        input_layout.addWidget(self.nota_input)

        self.search_btn = QPushButton("Pesquisar")
        self.search_btn.clicked.connect(self._pesquisar)
        input_layout.addWidget(self.search_btn)

        main_layout.addWidget(input_group)

        self.table = QTableWidget()
        self.table.setColumnCount(4)
        self.table.setHorizontalHeaderLabels([
            "Nota CISS",
            "Nº Pedido Fusion",
            "Está no Fusion",
            "Pode formar carga",
        ])
        self.table.setEditTriggers(QTableWidget.NoEditTriggers)
        self.table.setSelectionBehavior(QTableWidget.SelectRows)
        main_layout.addWidget(self.table)

        self.nota_input.setFocus()

    def _pesquisar(self):
        raw = self.nota_input.text().strip()
        if not raw:
            QMessageBox.warning(
                self,
                "Consulta Pedido",
                "Informe ao menos uma Nota/Cupom."
            )
            return

        notas = [n.strip() for n in raw.split(",") if n.strip()]
        cisspoder = self.context.cisspoder_config.get()
        if not cisspoder or not cisspoder.host or not cisspoder.database_name or not cisspoder.username:
            QMessageBox.warning(
                self,
                "Consulta Pedido",
                "Credenciais do CISSPoder (DB2) não configuradas.\n"
                "Acesse Arquivo > Configurações."
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
                    self,
                    "Erro de conexão",
                    f"Falha ao conectar ao DB2:\n{error}"
                )
                return

            sql_pedido = (
                "SELECT NUM_PEDIDO_ORIG_680, SN_PODE_FORMAR_CARGA "
                "FROM FUSIONT.FUSION_VW_ENTREGA "
                "WHERE NF_PK_680 = ?"
            )
            stmt_pedido = ibm_db.prepare(conn, sql_pedido)

            sql_fallback = (
                "SELECT fvp.NF_PK_680, fvp.NUM_PEDIDO_ORIG_680, "
                "fvp.SN_PODE_FORMAR_CARGA "
                "FROM UTILFUSION.FUSION_VW_PEDIDOS fvp "
                "WHERE fvp.NF_PK_680 = ?"
            )
            stmt_fallback = ibm_db.prepare(conn, sql_fallback)

            self.table.setRowCount(0)

            for nota in notas:
                ibm_db.bind_param(stmt_pedido, 1, nota)
                ibm_db.execute(stmt_pedido)
                row = ibm_db.fetch_tuple(stmt_pedido)
                num_pedido = row[0] if row and row[0] else None
                pode_formar_carga = (
                    "Sim" if row and row[1] == 'S' else "Não"
                ) if row else "—"

                if not num_pedido:
                    reply = QMessageBox.question(
                        self,
                        "Nota não encontrada",
                        f"Nota {nota} não encontrada na tabela principal.\n\n"
                        "Deseja consultar a tabela secundária?\n"
                        "(Esta consulta é mais lenta.)",
                        QMessageBox.Yes | QMessageBox.No,
                    )
                    if reply == QMessageBox.Yes:
                        ibm_db.bind_param(stmt_fallback, 1, nota)
                        ibm_db.execute(stmt_fallback)
                        fallback_row = ibm_db.fetch_tuple(stmt_fallback)
                        if fallback_row:
                            num_pedido = fallback_row[1]
                            pode_formar_carga = (
                                "Sim" if fallback_row[2] == 'S' else "Não"
                            )

                esta_no_fusion = (
                    self._verificar_fusion(num_pedido) if num_pedido else "—"
                )

                self._add_row(nota, num_pedido, esta_no_fusion, pode_formar_carga)
                QApplication.processEvents()

            ibm_db.close(conn)

        except Exception as e:
            QMessageBox.critical(
                self,
                "Erro",
                f"Erro ao consultar DB2:\n{e}"
            )

    def _add_row(self, nota, num_pedido, esta_no_fusion, pode_formar_carga):
        row = self.table.rowCount()
        self.table.insertRow(row)

        nota_item = QTableWidgetItem(nota)
        nota_item.setTextAlignment(Qt.AlignCenter)
        self.table.setItem(row, 0, nota_item)

        pedido_item = QTableWidgetItem(
            num_pedido if num_pedido else "Não encontrado"
        )
        pedido_item.setTextAlignment(Qt.AlignCenter)
        self.table.setItem(row, 1, pedido_item)

        fusion_item = QTableWidgetItem(esta_no_fusion)
        fusion_item.setTextAlignment(Qt.AlignCenter)
        if esta_no_fusion == "Sim":
            fusion_item.setForeground(QColor("green"))
        elif esta_no_fusion == "Não":
            fusion_item.setForeground(QColor("red"))
        self.table.setItem(row, 2, fusion_item)

        carga_item = QTableWidgetItem(pode_formar_carga)
        carga_item.setTextAlignment(Qt.AlignCenter)
        if pode_formar_carga == "Sim":
            carga_item.setForeground(QColor("green"))
        elif pode_formar_carga == "Não":
            carga_item.setForeground(QColor("red"))
        self.table.setItem(row, 3, carga_item)

    def _verificar_fusion(self, num_pedido: str) -> str:
        fusion = self.context.FusionClient
        if fusion is None or fusion.token is None:
            return "—"

        try:
            if fusion.pedido_esta_no_fusion(num_pedido):
                return "Sim"
            else:
                return "Não"
        except Exception:
            return "—"
