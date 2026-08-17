from PySide6.QtWidgets import QMainWindow, QMdiArea, QMessageBox

from services.permissions import can


class MainWindow(QMainWindow):
    def __init__(self, context, settings):
        super().__init__()
        self.context = context
        self.settings = settings

        self.setWindowTitle("CompanyKit")

        self.mdi = QMdiArea()
        self.setCentralWidget(self.mdi)

        self._routine_actions: dict[str, object] = {}

        self.showMaximized()

        self.create_menu()
        self.apply_permissions()

    def create_menu(self):
        menu_bar = self.menuBar()

        arquivo_menu = menu_bar.addMenu("&Arquivo")
        self._routine_actions["config"] = arquivo_menu.addAction(
            "&Configurações", self.open_configurations
        )
        arquivo_menu.addAction("Al&terar Senha", self.open_alterar_senha)
        arquivo_menu.addSeparator()
        arquivo_menu.addAction("&Sair", self.close)

        cadastro_menu = menu_bar.addMenu("&Cadastros")
        self._routine_actions["filiais"] = cadastro_menu.addAction(
            "&Filiais", self.open_filiais
        )
        self._routine_actions["concorrentes"] = cadastro_menu.addAction(
            "&Concorrentes", self.open_concorrentes
        )
        self._routine_actions["usuarios"] = cadastro_menu.addAction(
            "&Usuários", self.open_usuarios
        )

        cotacao_menu = menu_bar.addMenu("Cota&ção")
        self._routine_actions["consulta_menor_preco"] = cotacao_menu.addAction(
            "Atualizar via &Menor Preço", self.open_consulta_menor_preco
        )
        self._routine_actions["cotar_site_concorrente"] = cotacao_menu.addAction(
            "Cotar no site do &concorrente", self.cotar_site_concorrente
        )

        utilitarios_menu = menu_bar.addMenu("&Utilitários")
        self._routine_actions["consulta_pedido_fusion"] = utilitarios_menu.addAction(
            "Consulta &Pedido Fusion", self.open_consulta_pedido_fusion
        )

        relatorios_menu = menu_bar.addMenu("&Relatórios")
        self._routine_actions["relatorio_concorrencia"] = relatorios_menu.addAction(
            "&Concorrência", self.open_relatorio_concorrencia
        )

        ajuda_menu = menu_bar.addMenu("A&juda")
        ajuda_menu.addAction("&Sobre", self.open_about)

    def apply_permissions(self):
        """Habilita/desabilita as rotinas conforme as permissoes do usuario
        logado. Chamado na abertura e quando a janela de Usuários salva."""
        for routine, action in self._routine_actions.items():
            action.setEnabled(can(self.context, routine))

    def _require(self, routine: str) -> bool:
        if can(self.context, routine):
            return True
        QMessageBox.warning(
            self,
            "Sem permissão",
            "Você não tem permissão para acessar esta rotina.",
        )
        return False

    def open_configurations(self):
        if not self._require("config"):
            return
        from windows.config_window import ConfigWindow

        config_window = ConfigWindow(self.context, self.settings)
        self.mdi.addSubWindow(config_window)
        config_window.show()

    def open_alterar_senha(self):
        from windows.alterar_senha_window import AlterarSenhaDialog

        AlterarSenhaDialog(self.context, self).exec()

    def open_filiais(self):
        if not self._require("filiais"):
            return
        from windows.filiais_window import FiliaisWindow

        filiais_window = FiliaisWindow(self.context)
        self.mdi.addSubWindow(filiais_window)
        filiais_window.show()

    def open_concorrentes(self):
        if not self._require("concorrentes"):
            return
        from windows.concorrentes_window import ConcorrentesWindow

        window = ConcorrentesWindow(self.context)
        self.mdi.addSubWindow(window)
        window.show()

    def open_usuarios(self):
        if not self._require("usuarios"):
            return
        from windows.usuarios_window import UsuariosWindow

        window = UsuariosWindow(self.context)
        window.permissions_changed.connect(self.apply_permissions)
        self.mdi.addSubWindow(window)
        window.show()

    def open_consulta_pedido_fusion(self):
        if not self._require("consulta_pedido_fusion"):
            return
        from windows.consulta_pedido_fusion_window import ConsultaPedidoFusionWindow

        consulta = ConsultaPedidoFusionWindow(self.context)
        self.mdi.addSubWindow(consulta)
        consulta.show()

    def open_consulta_menor_preco(self):
        if not self._require("consulta_menor_preco"):
            return
        from windows.consulta_menor_preco_window import ConsultaMenorPrecoWindow

        consulta = ConsultaMenorPrecoWindow(self.context)
        self.mdi.addSubWindow(consulta)
        consulta.show()

    def cotar_site_concorrente(self):
        if not self._require("cotar_site_concorrente"):
            return
        from windows.cotar_site_concorrente_window import CotarSiteConcorrenteWindow

        window = CotarSiteConcorrenteWindow(self.context, self.settings)
        self.mdi.addSubWindow(window)
        window.show()

    def open_relatorio_concorrencia(self):
        if not self._require("relatorio_concorrencia"):
            return
        from windows.relatorio_concorrencia_window import RelatorioConcorrenciaWindow

        relatorio = RelatorioConcorrenciaWindow(self.context)
        self.mdi.addSubWindow(relatorio)
        relatorio.show()

    def open_about(self):
        from windows.about_window import AboutWindow

        AboutWindow(self).exec()