#!/usr/bin/env python3
"""
Скрипт для настройки проекта
"""
import os
import sys
from pathlib import Path

def setup_project():
    """Настроить структуру проекта"""
    print("🔧 Настройка ZeroTrust Inspector...")
    
    # Создаем структуру
    folders = [
        "logs", "configs", "exports", "backups", "assets",
        "src", "src/core", "src/gui", "src/scanner",
        "src/engine", "src/validation", "src/utils",
        "src/gui/components"
    ]
    
    for folder in folders:
        Path(folder).mkdir(parents=True, exist_ok=True)
        print(f"📁 Создана папка: {folder}")
    
    # Создаем необходимые файлы
    files_content = {
        "src/__init__.py": "# Package\n__version__ = '1.0.0'",
        "src/core/__init__.py": "from .models import NetworkDevice, SecurityZone, NetworkPolicy",
        "src/gui/__init__.py": "from .main_window import MainWindow",
    }
    
    for filepath, content in files_content.items():
        if not Path(filepath).exists():
            Path(filepath).write_text(content, encoding='utf-8')
            print(f"📄 Создан файл: {filepath}")
    
    print("\n✅ Проект настроен!")
    print("📋 Запустите: python main.py")

if __name__ == "__main__":
    setup_project()
