"""
Главное окно приложения
"""

from PyQt6.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QTabWidget,
    QPushButton, QLabel, QProgressBar, QMessageBox, QListWidget,
    QSplitter, QGroupBox, QTreeWidget, QTreeWidgetItem
)
from PyQt6.QtCore import Qt, QTimer, pyqtSignal, QThread, pyqtSlot
from PyQt6.QtGui import QIcon, QFont

# Используем абсолютные импорты
from src.core.models import NetworkDevice, SecurityZone, NetworkPolicy, ZoneType, ActionType

class ScanThread(QThread):
    """Поток для выполнения сканирования"""
    scan_progress = pyqtSignal(int)
    scan_completed = pyqtSignal(list)
    scan_error = pyqtSignal(str)
    
    def __init__(self, network_range="192.168.1.0/24"):
        super().__init__()
        self.network_range = network_range
        self.running = True
    
    def run(self):
        """Выполнить сканирование в отдельном потоке"""
        try:
            devices = []
            
            # Имитация сканирования с прогрессом
            test_devices = [
                NetworkDevice("192.168.1.1", "00:11:22:33:44:55", "router", vendor="TP-Link"),
                NetworkDevice("192.168.1.10", "AA:BB:CC:DD:EE:FF", "home-pc", vendor="Dell"),
                NetworkDevice("192.168.1.20", "11:22:33:44:55:66", "phone", vendor="Samsung"),
                NetworkDevice("192.168.1.30", "FF:EE:DD:CC:BB:AA", "smart-tv", vendor="Sony"),
                NetworkDevice("192.168.1.40", "22:33:44:55:66:77", "printer", vendor="HP"),
            ]
            
            for i, device in enumerate(test_devices):
                if not self.running:
                    break
                    
                # Имитация задержки сканирования
                self.msleep(200)
                
                # Обновляем прогресс
                progress = int((i + 1) / len(test_devices) * 100)
                self.scan_progress.emit(progress)
                
                devices.append(device)
            
            if self.running:
                self.scan_completed.emit(devices)
                
        except Exception as e:
            self.scan_error.emit(str(e))
    
    def stop(self):
        """Остановить сканирование"""
        self.running = False

class ValidationThread(QThread):
    """Поток для выполнения валидации"""
    validation_progress = pyqtSignal(int)
    validation_completed = pyqtSignal(dict)
    validation_error = pyqtSignal(str)
    
    def __init__(self, policy):
        super().__init__()
        self.policy = policy
        self.running = True
    
    def run(self):
        """Выполнить валидацию в отдельном потоке"""
        try:
            # Имитация валидации с прогрессом
            for i in range(1, 101):
                if not self.running:
                    break
                    
                self.msleep(30)
                self.validation_progress.emit(i)
            
            if self.running:
                # Тестовые результаты
                results = {
                    'summary': {
                        'total_tests': 12,
                        'passed_tests': 10,
                        'failed_tests': 2,
                        'success_rate': '83.3%',
                        'overall_status': 'warning',
                        'issues': ['Обнаружены утечки трафика между зонами'],
                        'recommendations': ['Добавьте правило блокировки из IoT в Trusted']
                    }
                }
                self.validation_completed.emit(results)
                
        except Exception as e:
            self.validation_error.emit(str(e))
    
    def stop(self):
        """Остановить валидацию"""
        self.running = False

