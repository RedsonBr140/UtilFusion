from PySide6.QtWidgets import QMainWindow, QMdiArea
class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("UtilFusion")
        
        self.mdi = QMdiArea()
        self.setCentralWidget(self.mdi)

        self.showMaximized()

        self.create_menu()

    def create_menu(self):
        menu_bar = self.menuBar()

        arquivo_menu = menu_bar.addMenu("&Arquivo")
        #cadastro_menu = menu_bar.addMenu("Cadastros")
        #estoque_menu = menu_bar.addMenu("Estoque")
        relatorios_menu = menu_bar.addMenu("&Relatórios")
        ajuda_menu = menu_bar.addMenu("A&juda")