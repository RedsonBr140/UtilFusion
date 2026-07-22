from pathlib import Path
import sys
import tempfile

from PySide6.QtWidgets import QApplication, QDialog
from PySide6.QtUiTools import QUiLoader
from PySide6.QtCore import QFile
from PySide6.QtGui import QPalette
from context import AppContext
from database.connection import Database
from database.repositories.filial_repository import FilialRepository
from database.repositories.user_repository import UserRepository
from services.auth_service import AuthService
from settings import AppSettings
from windows.login_window import LoginWindow
from windows.configurar_url_window import ConfigurarURLWindow
from fusion import FusionClient
from windows.main_window import MainWindow

app = QApplication(sys.argv)
app.setStyle("windowsvista")

#palette = QPalette().setColor()
#app.setPalette(palette)

context = AppContext()
settings = AppSettings()

context.database = Database(settings.getConnectionUrl())
context.users = UserRepository(context.database)
context.filiais = FilialRepository(context.database)
context.auth = AuthService(context.users)

login = LoginWindow(context, settings)

if not settings.getConnectionUrl():
    configurar_url = ConfigurarURLWindow(context, settings)
    configurar_url.exec()

#context.FusionClient = FusionClient(tempfile.gettempdir() + "/fusion_client")

if login.exec() == QDialog.Accepted:
    main_window = MainWindow(context)
    main_window.show()

    sys.exit(app.exec())

sys.exit()