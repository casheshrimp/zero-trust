"""
Константы приложения
"""

import os
from pathlib import Path

# Пути
PROJECT_ROOT = Path(__file__).parent.parent.parent
ASSETS_DIR = PROJECT_ROOT / "assets"
CONFIGS_DIR = PROJECT_ROOT / "configs"
LOGS_DIR = PROJECT_ROOT / "logs"
EXPORTS_DIR = PROJECT_ROOT / "exports"
BACKUPS_DIR = PROJECT_ROOT / "backups"
TEMPLATES_DIR = PROJECT_ROOT / "src" / "engine" / "templates"

# Цвета зон (в формате HEX)
ZONE_COLORS = {
    "trusted": "#90EE90",    # Светло-зеленый
    "iot": "#FFFF99",        # Светло-желтый
    "guest": "#D3D3D3",      # Светло-серый
    "server": "#ADD8E6",     # Светло-голубой
    "dmz": "#FFB6C1",        # Светло-розовый
    "custom": "#E6E6FA",     # Лавандовый
}

# Иконки устройств (можно заменить на пути к файлам)
DEVICE_ICONS = {
    "computer": "💻",
    "phone": "📱",
    "tablet": "📱",
    "iot": "💡",
    "printer": "🖨️",
    "router": "🌐",
    "switch": "🔌",
    "camera": "📷",
    "unknown": "❓",
}

# Порты для быстрого сканирования
COMMON_PORTS = [
    21,    # FTP
    22,    # SSH
    23,    # Telnet
    25,    # SMTP
    53,    # DNS
    80,    # HTTP
    110,   # POP3
    123,   # NTP
    143,   # IMAP
    443,   # HTTPS
    445,   # SMB
    993,   # IMAPS
    995,   # POP3S
    1433,  # MSSQL
    3306,  # MySQL
    3389,  # RDP
    5432,  # PostgreSQL
    5900,  # VNC
    8080,  # HTTP-alt
    9100,  # Printer
]

# Максимальное количество устройств в сети
MAX_DEVICES = 254

# Время ожидания для сетевых операций (в секундах)
NETWORK_TIMEOUT = 5
SCAN_TIMEOUT = 30

# Версия приложения
APP_VERSION = "1.0.0"
APP_NAME = "ZeroTrust Inspector"
ORGANIZATION_NAME = "ZeroTrust Project"

# Настройки по умолчанию
DEFAULT_SETTINGS = {
    "scan_network": "192.168.1.0/24",
    "scan_speed": "normal",  # slow, normal, fast
    "auto_classify": True,
    "theme": "dark",
    "language": "ru",
    "auto_save": True,
    "backup_enabled": True,
    "notifications": True,
}
