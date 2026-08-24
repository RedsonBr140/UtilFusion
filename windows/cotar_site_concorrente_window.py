import threading

from PySide6.QtCore import QObject, QRunnable, QThreadPool, Qt, QUrl, Signal
from PySide6.QtGui import QAction, QColor, QDesktopServices, QPixmap
from PySide6.QtWidgets import (
    QApplication,
    QComboBox,
    QDialog,
    QDialogButtonBox,
    QGroupBox,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QMessageBox,
    QPushButton,
    QSizePolicy,
    QSpacerItem,
    QTableWidget,
    QTableWidgetItem,
    QToolBar,
    QVBoxLayout,
    QWidget,
)

from services.concorrente_site import get_fetcher
from windows.app_behaviors import AppSubWindow


class _WorkQueue:
    """Indices das linhas ainda nao processadas, consumidos pelas threads."""

    def __init__(self, indices: list[int]):
        self._indices = list(indices)
        self._lock = threading.Lock()

    def next(self) -> int | None:
        with self._lock:
            if self._indices:
                return self._indices.pop(0)
            return None


class _SearchSignals(QObject):
    row_done = Signal(int)
    error = Signal(str)


class _ConfirmRequest:
    __slots__ = (
        "descricao_erp",
        "nome_candidato",
        "preco",
        "score",
        "image",
        "event",
        "answer",
    )

    def __init__(self, descricao_erp, nome_candidato, preco, score, image):
        self.descricao_erp = descricao_erp
        self.nome_candidato = nome_candidato
        self.preco = preco
        self.score = score
        self.image = image
        self.event = threading.Event()
        self.answer = False


class _ConfirmBridge(QObject):
    """Ponte entre as threads de busca e o QMessageBox (que so pode rodar na
    thread principal). A thread do worker bloqueia ate o usuario responder."""

    _requested = Signal(object)

    def __init__(self, window):
        super().__init__()
        self._window = window
        self._requested.connect(self._handle, Qt.ConnectionType.QueuedConnection)

    def confirm(self, descricao_erp, nome_candidato, preco, score, image="") -> bool:
        req = _ConfirmRequest(descricao_erp, nome_candidato, preco, score, image)
        self._requested.emit(req)
        req.event.wait()
        return req.answer

    def _handle(self, req: _ConfirmRequest):
        req.answer = self._window._confirm_match(
            req.descricao_erp, req.nome_candidato, req.preco, req.score, req.image
        )
        req.event.set()


class _SearchRunnable(QRunnable):
    """Processa itens de uma cotacao numa thread propria, com seu proprio
    fetcher (sessao HTTP independente)."""

    def __init__(self, queue, tipo, llm, bridge, rows, signals, fonte_default):
        super().__init__()
        self._queue = queue
        self._tipo = tipo
        self._llm = llm
        self._bridge = bridge
        self._rows = rows
        self._signals = signals
        self._fonte_default = fonte_default
        self.setAutoDelete(True)

    def run(self):
        try:
            fetcher = get_fetcher(
                self._tipo, llm=self._llm, confirm=self._bridge.confirm
            )
        except ValueError as e:
            self._signals.error.emit(str(e))
            self._drain()
            return

        while True:
            idx = self._queue.next()
            if idx is None:
                break
            try:
                row = self._rows[idx]
                descricao = row["descricao"]
                if not descricao or descricao == "—":
                    row["preco_site"] = None
                    row["fonte"] = ""
                    row["url"] = ""
                else:
                    result = fetcher.fetch_by_name(
                        descricao,
                        gtin=row["codbar"],
                        referencia=row["referencia"],
                    )
                    if result and result.preco is not None and result.preco > 0:
                        row["preco_site"] = result.preco
                        row["fonte"] = result.fonte or self._fonte_default
                        row["url"] = result.url or ""
                    else:
                        row["preco_site"] = None
                        row["fonte"] = ""
                        row["url"] = ""
            except Exception as e:
                print(f"[Cotar] erro item {idx}: {e}")
                row["preco_site"] = None
                row["fonte"] = ""
                row["url"] = ""
            self._signals.row_done.emit(idx)

    def _drain(self):
        while True:
            idx = self._queue.next()
            if idx is None:
                break
            self._signals.row_done.emit(idx)


