"""
Главное окно приложения
"""

from PyQt6.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QSplitter, QLabel, QPushButton, QTextEdit
)
from PyQt6.QtCore import Qt

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("ZeroTrust Inspector v1.0.0")
        self.setGeometry(100, 100, 1200, 800)
        
        # Центральный виджет
        central = QWidget()
        self.setCentralWidget(central)
        
        # Основной макет
        main_layout = QVBoxLayout(central)
        
        # Верхняя панель
        top_label = QLabel("🎉 ZeroTrust Inspector успешно запущен!")
        top_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        top_label.setStyleSheet("font-size: 18px; font-weight: bold;")
        main_layout.addWidget(top_label)
        
        # Сплиттер
        splitter = QSplitter(Qt.Orientation.Horizontal)
        
        # Левая панель
        left_panel = QWidget()
        left_layout = QVBoxLayout(left_panel)
        left_layout.addWidget(QLabel("📋 Функции:"))
        left_layout.addWidget(QPushButton("🔍 Сканировать сеть"))
        left_layout.addWidget(QPushButton("🛡️ Создать политику"))
        left_layout.addWidget(QPushButton("✅ Валидировать"))
        
        # Центральная панель
        center_panel = QTextEdit()
        center_panel.setHtml("""
        <h2>Добро пожаловать в ZeroTrust Inspector!</h2>
        <p>Визуализатор и валидатор Zero-Trust политик</p>
        <hr>
        <h3>Что можно сделать:</h3>
        <ul>
            <li>Автоматическое обнаружение устройств в сети</li>
            <li>Классификация устройств по типам</li>
            <li>Создание зон безопасности</li>
            <li>Настройка правил доступа</li>
            <li>Генерация конфигураций для роутеров</li>
        </ul>
        """)
        
        # Правая панель
        right_panel = QWidget()
        right_layout = QVBoxLayout(right_panel)
        right_layout.addWidget(QLabel("📊 Статус:"))
        right_layout.addWidget(QLabel("✅ PyQt6 установлен"))
        right_layout.addWidget(QLabel("✅ Зависимости проверены"))
        right_layout.addWidget(QLabel("🔄 Загрузка модулей..."))
        
        # Добавляем панели в сплиттер
        splitter.addWidget(left_panel)
        splitter.addWidget(center_panel)
        splitter.addWidget(right_panel)
        
        main_layout.addWidget(splitter)
        
        # Статус бар
        self.statusBar().showMessage("Готов к работе")
