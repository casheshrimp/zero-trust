#!/usr/bin/env python3
"""
ZeroTrust Inspector - Главный файл приложения
Визуализатор и валидатор Zero-Trust политик для домашних сетей и малых офисов
"""

import sys
import os
import logging
from pathlib import Path

# Добавляем путь к src в sys.path для корректного импорта
current_dir = Path(__file__).parent
src_dir = current_dir / "src"
sys.path.insert(0, str(src_dir))

# Инициализируем логирование ДО импорта модулей
def setup_logging():
    """Настройка системы логирования"""
    log_dir = current_dir / "logs"
    log_dir.mkdir(exist_ok=True)
    
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler(log_dir / 'zerotrust.log', encoding='utf-8'),
            logging.StreamHandler(sys.stdout)
        ]
    )
    
    # Уменьшаем уровень логирования для некоторых библиотек
    logging.getLogger('PyQt6').setLevel(logging.WARNING)
    logging.getLogger('nmap').setLevel(logging.WARNING)
    
    return logging.getLogger(__name__)

logger = setup_logging()

def check_dependencies():
    """Проверка наличия необходимых зависимостей"""
    missing_deps = []
    
    try:
        import PyQt6
    except ImportError:
        missing_deps.append("PyQt6 - библиотека для графического интерфейса")
    
    try:
        import nmap
    except ImportError:
        missing_deps.append("python-nmap - для сканирования сети")
    
    try:
        import jinja2
    except ImportError:
        missing_deps.append("Jinja2 - для генерации конфигураций")
    
    if missing_deps:
        logger.error("Отсутствуют необходимые зависимости:")
        for dep in missing_deps:
            logger.error(f"  - {dep}")
        
        print("\n❌ ОШИБКА: Отсутствуют необходимые библиотеки")
        print("Установите их командой:")
        print("pip install PyQt6 python-nmap jinja2 scapy psutil")
        return False
    
    return True

def check_permissions():
    """Проверка необходимых прав доступа"""
    if os.name == 'posix' and os.geteuid() != 0:
        logger.warning("Приложение запущено без прав администратора.")
        logger.warning("Некоторые функции сканирования могут быть ограничены.")
        return False
    return True

def create_necessary_directories():
    """Создание необходимых директорий"""
    directories = [
        current_dir / "logs",
        current_dir / "configs",
        current_dir / "exports",
        current_dir / "backups",
        current_dir / "assets" / "icons",
        current_dir / "src" / "engine" / "templates",
    ]
    
    for directory in directories:
        directory.mkdir(parents=True, exist_ok=True)
        logger.debug(f"Проверена директория: {directory}")

def create_default_templates():
    """Создание шаблонов по умолчанию, если их нет"""
    templates_dir = current_dir / "src" / "engine" / "templates"
    
    # Шаблон для OpenWrt
    openwrt_template = templates_dir / "openwrt.conf.j2"
    if not openwrt_template.exists():
        openwrt_template.write_text("""# ZeroTrust Inspector - Конфигурация для OpenWrt
# Сгенерировано: {{ timestamp }}

config defaults
    option syn_flood '1'
    option input 'ACCEPT'
    option output 'ACCEPT'
    option forward 'REJECT'

{% for zone in zones %}
config zone
    option name '{{ zone.name }}'
    list network 'lan'
    option input 'ACCEPT'
    option output 'ACCEPT'
    option forward 'ACCEPT'
    option masq '1'
{% endfor %}

{% for rule in rules %}
config rule
    option name '{{ rule.name }}'
    option src '{{ rule.src_zone }}'
    option dest '{{ rule.dst_zone }}'
    option proto '{{ rule.proto|default('all') }}'
    option dest_port '{{ rule.port|default('') }}'
    option target '{{ rule.action|upper }}'
{% endfor %}
""", encoding='utf-8')
        logger.info("Создан шаблон для OpenWrt")

def show_splash_screen():
    """Показать заставку при запуске"""
    splash = """
    ╔══════════════════════════════════════════════════════╗
    ║                                                      ║
    ║         ZERO TRUST INSPECTOR v1.0.0                 ║
    ║                                                      ║
    ║    Визуализатор и валидатор Zero-Trust политик      ║
    ║      для домашних сетей и малых офисов              ║
    ║                                                      ║
    ║                  [ Загрузка... ]                    ║
    ║                                                      ║
    ╚══════════════════════════════════════════════════════╝
    """
    print(splash)

def check_application_updates():
    """Проверить наличие обновлений приложения"""
    # В будущем можно добавить проверку через GitHub API
    return {
        'update_available': False,
        'latest_version': '1.0.0',
        'current_version': '1.0.0'
    }

