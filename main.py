import os
from pathlib import Path
import sys
import tempfile

from PySide6.QtWidgets import QApplication, QDialog
from context import AppContext
from database.connection import Database
from database.repositories.filial_repository import FilialRepository
from database.repositories.user_repository import UserRepository
from database.repositories.user_permission_repository import UserPermissionRepository
from database.repositories.cisspoder_config_repository import CisspoderConfigRepository
from database.repositories.concorrente_repository import ConcorrenteRepository
from services.auth_service import AuthService
from settings import AppSettings
from windows.login_window import LoginWindow
from windows.configurar_url_window import ConfigurarURLWindow
from fusion import FusionClient
from windows.main_window import MainWindow

# If you don't do this, ibm_db will fail to import the DLLs on Windows. This is because the DLLs are not in the PATH, and Python doesn't know where to find them.
if os.name == "nt" and os.getenv("IBM_DB_HOME"):
    os.add_dll_directory(os.getenv("IBM_DB_HOME"))
# Avoid UnicodeDecodeError on accented DB2 CHAR/VARCHAR fields.
os.environ.setdefault("DB2CODEPAGE", "1208")

app = QApplication(sys.argv)
app.setStyle("windowsvista")

# palette = QPalette().setColor()
# app.setPalette(palette)

context = AppContext()
settings = AppSettings()

if not settings.getConnectionUrl():
    configurar_url = ConfigurarURLWindow(context, settings)
    configurar_url.exec()

context.database = Database(settings.getConnectionUrl())
context.users = UserRepository(context.database)
context.user_permissions = UserPermissionRepository(context.database)
context.filiais = FilialRepository(context.database)
context.cisspoder_config = CisspoderConfigRepository(context.database)
context.concorrentes = ConcorrenteRepository(context.database)
context.auth = AuthService(context.users)

login = LoginWindow(context, settings)

context.FusionClient = FusionClient(tempfile.gettempdir() + "/fusion_client")

if login.exec() == QDialog.Accepted:
    main_window = MainWindow(context, settings)
    main_window.show()

    sys.exit(app.exec())

sys.exit()
