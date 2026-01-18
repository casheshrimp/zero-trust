"""
Модели данных для ZeroTrust Inspector
"""

from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import List, Dict, Optional, Set
from ipaddress import IPv4Address, IPv4Network

class ZoneType(Enum):
    """Типы зон безопасности"""
    TRUSTED = "trusted"
    DMZ = "dmz"
    IOT = "iot"
    GUEST = "guest"
    SERVER = "server"
    CUSTOM = "custom"

class DeviceType(Enum):
    """Типы сетевых устройств"""
    ROUTER = "router"
    SWITCH = "switch"
    COMPUTER = "computer"
    PHONE = "phone"
    TABLET = "tablet"
    IOT = "iot"
    PRINTER = "printer"
    CAMERA = "camera"
    SERVER = "server"
    UNKNOWN = "unknown"

class ActionType(Enum):
    """Типы действий для правил"""
    ALLOW = "allow"
    DENY = "deny"
    INSPECT = "inspect"
    LOG = "log"

@dataclass
class NetworkDevice:
    """Сетевое устройство"""
    ip_address: str
    mac_address: Optional[str] = None
    hostname: Optional[str] = None
    device_type: DeviceType = DeviceType.UNKNOWN
    vendor: Optional[str] = None
    model: Optional[str] = None
    os: Optional[str] = None
    open_ports: List[int] = field(default_factory=list)
    vulnerabilities: List[str] = field(default_factory=list)
    first_seen: datetime = field(default_factory=datetime.now)
    last_seen: datetime = field(default_factory=datetime.now)
    risk_score: float = 0.0
    
    def to_dict(self) -> Dict:
        """Конвертировать в словарь"""
        return {
            'ip_address': self.ip_address,
            'mac_address': self.mac_address,
            'hostname': self.hostname,
            'device_type': self.device_type.value,
            'vendor': self.vendor,
            'model': self.model,
            'os': self.os,
            'open_ports': self.open_ports,
            'vulnerabilities': self.vulnerabilities,
            'first_seen': self.first_seen.isoformat(),
            'last_seen': self.last_seen.isoformat(),
            'risk_score': self.risk_score
        }
    
    @classmethod
    def from_dict(cls, data: Dict) -> 'NetworkDevice':
        """Создать из словаря"""
        return cls(
            ip_address=data['ip_address'],
            mac_address=data.get('mac_address'),
            hostname=data.get('hostname'),
            device_type=DeviceType(data.get('device_type', 'unknown')),
            vendor=data.get('vendor'),
            model=data.get('model'),
            os=data.get('os'),
            open_ports=data.get('open_ports', []),
            vulnerabilities=data.get('vulnerabilities', []),
            first_seen=datetime.fromisoformat(data.get('first_seen', datetime.now().isoformat())),
            last_seen=datetime.fromisoformat(data.get('last_seen', datetime.now().isoformat())),
            risk_score=data.get('risk_score', 0.0)
        )

@dataclass
class SecurityZone:
    """Зона безопасности"""
    name: str
    zone_type: ZoneType
    description: str = ""
    network_range: Optional[str] = None
    devices: List[NetworkDevice] = field(default_factory=list)
    allowed_services: List[str] = field(default_factory=list)
    security_level: int = 3  # 1-5, где 5 самый высокий
    
    def add_device(self, device: NetworkDevice):
        """Добавить устройство в зону"""
        self.devices.append(device)
    
    def remove_device(self, device_ip: str) -> bool:
        """Удалить устройство из зоны"""
        for i, device in enumerate(self.devices):
            if device.ip_address == device_ip:
                self.devices.pop(i)
                return True
        return False
    
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
            'network_range': self.network_range,
            'devices': [device.to_dict() for device in self.devices],
            'allowed_services': self.allowed_services,
            'security_level': self.security_level
        }

@dataclass
class Rule:
    """Правило безопасности"""
    source_zone: SecurityZone
    destination_zone: SecurityZone
    action: ActionType
    protocol: Optional[str] = None  # tcp, udp, icmp, any
    source_port: Optional[str] = None  # порт или диапазон
    destination_port: Optional[str] = None  # порт или диапазон
    description: str = ""
    enabled: bool = True
    
    def to_dict(self) -> Dict:
        """Конвертировать в словарь"""
        return {
            'source_zone': self.source_zone.name,
            'destination_zone': self.destination_zone.name,
            'action': self.action.value,
            'protocol': self.protocol,
            'source_port': self.source_port,
            'destination_port': self.destination_port,
            'description': self.description,
            'enabled': self.enabled
        }

@dataclass
class NetworkPolicy:
    """Политика безопасности сети"""
    name: str
    description: str = ""
    zones: Dict[str, SecurityZone] = field(default_factory=dict)
    rules: List[Rule] = field(default_factory=list)
    created_at: datetime = field(default_factory=datetime.now)
    updated_at: datetime = field(default_factory=datetime.now)
    
    def add_zone(self, zone: SecurityZone):
        """Добавить зону в политику"""
        self.zones[zone.name] = zone
        self.updated_at = datetime.now()
    
    def remove_zone(self, zone_name: str) -> bool:
        """Удалить зону из политики"""
        if zone_name in self.zones:
            del self.zones[zone_name]
            self.updated_at = datetime.now()
            return True
        return False
    
    def add_rule(self, rule: Rule):
        """Добавить правило в политику"""
        self.rules.append(rule)
        self.updated_at = datetime.now()
    
    def remove_rule(self, rule_index: int) -> bool:
        """Удалить правило из политики"""
        if 0 <= rule_index < len(self.rules):
            self.rules.pop(rule_index)
            self.updated_at = datetime.now()
            return True
        return False
    
    def get_rules_between(self, source_zone: str, dest_zone: str) -> List[Rule]:
        """Получить правила между двумя зонами"""
        return [
            rule for rule in self.rules
            if rule.source_zone.name == source_zone 
            and rule.destination_zone.name == dest_zone
        ]
    
    def validate(self) -> bool:
        """Валидировать политику"""
        # Проверка наличия зон
        if not self.zones:
            return False
        
        # Проверка правил
        for rule in self.rules:
            if rule.source_zone.name not in self.zones:
                return False
            if rule.destination_zone.name not in self.zones:
                return False
        
        return True
    
    def to_dict(self) -> Dict:
        """Конвертировать в словарь"""
        return {
            'name': self.name,
            'description': self.description,
            'zones': {name: zone.to_dict() for name, zone in self.zones.items()},
            'rules': [rule.to_dict() for rule in self.rules],
            'created_at': self.created_at.isoformat(),
            'updated_at': self.updated_at.isoformat()
        }
