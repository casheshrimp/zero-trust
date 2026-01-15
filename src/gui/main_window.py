"""
Главное окно приложения с новым дизайном
"""

import sys
from pathlib import Path
from PyQt6.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QStackedWidget,
    QSplitter, QStatusBar, QToolBar, QMenuBar, QMessageBox,
    QLabel, QPushButton, QFrame, QSizePolicy, QSpacerItem
)
from PyQt6.QtCore import Qt, pyqtSignal, QSize
from PyQt6.QtGui import QAction, QIcon, QKeySequence, QPixmap

from .styles import AppStyles
from .pages.dashboard import DashboardPage
from .pages.scanner import ScannerPage
from .pages.constructor import ConstructorPage
from .pages.generator import GeneratorPage
from .pages.validator import ValidatorPage
from .pages.reports import ReportsPage
from .pages.settings import SettingsPage

class MainWindow(QMainWindow):
    """Главное окно с новым дизайном"""
    
    def __init__(self):
        super().__init__()
        
        self.setWindowTitle("ZeroTrust Inspector v1.0.0")
        self.setGeometry(100, 100, 1400, 800)
        
        # Применяем стили
        self.setPalette(AppStyles.create_dark_palette())
        self.setStyleSheet(AppStyles.get_stylesheet())
        
        self.init_ui()
        self.create_menu()
        self.create_toolbar()
        self.create_statusbar()
        
        self.statusBar().showMessage("Готов к работе")
        
    def init_ui(self):
        """Инициализация интерфейса"""
        # Центральный виджет
        central_widget = QWidget()
        central_widget.setObjectName("centralWidget")
        self.setCentralWidget(central_widget)
        
        # Основной макет
        main_layout = QHBoxLayout(central_widget)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)
        
        # Боковое меню (Navigation Rail)
        self.sidebar = self.create_sidebar()
        main_layout.addWidget(self.sidebar)
        
        # Основная область
        main_area = QWidget()
        main_area.setObjectName("mainArea")
        main_area_layout = QVBoxLayout(main_area)
        main_area_layout.setContentsMargins(0, 0, 0, 0)
        
        # Верхняя панель с заголовком
        self.top_bar = self.create_top_bar()
        main_area_layout.addWidget(self.top_bar)
        
        # Область содержимого (стек виджетов)
        self.content_stack = QStackedWidget()
        self.content_stack.setObjectName("contentStack")
        
        # Создаем страницы
        self.pages = {
            'dashboard': DashboardPage(),
            'scanner': ScannerPage(),
            'constructor': ConstructorPage(),
            'generator': GeneratorPage(),
            'validator': ValidatorPage(),
            'reports': ReportsPage(),
            'settings': SettingsPage(),
        }
        
        for page_name, page in self.pages.items():
            self.content_stack.addWidget(page)
        
        main_area_layout.addWidget(self.content_stack)
        
        main_layout.addWidget(main_area, 1)
        
        # Показываем начальную страницу
        self.show_page('dashboard')
        
    def create_sidebar(self):
        """Создать боковое меню"""
        sidebar = QFrame()
        sidebar.setObjectName("sidebar")
        sidebar.setFixedWidth(80)
        sidebar.setStyleSheet("""
            QFrame#sidebar {
                background-color: #252525;
                border-right: 1px solid #404040;
            }
        """)
        
        layout = QVBoxLayout(sidebar)
        layout.setContentsMargins(0, 20, 0, 20)
        layout.setSpacing(10)
        
        # Логотип
        logo_label = QLabel("🛡️")
        logo_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        logo_label.setStyleSheet("font-size: 28px; margin-bottom: 30px;")
        layout.addWidget(logo_label)
        
        # Кнопки навигации
        nav_buttons = [
            ("👁️", "Обзор", "dashboard", "Обзор сети"),
            ("🔍", "Сканер", "scanner", "Сканирование сети"),
            ("🎨", "Конструктор", "constructor", "Конструктор политик"),
            ("⚙️", "Генератор", "generator", "Генератор конфигураций"),
            ("✅", "Валидатор", "validator", "Валидация политик"),
            ("📊", "Отчеты", "reports", "Отчеты и аналитика"),
        ]
        
        self.nav_buttons = {}
        for icon, text, page_id, tooltip in nav_buttons:
            btn = QPushButton(icon)
            btn.setToolTip(tooltip)
            btn.setFixedSize(60, 60)
            btn.setCheckable(True)
            btn.setStyleSheet("""
                QPushButton {
                    font-size: 24px;
                    border: none;
                    border-radius: 8px;
                    background-color: transparent;
                }
                QPushButton:hover {
                    background-color: #404040;
                }
                QPushButton:checked {
                    background-color: #0B5394;
                }
            """)
            
            btn.clicked.connect(lambda checked, pid=page_id: self.show_page(pid))
            layout.addWidget(btn)
            self.nav_buttons[page_id] = btn
        
        # Разделитель
        layout.addSpacerItem(QSpacerItem(20, 40, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Expanding))
        
        # Кнопки внизу
        settings_btn = QPushButton("⚙️")
        settings_btn.setToolTip("Настройки")
        settings_btn.setFixedSize(60, 60)
        settings_btn.setCheckable(True)
        settings_btn.setStyleSheet("""
            QPushButton {
                font-size: 24px;
                border: none;
                border-radius: 8px;
                background-color: transparent;
            }
            QPushButton:hover {
                background-color: #404040;
            }
            QPushButton:checked {
                background-color: #0B5394;
            }
        """)
        settings_btn.clicked.connect(lambda: self.show_page('settings'))
        layout.addWidget(settings_btn)
        
        help_btn = QPushButton("❓")
        help_btn.setToolTip("Помощь")
        help_btn.setFixedSize(60, 60)
        help_btn.setStyleSheet("""
            QPushButton {
                font-size: 24px;
                border: none;
                border-radius: 8px;
                background-color: transparent;
            }
            QPushButton:hover {
                background-color: #404040;
            }
        """)
        help_btn.clicked.connect(self.show_help)
        layout.addWidget(help_btn)
        
        return sidebar
    
    def create_top_bar(self):
        """Создать верхнюю панель"""
        top_bar = QFrame()
        top_bar.setObjectName("topBar")
        top_bar.setFixedHeight(60)
        top_bar.setStyleSheet("""
            QFrame#topBar {
                background-color: #252525;
                border-bottom: 1px solid #404040;
            }
        """)
        
        layout = QHBoxLayout(top_bar)
        layout.setContentsMargins(20, 0, 20, 0)
        
        # Заголовок страницы
        self.page_title = QLabel("Обзор сети")
        self.page_title.setObjectName("pageTitle")
        self.page_title.setStyleSheet("""
            QLabel#pageTitle {
                font-size: 18px;
                font-weight: bold;
                color: #FFFFFF;
            }
        """)
        layout.addWidget(self.page_title)
        
        # Пространство
        layout.addSpacerItem(QSpacerItem(40, 20, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum))
        
        # Кнопки быстрых действий
        refresh_btn = QPushButton("🔄")
        refresh_btn.setToolTip("Обновить")
        refresh_btn.setFixedSize(40, 40)
        refresh_btn.setStyleSheet("""
            QPushButton {
                font-size: 18px;
                border: none;
                border-radius: 6px;
                background-color: #404040;
            }
            QPushButton:hover {
                background-color: #505050;
            }
        """)
        
        quick_action_btn = QPushButton("⚡")
        quick_action_btn.setToolTip("Быстрые действия")
        quick_action_btn.setFixedSize(40, 40)
        quick_action_btn.setStyleSheet("""
            QPushButton {
                font-size: 18px;
                border: none;
                border-radius: 6px;
                background-color: #0B5394;
            }
            QPushButton:hover {
                background-color: #3D85C6;
            }
        """)
        
        layout.addWidget(refresh_btn)
        layout.addWidget(quick_action_btn)
        
        return top_bar
    
    def show_page(self, page_id):
        """Показать страницу по ID"""
        # Сбрасываем все кнопки
        for btn in self.nav_buttons.values():
            btn.setChecked(False)
        
        # Активируем текущую кнопку
        if page_id in self.nav_buttons:
            self.nav_buttons[page_id].setChecked(True)
        
        # Меняем заголовок
        page_titles = {
            'dashboard': 'Обзор сети',
            'scanner': 'Сканер сети',
            'constructor': 'Конструктор политик',
            'generator': 'Генератор конфигураций',
            'validator': 'Валидация политик',
            'reports': 'Отчеты',
            'settings': 'Настройки',
        }
        
        if page_id in page_titles:
            self.page_title.setText(page_titles[page_id])
        
        # Показываем страницу
        if page_id in self.pages:
            self.content_stack.setCurrentWidget(self.pages[page_id])
    
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
        
        import_action = QAction("📥 Импорт...", self)
        import_action.triggered.connect(self.import_policy)
        
        export_action = QAction("📤 Экспорт...", self)
        export_action.triggered.connect(self.export_policy)
        
        exit_action = QAction("🚪 Выход", self)
        exit_action.setShortcut("Alt+F4")
        exit_action.triggered.connect(self.close)
        
        file_menu.addAction(new_action)
        file_menu.addAction(open_action)
        file_menu.addAction(save_action)
        file_menu.addSeparator()
        file_menu.addAction(import_action)
        file_menu.addAction(export_action)
        file_menu.addSeparator()
        file_menu.addAction(exit_action)
        
        # Меню "Вид"
        view_menu = menubar.addMenu("👁️ Вид")
        
        dashboard_action = QAction("👁️ Обзор сети", self)
        dashboard_action.setShortcut("Ctrl+1")
        dashboard_action.triggered.connect(lambda: self.show_page('dashboard'))
        
        scanner_action = QAction("🔍 Сканер", self)
        scanner_action.setShortcut("Ctrl+2")
        scanner_action.triggered.connect(lambda: self.show_page('scanner'))
        
        constructor_action = QAction("🎨 Конструктор", self)
        constructor_action.setShortcut("Ctrl+3")
        constructor_action.triggered.connect(lambda: self.show_page('constructor'))
        
        view_menu.addAction(dashboard_action)
        view_menu.addAction(scanner_action)
        view_menu.addAction(constructor_action)
        view_menu.addSeparator()
        
        fullscreen_action = QAction("🔲 Полный экран", self)
        fullscreen_action.setShortcut("F11")
        fullscreen_action.triggered.connect(self.toggle_fullscreen)
        
        view_menu.addAction(fullscreen_action)
        
        # Меню "Инструменты"
        tools_menu = menubar.addMenu("🔧 Инструменты")
        
        quick_scan_action = QAction("⚡ Быстрое сканирование", self)
        quick_scan_action.setShortcut("F5")
        quick_scan_action.triggered.connect(self.quick_scan)
        
        validate_action = QAction("✅ Проверить безопасность", self)
        validate_action.setShortcut("F9")
        validate_action.triggered.connect(self.validate_security)
        
        generate_action = QAction("⚙️ Сгенерировать конфигурацию", self)
        generate_action.setShortcut("F10")
        generate_action.triggered.connect(self.generate_config)
        
        tools_menu.addAction(quick_scan_action)
        tools_menu.addAction(validate_action)
        tools_menu.addAction(generate_action)
        
        # Меню "Справка"
        help_menu = menubar.addMenu("❓ Справка")
        
        documentation_action = QAction("📚 Документация", self)
        documentation_action.triggered.connect(self.show_documentation)
        
        about_action = QAction("ℹ️ О программе", self)
        about_action.triggered.connect(self.show_about)
        
        help_menu.addAction(documentation_action)
        help_menu.addAction(about_action)
    
    def create_toolbar(self):
        """Создать панель инструментов"""
        toolbar = self.addToolBar("Инструменты")
        toolbar.setMovable(False)
        toolbar.setIconSize(QSize(24, 24))
        
        # Кнопка сканирования
        scan_action = QAction("🔍", self)
        scan_action.setToolTip("Сканировать сеть")
        scan_action.triggered.connect(self.scan_network)
        toolbar.addAction(scan_action)
        
        toolbar.addSeparator()
        
        # Кнопка конструктора
        construct_action = QAction("🎨", self)
        construct_action.setToolTip("Конструктор политик")
        construct_action.triggered.connect(lambda: self.show_page('constructor'))
        toolbar.addAction(construct_action)
        
        # Кнопка валидации
        validate_action = QAction("✅", self)
        validate_action.setToolTip("Валидация")
        validate_action.triggered.connect(lambda: self.show_page('validator'))
        toolbar.addAction(validate_action)
        
        toolbar.addSeparator()
        
        # Кнопка экспорта
        export_action = QAction("📤", self)
        export_action.setToolTip("Экспорт")
        export_action.triggered.connect(self.export_config)
        toolbar.addAction(export_action)
        
        toolbar.addSeparator()
        
        # Кнопка настроек
        settings_action = QAction("⚙️", self)
        settings_action.setToolTip("Настройки")
        settings_action.triggered.connect(lambda: self.show_page('settings'))
        toolbar.addAction(settings_action)
    
    def create_statusbar(self):
        """Создать строку состояния"""
        self.statusbar = QStatusBar()
        self.setStatusBar(self.statusbar)
        
        # Левая часть: сообщения
        self.status_label = QLabel("Готов к работе")
        self.statusbar.addWidget(self.status_label, 1)
        
        # Правая часть: индикаторы
        network_label = QLabel("🌐 Сеть: онлайн")
        network_label.setStyleSheet("color: #93C47D;")
        self.statusbar.addPermanentWidget(network_label)
        
        memory_label = QLabel("💾 Память: 125/512 МБ")
        memory_label.setStyleSheet("color: #76A5AF; margin-left: 20px;")
        self.statusbar.addPermanentWidget(memory_label)
    
    def show_help(self):
        """Показать справку"""
        QMessageBox.information(self, "Справка", 
            "ZeroTrust Inspector - Визуализатор и валидатор Zero-Trust политик\n\n"
            "Используйте боковое меню для навигации:\n"
            "• 👁️ Обзор сети - дашборд и статистика\n"
            "• 🔍 Сканер - обнаружение устройств в сети\n"
            "• 🎨 Конструктор - создание политик безопасности\n"
            "• ⚙️ Генератор - создание конфигураций для роутеров\n"
            "• ✅ Валидатор - проверка настроенных правил\n"
            "• 📊 Отчеты - аналитика и отчеты\n\n"
            "Горячие клавиши:\n"
            "F5 - Быстрое сканирование\n"
            "F9 - Проверка безопасности\n"
            "F11 - Полный экран\n"
            "Ctrl+S - Сохранить политику")
    
    def toggle_fullscreen(self):
        """Переключить полноэкранный режим"""
        if self.isFullScreen():
            self.showNormal()
        else:
            self.showFullScreen()
    
    def quick_scan(self):
        """Быстрое сканирование"""
        self.status_label.setText("Сканирование сети...")
        QMessageBox.information(self, "Сканирование", "Запущено быстрое сканирование сети")
    
    def validate_security(self):
        """Проверить безопасность"""
        self.show_page('validator')
    
    def generate_config(self):
        """Сгенерировать конфигурацию"""
        self.show_page('generator')
    
    def scan_network(self):
        """Сканировать сеть"""
        self.show_page('scanner')
    
    def new_policy(self):
        """Создать новую политику"""
        reply = QMessageBox.question(self, "Новая политика", 
            "Создать новую политику безопасности?\nТекущие изменения будут потеряны.",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)
        
        if reply == QMessageBox.StandardButton.Yes:
            self.status_label.setText("Создана новая политика")
    
    def open_policy(self):
        """Открыть политику"""
        # Здесь будет диалог открытия файла
        self.status_label.setText("Открытие политики...")
    
    def save_policy(self):
        """Сохранить политику"""
        self.status_label.setText("Политика сохранена")
    
    def import_policy(self):
        """Импортировать политику"""
        QMessageBox.information(self, "Импорт", "Импорт политики")
    
    def export_policy(self):
        """Экспортировать политику"""
        QMessageBox.information(self, "Экспорт", "Экспорт политики")
    
    def export_config(self):
        """Экспортировать конфигурацию"""
        self.show_page('generator')
    
    def show_documentation(self):
        """Показать документацию"""
        QMessageBox.information(self, "Документация", 
            "Документация доступна по ссылке:\nhttps://github.com/casheshrimp/zero-trust/wiki")
    
    def show_about(self):
        """Показать информацию о программе"""
        QMessageBox.about(self, "О программе",
            "<h2>ZeroTrust Inspector v1.0.0</h2>"
            "<p><b>Визуализатор и валидатор Zero-Trust политик</b></p>"
            "<p>Для домашних сетей и малых офисов</p><hr>"
            "<p>Автор: CashShrimp</p>"
            "<p>Лицензия: MIT</p>"
            "<p>GitHub: github.com/casheshrimp/zero-trust</p>"
            "<p>Поддержка: zerotrust@example.com</p>")
