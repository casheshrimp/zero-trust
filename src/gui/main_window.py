import sys
from PyQt6.QtWidgets import (QMainWindow, QApplication, QWidget, 
                             QVBoxLayout, QHBoxLayout, QPushButton,
                             QLabel, QListWidget, QSplitter, QStatusBar)
from PyQt6.QtCore import Qt, QSize
from PyQt6.QtGui import QIcon, QFont

from src.scanner.network_scanner import NetworkScanner
from src.gui.components.device_list import DeviceListWidget
from src.gui.components.network_canvas import NetworkCanvas

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.scanner = NetworkScanner()
        self.init_ui()
        
    def init_ui(self):
        self.setWindowTitle("ZeroTrust Inspector")
        self.setGeometry(100, 100, 1200, 800)
        
        # Центральный виджет
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        # Главный лейаут
        main_layout = QHBoxLayout(central_widget)
        
        # Создаем сплиттер для разделения областей
        splitter = QSplitter(Qt.Orientation.Horizontal)
        
        # Левая панель: устройства
        left_panel = QWidget()
        left_layout = QVBoxLayout(left_panel)
        
        left_layout.addWidget(QLabel("Обнаруженные устройства"))
        self.device_list = DeviceListWidget()
        left_layout.addWidget(self.device_list)
        
        scan_button = QPushButton("🔄 Сканировать сеть")
        scan_button.clicked.connect(self.scan_network)
        left_layout.addWidget(scan_button)
        
        # Центральная панель: холст для зон
        self.canvas = NetworkCanvas()
        
        # Правая панель: управление
        right_panel = QWidget()
        right_layout = QVBoxLayout(right_panel)
        
        right_layout.addWidget(QLabel("Управление"))
        self.generate_button = QPushButton("⚡ Сгенерировать правила")
        self.generate_button.setEnabled(False)
        right_layout.addWidget(self.generate_button)
        
        self.validate_button = QPushButton("✅ Проверить безопасность")
        self.validate_button.setEnabled(False)
        right_layout.addWidget(self.validate_button)
        
        # Добавляем панели в сплиттер
        splitter.addWidget(left_panel)
        splitter.addWidget(self.canvas)
        splitter.addWidget(right_panel)
        
        # Настраиваем размеры сплиттера
        splitter.setSizes([300, 600, 300])
        
        main_layout.addWidget(splitter)
        
        # Строка состояния
        self.status_bar = QStatusBar()
        self.setStatusBar(self.status_bar)
        self.status_bar.showMessage("Готов к работе")
        
        # Меню
        self.create_menu()
        
    def create_menu(self):
        menubar = self.menuBar()
        
        # Меню Файл
        file_menu = menubar.addMenu('Файл')
        file_menu.addAction('Новый проект', self.new_project)
        file_menu.addAction('Открыть...', self.open_project)
        file_menu.addAction('Сохранить', self.save_project)
        file_menu.addSeparator()
        file_menu.addAction('Выход', self.close)
        
        # Меню Сервис
        tool_menu = menubar.addMenu('Сервис')
        tool_menu.addAction('Сканировать сеть', self.scan_network)
        tool_menu.addAction('Настройки', self.show_settings)
        
    def scan_network(self):
        self.status_bar.showMessage("Сканирую сеть...")
        
        try:
            devices = self.scanner.scan_network()
            self.device_list.update_devices(devices)
            self.status_bar.showMessage(f"Найдено {len(devices)} устройств")
            
            # Активируем кнопки
            self.generate_button.setEnabled(True)
            self.validate_button.setEnabled(True)
            
        except Exception as e:
            self.status_bar.showMessage(f"Ошибка: {str(e)}")
    
    def new_project(self):
        pass
    
    def open_project(self):
        pass
    
    def save_project(self):
        pass
    
    def show_settings(self):
        pass

def main():
    app = QApplication(sys.argv)
    
    # Настройка стиля
    app.setStyle('Fusion')
    
    window = MainWindow()
    window.show()
    
    sys.exit(app.exec())

if __name__ == '__main__':
    main()
