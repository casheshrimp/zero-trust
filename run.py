#!/usr/bin/env python3
"""
Точка входа для запуска приложения
Альтернатива main.py для простого запуска
"""

import sys
import os
from pathlib import Path

# Добавляем путь к src в sys.path
src_dir = Path(__file__).parent / "src"
sys.path.insert(0, str(src_dir))

# Проверяем зависимости
try:
    from PyQt6.QtWidgets import QApplication
    from gui.main_window import MainWindow
except ImportError as e:
    print(f"❌ Ошибка: Не удалось импортировать модули: {e}")
    print("Убедитесь, что установлены все зависимости:")
    print("pip install PyQt6 python-nmap jinja2")
    sys.exit(1)

def main():
    """Основная функция запуска"""
    app = QApplication(sys.argv)
    app.setApplicationName("ZeroTrust Inspector")
    app.setApplicationVersion("1.0.0")
    
    window = MainWindow()
    window.show()
    
    sys.exit(app.exec())

if __name__ == "__main__":
    main()
