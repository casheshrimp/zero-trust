"""
Главное окно приложения
"""

import sys
from pathlib import Path
from typing import List

from PyQt6.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QSplitter, QTabWidget, QStatusBar, QToolBar,
    QMenuBar, QMessageBox, QFileDialog, QProgressBar
)
from PyQt6.QtCore import Qt, pyqtSignal, QTimer
from PyQt6.QtGui import QAction, QIcon, QKeySequence

from ...core.models import NetworkDevice, NetworkPolicy, SecurityZone, ZoneType
from ...scanner.network_scanner import NetworkScanner
from ...engine.policy_engine import PolicyEngine
from ...validation.policy_validator import PolicyValidator

from .components.device_list import DeviceListWidget
from .components.network_canvas import NetworkCanvas

class MainWindow(QMainWindow):
    """Главное окно приложения"""
    
    def __init__(self):
        super().__init__()
        
        self.scanner = NetworkScanner()
        self.policy_engine = PolicyEngine()
        self.validator = PolicyValidator()
        
        self.current_policy = None
        self.devices = []
        
        self.init_ui()
        self.setup_connections()
        self.load_default_policy()
    
    def init_ui(self):
        """Инициализация интерфейса"""
        self.setWindowTitle("ZeroTrust Inspector v1.0.0")
        self.setGeometry(100, 100, 1400, 800)
        
        # Создаем центральный виджет
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        # Основной макет
        main_layout = QVBoxLayout(central_widget)
        
        # Создаем сплиттер
        splitter = QSplitter(Qt.Orientation.Horizontal)
        
        # Левая панель: список устройств
        self.device_list = DeviceListWidget()
        
        # Центральная панель: холст сети
        self.network_canvas = NetworkCanvas()
        
        # Правая панель: свойства и правила
        self.properties_widget = self.create_properties_widget()
        
        splitter.addWidget(self.device_list)
        splitter.addWidget(self.network_canvas)
        splitter.addWidget(self.properties_widget)
        splitter.setSizes([300, 700, 400])
        
        main_layout.addWidget(splitter)
        
        # Создаем меню
        self.create_menu()
        
        # Создаем тулбар
        self.create_toolbar()
        
        # Создаем статус бар
        self.create_statusbar()
    
    def create_properties_widget(self) -> QTabWidget:
        """Создать виджет свойств"""
        tabs = QTabWidget()
        
        # Вкладка "Политика"
        policy_widget = QWidget()
        policy_layout = QVBoxLayout(policy_widget)
        tabs.addTab(policy_widget, "📋 Политика")
        
        # Вкладка "Правила"
        rules_widget = QWidget()
        rules_layout = QVBoxLayout(rules_widget)
        tabs.addTab(rules_widget, "🔒 Правила")
        
        # Вкладка "Отчет"
        report_widget = QWidget()
        report_layout = QVBoxLayout(report_widget)
        tabs.addTab(report_widget, "📊 Отчет")
        
        return tabs
    
    def create_menu(self):
        """Создать меню приложения"""
        menubar = self.menuBar()
        
        # Меню "Файл"
        file_menu = menubar.addMenu("📁 Файл")
        
        new_action = QAction("📄 Новая политика", self)
        new_action.setShortcut(QKeySequence.StandardKey.New)
        new_action.triggered.connect(self.new_policy)
        
        open_action = QAction("📂 Открыть...", self)
        open_action.setShortcut(QKeySequence.StandardKey.Open)
        open_action.triggered.connect(self.open_policy)
        
        save_action = QAction("💾 Сохранить", self)
        save_action.setShortcut(QKeySequence.StandardKey.Save)
        save_action.triggered.connect(self.save_policy)
        
        export_action = QAction("📤 Экспорт конфигурации...", self)
        export_action.triggered.connect(self.export_config)
        
        exit_action = QAction("🚪 Выход", self)
        exit_action.setShortcut(QKeySequence.StandardKey.Quit)
        exit_action.triggered.connect(self.close)
        
        file_menu.addAction(new_action)
        file_menu.addAction(open_action)
        file_menu.addAction(save_action)
        file_menu.addAction(export_action)
        file_menu.addSeparator()
        file_menu.addAction(exit_action)
        
        # Меню "Сеть"
        network_menu = menubar.addMenu("🌐 Сеть")
        
        scan_action = QAction("🔍 Сканировать сеть", self)
        scan_action.setShortcut("F5")
        scan_action.triggered.connect(self.scan_network)
        
        stop_scan_action = QAction("⏹️ Остановить сканирование", self)
        stop_scan_action.triggered.connect(self.stop_scanning)
        
        network_menu.addAction(scan_action)
        network_menu.addAction(stop_scan_action)
        
        # Меню "Политика"
        policy_menu = menubar.addMenu("🛡️ Политика")
        
        validate_action = QAction("✅ Валидировать политику", self)
        validate_action.setShortcut("F9")
        validate_action.triggered.connect(self.validate_policy)
        
        add_zone_action = QAction("➕ Добавить зону", self)
        add_zone_action.triggered.connect(self.add_zone)
        
        policy_menu.addAction(validate_action)
        policy_menu.addAction(add_zone_action)
        
        # Меню "Вид"
        view_menu = menubar.addMenu("👁️ Вид")
        
        arrange_action = QAction("📐 Автоматически расположить", self)
        arrange_action.triggered.connect(self.auto_arrange)
        
        view_menu.addAction(arrange_action)
        
        # Меню "Помощь"
        help_menu = menubar.addMenu("❓ Помощь")
        
        about_action = QAction("ℹ️ О программе", self)
        about_action.triggered.connect(self.show_about)
        
        help_menu.addAction(about_action)
    
    def create_toolbar(self):
        """Создать панель инструментов"""
        toolbar = self.addToolBar("Панель инструментов")
        toolbar.setMovable(False)
        
        # Кнопки сканирования
        scan_action = QAction("🔍 Сканировать", self)
        scan_action.triggered.connect(self.scan_network)
        toolbar.addAction(scan_action)
        
        toolbar.addSeparator()
        
        # Кнопки зон
        add_zone_action = QAction("➕ Зона", self)
        add_zone_action.triggered.connect(self.add_zone)
        toolbar.addAction(add_zone_action)
        
        toolbar.addSeparator()
        
        # Кнопка валидации
        validate_action = QAction("✅ Валидировать", self)
        validate_action.triggered.connect(self.validate_policy)
        toolbar.addAction(validate_action)
    
    def create_statusbar(self):
        """Создать статус бар"""
        statusbar = self.statusBar()
        
        # Статус сети
        self.network_status = statusbar.addWidget(QProgressBar())
        self.network_status.setMaximumWidth(200)
        self.network_status.setVisible(False)
        
        # Сообщение
        statusbar.showMessage("Готов")
    
    def setup_connections(self):
        """Настройка сигналов"""
        self.device_list.device_selected.connect(self.on_device_selected)
        self.device_list.device_dragged.connect(self.on_device_dragged)
        
        self.network_canvas.selection_changed.connect(self.on_selection_changed)
    
    def load_default_policy(self):
        """Загрузить политику по умолчанию"""
        self.current_policy = self.policy_engine.create_policy(
            "Новая политика",
            "Политика безопасности по умолчанию"
        )
        
        # Добавляем стандартные зоны
        zones = [
            SecurityZone("Trusted", ZoneType.TRUSTED),
            SecurityZone("IoT", ZoneType.IOT),
            SecurityZone("Guests", ZoneType.GUEST),
        ]
        
        for zone in zones:
            self.current_policy.add_zone(zone)
            self.network_canvas.add_zone(zone)
    
    def scan_network(self):
        """Сканировать сеть"""
        self.statusBar().showMessage("Сканирование сети...")
        self.network_status.setVisible(True)
        self.network_status.setValue(0)
        
        self.scanner.scan_network_async(
            callback=self.on_scan_progress
        )
    
    def on_scan_progress(self, phase: str, message: str, progress: int):
        """Обработка прогресса сканирования"""
        if phase == "complete":
            devices = self.scanner.get_scan_results()
            self.devices = devices
            self.device_list.update_devices(devices)
            self.statusBar().showMessage(f"Найдено {len(devices)} устройств")
            self.network_status.setVisible(False)
        elif phase == "error":
            QMessageBox.critical(self, "Ошибка", message)
            self.network_status.setVisible(False)
        else:
            self.statusBar().showMessage(message)
            self.network_status.setValue(progress)
    
    def stop_scanning(self):
        """Остановить сканирование"""
        self.scanner.stop_scan()
        self.statusBar().showMessage("Сканирование остановлено")
        self.network_status.setVisible(False)
    
    def validate_policy(self):
        """Валидировать текущую политику"""
        if not self.current_policy:
            QMessageBox.warning(self, "Внимание", "Нет активной политики")
            return
        
        self.statusBar().showMessage("Валидация политики...")
        
        # Запускаем валидацию
        results = self.validator.validate_policy(
            self.current_policy,
            callback=self.on_validation_progress
        )
        
        # Показываем результаты
        self.show_validation_results(results)
    
    def on_validation_progress(self, event: str, message: str, progress: int):
        """Обработка прогресса валидации"""
        if event == "validation_complete":
            self.statusBar().showMessage("Валидация завершена")
        else:
            self.statusBar().showMessage(message)
    
    def show_validation_results(self, results: dict):
        """Показать результаты валидации"""
        summary = results.get('summary', {})
        
        if summary.get('overall_status') == 'passed':
            QMessageBox.information(
                self,
                "Валидация пройдена",
                f"Политика успешно валидирована!\n\n"
                f"Успешно: {summary['passed_tests']}/{summary['total_tests']}\n"
                f"Рейтинг: {summary['success_rate']}"
            )
        else:
            QMessageBox.warning(
                self,
                "Валидация не пройдена",
                f"Обнаружены проблемы:\n\n"
                f"{chr(10).join(summary.get('issues', []))}\n\n"
                f"Рекомендации:\n{chr(10).join(summary.get('recommendations', []))}"
            )
    
    def add_zone(self):
        """Добавить новую зону"""
        from PyQt6.QtWidgets import QInputDialog
        
        name, ok = QInputDialog.getText(
            self,
            "Добавить зону",
            "Введите имя зоны:",
            text=f"Zone_{len(self.current_policy.zones) + 1}"
        )
        
        if ok and name:
            zone = SecurityZone(name, ZoneType.CUSTOM)
            self.current_policy.add_zone(zone)
            
            # Добавляем зону на холст
            self.network_canvas.add_zone(zone)
            
            # Обновляем правила
            self.policy_engine.generate_default_rules(self.current_policy)
    
    def on_device_selected(self, device: NetworkDevice):
        """Обработка выбора устройства"""
        # Здесь можно показать свойства устройства
        pass
    
    def on_device_dragged(self, device_id: str, zone_name: str):
        """Обработка перетаскивания устройства"""
        # Ищем устройство
        device = next((d for d in self.devices if d.ip_address == device_id), None)
        if device and zone_name:
            # Добавляем устройство в зону
            self.network_canvas.add_device_to_zone(device, zone_name)
    
    def on_selection_changed(self, devices: list):
        """Обработка изменения выбора"""
        # Обновляем свойства выбранных устройств
        pass
    
    def new_policy(self):
        """Создать новую политику"""
        reply = QMessageBox.question(
            self,
            "Новая политика",
            "Создать новую политику? Текущие изменения будут потеряны.",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )
        
        if reply == QMessageBox.StandardButton.Yes:
            self.load_default_policy()
    
    def save_policy(self):
        """Сохранить политику"""
        if not self.current_policy:
            return
        
        filepath, _ = QFileDialog.getSaveFileName(
            self,
            "Сохранить политику",
            f"{self.current_policy.name}.json",
            "JSON Files (*.json)"
        )
        
        if filepath:
            try:
                self.policy_engine.save_policy(
                    self.current_policy,
                    Path(filepath)
                )
                self.statusBar().showMessage(f"Политика сохранена: {filepath}")
            except Exception as e:
                QMessageBox.critical(self, "Ошибка", f"Ошибка сохранения: {e}")
    
    def open_policy(self):
        """Открыть политику"""
        filepath, _ = QFileDialog.getOpenFileName(
            self,
            "Открыть политику",
            "",
            "JSON Files (*.json)"
        )
        
        if filepath:
            try:
                policy = self.policy_engine.load_policy(Path(filepath))
                self.current_policy = policy
                
                # Обновляем интерфейс
                self.network_canvas.clear_canvas()
                for zone in policy.zones.values():
                    self.network_canvas.add_zone(zone)
                
                self.statusBar().showMessage(f"Политика загружена: {policy.name}")
            except Exception as e:
                QMessageBox.critical(self, "Ошибка", f"Ошибка загрузки: {e}")
    
    def export_config(self):
        """Экспортировать конфигурацию"""
        if not self.current_policy:
            QMessageBox.warning(self, "Внимание", "Нет активной политики")
            return
        
        from PyQt6.QtWidgets import QDialog, QComboBox, QDialogButtonBox
        
        dialog = QDialog(self)
        dialog.setWindowTitle("Экспорт конфигурации")
        
        layout = QVBoxLayout(dialog)
        
        # Выбор платформы
        layout.addWidget(QLabel("Выберите целевую платформу:"))
        platform_combo = QComboBox()
        platform_combo.addItems(self.policy_engine.SUPPORTED_PLATFORMS.keys())
        layout.addWidget(platform_combo)
        
        # Кнопки
        buttons = QDialogButtonBox(
            QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel
        )
        buttons.accepted.connect(dialog.accept)
        buttons.rejected.connect(dialog.reject)
        layout.addWidget(buttons)
        
        if dialog.exec() == QDialog.DialogCode.Accepted:
            platform = platform_combo.currentText()
            
            filepath, _ = QFileDialog.getSaveFileName(
                self,
                f"Экспорт для {platform}",
                f"config_{platform}_{self.current_policy.name}.txt",
                "Text Files (*.txt);;All Files (*)"
            )
            
            if filepath:
                try:
                    config = self.policy_engine.generate_config(
                        self.current_policy,
                        platform
                    )
                    
                    with open(filepath, 'w', encoding='utf-8') as f:
                        f.write(config)
                    
                    QMessageBox.information(
                        self,
                        "Экспорт завершен",
                        f"Конфигурация успешно экспортирована в:\n{filepath}\n\n"
                        f"Инструкции по применению:\n{self.policy_engine.get_platform_instructions(platform)}"
                    )
                except Exception as e:
                    QMessageBox.critical(self, "Ошибка", f"Ошибка экспорта: {e}")
    
    def auto_arrange(self):
        """Автоматически расположить зоны на холсте"""
        self.network_canvas.auto_arrange()
    
    def show_about(self):
        """Показать информацию о программе"""
        about_text = """
        <h2>ZeroTrust Inspector v1.0.0</h2>
        <p>Визуализатор и валидатор Zero-Trust политик</p>
        <p>Для домашних сетей и малых офисов</p>
        <hr>
        <p>Автор: Ваше Имя</p>
        <p>Лицензия: MIT</p>
        <p>GitHub: github.com/username/zerotrust-inspector</p>
        """
        
        QMessageBox.about(self, "О программе", about_text)
    
    def closeEvent(self, event):
        """Обработка закрытия окна"""
        reply = QMessageBox.question(
            self,
            "Выход",
            "Вы уверены, что хотите выйти?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )
        
        if reply == QMessageBox.StandardButton.Yes:
            event.accept()
        else:
            event.ignore()
