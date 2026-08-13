from PySide6.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QGroupBox,
    QFormLayout,
    QLineEdit,
    QPushButton,
    QHBoxLayout,
    QMessageBox,
)

from database.models import CisspoderConfig
from windows.app_behaviors import AppSubWindow


class ConfigWindow(AppSubWindow):
    def __init__(self, context, settings):
        super().__init__()
        self.context = context
        self.settings = settings
        self.setWindowTitle("Configurações")
        self.setMinimumSize(420, 560)

        widget = QWidget()
        self.setWidget(widget)

        main_layout = QVBoxLayout(widget)
        main_layout.setContentsMargins(16, 16, 16, 16)
        main_layout.setSpacing(14)

        # --- CISSPoder DB2 ---
        cisspoder_group = QGroupBox("CISSPoder - DB2")
        cisspoder_layout = QFormLayout(cisspoder_group)
        cisspoder_layout.setSpacing(6)
        cisspoder_layout.setContentsMargins(12, 16, 12, 12)

        self.cisspoder_host = QLineEdit()
        self.cisspoder_host.setPlaceholderText("Ex: 10.0.0.1")
        cisspoder_layout.addRow("Host:", self.cisspoder_host)

        self.cisspoder_port = QLineEdit()
        self.cisspoder_port.setPlaceholderText("Ex: 50000")
        cisspoder_layout.addRow("Porta:", self.cisspoder_port)

        self.cisspoder_db = QLineEdit()
        self.cisspoder_db.setPlaceholderText("Ex: CISSPODER")
        cisspoder_layout.addRow("Banco:", self.cisspoder_db)

        self.cisspoder_user = QLineEdit()
        self.cisspoder_user.setPlaceholderText("Usuário DB2")
        cisspoder_layout.addRow("Usuário:", self.cisspoder_user)

        self.cisspoder_password = QLineEdit()
        self.cisspoder_password.setEchoMode(QLineEdit.Password)
        self.cisspoder_password.setPlaceholderText("Senha DB2")
        cisspoder_layout.addRow("Senha:", self.cisspoder_password)

        self.test_cisspoder_btn = QPushButton("Testar Conexão CISSPoder")
        self.test_cisspoder_btn.clicked.connect(self._test_cisspoder)
        cisspoder_layout.addRow("", self.test_cisspoder_btn)

        main_layout.addWidget(cisspoder_group)

        # --- OpenAI (ChatGPT) ---
        openai_group = QGroupBox("OpenAI (ChatGPT)")
        openai_layout = QFormLayout(openai_group)
        openai_layout.setSpacing(6)
        openai_layout.setContentsMargins(12, 16, 12, 12)

        self.openai_key = QLineEdit()
        self.openai_key.setEchoMode(QLineEdit.Password)
        self.openai_key.setPlaceholderText("sk-...")
        openai_layout.addRow("API Key:", self.openai_key)

        self.openai_model = QLineEdit()
        self.openai_model.setPlaceholderText("Ex: gpt-4o-mini")
        openai_layout.addRow("Modelo:", self.openai_model)

        self.test_openai_btn = QPushButton("Testar API Key")
        self.test_openai_btn.clicked.connect(self._test_openai)
        openai_layout.addRow("", self.test_openai_btn)

        main_layout.addWidget(openai_group)

        # --- Banco de Dados CompanyKit ---
        companykit_group = QGroupBox("Banco de Dados CompanyKit")
        companykit_layout = QVBoxLayout(companykit_group)
        companykit_layout.setContentsMargins(12, 16, 12, 12)

        self.config_db_btn = QPushButton("Configurar Banco de Dados")
        self.config_db_btn.clicked.connect(self._open_db_config)
        companykit_layout.addWidget(self.config_db_btn)

        main_layout.addWidget(companykit_group)

        # --- Botões inferiores ---
        main_layout.addStretch()

        buttons_layout = QHBoxLayout()
        buttons_layout.addStretch()
        self.save_btn = QPushButton("Salvar")
        self.save_btn.clicked.connect(self._save)
        self.cancel_btn = QPushButton("Cancelar")
        self.cancel_btn.clicked.connect(self.close)
        buttons_layout.addWidget(self.save_btn)
        buttons_layout.addWidget(self.cancel_btn)
        main_layout.addLayout(buttons_layout)

        self._load_cisspoder_config()

    def _load_cisspoder_config(self):
        repo = self.context.cisspoder_config
        config = repo.get()
        self.cisspoder_host.setText(config.host)
        self.cisspoder_port.setText(config.port)
        self.cisspoder_db.setText(config.database_name)
        self.cisspoder_user.setText(config.username)
        self.cisspoder_password.setText(config.password)

        self.openai_key.setText(self.settings.getOpenAIKey())
        self.openai_model.setText(self.settings.getOpenAIModel())

    def _save(self):
        repo = self.context.cisspoder_config
        config = CisspoderConfig(
            host=self.cisspoder_host.text().strip(),
            port=self.cisspoder_port.text().strip(),
            database_name=self.cisspoder_db.text().strip(),
            username=self.cisspoder_user.text().strip(),
            password=self.cisspoder_password.text(),
        )
        repo.save(config)
        self.settings.setOpenAIKey(self.openai_key.text().strip())
        self.settings.setOpenAIModel(self.openai_model.text().strip() or "gpt-4o-mini")
        self.settings.settings.sync()
        QMessageBox.information(
            self,
            "Configuração",
            "Configurações salvas com sucesso."
        )
        self.close()

    def _open_db_config(self):
        from windows.configurar_url_window import ConfigurarURLWindow
        dlg = ConfigurarURLWindow(self.context, self.settings)
        dlg.exec()

    def _test_openai(self):
        from services.llm_client import LLMClient

        api_key = self.openai_key.text().strip()
        if not api_key:
            QMessageBox.warning(self, "OpenAI", "Informe a API Key primeiro.")
            return

        llm = LLMClient(api_key, self.openai_model.text().strip() or "gpt-4o-mini")
        result = llm.rewrite_query("QUARTZOLIT ARGAMASSA AC-I 20KG INTERNA")
        if result is None:
            QMessageBox.critical(
                self,
                "OpenAI",
                "Falha ao testar a API Key.\nVerifique a chave e o modelo.",
            )
            return
        QMessageBox.information(
            self,
            "OpenAI",
            f"Conexão realizada com sucesso!\n\n"
            f"Exemplo de reescrita:\n"
            f"'QUARTZOLIT ARGAMASSA AC-I 20KG INTERNA'\n-> '{result}'",
        )

    def _test_cisspoder(self):
        host = self.cisspoder_host.text().strip()
        port = self.cisspoder_port.text().strip()
        database = self.cisspoder_db.text().strip()
        username = self.cisspoder_user.text().strip()
        password = self.cisspoder_password.text()

        if not all([host, port, database, username]):
            QMessageBox.warning(
                self,
                "CISSPoder",
                "Preencha todos os campos antes de testar a conexão."
            )
            return

        try:
            int(port)
        except ValueError:
            QMessageBox.warning(
                self,
                "CISSPoder",
                "Porta inválida."
            )
            return

        try:
            import ibm_db

            conn_str = (
                f"DATABASE={database};"
                f"HOSTNAME={host};"
                f"PORT={port};"
                f"PROTOCOL=TCPIP;"
                f"UID={username};"
                f"PWD={password};"
            )
            conn = ibm_db.connect(conn_str, "", "")
            if conn:
                ibm_db.exec_immediate(conn, "SELECT 1 FROM SYSIBM.SYSDUMMY1")
                ibm_db.close(conn)
                QMessageBox.information(
                    self,
                    "CISSPoder",
                    "Conexão realizada com sucesso!"
                )
            else:
                error = ibm_db.conn_errormsg()
                QMessageBox.critical(
                    self,
                    "CISSPoder",
                    f"Falha na conexão DB2:\n{error}"
                )
        except Exception as e:
            QMessageBox.critical(
                self,
                "CISSPoder",
                f"Erro ao conectar ao DB2:\n{e}"
            )
