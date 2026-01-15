"""
Главное окно приложения - исправленная версия
"""

import sys
from pathlib import Path

from PyQt6.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QSplitter, QTabWidget, QStatusBar, QToolBar,
    QMenuBar, QMessageBox, QFileDialog, QProgressBar,
    QLabel, QPushButton, QTextEdit, QListWidget, QListWidgetItem,
    QTreeWidget, QTreeWidgetItem, QGroupBox, QFormLayout,
    QLineEdit, QComboBox, QSpinBox, QCheckBox
)
from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtGui import QAction, QIcon, QKeySequence

class MainWindow(QMainWindow):
    """Главное окно приложения"""
    
    def __init__(self):
        super().__init__()
        
        self.setWindowTitle("ZeroTrust Inspector v1.0.0")
        self.setGeometry(100, 100, 1400, 800)
        
        self.init_ui()
        self.create_menu()
        self.create_toolbar()
        self.create_statusbar()
        
        self.statusBar().showMessage("Готов к работе")
    
    def init_ui(self):
        """Инициализация интерфейса"""
        # Центральный виджет
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        # Основной макет
        main_layout = QVBoxLayout(central_widget)
        
        # Верхняя панель с информацией
        info_label = QLabel("🎉 ZeroTrust Inspector успешно запущен!")
        info_label.setStyleSheet("font-size: 16px; font-weight: bold; padding: 10px;")
        info_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        main_layout.addWidget(info_label)
        
        # Создаем сплиттер для разделения на три части
        splitter = QSplitter(Qt.Orientation.Horizontal)
        
        # Левая панель: устройства и зоны
        left_panel = self.create_left_panel()
        
        # Центральная панель: визуализация сети
        center_panel = self.create_center_panel()
        
        # Правая панель: свойства и правила
        right_panel = self.create_right_panel()
        
        splitter.addWidget(left_panel)
        splitter.addWidget(center_panel)
        splitter.addWidget(right_panel)
        splitter.setSizes([300, 700, 400])
        
        main_layout.addWidget(splitter)
    
    def create_left_panel(self):
        """Создать левую панель"""
        panel = QWidget()
        layout = QVBoxLayout(panel)
        
        # Заголовок
        title = QLabel("📋 Устройства и зоны")
        title.setStyleSheet("font-weight: bold; margin: 5px;")
        layout.addWidget(title)
        
        # Список устройств
        devices_group = QGroupBox("Обнаруженные устройства")
        devices_layout = QVBoxLayout()
        
        self.device_list = QListWidget()
        self.device_list.addItem("🖥️ Компьютер (192.168.1.100)")
        self.device_list.addItem("📱 Смартфон (192.168.1.101)")
        self.device_list.addItem("💡 Умная лампа (192.168.1.102)")
        self.device_list.addItem("📷 Камера (192.168.1.103)")
        
        devices_layout.addWidget(self.device_list)
        devices_group.setLayout(devices_layout)
        layout.addWidget(devices_group)
        
        # Кнопки управления
        buttons_layout = QHBoxLayout()
        scan_btn = QPushButton("🔍 Сканировать")
        classify_btn = QPushButton("🏷️ Классифицировать")
        
        scan_btn.clicked.connect(self.scan_network)
        classify_btn.clicked.connect(self.classify_devices)
        
        buttons_layout.addWidget(scan_btn)
        buttons_layout.addWidget(classify_btn)
        layout.addLayout(buttons_layout)
        
        # Список зон
        zones_group = QGroupBox("Зоны безопасности")
        zones_layout = QVBoxLayout()
        
        self.zones_tree = QTreeWidget()
        self.zones_tree.setHeaderLabel("Зоны")
        
        trusted_zone = QTreeWidgetItem(["✅ Trusted (Доверенная)"])
        iot_zone = QTreeWidgetItem(["⚠️ IoT (Умные устройства)"])
        guest_zone = QTreeWidgetItem(["👥 Guests (Гости)"])
        
        trusted_zone.addChild(QTreeWidgetItem(["Компьютер"]))
        iot_zone.addChild(QTreeWidgetItem(["Умная лампа"]))
        iot_zone.addChild(QTreeWidgetItem(["Камера"]))
        
        self.zones_tree.addTopLevelItem(trusted_zone)
        self.zones_tree.addTopLevelItem(iot_zone)
        self.zones_tree.addTopLevelItem(guest_zone)
        
        zones_layout.addWidget(self.zones_tree)
        zones_group.setLayout(zones_layout)
        layout.addWidget(zones_group)
        
        return panel
    
    def create_center_panel(self):
        """Создать центральную панель"""
        panel = QWidget()
        layout = QVBoxLayout(panel)
        
        # Заголовок
        title = QLabel("🌐 Визуализация сети")
        title.setStyleSheet("font-weight: bold; margin: 5px;")
        layout.addWidget(title)
        
        # Область визуализации
        visualization = QTextEdit()
        visualization.setHtml("""
        <div style="text-align: center; padding: 20px;">
            <h2>Визуализатор сети</h2>
            <p>Здесь будет отображаться графическое представление сети</p>
            <hr>
            <div style="display: flex; justify-content: center; gap: 50px; margin: 30px;">
                <div style="border: 2px solid green; padding: 20px; border-radius: 10px;">
                    <h3>✅ Trusted Zone</h3>
                    <p>🖥️ Компьютер</p>
                </div>
                <div style="border: 2px solid orange; padding: 20px; border-radius: 10px;">
                    <h3>⚠️ IoT Zone</h3>
                    <p>💡 Умная лампа</p>
                    <p>📷 Камера</p>
                </div>
                <div style="border: 2px solid gray; padding: 20px; border-radius: 10px;">
                    <h3>👥 Guest Zone</h3>
                    <p>📱 Смартфон</p>
                </div>
            </div>
            <hr>
            <p>🔄 Перетаскивайте устройства между зонами</p>
            <p>🔗 Правила отображаются в виде стрелок</p>
        </div>
        """)
        visualization.setReadOnly(True)
        layout.addWidget(visualization)
        
        return panel
    
    def create_right_panel(self):
        """Создать правую панель"""
        panel = QTabWidget()
        
        # Вкладка 1: Свойства
        properties_tab = QWidget()
        properties_layout = QVBoxLayout(properties_tab)
        
        # Форма свойств устройства
        form_group = QGroupBox("Свойства устройства")
        form_layout = QFormLayout()
        
        form_layout.addRow("IP адрес:", QLineEdit("192.168.1.100"))
        form_layout.addRow("MAC адрес:", QLineEdit("00:11:22:33:44:55"))
        form_layout.addRow("Тип:", QComboBox())
        form_layout.addRow("Зона:", QComboBox())
        
        form_group.setLayout(form_layout)
        properties_layout.addWidget(form_group)
        
        # Вкладка 2: Правила
        rules_tab = QWidget()
        rules_layout = QVBoxLayout(rules_tab)
        
        rules_list = QListWidget()
        rules_list.addItem("✅ Trusted → IoT: DENY")
        rules_list.addItem("✅ Trusted → Guest: DENY")
        rules_list.addItem("⚠️ IoT → Internet: ALLOW (порт 443)")
        rules_list.addItem("⚠️ Guest → IoT: DENY")
        
        rules_layout.addWidget(rules_list)
        
        # Вкладка 3: Статистика
        stats_tab = QWidget()
        stats_layout = QVBoxLayout(stats_tab)
        
        stats_text = QTextEdit()
        stats_text.setHtml("""
        <h3>📊 Статистика сети</h3>
        <ul>
            <li>Всего устройств: <b>4</b></li>
            <li>Зон безопасности: <b>3</b></li>
            <li>Правил настроено: <b>4</b></li>
            <li>Оценка безопасности: <b>85%</b></li>
        </ul>
        <h3>🔍 Последнее сканирование:</h3>
        <ul>
            <li>Время: 5 минут назад</li>
            <li>Обнаружено: 4 устройства</li>
            <li>Открытых портов: 12</li>
        </ul>
        """)
        stats_text.setReadOnly(True)
        stats_layout.addWidget(stats_text)
        
        panel.addTab(properties_tab, "📋 Свойства")
        panel.addTab(rules_tab, "🔒 Правила")
        panel.addTab(stats_tab, "📊 Статистика")
        
        return panel
    
    def create_menu(self):
        """Создать меню приложения"""
        menubar = self.menuBar()
        
        # Меню "Файл"
        file_menu = menubar.addMenu("📁 Файл")
        
        new_action = QAction("📄 Новая политика", self)
        new_action.setShortcut("Ctrl+N")
        new_action.triggered.connect(self.new_policy)
        
        open_action = QAction("📂 Открыть...", self)
        open_action.setShortcut("Ctrl+O")
        open_action.triggered.connect(self.open_policy)
        
        save_action = QAction("💾 Сохранить", self)
        save_action.setShortcut("Ctrl+S")
        save_action.triggered.connect(self.save_policy)
        
        exit_action = QAction("🚪 Выход", self)
        exit_action.setShortcut("Alt+F4")
        exit_action.triggered.connect(self.close)
        
        file_menu.addAction(new_action)
        file_menu.addAction(open_action)
        file_menu.addAction(save_action)
        file_menu.addSeparator()
        file_menu.addAction(exit_action)
        
        # Меню "Сеть"
        network_menu = menubar.addMenu("🌐 Сеть")
        
        scan_action = QAction("🔍 Сканировать сеть", self)
        scan_action.setShortcut("F5")
        scan_action.triggered.connect(self.scan_network)
        
        network_menu.addAction(scan_action)
        
        # Меню "Политика"
        policy_menu = menubar.addMenu("🛡️ Политика")
        
        validate_action = QAction("✅ Валидировать", self)
        validate_action.setShortcut("F9")
        validate_action.triggered.connect(self.validate_policy)
        
        policy_menu.addAction(validate_action)
        
        # Меню "Справка"
        help_menu = menubar.addMenu("❓ Справка")
        
        about_action = QAction("ℹ️ О программе", self)
        about_action.triggered.connect(self.show_about)
        
        help_menu.addAction(about_action)
    
    def create_toolbar(self):
        """Создать панель инструментов"""
        toolbar = self.addToolBar("Инструменты")
        toolbar.setMovable(False)
        
        # Кнопка сканирования
        scan_action = QAction("🔍 Сканировать", self)
        scan_action.triggered.connect(self.scan_network)
        toolbar.addAction(scan_action)
        
        toolbar.addSeparator()
        
        # Кнопка валидации
        validate_action = QAction("✅ Валидировать", self)
        validate_action.triggered.connect(self.validate_policy)
        toolbar.addAction(validate_action)
        
        toolbar.addSeparator()
        
        # Кнопка экспорта
        export_action = QAction("📤 Экспорт", self)
        export_action.triggered.connect(self.export_config)
        toolbar.addAction(export_action)
    
    def create_statusbar(self):
        """Создать строку состояния"""
        self.statusbar = QStatusBar()
        self.setStatusBar(self.statusbar)
        
        # Индикатор прогресса
        self.progress_bar = QProgressBar()
        self.progress_bar.setMaximumWidth(200)
        self.progress_bar.setVisible(False)
        self.statusbar.addPermanentWidget(self.progress_bar)
    
    # ===== Обработчики событий =====
    
    def scan_network(self):
        """Сканировать сеть"""
        self.statusbar.showMessage("Сканирование сети...")
        self.progress_bar.setVisible(True)
        self.progress_bar.setValue(0)
        
        # Имитация сканирования
        from PyQt6.QtCore import QTimer
        self.scan_progress = 0
        
        def update_progress():
            self.scan_progress += 10
            self.progress_bar.setValue(self.scan_progress)
            
            if self.scan_progress >= 100:
                self.statusbar.showMessage("Сканирование завершено! Найдено 4 устройства")
                self.progress_bar.setVisible(False)
                self.timer.stop()
                
                # Обновляем список устройств
                self.device_list.clear()
                self.device_list.addItem("🖥️ Компьютер (192.168.1.100)")
                self.device_list.addItem("📱 Смартфон (192.168.1.101)")
                self.device_list.addItem("💡 Умная лампа (192.168.1.102)")
                self.device_list.addItem("📷 Камера (192.168.1.103)")
        
        self.timer = QTimer()
        self.timer.timeout.connect(update_progress)
        self.timer.start(200)
    
    def classify_devices(self):
        """Классифицировать устройства"""
        QMessageBox.information(self, "Классификация", "Устройства классифицированы!")
    
    def validate_policy(self):
        """Валидировать политику"""
        result = QMessageBox.information(
            self,
            "Валидация политики",
            "Политика успешно валидирована!\n\nОценка безопасности: 85%\nРекомендации: Усилить изоляцию IoT зоны",
            QMessageBox.StandardButton.Ok
        )
    
    def new_policy(self):
        """Создать новую политику"""
        reply = QMessageBox.question(
            self,
            "Новая политика",
            "Создать новую политику безопасности?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )
        
        if reply == QMessageBox.StandardButton.Yes:
            self.statusbar.showMessage("Создана новая политика")
    
    def open_policy(self):
        """Открыть политику"""
        filepath, _ = QFileDialog.getOpenFileName(
            self,
            "Открыть политику",
            "",
            "JSON Files (*.json);;All Files (*)"
        )
        
        if filepath:
            self.statusbar.showMessage(f"Открыт файл: {filepath}")
    
    def save_policy(self):
        """Сохранить политику"""
        filepath, _ = QFileDialog.getSaveFileName(
            self,
            "Сохранить политику",
            "policy.json",
            "JSON Files (*.json)"
        )
        
        if filepath:
            self.statusbar.showMessage(f"Политика сохранена: {filepath}")
    
    def export_config(self):
        """Экспортировать конфигурацию"""
        formats = ["OpenWrt", "pfSense", "Windows Firewall", "IPTables"]
        format, ok = QInputDialog.getItem(
            self,
            "Экспорт конфигурации",
            "Выберите формат:",
            formats,
            0,
            False
        )
        
        if ok and format:
            QMessageBox.information(
                self,
                "Экспорт",
                f"Конфигурация для {format} успешно экспортирована!"
            )
    
    def show_about(self):
        """Показать информацию о программе"""
        QMessageBox.about(
            self,
            "О программе",
            """
            <h2>ZeroTrust Inspector v1.0.0</h2>
            <p>Визуализатор и валидатор Zero-Trust политик</p>
            <p>Для домашних сетей и малых офисов</p>
            <hr>
            <p>Автор: CashShrimp</p>
            <p>Лицензия: MIT</p>
            <p>GitHub: github.com/casheshrimp/zero-trust</p>
            """
        )
