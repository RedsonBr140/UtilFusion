from PySide6.QtWidgets import (
    QDialog,
    QVBoxLayout,
    QLabel,
    QProgressBar,
    QPushButton,
    QApplication,
    QMessageBox,
)
from PySide6.QtCore import Qt, QTimer


class ConnectionSplash(QDialog):
    def __init__(self, context, settings, parent=None):
        super().__init__(parent)
        self.context = context
        self.settings = settings

        self.setWindowTitle("Conectando...")
        self.setFixedSize(380, 180)
        self.setWindowFlags(Qt.Dialog | Qt.FramelessWindowHint)
        self.setModal(True)
        self.setStyleSheet(
            """
            QDialog {
                background-color: white;
                border: 2px solid #c0c0c0;
                border-radius: 8px;
            }
            """
        )

        layout = QVBoxLayout(self)
        layout.setContentsMargins(24, 20, 24, 16)
        layout.setSpacing(10)

        self.title_label = QLabel("Verificando conexões...")
        self.title_label.setAlignment(Qt.AlignCenter)
        self.title_label.setStyleSheet("font-size: 14px; font-weight: bold;")
        layout.addWidget(self.title_label)

        self.status_label = QLabel("")
        self.status_label.setAlignment(Qt.AlignCenter)
        self.status_label.setStyleSheet("font-size: 11px; color: #555;")
        layout.addWidget(self.status_label)

        self.progress = QProgressBar()
        self.progress.setRange(0, 0)
        self.progress.setTextVisible(False)
        self.progress.setFixedHeight(8)
        layout.addWidget(self.progress)

        self.close_btn = QPushButton("Fechar")
        self.close_btn.setVisible(False)
        self.close_btn.clicked.connect(self.accept)
        self.close_btn.setStyleSheet(
            """
            QPushButton {
                padding: 6px 24px;
                border: 1px solid #ccc;
                border-radius: 4px;
                background: #f0f0f0;
            }
            QPushButton:hover {
                background: #e0e0e0;
            }
            """
        )
        layout.addWidget(self.close_btn, alignment=Qt.AlignCenter)

        QTimer.singleShot(80, self._run_tests)

    def _set_status(self, text):
        self.status_label.setText(text)
        QApplication.processEvents()

    def _run_tests(self):
        cisspoder = self.context.cisspoder_config.get() if self.context.cisspoder_config else None
        db2_configured = bool(
            cisspoder
            and cisspoder.host
            and cisspoder.database_name
            and cisspoder.username
        )

        if not db2_configured:
            self.accept()
            QMessageBox.warning(
                self.parent(),
                "Banco de dados não configurado",
                "As credenciais do CISSPoder (DB2) não estão configuradas.\n\n"
                "Acesse Arquivo > Configurações para configurar "
                "o banco de dados CISSPoder."
            )
            return

        self._set_status("Testando conexão CISSPoder (DB2)...")
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
            if conn:
                ibm_db.exec_immediate(conn, "SELECT 1 FROM SYSIBM.SYSDUMMY1")
                ibm_db.close(conn)
                self._set_status("CISSPoder (DB2): OK")
                self.title_label.setText("Conexão verificada")
                self.title_label.setStyleSheet(
                    "font-size: 14px; font-weight: bold; color: green;"
                )
                self._set_status("Iniciando aplicação...")
                QTimer.singleShot(500, self.accept)
            else:
                error = ibm_db.conn_errormsg()
                self._set_status(f"CISSPoder (DB2): FALHOU")
                self.title_label.setText("Erro de conexão")
                self.title_label.setStyleSheet(
                    "font-size: 14px; font-weight: bold; color: red;"
                )
                self.progress.setVisible(False)
                self.close_btn.setVisible(True)
        except Exception as e:
            self._set_status("CISSPoder (DB2): FALHOU")
            self.title_label.setText("Erro de conexão")
            self.title_label.setStyleSheet(
                "font-size: 14px; font-weight: bold; color: red;"
            )
            self.progress.setVisible(False)
            self.close_btn.setVisible(True)
