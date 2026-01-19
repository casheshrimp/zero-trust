#!/usr/bin/env python3
"""
Проверка структуры проекта ZeroTrust Inspector
"""

import sys
from pathlib import Path

def check_project_structure():
    """Проверить структуру проекта"""
    print("🔍 Проверка структуры проекта ZeroTrust Inspector...")
    
    required_files = [
        "main.py",
        "run_app.py",
        "requirements.txt",
        "README.md",
    ]
    
    required_dirs = [
        "src/__init__.py",
        "src/core/__init__.py",
        "src/core/models.py",
        "src/core/exceptions.py",
        "src/gui/__init__.py",
        "src/gui/main_window.py",
        "logs/",
        "configs/",
        "exports/",
        "backups/",
        "assets/",
    ]
    
    all_ok = True
    
    print("\n📁 Проверка основных файлов:")
    for file in required_files:
        if Path(file).exists():
            print(f"  ✓ {file}")
        else:
            print(f"  ✗ {file} - ОТСУТСТВУЕТ!")
            all_ok = False
    
    print("\n📁 Проверка структуры папок:")
    for item in required_dirs:
        if item.endswith('/'):
            # Это папка
            if Path(item).exists():
                print(f"  ✓ Папка {item}")
            else:
                print(f"  ✗ Папка {item} - ОТСУТСТВУЕТ!")
                all_ok = False
        else:
            # Это файл
            if Path(item).exists():
                print(f"  ✓ Файл {item}")
            else:
                print(f"  ✗ Файл {item} - ОТСУТСТВУЕТ!")
                all_ok = False
    
    # Проверка импортов
    print("\n🔧 Проверка импортов в main_window.py:")
    try:
        with open("src/gui/main_window.py", "r", encoding="utf-8") as f:
            content = f.read()
            if "DeviceType" in content and "device_type.value" in content:
                print("  ✓ Импорты DeviceType настроены правильно")
            else:
                print("  ⚠ Возможные проблемы с импортами DeviceType")
    except Exception as e:
        print(f"  ✗ Не удалось проверить main_window.py: {e}")
        all_ok = False
    
    if all_ok:
        print("\n✅ Структура проекта в порядке!")
        print("\n📋 Инструкция по запуску:")
        print("1. Установите зависимости: pip install -r requirements.txt")
        print("2. Запустите приложение: python run_app.py")
        print("3. Или используйте: python main.py")
        return 0
    else:
        print("\n❌ Обнаружены проблемы со структурой проекта!")
        print("\n🛠 Исправьте следующие проблемы:")
        print("1. Создайте отсутствующие файлы и папки")
        print("2. Проверьте структуру согласно README.md")
        return 1

if __name__ == "__main__":
    sys.exit(check_project_structure())
