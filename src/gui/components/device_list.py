"""
Виджет списка устройств
"""
from PyQt6.QtWidgets import QListWidget
from PyQt6.QtCore import pyqtSignal

class DeviceListWidget(QListWidget):
    """Список устройств"""
    
    device_selected = pyqtSignal(str)  # device_id
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setup_ui()
    
    def setup_ui(self):
        """Настройка интерфейса"""
        self.setMinimumWidth(200)
