#!/usr/bin/env python3
"""
Скрипт настройки ZeroTrust Inspector
"""

import os
import sys
from pathlib import Path

def create_structure():
    """Создать структуру папок и файлов"""
    print("🔧 Настройка ZeroTrust Inspector...")
    
    # Создаем папки
    folders = [
        "logs", "configs", "exports", "backups",
        "assets", "assets/icons",
        "src", "src/core", "src/scanner", "src/gui",
        "src/gui/components", "src/engine", "src/engine/templates",
        "src/validation", "src/utils"
    ]
    
    for folder in folders:
        Path(folder).mkdir(parents=True, exist_ok=True)
        print(f"📁 Создана папка: {folder}")
    
    # Создаем файлы __init__.py
    init_files = [
        "src/__init__.py",
        "src/core/__init__.py",
        "src/scanner/__init__.py",
        "src/gui/__init__.py",
        "src/engine/__init__.py",
        "src/validation/__init__.py",
        "src/utils/__init__.py",
        "src/gui/components/__init__.py"
    ]
    
    for file in init_files:
        if not Path(file).exists():
            with open(file, 'w', encoding='utf-8') as f:
                f.write("# Package initialization\n")
            print(f"📄 Создан файл: {file}")
    
    # Создаем основные файлы если их нет
    if not Path("src/gui/main_window.py").exists():
        with open("src/gui/main_window.py", 'w', encoding='utf-8') as f:
            f.write("""
from PyQt6.QtWidgets import QMainWindow, QLabel
from PyQt6.QtCore import Qt

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("ZeroTrust Inspector")
        self.setGeometry(100, 100, 800, 600)
        label = QLabel("ZeroTrust Inspector успешно запущен!")
        label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.setCentralWidget(label)
""")
        print("📄 Создан файл: src/gui/main_window.py")
    
    print("\n✅ Структура проекта создана!")
    print("\n📋 Следующие шаги:")
    print("1. Установите зависимости: pip install PyQt6 python-nmap jinja2")
    print("2. Запустите приложение: python main.py")
    print("3. Проверьте установку: python check_installation.py")

if __name__ == "__main__":
    create_structure()
