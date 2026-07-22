from PySide6.QtWidgets import QMainWindow, QMdiArea


class MainWindow(QMainWindow):
    def __init__(self, context):
        super().__init__()
        self.context = context

        self.setWindowTitle("UtilFusion")

        self.mdi = QMdiArea()
        self.setCentralWidget(self.mdi)

        self.showMaximized()

        self.create_menu()

    def create_menu(self):
        menu_bar = self.menuBar()

        arquivo_menu = menu_bar.addMenu("&Arquivo")
        arquivo_menu.addAction("&Configurações", self.open_configurations)
        arquivo_menu.addSeparator()
        arquivo_menu.addAction("&Sair", self.close)
        cadastro_menu = menu_bar.addMenu("Cadastros")
        cadastro_menu.addAction("&Filiais", self.open_filiais)
        #estoque_menu = menu_bar.addMenu("Estoque")
        relatorios_menu = menu_bar.addMenu("&Relatórios")
        ajuda_menu = menu_bar.addMenu("A&juda")
    def open_configurations(self):
        from windows.config_window import ConfigWindow
        config_window = ConfigWindow()
        self.mdi.addSubWindow(config_window)
        config_window.show()
    
    def open_filiais(self):
        from windows.filiais_window import FiliaisWindow
        filiais_window = FiliaisWindow(self.context)
        self.mdi.addSubWindow(filiais_window)
        filiais_window.show()