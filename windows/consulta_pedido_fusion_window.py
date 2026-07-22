from PySide6.QtWidgets import (
    QMdiSubWindow,
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QPushButton,
    QGroupBox,
    QMessageBox,
)
from PySide6.QtCore import Qt


class ConsultaPedidoFusionWindow(QMdiSubWindow):
    def __init__(self, context):
        super().__init__()
        self.context = context
        self.setWindowTitle("Consulta Pedido Fusion")
        self.setMinimumSize(400, 220)

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
        self.nota_input.setPlaceholderText("Digite o número da Nota/Cupom")
        self.nota_input.returnPressed.connect(self._pesquisar)
        input_layout.addWidget(self.nota_input)

        self.search_btn = QPushButton("Pesquisar")
        self.search_btn.clicked.connect(self._pesquisar)
        input_layout.addWidget(self.search_btn)

        main_layout.addWidget(input_group)

        result_group = QGroupBox("Resultado")
        result_layout = QVBoxLayout(result_group)
        result_layout.setContentsMargins(12, 12, 12, 12)

        self.result_label = QLabel("")
        self.result_label.setAlignment(Qt.AlignCenter)
        self.result_label.setStyleSheet(
            "font-size: 20px; font-weight: bold; padding: 16px;"
        )
        result_layout.addWidget(self.result_label)

        main_layout.addWidget(result_group)
        main_layout.addStretch()

        self.nota_input.setFocus()

    def _pesquisar(self):
        nota = self.nota_input.text().strip()

        if not nota:
            QMessageBox.warning(
                self,
                "Consulta Pedido",
                "Informe o número da Nota/Cupom."
            )
            return

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

            sql = (
                "SELECT NUM_PEDIDO_ORIG_680 "
                "FROM FUSIONT.FUSION_VW_ENTREGA "
                "WHERE NF_PK_680 = ?"
            )
            stmt = ibm_db.prepare(conn, sql)
            ibm_db.bind_param(stmt, 1, nota)
            ibm_db.execute(stmt)

            row = ibm_db.fetch_tuple(stmt)
            ibm_db.close(conn)

            if row and row[0]:
                self.result_label.setText(f"Pedido: {row[0]}")
                self.result_label.setStyleSheet(
                    "font-size: 20px; font-weight: bold; color: green; padding: 16px;"
                )
            else:
                self.result_label.setText("Não encontrado")
                self.result_label.setStyleSheet(
                    "font-size: 20px; font-weight: bold; color: #cc6600; padding: 16px;"
                )

        except Exception as e:
            QMessageBox.critical(
                self,
                "Erro",
                f"Erro ao consultar:\n{e}"
            )
