"""
Упрощенные модели данных для ZeroTrust Inspector
"""

from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import List, Dict, Optional

class ZoneType(Enum):
    """Типы зон безопасности"""
    TRUSTED = "trusted"
    IOT = "iot"
    GUEST = "guest"
    SERVER = "server"
    DMZ = "dmz"
    CUSTOM = "custom"

class DeviceType(Enum):
    """Типы сетевых устройств"""
    ROUTER = "router"
    COMPUTER = "computer"
    PHONE = "phone"
    IOT = "iot"
    PRINTER = "printer"
    CAMERA = "camera"
    UNKNOWN = "unknown"

class ActionType(Enum):
    """Типы действий для правил"""
    ALLOW = "allow"
    DENY = "deny"

@dataclass
class NetworkDevice:
    """Сетевое устройство"""
    ip_address: str
    mac_address: Optional[str] = None
    hostname: Optional[str] = None
    device_type: DeviceType = DeviceType.UNKNOWN
    vendor: Optional[str] = None
    
    def to_dict(self) -> Dict:
        """Конвертировать в словарь"""
        return {
            'ip_address': self.ip_address,
            'mac_address': self.mac_address,
            'hostname': self.hostname,
            'device_type': self.device_type.value,
            'vendor': self.vendor,
        }

@dataclass
class SecurityZone:
    """Зона безопасности"""
    name: str
    zone_type: ZoneType
    description: str = ""
    devices: List[NetworkDevice] = field(default_factory=list)
    
    def add_device(self, device: NetworkDevice):
        """Добавить устройство в зону"""
        self.devices.append(device)
    
    @property
    def device_count(self) -> int:
        """Количество устройств в зоне"""
        return len(self.devices)
    
    def to_dict(self) -> Dict:
        """Конвертировать в словарь"""
        return {
            'name': self.name,
            'zone_type': self.zone_type.value,
            'description': self.description,
            'devices': [device.to_dict() for device in self.devices],
        }

@dataclass
class Rule:
    """Правило безопасности"""
    source_zone: SecurityZone
    destination_zone: SecurityZone
    action: ActionType
    description: str = ""
    
    def to_dict(self) -> Dict:
        """Конвертировать в словарь"""
        return {
            'source_zone': self.source_zone.name,
            'destination_zone': self.destination_zone.name,
            'action': self.action.value,
            'description': self.description,
        }

@dataclass
class NetworkPolicy:
    """Политика безопасности сети"""
    name: str
    description: str = ""
    zones: Dict[str, SecurityZone] = field(default_factory=dict)
    rules: List[Rule] = field(default_factory=list)
    created_at: datetime = field(default_factory=datetime.now)
    
    def add_zone(self, zone: SecurityZone):
        """Добавить зону в политику"""
        self.zones[zone.name] = zone
    
    def add_rule(self, rule: Rule):
        """Добавить правило в политику"""
        self.rules.append(rule)
    
    def to_dict(self) -> Dict:
        """Конвертировать в словарь"""
        return {
            'name': self.name,
            'description': self.description,
            'zones': {name: zone.to_dict() for name, zone in self.zones.items()},
            'rules': [rule.to_dict() for rule in self.rules],
            'created_at': self.created_at.isoformat(),
        }
