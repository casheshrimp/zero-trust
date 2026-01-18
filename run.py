#!/usr/bin/env python3
"""
Упрощенный запуск ZeroTrust Inspector
"""

import sys
import os
from pathlib import Path

# Добавляем текущую директорию в PYTHONPATH
sys.path.insert(0, str(Path(__file__).parent))

def main():
    """Упрощенный запуск"""
    print("🚀 Запуск ZeroTrust Inspector...")
    
    # Проверяем зависимости
    try:
        from PyQt6.QtWidgets import QApplication
        print("✅ PyQt6 установлен")
    except ImportError:
        print("❌ PyQt6 не установлен")
        print("Установите: pip install PyQt6")
        return 1
    
    try:
        import nmap
        print("✅ python-nmap установлен")
    except ImportError:
        print("❌ python-nmap не установлен")
        print("Установите: pip install python-nmap")
        return 1
    
    # Создаем необходимые директории
    directories = ["logs", "configs", "exports", "backups", "assets"]
    for directory in directories:
        Path(directory).mkdir(parents=True, exist_ok=True)
        print(f"📁 Создана папка: {directory}")
    
    # Импортируем и запускаем GUI
    try:
        from src.gui.main_window import MainWindow
        
        app = QApplication(sys.argv)
        app.setApplicationName("ZeroTrust Inspector")
        app.setApplicationVersion("1.0.0")
        
        window = MainWindow()
        window.show()
        
        print("✅ Приложение запущено успешно!")
        print("👆 Используйте кнопки в интерфейсе для работы")
        
        return app.exec()
        
    except ImportError as e:
        print(f"❌ Ошибка импорта: {e}")
        print("Проверьте структуру файлов:")
        print("1. Убедитесь, что файл src/gui/main_window.py существует")
        print("2. Убедитесь, что все импорты используют абсолютные пути")
        return 1
    except Exception as e:
        print(f"❌ Неожиданная ошибка: {e}")
        return 1

if __name__ == "__main__":
    sys.exit(main())