def setup_application_style():
    """Настройка стиля приложения"""
    from PyQt6.QtGui import QFont, QPalette, QColor
    from PyQt6.QtCore import Qt
    
    # Установка темной темы по умолчанию
    palette = QPalette()
    palette.setColor(QPalette.ColorRole.Window, QColor(53, 53, 53))
    palette.setColor(QPalette.ColorRole.WindowText, Qt.GlobalColor.white)
    palette.setColor(QPalette.ColorRole.Base, QColor(25, 25, 25))
    palette.setColor(QPalette.ColorRole.AlternateBase, QColor(53, 53, 53))
    palette.setColor(QPalette.ColorRole.ToolTipBase, Qt.GlobalColor.black)
    palette.setColor(QPalette.ColorRole.ToolTipText, Qt.GlobalColor.white)
    palette.setColor(QPalette.ColorRole.Text, Qt.GlobalColor.white)
    palette.setColor(QPalette.ColorRole.Button, QColor(53, 53, 53))
    palette.setColor(QPalette.ColorRole.ButtonText, Qt.GlobalColor.white)
    palette.setColor(QPalette.ColorRole.BrightText, Qt.GlobalColor.red)
    palette.setColor(QPalette.ColorRole.Link, QColor(42, 130, 218))
    palette.setColor(QPalette.ColorRole.Highlight, QColor(42, 130, 218))
    palette.setColor(QPalette.ColorRole.HighlightedText, Qt.GlobalColor.black)
    
    return palette

def handle_uncaught_exceptions(exc_type, exc_value, exc_traceback):
    """Обработчик неперехваченных исключений"""
    logger.critical("Неперехваченное исключение:", exc_info=(exc_type, exc_value, exc_traceback))
    
    from PyQt6.QtWidgets import QMessageBox, QApplication
    import traceback
    
    # Создаем сообщение об ошибке
    error_msg = f"""
    ⚠️ КРИТИЧЕСКАЯ ОШИБКА
    
    Тип: {exc_type.__name__}
    Сообщение: {str(exc_value)}
    
    Приложение будет закрыто.
    Подробности в файле logs/zerotrust.log
    """
    
    # Показываем сообщение, если есть QApplication
    app = QApplication.instance()
    if app:
        QMessageBox.critical(None, "Критическая ошибка", error_msg)
    
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
    
    # Проверяем права доступа (предупреждение)
    check_permissions()
    
    # Создаем необходимые директории
    create_necessary_directories()
    
    # Создаем шаблоны по умолчанию
    create_default_templates()
    
    # Проверяем обновления
    update_info = check_application_updates()
    if update_info['update_available']:
        logger.info(f"Доступно обновление: {update_info['latest_version']}")
    
    try:
        # Импортируем здесь, чтобы логирование уже было настроено
        from PyQt6.QtWidgets import QApplication
        from PyQt6.QtCore import QTimer
        from src.gui.main_window import MainWindow
        
        logger.info("Инициализация графического интерфейса...")
        
        # Создаем QApplication
        app = QApplication(sys.argv)
        app.setApplicationName("ZeroTrust Inspector")
        app.setApplicationVersion("1.0.0")
        app.setOrganizationName("ZeroTrust Project")
        
        # Устанавливаем стиль
        palette = setup_application_style()
        app.setPalette(palette)
        app.setStyle('Fusion')
        
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
        
    except ImportError as e:
        logger.error(f"Ошибка импорта модулей: {e}")
        print(f"\n❌ ОШИБКА: Не удалось импортировать модули: {e}")
        print("Убедитесь, что все зависимости установлены правильно.")
        return 1
        
    except Exception as e:
        logger.error(f"Неожиданная ошибка при запуске: {e}", exc_info=True)
        print(f"\n❌ КРИТИЧЕСКАЯ ОШИБКА: {e}")
        print("Подробности в файле logs/zerotrust.log")
        return 1

def run_cli_mode():
    """Запуск в режиме командной строки (для автоматизации)"""
    import argparse
    
    parser = argparse.ArgumentParser(description='ZeroTrust Inspector - CLI Mode')
    parser.add_argument('--scan', action='store_true', help='Сканировать сеть')
    parser.add_argument('--export', type=str, help='Экспортировать конфигурацию')
    parser.add_argument('--validate', action='store_true', help='Проверить политики')
    
    args = parser.parse_args()
    
    if args.scan:
        print("Режим CLI: сканирование сети...")
        # Здесь будет код для сканирования
        pass
    
    logger.info("Завершение работы в CLI режиме")

if __name__ == "__main__":
    # Если есть аргументы командной строки - запускаем CLI режим
    if len(sys.argv) > 1:
        run_cli_mode()
    else:
        # Обычный запуск с GUI
        sys.exit(main())