class MainWindow(QMainWindow):
    """Главное окно ZeroTrust Inspector"""
    
    def __init__(self):
        super().__init__()
        self.scan_thread = None
        self.validation_thread = None
        self.current_policy = None
        
        self.setup_ui()
        self.setup_connections()
    
    def setup_ui(self):
        """Настроить пользовательский интерфейс"""
        self.setWindowTitle("ZeroTrust Inspector v1.0.0")
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
        self.progress_bar.setFixedWidth(200)
        self.status_bar.addPermanentWidget(self.progress_bar)
        self.progress_bar.hide()
        
    def create_toolbar(self) -> QWidget:
        """Создать панель инструментов"""
        toolbar = QWidget()
        layout = QHBoxLayout(toolbar)
        
        # Кнопки управления
        self.btn_scan = QPushButton("🔍 Сканировать сеть")
        self.btn_scan.setToolTip("Запустить сканирование сети")
        
        self.btn_stop_scan = QPushButton("⏹️ Остановить")
        self.btn_stop_scan.setToolTip("Остановить текущее сканирование")
        self.btn_stop_scan.setEnabled(False)
        
        self.btn_validate = QPushButton("✅ Валидировать")
        self.btn_validate.setToolTip("Валидировать текущую политику")
        
        self.btn_export = QPushButton("📁 Экспорт")
        self.btn_export.setToolTip("Экспортировать конфигурацию")
        
        self.btn_settings = QPushButton("⚙ Настройки")
        self.btn_settings.setToolTip("Настройки приложения")
        
        layout.addWidget(self.btn_scan)
        layout.addWidget(self.btn_stop_scan)
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
        
        # Добавляем тестовые данные
        self.add_test_devices()
        
        devices_layout.addWidget(self.devices_list)
        devices_group.setLayout(devices_layout)
        layout.addWidget(devices_group)
        
        # Группа зон
        zones_group = QGroupBox("Зоны безопасности")
        zones_layout = QVBoxLayout()
        
        self.zones_list = QListWidget()
        self.zones_list.addItems(["Trusted", "IoT", "Guests", "DMZ"])
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
        self.visualization_area = QLabel("""
        <center>
        <h3>ZeroTrust Inspector успешно запущен!</h3>
        <p>Для начала работы нажмите "Сканировать сеть"</p>
        <p>Или создайте тестовую политику:</p>
        </center>
        """)
        self.visualization_area.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.visualization_area.setStyleSheet("""
            QLabel {
                background-color: #f0f0f0;
                border: 2px dashed #ccc;
                font-size: 14px;
                padding: 40px;
                border-radius: 10px;
            }
        """)
        layout.addWidget(self.visualization_area)
        
        # Кнопка создания тестовой политики
        self.btn_test_policy = QPushButton("Создать тестовую политику")
        self.btn_test_policy.setToolTip("Создать пример политики безопасности")
        layout.addWidget(self.btn_test_policy)
        
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
        
        # Добавляем тестовые правила
        self.add_test_rules()
        
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
        
        self.validation_results = QLabel("""
        <h3>Валидация Zero Trust политик</h3>
        <p>Нажмите кнопку "Валидировать" для проверки текущей политики</p>
        <p>Будут выполнены тесты:</p>
        <ul>
            <li>Проверка связности внутри зон</li>
            <li>Тест изоляции между зонами</li>
            <li>Проверка производительности</li>
            <li>Валидация правил безопасности</li>
        </ul>
        """)
        self.validation_results.setWordWrap(True)
        
        layout.addWidget(self.validation_results)
        layout.addStretch()
        
        return tab
    
    def add_test_devices(self):
        """Добавить тестовые устройства"""
        test_devices = [
            ("Домашний компьютер", "192.168.1.10", "Компьютер"),
            ("Ноутбук", "192.168.1.15", "Компьютер"),
            ("Телефон", "192.168.1.20", "Телефон"),
            ("Умная камера", "192.168.1.30", "IoT"),
            ("Принтер", "192.168.1.40", "Принтер"),
            ("Роутер", "192.168.1.1", "Роутер"),
        ]
        
        for device in test_devices:
            item = QTreeWidgetItem(list(device))
            self.devices_list.addTopLevelItem(item)
    
    def add_test_rules(self):
        """Добавить тестовые правила"""
        test_rules = [
            ("Trusted", "IoT", "DENY", "Блокировать IoT из доверенной зоны"),
            ("Trusted", "Guests", "DENY", "Изолировать гостевую сеть"),
            ("Trusted", "Internet", "ALLOW", "Разрешить интернет"),
            ("IoT", "Internet", "LIMIT", "Ограниченный доступ в интернет"),
            ("Guests", "Internet", "ALLOW", "Только интернет"),
        ]
        
        for rule in test_rules:
            item = QTreeWidgetItem(list(rule))
            self.rules_list.addTopLevelItem(item)
    
    def setup_connections(self):
        """Настроить соединения сигналов и слотов"""
        self.btn_scan.clicked.connect(self.start_scan)
        self.btn_stop_scan.clicked.connect(self.stop_scan)
        self.btn_validate.clicked.connect(self.start_validation)
        self.btn_test_policy.clicked.connect(self.create_test_policy)
        
        self.devices_list.itemClicked.connect(self.on_device_selected)
        self.zones_list.itemClicked.connect(self.on_zone_selected)
    
    def start_scan(self):
        """Запустить сканирование сети"""
        if self.scan_thread and self.scan_thread.isRunning():
            QMessageBox.warning(self, "Сканирование", "Сканирование уже выполняется")
            return
        
        # Очищаем старые результаты
        self.devices_list.clear()
        
        # Показываем прогресс
        self.progress_bar.show()
        self.progress_bar.setValue(0)
        self.status_bar.showMessage("Сканирование сети...")
        
        # Обновляем состояние кнопок
        self.btn_scan.setEnabled(False)
        self.btn_stop_scan.setEnabled(True)
        
        # Создаем и запускаем поток сканирования
        self.scan_thread = ScanThread()
        self.scan_thread.scan_progress.connect(self.on_scan_progress)
        self.scan_thread.scan_completed.connect(self.on_scan_completed)
        self.scan_thread.scan_error.connect(self.on_scan_error)
        self.scan_thread.finished.connect(self.on_scan_finished)
        
        self.scan_thread.start()
    
    def stop_scan(self):
        """Остановить сканирование"""
        if self.scan_thread and self.scan_thread.isRunning():
            self.scan_thread.stop()
            self.status_bar.showMessage("Сканирование остановлено")
    
    @pyqtSlot(int)
    def on_scan_progress(self, progress):
        """Обновить прогресс сканирования"""
        self.progress_bar.setValue(progress)
    
    @pyqtSlot(list)
    def on_scan_completed(self, devices):
        """Обработчик завершения сканирования"""
        # Обновляем список устройств
        for device in devices:
            item = QTreeWidgetItem([
                device.hostname or "Неизвестно",
                device.ip_address,
                getattr(device, 'device_type', 'unknown')
            ])
            self.devices_list.addTopLevelItem(item)
        
        self.status_bar.showMessage(f"Найдено {len(devices)} устройств")
        
        # Обновляем визуализацию
        self.visualization_area.setText(f"""
        <center>
        <h3>Сканирование завершено!</h3>
        <p>Найдено устройств: <b>{len(devices)}</b></p>
        <p>Создайте зоны безопасности и настройте правила.</p>
        </center>
        """)
    
    @pyqtSlot(str)
    def on_scan_error(self, error_message):
        """Обработчик ошибки сканирования"""
        self.status_bar.showMessage(f"Ошибка сканирования: {error_message}")
        QMessageBox.critical(self, "Ошибка сканирования", error_message)
    
    def on_scan_finished(self):
        """Очистка после завершения сканирования"""
        self.progress_bar.hide()
        self.btn_scan.setEnabled(True)
        self.btn_stop_scan.setEnabled(False)
        
        if self.scan_thread:
            self.scan_thread.deleteLater()
            self.scan_thread = None
    
    def start_validation(self):
        """Запустить валидацию политики"""
        if not self.current_policy:
            QMessageBox.warning(self, "Предупреждение", 
                              "Сначала создайте тестовую политику или загрузите существующую")
            return
        
        if self.validation_thread and self.validation_thread.isRunning():
            QMessageBox.warning(self, "Валидация", "Валидация уже выполняется")
            return
        
        # Показываем прогресс
        self.progress_bar.show()
        self.progress_bar.setValue(0)
        self.status_bar.showMessage("Валидация политики...")
        
        # Создаем и запускаем поток валидации
        self.validation_thread = ValidationThread(self.current_policy)
        self.validation_thread.validation_progress.connect(self.on_validation_progress)
        self.validation_thread.validation_completed.connect(self.on_validation_completed)
        self.validation_thread.validation_error.connect(self.on_validation_error)
        self.validation_thread.finished.connect(self.on_validation_finished)
        
        self.validation_thread.start()
    
    @pyqtSlot(int)
    def on_validation_progress(self, progress):
        """Обновить прогресс валидации"""
        self.progress_bar.setValue(progress)
    
    @pyqtSlot(dict)
    def on_validation_completed(self, results):
        """Обработчик завершения валидации"""
        self.status_bar.showMessage("Валидация завершена")
        
        # Обновляем результаты
        summary = results.get('summary', {})
        success_rate = summary.get('success_rate', '0%')
        
        self.validation_results.setText(f"""
        <h3>Результаты валидации:</h3>
        <p><b>Статус:</b> <span style='color: orange'>{summary.get('overall_status', 'unknown').upper()}</span></p>
        <p><b>Успешность:</b> {success_rate}</p>
        <p><b>Тестов выполнено:</b> {summary.get('total_tests', 0)}</p>
        <p><b>Успешно:</b> {summary.get('passed_tests', 0)}</p>
        <p><b>Неудачно:</b> {summary.get('failed_tests', 0)}</p>
        
        <h4>Проблемы:</h4>
        <ul>
            {"".join(f"<li style='color: red'>{issue}</li>" for issue in summary.get('issues', []))}
        </ul>
        
        <h4>Рекомендации:</h4>
        <ul>
            {"".join(f"<li style='color: green'>{rec}</li>" for rec in summary.get('recommendations', []))}
        </ul>
        """)
    
    @pyqtSlot(str)
    def on_validation_error(self, error_message):
        """Обработчик ошибки валидации"""
        self.status_bar.showMessage(f"Ошибка валидации: {error_message}")
        QMessageBox.critical(self, "Ошибка валидации", error_message)
    
    def on_validation_finished(self):
        """Очистка после завершения валидации"""
        self.progress_bar.hide()
        
        if self.validation_thread:
            self.validation_thread.deleteLater()
            self.validation_thread = None
    
    def create_test_policy(self):
        """Создать тестовую политику"""
        try:
            # Создаем тестовую политику
            policy = NetworkPolicy(
                name="Тестовая политика",
                description="Пример политики Zero Trust для домашней сети"
            )
            
            # Создаем зоны
            trusted_zone = SecurityZone("Trusted", ZoneType.TRUSTED)
            iot_zone = SecurityZone("IoT", ZoneType.IOT)
            guest_zone = SecurityZone("Guests", ZoneType.GUEST)
            
            policy.add_zone(trusted_zone)
            policy.add_zone(iot_zone)
            policy.add_zone(guest_zone)
            
            self.current_policy = policy
            
            # Обновляем визуализацию
            self.visualization_area.setText(f"""
            <center>
            <h3>Тестовая политика создана!</h3>
            <p><b>Имя:</b> {policy.name}</p>
            <p><b>Описание:</b> {policy.description}</p>
            <p><b>Зоны:</b> {len(policy.zones)}</p>
            <ul>
                <li>Trusted - Доверенные устройства</li>
                <li>IoT - Умные устройства</li>
                <li>Guests - Гостевая сеть</li>
            </ul>
            <p>Теперь вы можете запустить валидацию.</p>
            </center>
            """)
            
            QMessageBox.information(self, "Политика создана", 
                                  f"Создана тестовая политика '{policy.name}' с {len(policy.zones)} зонами")
            
        except Exception as e:
            QMessageBox.critical(self, "Ошибка", f"Ошибка создания политики: {e}")
    
    def on_device_selected(self, item, column):
        """Обработчик выбора устройства"""
        device_name = item.text(0)
        ip_address = item.text(1)
        device_type = item.text(2)
        
        self.details_text.setText(f"""
        <h3>Детали устройства:</h3>
        <p><b>Имя:</b> {device_name}</p>
        <p><b>IP адрес:</b> {ip_address}</p>
        <p><b>Тип:</b> {device_type}</p>
        <p><b>Статус:</b> <span style='color: green'>Активно</span></p>
        <p><b>Оценка риска:</b> <span style='color: orange'>Средняя</span></p>
        
        <h4>Рекомендации:</h4>
        <ul>
            <li>Проверьте обновления безопасности</li>
            <li>Используйте сложный пароль</li>
            <li>Включите шифрование</li>
        </ul>
        """)
    
    def on_zone_selected(self, item):
        """Обработчик выбора зоны"""
        zone_name = item.text()
        
        self.details_text.setText(f"""
        <h3>Детали зоны:</h3>
        <p><b>Имя:</b> {zone_name}</p>
        <p><b>Статус:</b> <span style='color: green'>Активна</span></p>
        
        <h4>Типичные устройства:</h4>
        <ul>
            <li>Компьютеры и ноутбуки</li>
            <li>Смартфоны и планшеты</li>
            <li>Серверы</li>
        </ul>
        
        <h4>Политика безопасности:</h4>
        <p>Высокий уровень безопасности. Разрешен доступ к интернету и внутренним ресурсам.</p>
        """)
    
    def closeEvent(self, event):
        """Обработчик закрытия окна"""
        # Останавливаем все потоки
        if self.scan_thread and self.scan_thread.isRunning():
            self.scan_thread.stop()
            self.scan_thread.wait(1000)
        
        if self.validation_thread and self.validation_thread.isRunning():
            self.validation_thread.stop()
            self.validation_thread.wait(1000)
        
        event.accept()
