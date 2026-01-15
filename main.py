#!/usr/bin/env python3
"""
ZeroTrust Inspector - Главный файл приложения с новым дизайном
"""

import sys
import os
import logging
from pathlib import Path

# Добавляем путь к src
sys.path.insert(0, str(Path(__file__).parent / "src"))

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

def show_splash_screen():
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

def main():
    """Главная функция приложения"""
    show_splash_screen()
    logger.info("=" * 60)
    logger.info("Запуск ZeroTrust Inspector с новым дизайном")
    logger.info("=" * 60)
    
    # Создаем необходимые директории
    directories = ["logs", "configs", "exports", "backups", "assets/icons"]
    for directory in directories:
        Path(directory).mkdir(parents=True, exist_ok=True)
    
    try:
        from PyQt6.QtWidgets import QApplication
        from PyQt6.QtCore import QTimer
        from src.gui.main_window import MainWindow
        
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
