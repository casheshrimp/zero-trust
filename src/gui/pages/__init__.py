"""
Страницы приложения
"""

from .dashboard import DashboardPage
from .scanner import ScannerPage
from .constructor import ConstructorPage
from .generator import GeneratorPage
from .validator import ValidatorPage
from .reports import ReportsPage
from .settings import SettingsPage

__all__ = [
    'DashboardPage',
    'ScannerPage',
    'ConstructorPage',
    'GeneratorPage',
    'ValidatorPage',
    'ReportsPage',
    'SettingsPage',
]
