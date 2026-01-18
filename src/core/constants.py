"""
Константы приложения
"""

from pathlib import Path

# Пути
PROJECT_ROOT = Path(__file__).parent.parent.parent
SRC_DIR = PROJECT_ROOT / "src"
ASSETS_DIR = PROJECT_ROOT / "assets"
LOGS_DIR = PROJECT_ROOT / "logs"
CONFIGS_DIR = PROJECT_ROOT / "configs"
EXPORTS_DIR = PROJECT_ROOT / "exports"
BACKUPS_DIR = PROJECT_ROOT / "backups"

# Порт по умолчанию для сканирования
DEFAULT_SCAN_PORTS = [22, 23, 80, 443, 3389, 8080, 8443, 9100, 515, 631, 21, 25, 53, 67, 68, 69]

# Настройки безопасности
DEFAULT_SECURITY_LEVELS = {
    "trusted": 5,
    "dmz": 3,
    "iot": 2,
    "guest": 1,
    "server": 4,
    "custom": 3
}

# Цвета для зон (RGB)
ZONE_COLORS = {
    "trusted": (76, 175, 80),      # Зеленый
    "dmz": (255, 193, 7),          # Желтый
    "iot": (156, 39, 176),         # Фиолетовый
    "guest": (33, 150, 243),       # Синий
    "server": (244, 67, 54),       # Красный
    "custom": (158, 158, 158)      # Серый
}

# Иконки для типов устройств
DEVICE_ICONS = {
    "router": "router.svg",
    "switch": "switch.svg",
    "computer": "computer.svg",
    "phone": "phone.svg",
    "tablet": "tablet.svg",
    "iot": "iot.svg",
    "printer": "printer.svg",
    "camera": "camera.svg",
    "server": "server.svg",
    "unknown": "unknown.svg"
}

# Настройки валидации
VALIDATION_TIMEOUT = 5  # секунд
MAX_CONCURRENT_TESTS = 10

# Версия приложения
APP_VERSION = "1.0.0"
APP_NAME = "ZeroTrust Inspector"
