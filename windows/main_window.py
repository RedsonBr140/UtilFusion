from PySide6.QtWidgets import QMainWindow, QMdiArea


class MainWindow(QMainWindow):
    def __init__(self, context, settings):
        super().__init__()
        self.context = context
        self.settings = settings

        self.setWindowTitle("CompanyKit")

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

        cadastro_menu = menu_bar.addMenu("&Cadastros")
        cadastro_menu.addAction("&Filiais", self.open_filiais)
        cadastro_menu.addAction("&Concorrentes", self.open_concorrentes)

        cotacao_menu = menu_bar.addMenu("Cota&ção")
        cotacao_menu.addAction(
            "Atualizar via &Menor Preço", self.open_consulta_menor_preco
        )
        cotacao_menu.addAction(
            "Cotar no site do &concorrente", self.cotar_site_concorrente
        )

        utilitarios_menu = menu_bar.addMenu("&Utilitários")
        utilitarios_menu.addAction(
            "Consulta &Pedido Fusion", self.open_consulta_pedido_fusion
        )

        relatorios_menu = menu_bar.addMenu("&Relatórios")
        relatorios_menu.addAction("&Concorrência", self.open_relatorio_concorrencia)

        ajuda_menu = menu_bar.addMenu("A&juda")
        ajuda_menu.addAction("&Sobre", self.open_about)

    def open_configurations(self):
        from windows.config_window import ConfigWindow

        config_window = ConfigWindow(self.context, self.settings)
        self.mdi.addSubWindow(config_window)
        config_window.show()

    def open_filiais(self):
        from windows.filiais_window import FiliaisWindow

        filiais_window = FiliaisWindow(self.context)
        self.mdi.addSubWindow(filiais_window)
        filiais_window.show()

    def open_concorrentes(self):
        from windows.concorrentes_window import ConcorrentesWindow

        window = ConcorrentesWindow(self.context)
        self.mdi.addSubWindow(window)
        window.show()

    def open_consulta_pedido_fusion(self):
        from windows.consulta_pedido_fusion_window import ConsultaPedidoFusionWindow

        consulta = ConsultaPedidoFusionWindow(self.context)
        self.mdi.addSubWindow(consulta)
        consulta.show()

    def open_consulta_menor_preco(self):
        from windows.consulta_menor_preco_window import ConsultaMenorPrecoWindow

        consulta = ConsultaMenorPrecoWindow(self.context)
        self.mdi.addSubWindow(consulta)
        consulta.show()

    def cotar_site_concorrente(self):
        from windows.cotar_site_concorrente_window import CotarSiteConcorrenteWindow

        window = CotarSiteConcorrenteWindow(self.context, self.settings)
        self.mdi.addSubWindow(window)
        window.show()

    def open_relatorio_concorrencia(self):
        from windows.relatorio_concorrencia_window import RelatorioConcorrenciaWindow

        relatorio = RelatorioConcorrenciaWindow(self.context)
        self.mdi.addSubWindow(relatorio)
        relatorio.show()

    def open_about(self):
        from windows.about_window import AboutWindow

        AboutWindow(self).exec()
