#!/usr/bin/env python3
"""
Альтернативный запуск ZeroTrust Inspector
"""

import sys
import os
from pathlib import Path

# Добавляем пути для импортов
sys.path.insert(0, str(Path(__file__).parent))

# Запускаем основной файл
if __name__ == "__main__":
    from main import main
    sys.exit(main())
