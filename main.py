#!/usr/bin/env python3
"""
ZeroTrust Inspector - Главный файл приложения
"""

import sys
import logging
from pathlib import Path

# Инициализируем логирование
def setup_logging():
    """Настройка системы логирования"""
    log_dir = Path("logs")
    log_dir.mkdir(exist_ok=True)
    
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler(log_dir / 'zerotrust.log', encoding='utf-8'),
            logging.StreamHandler(sys.stdout)
        ]
    )
    
    return logging.getLogger(__name__)

logger = setup_logging()

def check_dependencies():
    """Проверка наличия необходимых зависимостей"""
    missing_deps = []
    
    try:
        import PyQt6
    except ImportError:
        missing_deps.append("PyQt6")
    
    if missing_deps:
        logger.error("Отсутствуют необходимые зависимости:")
        for dep in missing_deps:
            logger.error(f"  - {dep}")
        
        print("\n❌ ОШИБКА: Отсутствуют необходимые библиотеки")
        print("Установите их командой:")
        print("pip install PyQt6")
        return False
    
    return True

def show_splash_screen():
    """Показать заставку при запуске"""
    splash = """
    ╔══════════════════════════════════════════════════════╗
    ║                                                      ║
    ║         ZERO TRUST INSPECTOR v1.0.0                  ║
    ║                                                      ║
    ║    Визуализатор и валидатор Zero-Trust политик       ║
    ║      для домашних сетей и малых офисов               ║
    ║                                                      ║
    ║                  [ Загрузка... ]                     ║
    ║                                                      ║
    ╚══════════════════════════════════════════════════════╝
    """
    print(splash)

def handle_uncaught_exceptions(exc_type, exc_value, exc_traceback):
    """Обработчик неперехваченных исключений"""
    logger.critical("Неперехваченное исключение:", exc_info=(exc_type, exc_value, exc_traceback))
    
    try:
        from PyQt6.QtWidgets import QMessageBox, QApplication
        
        error_msg = f"""
        ⚠️ КРИТИЧЕСКАЯ ОШИБКА
        
        Тип: {exc_type.__name__}
        Сообщение: {str(exc_value)}
        
        Приложение будет закрыто.
        Подробности в файле logs/zerotrust.log
        """
        
        app = QApplication.instance()
        if app:
            QMessageBox.critical(None, "Критическая ошибка", error_msg)
    except:
        pass
    
    sys.exit(1)

def main():
    """Главная функция приложения"""
    
    # Устанавливаем обработчик неперехваченных исключений
    sys.excepthook = handle_uncaught_exceptions
    
    show_splash_screen()
    logger.info("=" * 60)
    logger.info("Запуск ZeroTrust Inspector")
    logger.info("=" * 60)
    
    # Проверяем зависимости
    if not check_dependencies():
        sys.exit(1)
    
    # Создаем необходимые директории
    directories = ["logs", "configs", "exports", "backups", "assets"]
    for directory in directories:
        Path(directory).mkdir(parents=True, exist_ok=True)
        logger.debug(f"Проверена директория: {directory}")
    
    try:
        # Импортируем здесь, чтобы логирование уже было настроено
        from PyQt6.QtWidgets import QApplication
        from PyQt6.QtCore import QTimer
        
        # Пробуем импортировать главное окно
        try:
            from src.gui.main_window import MainWindow
            logger.info("GUI модуль успешно импортирован")
        except ImportError as e:
            logger.warning(f"Не удалось импортировать MainWindow: {e}")
            # Создаем простую версию
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
            
                    label = QLabel("""
                    <h1>ZeroTrust Inspector v1.0.0</h1>
                    <p>Визуализатор и валидатор Zero-Trust политик</p>
                    <p>Для домашних сетей и малых офисов</p>
                    <hr>
                    <p>✅ Приложение успешно запущено!</p>
                    <p>⚠️ Основной GUI модуль недоступен</p>
                    <p>Проверьте наличие файла src/gui/main_window.py</p>
                    """)
                    label.setAlignment(Qt.AlignmentFlag.AlignCenter)
                    layout.addWidget(label)
        
        logger.info("Инициализация графического интерфейса...")
        
        # Создаем QApplication
        app = QApplication(sys.argv)
        app.setApplicationName("ZeroTrust Inspector")
        app.setApplicationVersion("1.0.0")
        app.setOrganizationName("ZeroTrust Project")
        
        # Создаем главное окно
        logger.info("Создание главного окна...")
        window = MainWindow()
        
        # Показываем окно с небольшой задержкой для плавности
        QTimer.singleShot(100, window.show)
        
        logger.info("Приложение успешно запущено")
        
        # Запускаем основной цикл
        return_code = app.exec()
        
        logger.info(f"Приложение завершено с кодом: {return_code}")
        return return_code
        
    except Exception as e:
        logger.error(f"Неожиданная ошибка при запуске: {e}", exc_info=True)
        print(f"\n❌ КРИТИЧЕСКАЯ ОШИБКА: {e}")
        print("Подробности в файле logs/zerotrust.log")
        return 1

if __name__ == "__main__":
    sys.exit(main())
