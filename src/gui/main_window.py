"""
Главное окно приложения
"""

from PyQt6.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QTabWidget,
    QPushButton, QLabel, QProgressBar, QMessageBox, QListWidget,
    QSplitter, QGroupBox, QTreeWidget, QTreeWidgetItem
)
from PyQt6.QtCore import Qt, QTimer, pyqtSignal
from PyQt6.QtGui import QIcon, QFont

from ...core.models import NetworkDevice, SecurityZone, NetworkPolicy
from ...scanner import NetworkScanner
from ...validation import PolicyValidator

class MainWindow(QMainWindow):
    """Главное окно ZeroTrust Inspector"""
    
    scan_completed = pyqtSignal(list)
    validation_completed = pyqtSignal(dict)
    
    def __init__(self):
        super().__init__()
        self.scanner = NetworkScanner()
        self.validator = PolicyValidator()
        self.current_policy = None
        
        self.setup_ui()
        self.setup_connections()
        
    def setup_ui(self):
        """Настроить пользовательский интерфейс"""
        self.setWindowTitle("ZeroTrust Inspector")
        self.setGeometry(100, 100, 1200, 800)
        
        # Центральный виджет
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        main_layout = QVBoxLayout(central_widget)
        
        # Панель инструментов
        toolbar = self.create_toolbar()
        main_layout.addWidget(toolbar)
        
        # Разделитель для основной области
        splitter = QSplitter(Qt.Orientation.Horizontal)
        
        # Левая панель - устройства и зоны
        left_panel = self.create_left_panel()
        splitter.addWidget(left_panel)
        
        # Центральная панель - визуализация
        center_panel = self.create_center_panel()
        splitter.addWidget(center_panel)
        
        # Правая панель - детали и правила
        right_panel = self.create_right_panel()
        splitter.addWidget(right_panel)
        
        splitter.setSizes([300, 600, 300])
        main_layout.addWidget(splitter)
        
        # Статус бар
        self.status_bar = self.statusBar()
        self.progress_bar = QProgressBar()
        self.status_bar.addPermanentWidget(self.progress_bar)
        self.progress_bar.hide()
        
    def create_toolbar(self) -> QWidget:
        """Создать панель инструментов"""
        toolbar = QWidget()
        layout = QHBoxLayout(toolbar)
        
        # Кнопки управления
        self.btn_scan = QPushButton("🔍 Сканировать сеть")
        self.btn_scan.setToolTip("Запустить сканирование сети")
        
        self.btn_validate = QPushButton("✅ Валидировать")
        self.btn_validate.setToolTip("Валидировать текущую политику")
        
        self.btn_export = QPushButton("📁 Экспорт")
        self.btn_export.setToolTip("Экспортировать конфигурацию")
        
        self.btn_settings = QPushButton("⚙ Настройки")
        self.btn_settings.setToolTip("Настройки приложения")
        
        layout.addWidget(self.btn_scan)
        layout.addWidget(self.btn_validate)
        layout.addWidget(self.btn_export)
        layout.addWidget(self.btn_settings)
        layout.addStretch()
        
        return toolbar
    
    def create_left_panel(self) -> QWidget:
        """Создать левую панель (устройства и зоны)"""
        panel = QWidget()
        layout = QVBoxLayout(panel)
        
        # Группа устройств
        devices_group = QGroupBox("Обнаруженные устройства")
        devices_layout = QVBoxLayout()
        
        self.devices_list = QTreeWidget()
        self.devices_list.setHeaderLabels(["Устройство", "IP", "Тип"])
        self.devices_list.setSortingEnabled(True)
        
        devices_layout.addWidget(self.devices_list)
        devices_group.setLayout(devices_layout)
        layout.addWidget(devices_group)
        
        # Группа зон
        zones_group = QGroupBox("Зоны безопасности")
        zones_layout = QVBoxLayout()
        
        self.zones_list = QListWidget()
        zones_layout.addWidget(self.zones_list)
        
        zones_group.setLayout(zones_layout)
        layout.addWidget(zones_group)
        
        return panel
    
    def create_center_panel(self) -> QWidget:
        """Создать центральную панель (визуализация)"""
        panel = QWidget()
        layout = QVBoxLayout(panel)
        
        # Заголовок
        title_label = QLabel("Визуализация Zero Trust сети")
        title_font = QFont()
        title_font.setPointSize(16)
        title_font.setBold(True)
        title_label.setFont(title_font)
        title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(title_label)
        
        # Область визуализации
        self.visualization_area = QLabel("Здесь будет визуализация сети")
        self.visualization_area.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.visualization_area.setStyleSheet("""
            QLabel {
                background-color: #f0f0f0;
                border: 2px dashed #ccc;
                font-size: 14px;
                padding: 20px;
            }
        """)
        layout.addWidget(self.visualization_area)
        
        return panel
    
    def create_right_panel(self) -> QWidget:
        """Создать правую панель (детали и правила)"""
        panel = QWidget()
        layout = QVBoxLayout(panel)
        
        # Вкладки
        tabs = QTabWidget()
        
        # Вкладка деталей
        details_tab = self.create_details_tab()
        tabs.addTab(details_tab, "Детали")
        
        # Вкладка правил
        rules_tab = self.create_rules_tab()
        tabs.addTab(rules_tab, "Правила")
        
        # Вкладка валидации
        validation_tab = self.create_validation_tab()
        tabs.addTab(validation_tab, "Валидация")
        
        layout.addWidget(tabs)
        
        return panel
    
    def create_details_tab(self) -> QWidget:
        """Создать вкладку деталей"""
        tab = QWidget()
        layout = QVBoxLayout(tab)
        
        self.details_text = QLabel("Выберите устройство для просмотра деталей")
        self.details_text.setWordWrap(True)
        self.details_text.setAlignment(Qt.AlignmentFlag.AlignTop)
        
        layout.addWidget(self.details_text)
        layout.addStretch()
        
        return tab
    
    def create_rules_tab(self) -> QWidget:
        """Создать вкладку правил"""
        tab = QWidget()
        layout = QVBoxLayout(tab)
        
        self.rules_list = QTreeWidget()
        self.rules_list.setHeaderLabels(["Источник", "Назначение", "Действие", "Описание"])
        self.rules_list.setSortingEnabled(True)
        
        layout.addWidget(self.rules_list)
        
        # Кнопки управления правилами
        btn_layout = QHBoxLayout()
        
        self.btn_add_rule = QPushButton("+ Добавить правило")
        self.btn_edit_rule = QPushButton("✏ Редактировать")
        self.btn_delete_rule = QPushButton("🗑 Удалить")
        
        btn_layout.addWidget(self.btn_add_rule)
        btn_layout.addWidget(self.btn_edit_rule)
        btn_layout.addWidget(self.btn_delete_rule)
        
        layout.addLayout(btn_layout)
        
        return tab
    
    def create_validation_tab(self) -> QWidget:
        """Создать вкладку валидации"""
        tab = QWidget()
        layout = QVBoxLayout(tab)
        
        self.validation_results = QLabel("Результаты валидации будут здесь")
        self.validation_results.setWordWrap(True)
        
        layout.addWidget(self.validation_results)
        layout.addStretch()
        
        return tab
    
    def setup_connections(self):
        """Настроить соединения сигналов и слотов"""
        self.btn_scan.clicked.connect(self.start_scan)
        self.btn_validate.clicked.connect(self.start_validation)
        
        self.scan_completed.connect(self.on_scan_completed)
        self.validation_completed.connect(self.on_validation_completed)
        
        self.devices_list.itemClicked.connect(self.on_device_selected)
    
    def start_scan(self):
        """Запустить сканирование сети"""
        try:
            self.progress_bar.show()
            self.progress_bar.setValue(0)
            self.status_bar.showMessage("Сканирование сети...")
            
            # Запускаем в отдельном потоке
            import threading
            scan_thread = threading.Thread(target=self.perform_scan)
            scan_thread.start()
            
        except Exception as e:
            QMessageBox.critical(self, "Ошибка", f"Ошибка сканирования: {e}")
    
    def perform_scan(self):
        """Выполнить сканирование (в отдельном потоке)"""
        try:
            devices = self.scanner.scan_network()
            self.scan_completed.emit(devices)
        except Exception as e:
            self.status_bar.showMessage(f"Ошибка: {e}")
    
    def on_scan_completed(self, devices):
        """Обработчик завершения сканирования"""
        self.progress_bar.hide()
        self.status_bar.showMessage(f"Найдено {len(devices)} устройств")
        
        # Обновляем список устройств
        self.devices_list.clear()
        
        for device in devices:
            item = QTreeWidgetItem([
                device.hostname or "Неизвестно",
                device.ip_address,
                device.device_type.value
            ])
            self.devices_list.addTopLevelItem(item)
    
    def start_validation(self):
        """Запустить валидацию политики"""
        if not self.current_policy:
            QMessageBox.warning(self, "Предупреждение", "Сначала создайте политику безопасности")
            return
        
        try:
            self.progress_bar.show()
            self.progress_bar.setValue(0)
            self.status_bar.showMessage("Валидация политики...")
            
            # Запускаем в отдельном потоке
            import threading
            validation_thread = threading.Thread(
                target=self.perform_validation,
                args=(self.current_policy,)
            )
            validation_thread.start()
            
        except Exception as e:
            QMessageBox.critical(self, "Ошибка", f"Ошибка валидации: {e}")
    
    def perform_validation(self, policy):
        """Выполнить валидацию (в отдельном потоке)"""
        try:
            results = self.validator.validate_policy(policy)
            self.validation_completed.emit(results)
        except Exception as e:
            self.status_bar.showMessage(f"Ошибка валидации: {e}")
    
    def on_validation_completed(self, results):
        """Обработчик завершения валидации"""
        self.progress_bar.hide()
        self.status_bar.showMessage("Валидация завершена")
        
        # Обновляем результаты
        summary = results.get('summary', {})
        success_rate = summary.get('success_rate', '0%')
        
        self.validation_results.setText(f"""
        <h3>Результаты валидации:</h3>
        <p><b>Успешность:</b> {success_rate}</p>
        <p><b>Тестов выполнено:</b> {summary.get('total_tests', 0)}</p>
        <p><b>Успешно:</b> {summary.get('passed_tests', 0)}</p>
        <p><b>Неудачно:</b> {summary.get('failed_tests', 0)}</p>
        
        <h4>Проблемы:</h4>
        <ul>
            {"".join(f"<li>{issue}</li>" for issue in summary.get('issues', []))}
        </ul>
        
        <h4>Рекомендации:</h4>
        <ul>
            {"".join(f"<li>{rec}</li>" for rec in summary.get('recommendations', []))}
        </ul>
        """)
    
    def on_device_selected(self, item, column):
        """Обработчик выбора устройства"""
        ip_address = item.text(1)
        device_type = item.text(2)
        
        # Получаем детальную информацию
        device = self.scanner.scan_single_device(ip_address)
        
        if device:
            self.details_text.setText(f"""
            <h3>Детали устройства:</h3>
            <p><b>IP адрес:</b> {device.ip_address}</p>
            <p><b>MAC адрес:</b> {device.mac_address or "Неизвестно"}</p>
            <p><b>Hostname:</b> {device.hostname or "Неизвестно"}</p>
            <p><b>Тип:</b> {device.device_type.value}</p>
            <p><b>Производитель:</b> {device.vendor or "Неизвестно"}</p>
            <p><b>ОС:</b> {device.os or "Неизвестно"}</p>
            <p><b>Открытые порты:</b> {', '.join(map(str, device.open_ports)) or "Нет"}</p>
            <p><b>Оценка риска:</b> {device.risk_score:.2f}</p>
            """)
