"""
GUI модуль
"""

try:
    from .main_window import MainWindow
except ImportError:
    from PyQt6.QtWidgets import QMainWindow, QLabel, QVBoxLayout, QWidget
    from PyQt6.QtCore import Qt
    
    class MainWindow(QMainWindow):
        def __init__(self):
            super().__init__()
            self.setWindowTitle("ZeroTrust Inspector")
            self.setGeometry(100, 100, 800, 600)
            
            central = QWidget()
            self.setCentralWidget(central)
            layout = QVBoxLayout(central)
            
            label = QLabel("ZeroTrust Inspector GUI")
            label.setAlignment(Qt.AlignmentFlag.AlignCenter)
            layout.addWidget(label)
