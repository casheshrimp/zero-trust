"""
Страница "Сканер сети"
"""
from PyQt6.QtWidgets import QWidget, QVBoxLayout, QLabel

class ScannerPage(QWidget):
    def __init__(self):
        super().__init__()
        layout = QVBoxLayout()
        layout.addWidget(QLabel("🔍 Сканер сети (в разработке)"))
        self.setLayout(layout)
