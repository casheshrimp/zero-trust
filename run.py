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

def check_requirements():
    """Проверить наличие зависимостей"""
    try:
        import PyQt6
        print("✅ PyQt6 установлен")
    except ImportError:
        print("❌ PyQt6 не установлен")
        print("Установите: pip install PyQt6")
        return False
    
    try:
        import nmap
        print("✅ python-nmap установлен")
    except ImportError:
        print("❌ python-nmap не установлен")
        print("Установите: pip install python-nmap")
        return False
    
    try:
        import scapy
        print("✅ scapy установлен")
    except ImportError:
        print("❌ scapy не установлен")
        print("Установите: pip install scapy")
        return False
    
    return True

def main():
    """Упрощенный запуск"""
    print("🚀 Запуск ZeroTrust Inspector...")
    print("=" * 50)
    
    # Проверяем зависимости
    if not check_requirements():
        return 1
    
    # Создаем необходимые директории
    directories = ["logs", "configs", "exports", "backups", "assets"]
    for directory in directories:
        dir_path = Path(directory)
        dir_path.mkdir(parents=True, exist_ok=True)
        print(f"📁 Проверена папка: {directory}")
    
    # Импортируем и запускаем GUI
    try:
        from PyQt6.QtWidgets import QApplication
        from src.gui.main_window import MainWindow
        
        app = QApplication(sys.argv)
        app.setApplicationName("ZeroTrust Inspector")
        app.setApplicationVersion("1.0.0")
        
        window = MainWindow()
        window.show()
        
        print("\n✅ Приложение запущено успешно!")
        print("👆 Используйте кнопки в интерфейсе для работы")
        print("=" * 50)
        
        return app.exec()
        
    except ImportError as e:
        print(f"\n❌ Ошибка импорта: {e}")
        print("\nВозможные решения:")
        print("1. Установите все зависимости: pip install -r requirements.txt")
        print("2. Проверьте структуру файлов проекта")
        print("3. Убедитесь, что файл src/gui/main_window.py существует")
        return 1
    except Exception as e:
        print(f"\n❌ Неожиданная ошибка: {e}")
        import traceback
        traceback.print_exc()
        return 1

if __name__ == "__main__":
    sys.exit(main())