class CotarSiteConcorrenteWindow(AppSubWindow):
    MAX_WORKERS = 4

    def __init__(self, context, settings):
        super().__init__()
        self.context = context
        self.settings = settings
        self.setWindowTitle("Cotar no site do concorrente")
        self.setMinimumSize(900, 450)
        self._rows = []
        self._remaining = 0
        self._signals = None
        self._bridge = None

        widget = QWidget()
        self.setWidget(widget)
        main = QVBoxLayout(widget)
        main.setContentsMargins(12, 12, 12, 12)
        main.setSpacing(10)

        toolbar = QToolBar()
        toolbar.setMovable(False)
        self.gravar_action = QAction("Gravar", self)
        self.gravar_action.setEnabled(False)
        self.gravar_action.triggered.connect(self._gravar)
        toolbar.addAction(self.gravar_action)

        self.buscar_site_action = QAction("Buscar preços no site", self)
        self.buscar_site_action.setEnabled(False)
        self.buscar_site_action.triggered.connect(self._buscar_precos_site)
        toolbar.addAction(self.buscar_site_action)
        main.addWidget(toolbar)

        self.progress_label = QLabel("")
        main.addWidget(self.progress_label)

        filtros = QGroupBox("Filtros")
        filtro_layout = QHBoxLayout(filtros)
        filtro_layout.setSpacing(8)
        filtro_layout.setContentsMargins(12, 10, 12, 10)

        filtro_layout.addWidget(QLabel("ID Cotação:"))
        self.idcotacao_input = QLineEdit()
        self.idcotacao_input.setMaximumWidth(80)
        filtro_layout.addWidget(self.idcotacao_input)

        filtro_layout.addWidget(QLabel("Concorrente:"))
        self.concorrente_combo = QComboBox()
        self.concorrente_combo.setMinimumWidth(220)
        filtro_layout.addWidget(self.concorrente_combo)

        self.search_btn = QPushButton("Pesquisar")
        self.search_btn.clicked.connect(self._carregar)
        filtro_layout.addWidget(self.search_btn)

        filtro_layout.addItem(
            QSpacerItem(40, 20, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)
        )
        main.addWidget(filtros)

        self.table = QTableWidget(0, 6)
        self.table.setHorizontalHeaderLabels(
            [
                "ID",
                "Descrição",
                "Preço Varejo Atual",
                "Preço Site",
                "Fonte",
                "Link",
            ]
        )
        self.table.setEditTriggers(QTableWidget.NoEditTriggers)
        self.table.setSelectionBehavior(QTableWidget.SelectRows)
        self.table.setSortingEnabled(True)
        self.table.cellClicked.connect(self._open_link)
        main.addWidget(self.table)

        self.idcotacao_input.returnPressed.connect(self._carregar)
        self._load_concorrentes()

    def _load_concorrentes(self):
        self.concorrente_combo.clear()
        items = self.context.concorrentes.find_all(only_active=True)
        for item in items:
            label = f"{item.nome} (ERP {item.id_erp}) [{item.tipo}]"
            self.concorrente_combo.addItem(label, item)

        if self.concorrente_combo.count() == 0:
            self.concorrente_combo.addItem("Nenhum concorrente cadastrado", None)

    def _selected_concorrente(self):
        return self.concorrente_combo.currentData()

    def _format_preco(self, value) -> str:
        if value is None:
            return "—"
        try:
            num = float(str(value).replace(",", "."))
        except (TypeError, ValueError):
            return "—"
        if num <= 0:
            return "—"
        return f"R$ {num:.2f}".replace(".", ",")

    def _parse_preco(self, value):
        if value is None:
            return None
        try:
            num = float(str(value).replace(",", "."))
        except (TypeError, ValueError):
            return None
        return num if num > 0 else None

    @staticmethod
    def _as_str(value) -> str:
        if value is None:
            return ""
        if isinstance(value, bytes):
            for enc in ("utf-8", "latin-1", "cp1252", "cp850"):
                try:
                    return value.decode(enc).strip()
                except UnicodeDecodeError:
                    continue
            return value.decode("latin-1", errors="replace").strip()
        return str(value).strip()

    def _carregar(self):
        idcotacao = self.idcotacao_input.text().strip()
        concorrente = self._selected_concorrente()

        if not idcotacao:
            QMessageBox.warning(self, "Cotação", "Informe o ID da cotação.")
            return
        if concorrente is None:
            QMessageBox.warning(
                self,
                "Cotação",
                "Cadastre um concorrente em Cadastros > Concorrentes.",
            )
            return

        cisspoder = self.context.cisspoder_config.get()
        if (
            not cisspoder
            or not cisspoder.host
            or not cisspoder.database_name
            or not cisspoder.username
        ):
            QMessageBox.warning(
                self,
                "Cotação",
                "Credenciais do CISSPoder (DB2) não configuradas.\n"
                "Acesse Arquivo > Configurações.",
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
                    self, "Erro de conexão", f"Falha ao conectar ao DB2:\n{error}"
                )
                return

            sql = (
                "SELECT "
                "pg.IDPRODUTO, "
                "ccp.IDSUBPRODUTO, "
                "pg.CODBAR, "
                "ccp.VALPRECOVAREJOCONCORRENTE, "
                "CAST(pg.DESCRRESPRODUTO AS VARCHAR(254)), "
                "CAST(pg.REFERENCIA AS VARCHAR(254)) "
                "FROM COTACAO_CONCORRENCIA_PROD ccp "
                "LEFT JOIN PRODUTO_GRADE pg "
                "ON pg.IDPRODUTO = ccp.IDPRODUTO "
                "AND pg.IDSUBPRODUTO = ccp.IDSUBPRODUTO "
                "WHERE IDCOTACAO = ? "
                "AND IDCONCORRENTE = ? "
            )
            stmt = ibm_db.prepare(conn, sql)
            ibm_db.bind_param(stmt, 1, idcotacao)
            ibm_db.bind_param(stmt, 2, str(concorrente.id_erp))
            ibm_db.execute(stmt)

            self._rows.clear()
            self.table.setSortingEnabled(False)
            self.table.setRowCount(0)

            row_data = ibm_db.fetch_tuple(stmt)
            while row_data:
                idproduto = int(row_data[0]) if row_data[0] is not None else 0
                idsubproduto = int(row_data[1]) if row_data[1] is not None else 0
                item_id = self._as_str(row_data[0])
                codbar = self._as_str(row_data[2])
                preco_varejo_val = self._parse_preco(row_data[3])
                preco_varejo = self._format_preco(preco_varejo_val)
                descricao = self._as_str(row_data[4]) or "—"
                referencia = self._as_str(row_data[5])

                self._rows.append(
                    {
                        "idproduto": idproduto,
                        "idsubproduto": idsubproduto,
                        "item_id": item_id,
                        "codbar": codbar,
                        "referencia": referencia,
                        "descricao": descricao,
                        "preco_varejo": preco_varejo_val,
                        "preco_site": None,
                        "fonte": "",
                        "url": "",
                    }
                )
                self._add_row(item_id, descricao, preco_varejo, "—", "—")
                QApplication.processEvents()
                row_data = ibm_db.fetch_tuple(stmt)

            ibm_db.close(conn)
            self.table.setSortingEnabled(True)
            self._update_actions()

            if not self._rows:
                QMessageBox.information(
                    self,
                    "Cotação",
                    "Nenhum produto encontrado para esta cotação/concorrente.",
                )
        except Exception as e:
            QMessageBox.critical(self, "Erro", f"Erro ao consultar:\n{e}")

    def _buscar_precos_site(self):
        concorrente = self._selected_concorrente()
        if concorrente is None:
            QMessageBox.warning(self, "Cotação", "Selecione um concorrente.")
            return
        if not self._rows:
            QMessageBox.warning(self, "Cotação", "Pesquise a cotação primeiro.")
            return

        try:
            from services.llm_client import LLMClient

            llm = None
            if self.settings.getOpenAIKey():
                llm = LLMClient(
                    self.settings.getOpenAIKey(),
                    self.settings.getOpenAIModel(),
                )
                print("[Cotar] ChatGPT configurado para apoiar a busca de nomes")
            # Valida o tipo do concorrente antes de disparar as threads.
            get_fetcher(concorrente.tipo)
        except ValueError as e:
            QMessageBox.warning(self, "Cotação", str(e))
            return

        self.buscar_site_action.setEnabled(False)
        self.search_btn.setEnabled(False)
        self.table.setSortingEnabled(False)

        self._signals = _SearchSignals()
        self._signals.row_done.connect(self._on_row_done)
        self._signals.error.connect(self._on_worker_error)
        self._bridge = _ConfirmBridge(self)

        indices = list(range(len(self._rows)))
        queue = _WorkQueue(indices)
        self._remaining = len(indices)
        self._update_progress_label()

        num_workers = max(1, min(self.MAX_WORKERS, len(indices)))
        pool = QThreadPool.globalInstance()
        for _ in range(num_workers):
            runnable = _SearchRunnable(
                queue,
                concorrente.tipo,
                llm,
                self._bridge,
                self._rows,
                self._signals,
                concorrente.nome,
            )
            pool.start(runnable)

    def _on_row_done(self, idx: int):
        row = self._rows[idx]
        self._update_table_row(
            idx,
            row["item_id"],
            row["descricao"],
            self._format_preco(row["preco_varejo"]),
            self._format_preco(row["preco_site"]),
            row["fonte"] or "—",
            row["url"] or "",
        )
        self._remaining -= 1
        self._update_progress_label()
        if self._remaining <= 0:
            self._finish_search()

    def _on_worker_error(self, message: str):
        QMessageBox.warning(self, "Cotação", message)

    def _finish_search(self):
        self.table.setSortingEnabled(True)
        self.search_btn.setEnabled(True)
        self.progress_label.setText("")
        self._update_actions()

    def _update_progress_label(self):
        total = len(self._rows)
        done = total - self._remaining
        self.progress_label.setText(f"Processando... {done}/{total}")

    def _confirm_match(self, descricao_erp, nome_candidato, preco, score, image="") -> bool:
        preco_txt = self._format_preco(preco) if isinstance(preco, (int, float)) else "—"

        dialog = QDialog(self)
        dialog.setWindowTitle("Confirmar correspondência")
        dialog.setMinimumWidth(420)
        layout = QVBoxLayout(dialog)
        layout.setSpacing(10)

        info = QLabel(
            f"<b>Produto ERP:</b><br>{descricao_erp}<br><br>"
            f"<b>Candidato encontrado:</b><br>{nome_candidato}<br>"
            f"<b>Preço:</b> {preco_txt} &nbsp;&nbsp; <b>Score:</b> {score:.2f}"
        )
        info.setWordWrap(True)
        info.setTextFormat(Qt.TextFormat.RichText)
        layout.addWidget(info)

        if image:
            img_label = QLabel()
            img_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
            pixmap = self._download_pixmap(image)
            if pixmap is not None:
                img_label.setPixmap(
                    pixmap.scaled(
                        240,
                        240,
                        Qt.AspectRatioMode.KeepAspectRatio,
                        Qt.TransformationMode.SmoothTransformation,
                    )
                )
                img_label.setToolTip(image)
            else:
                img_label.setText("(imagem não disponível)")
            layout.addWidget(img_label)

        buttons = QDialogButtonBox(
            QDialogButtonBox.StandardButton.Yes | QDialogButtonBox.StandardButton.No
        )
        buttons.button(QDialogButtonBox.StandardButton.Yes).setText("Sim, corresponde")
        buttons.button(QDialogButtonBox.StandardButton.No).setText("Não")
        buttons.accepted.connect(dialog.accept)
        buttons.rejected.connect(dialog.reject)
        layout.addWidget(buttons)

        return dialog.exec() == QDialog.DialogCode.Accepted

    def _download_pixmap(self, url: str) -> QPixmap | None:
        try:
            import requests

            resp = requests.get(
                url,
                timeout=8,
                headers={"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"},
            )
            resp.raise_for_status()
            pixmap = QPixmap()
            if pixmap.loadFromData(resp.content):
                return pixmap
        except Exception as e:
            print(f"[Cotar] falha ao baixar imagem {url}: {e}")
        return None

    def _gravar(self):
        idcotacao = self.idcotacao_input.text().strip()
        concorrente = self._selected_concorrente()

        if not idcotacao or concorrente is None:
            QMessageBox.warning(
                self, "Gravar", "Informe ID Cotação e Concorrente."
            )
            return

        if not self._rows:
            QMessageBox.warning(self, "Gravar", "Pesquise a cotação primeiro.")
            return

        por_produto = {}
        for row in self._rows:
            preco_val = row["preco_site"]
            if preco_val is None or preco_val <= 0:
                continue
            chave = (row["idproduto"], row["idsubproduto"])
            if chave not in por_produto or preco_val < por_produto[chave]:
                por_produto[chave] = preco_val

        if not por_produto:
            QMessageBox.warning(
                self, "Gravar", "Nenhum produto com preço de site para gravar."
            )
            return

        reply = QMessageBox.question(
            self,
            "Confirmar",
            f"Gravar {len(por_produto)} produtos no ERP?\n\n"
            f"ID Cotação: {idcotacao}\n"
            f"Concorrente: {concorrente.nome} (ERP {concorrente.id_erp})",
            QMessageBox.Yes | QMessageBox.No,
        )
        if reply != QMessageBox.Yes:
            return

        cisspoder = self.context.cisspoder_config.get()
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
                    self, "Erro de conexão", f"Falha ao conectar ao DB2:\n{error}"
                )
                return

            sql = (
                "UPDATE COTACAO_CONCORRENCIA_PROD "
                "SET VALPRECOVAREJOCONCORRENTE = ? "
                "WHERE IDCOTACAO = ? "
                "AND IDCONCORRENTE = ? "
                "AND IDPRODUTO = ? "
                "AND IDSUBPRODUTO = ?"
            )
            stmt = ibm_db.prepare(conn, sql)

            atualizados = 0
            erros = 0
            for (idproduto, idsubproduto), preco in por_produto.items():
                try:
                    ibm_db.bind_param(stmt, 1, str(preco).replace(".", ","))
                    ibm_db.bind_param(stmt, 2, idcotacao)
                    ibm_db.bind_param(stmt, 3, str(concorrente.id_erp))
                    ibm_db.bind_param(stmt, 4, str(idproduto))
                    ibm_db.bind_param(stmt, 5, str(idsubproduto))
                    ibm_db.execute(stmt)
                    atualizados += 1
                except Exception as e:
                    print(f"[UPDATE] erro IDPRODUTO={idproduto}: {e}")
                    erros += 1

            ibm_db.close(conn)

            for row in self._rows:
                if row["preco_site"] is not None and row["preco_site"] > 0:
                    row["preco_varejo"] = row["preco_site"]

            self.table.setSortingEnabled(False)
            for idx, row in enumerate(self._rows):
                self._update_table_row(
                    idx,
                    row["item_id"],
                    row["descricao"],
                    self._format_preco(row["preco_varejo"]),
                    self._format_preco(row["preco_site"]),
                    row["fonte"] or "—",
                    row["url"] or "",
                )
            self.table.setSortingEnabled(True)

            QMessageBox.information(
                self,
                "Gravar",
                f"{atualizados} produtos gravados.\n"
                + (f"{erros} erros." if erros else ""),
            )
        except Exception as e:
            QMessageBox.critical(self, "Erro", f"Erro ao gravar:\n{e}")

    def _update_actions(self):
        has_rows = bool(self._rows)
        has_site = any(
            row["preco_site"] is not None and row["preco_site"] > 0
            for row in self._rows
        )
        self.buscar_site_action.setEnabled(has_rows)
        self.gravar_action.setEnabled(has_site)

    def _add_row(self, item_id, descricao, preco_varejo, preco_site, fonte, url=""):
        row = self.table.rowCount()
        self.table.insertRow(row)
        self._update_table_row(row, item_id, descricao, preco_varejo, preco_site, fonte, url)

    def _update_table_row(self, row, item_id, descricao, preco_varejo, preco_site, fonte, url=""):
        values = [item_id, descricao, preco_varejo, preco_site, fonte]
        for col, value in enumerate(values):
            cell = QTableWidgetItem(value)
            cell.setTextAlignment(Qt.AlignCenter if col != 1 else Qt.AlignLeft | Qt.AlignVCenter)
            if col == 3 and value != "—":
                cell.setForeground(QColor("green"))
            self.table.setItem(row, col, cell)

        link_cell = QTableWidgetItem("Abrir link" if url else "—")
        link_cell.setTextAlignment(Qt.AlignCenter)
        if url:
            link_cell.setData(Qt.UserRole, url)
            link_cell.setForeground(QColor("blue"))
            link_cell.setToolTip(url)
        self.table.setItem(row, 5, link_cell)

    def _open_link(self, row, col):
        if col != 5:
            return
        item = self.table.item(row, col)
        if item is None:
            return
        url = item.data(Qt.UserRole)
        if url:
            QDesktopServices.openUrl(QUrl(url))
