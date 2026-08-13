import subprocess
from pathlib import Path

from PySide6.QtCore import Qt
from PySide6.QtWidgets import QDialog, QVBoxLayout, QLabel, QPushButton, QHBoxLayout

from windows.app_behaviors import apply_standard_behaviors


def get_app_version() -> str:
    base = "0.0.1"
    try:
        root = Path(__file__).resolve().parents[1]
        commit = subprocess.check_output(
            ["git", "rev-parse", "HEAD"],
            cwd=root,
            stderr=subprocess.DEVNULL,
            text=True,
        ).strip()
        return f"{base}-{commit[:6]}"
    except Exception:
        return base


class AboutWindow(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Sobre")
        self.setFixedSize(360, 180)
        self.setModal(True)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(24, 24, 24, 16)
        layout.setSpacing(8)

        title = QLabel("CompanyKit")
        title.setAlignment(Qt.AlignCenter)
        title.setStyleSheet("font-size: 18px; font-weight: bold;")

        version = QLabel(f"Versão {get_app_version()}")
        version.setAlignment(Qt.AlignCenter)

        desc = QLabel("Ferramentas utilitárias para integração Fusion.")
        desc.setAlignment(Qt.AlignCenter)
        desc.setWordWrap(True)

        layout.addWidget(title)
        layout.addWidget(version)
        layout.addWidget(desc)
        layout.addStretch()

        buttons = QHBoxLayout()
        buttons.addStretch()
        ok_btn = QPushButton("OK")
        ok_btn.setDefault(True)
        ok_btn.clicked.connect(self.accept)
        buttons.addWidget(ok_btn)
        layout.addLayout(buttons)

        apply_standard_behaviors(self)
