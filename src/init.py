"""
ZeroTrust Inspector - Визуализатор и валидатор Zero-Trust политик
"""

__version__ = "1.0.0"
__author__ = "Ваше Имя"
__email__ = "your.email@example.com"

from .core.models import NetworkDevice, SecurityZone, NetworkPolicy
from .scanner.network_scanner import NetworkScanner
from .gui.main_window import MainWindow

__all__ = [
    'NetworkDevice',
    'SecurityZone', 
    'NetworkPolicy',
    'NetworkScanner',
    'MainWindow',
]
