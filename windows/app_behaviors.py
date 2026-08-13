from __future__ import annotations

import unicodedata

from PySide6.QtWidgets import (
    QApplication,
    QDialogButtonBox,
    QHeaderView,
    QMainWindow,
    QMdiSubWindow,
    QPushButton,
    QTableView,
    QTableWidget,
    QToolBar,
    QToolButton,
    QWidget,
)


def _strip_accents(text: str) -> str:
    normalized = unicodedata.normalize("NFD", text)
    return "".join(ch for ch in normalized if unicodedata.category(ch) != "Mn")


def _mnemonic_key(char: str) -> str:
    if not char:
        return ""
    return _strip_accents(char).casefold()


def extract_mnemonic(text: str) -> str | None:
    if not text:
        return None
    i = 0
    while i < len(text):
        if text[i] == "&":
            if i + 1 < len(text) and text[i + 1] == "&":
                i += 2
                continue
            if i + 1 < len(text) and text[i + 1].strip():
                return _mnemonic_key(text[i + 1])
            return None
        i += 1
    return None


def ensure_mnemonic(text: str, used: set[str], reserved: set[str]) -> str:
    if not text:
        return text

    existing = extract_mnemonic(text)
    if existing:
        used.add(existing)
        return text

    plain = text.replace("&&", "&")
    for idx, ch in enumerate(plain):
        if not ch.isalpha():
            continue
        key = _mnemonic_key(ch)
        if not key or key in used or key in reserved:
            continue
        used.add(key)
        return plain[:idx] + "&" + plain[idx:]
    return text


def menubar_reserved_mnemonics(widget: QWidget | None = None) -> set[str]:
    reserved: set[str] = set()
    app = QApplication.instance()
    windows = []
    if widget is not None:
        windows.append(widget.window())
    if app is not None:
        windows.extend(app.topLevelWidgets())

    seen = set()
    for win in windows:
        if win is None or id(win) in seen:
            continue
        seen.add(id(win))
        if not isinstance(win, QMainWindow):
            continue
        menu_bar = win.menuBar()
        if menu_bar is None:
            continue
        for action in menu_bar.actions():
            key = extract_mnemonic(action.text() or "")
            if key:
                reserved.add(key)
    return reserved


def configure_table(table: QTableView | QTableWidget) -> None:
    header = table.horizontalHeader()
    header.setSectionResizeMode(QHeaderView.Interactive)
    header.setStretchLastSection(False)
    header.setSectionsMovable(True)
    header.setSectionsClickable(True)
    header.setHighlightSections(True)


def configure_tables(root: QWidget) -> None:
    for table in root.findChildren(QTableWidget):
        configure_table(table)
    for table in root.findChildren(QTableView):
        if not isinstance(table, QTableWidget):
            configure_table(table)


def apply_button_mnemonics(root: QWidget, reserved: set[str] | None = None) -> None:
    if reserved is None:
        reserved = menubar_reserved_mnemonics(root)

    used: set[str] = set()
    buttons: list[QPushButton] = []

    for btn in root.findChildren(QPushButton):
        if isinstance(btn, QToolButton):
            continue
        buttons.append(btn)
        existing = extract_mnemonic(btn.text() or "")
        if existing:
            used.add(existing)

    for toolbar in root.findChildren(QToolBar):
        for action in toolbar.actions():
            existing = extract_mnemonic(action.text() or "")
            if existing:
                used.add(existing)

    for box in root.findChildren(QDialogButtonBox):
        for btn in box.buttons():
            existing = extract_mnemonic(btn.text() or "")
            if existing:
                used.add(existing)

    for btn in buttons:
        text = btn.text() or ""
        if not text.strip():
            continue
        new_text = ensure_mnemonic(text, used, reserved)
        if new_text != text:
            btn.setText(new_text)

    for toolbar in root.findChildren(QToolBar):
        for action in toolbar.actions():
            text = action.text() or ""
            if not text.strip() or action.isSeparator():
                continue
            new_text = ensure_mnemonic(text, used, reserved)
            if new_text != text:
                action.setText(new_text)

    for box in root.findChildren(QDialogButtonBox):
        for btn in box.buttons():
            text = btn.text() or ""
            if not text.strip():
                continue
            new_text = ensure_mnemonic(text, used, reserved)
            if new_text != text:
                btn.setText(new_text)


def apply_standard_behaviors(root: QWidget, reserved: set[str] | None = None) -> None:
    if reserved is None:
        reserved = menubar_reserved_mnemonics(root)
    configure_tables(root)
    apply_button_mnemonics(root, reserved)


class AppSubWindow(QMdiSubWindow):
    def showEvent(self, event):
        super().showEvent(event)
        self.apply_standard_behaviors()

    def apply_standard_behaviors(self):
        root = self.widget() or self
        reserved = menubar_reserved_mnemonics(self)
        apply_standard_behaviors(root, reserved)
        apply_button_mnemonics(self, reserved)
        configure_tables(self)
