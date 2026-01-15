"""
Модели данных приложения (упрощенная версия)
"""
from dataclasses import dataclass, field
from typing import List, Optional, Dict
from enum import Enum
from datetime import datetime

class ZoneType(Enum):
    TRUSTED = "trusted"
    IOT = "iot"
    GUEST = "guest"
    SERVER = "server"
    DMZ = "dmz"
    CUSTOM = "custom"

class DeviceType(Enum):
    COMPUTER = "computer"
    PHONE = "phone"
    IOT = "iot"
    PRINTER = "printer"
    ROUTER = "router"
    CAMERA = "camera"
    UNKNOWN = "unknown"

class ActionType(Enum):
    ALLOW = "allow"
    DENY = "deny"

@dataclass
class NetworkDevice:
    """Сетевое устройство"""
    ip_address: str
    mac_address: Optional[str] = None
    hostname: Optional[str] = None
    vendor: Optional[str] = None
    device_type: DeviceType = DeviceType.UNKNOWN
    open_ports: List[int] = field(default_factory=list)
    services: Dict[int, str] = field(default_factory=dict)
    
    def get_friendly_name(self):
        return self.hostname or self.ip_address

@dataclass
class SecurityZone:
    """Зона безопасности"""
    name: str
    zone_type: ZoneType
    devices: List[NetworkDevice] = field(default_factory=list)
    description: str = ""
    color: str = "#FFFFFF"
    
    @property
    def device_count(self):
        return len(self.devices)

@dataclass
class Rule:
    """Правило фильтрации"""
    source_zone: SecurityZone
    destination_zone: SecurityZone
    action: ActionType
    protocol: str = "any"
    port: Optional[int] = None
    description: str = ""

@dataclass
class NetworkPolicy:
    """Политика безопасности"""
    name: str
    zones: Dict[str, SecurityZone] = field(default_factory=dict)
    rules: List[Rule] = field(default_factory=list)
    description: str = ""
