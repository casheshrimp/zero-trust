#!/usr/bin/env python3
"""
Упрощенный запуск ZeroTrust Inspector
"""

import sys
import os
from pathlib import Path

# Добавляем текущую директорию в PYTHONPATH
current_dir = Path(__file__).parent
sys.path.insert(0, str(current_dir))

def main():
    """Упрощенный запуск"""
    print("🚀 Запуск ZeroTrust Inspector...")
    
    # Создаем необходимые директории
    directories = ["logs", "configs", "exports", "backups", "assets"]
    for directory in directories:
        dir_path = Path(directory)
        dir_path.mkdir(parents=True, exist_ok=True)
        print(f"📁 Проверена папка: {directory}")
    
    # Проверяем и импортируем GUI модуль
    try:
        from src.gui.main_window import MainWindow
        from PyQt6.QtWidgets import QApplication
        
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
        print("\nВозможные решения:")
        print("1. Установите зависимости: pip install -r requirements.txt")
        print("2. Проверьте структуру файлов:")
        print("   - Файл src/gui/main_window.py должен существовать")
        print("   - В файле main_window.py должны быть правильные импорты")
        return 1
    except Exception as e:
        print(f"❌ Неожиданная ошибка: {e}")
        import traceback
        traceback.print_exc()
        return 1

if __name__ == "__main__":
    sys.exit(main())
