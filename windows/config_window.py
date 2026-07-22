from PySide6.QtWidgets import QMdiSubWindow
class ConfigWindow(QMdiSubWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Configurações")
        self.setGeometry(100, 100, 400, 300)