"""
Модели данных для ZeroTrust Inspector
"""

from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import List, Dict, Optional, Set, Tuple
import json
import ipaddress

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
    TABLET = "tablet"
    IOT = "iot"
    PRINTER = "printer"
    CAMERA = "camera"
    TV = "tv"
    NAS = "nas"
    SERVER = "server"
    UNKNOWN = "unknown"

class ActionType(Enum):
    """Типы действий для правил"""
    ALLOW = "allow"
    DENY = "deny"
    LIMIT = "limit"

class ProtocolType(Enum):
    """Типы протоколов"""
    TCP = "tcp"
    UDP = "udp"
    ICMP = "icmp"
    ANY = "any"

@dataclass
class NetworkDevice:
    """Сетевое устройство"""
    ip_address: str
    mac_address: Optional[str] = None
    hostname: Optional[str] = None
    device_type: DeviceType = DeviceType.UNKNOWN
    vendor: Optional[str] = None
    open_ports: List[int] = field(default_factory=list)
    os_info: Optional[str] = None
    risk_score: float = 0.5
    is_gateway: bool = False
    last_seen: datetime = field(default_factory=datetime.now)
    
    def __post_init__(self):
        """Проверка корректности IP-адреса"""
        try:
            ipaddress.ip_address(self.ip_address)
        except ValueError:
            raise ValueError(f"Некорректный IP-адрес: {self.ip_address}")
    
    @property
    def is_trusted(self) -> bool:
        """Является ли устройство доверенным"""
        trusted_types = {DeviceType.COMPUTER, DeviceType.PHONE, DeviceType.TABLET, DeviceType.SERVER}
        return self.device_type in trusted_types and self.risk_score < 0.3
    
    def to_dict(self) -> Dict:
        """Конвертировать в словарь"""
        return {
            'ip_address': self.ip_address,
            'mac_address': self.mac_address,
            'hostname': self.hostname,
            'device_type': self.device_type.value,
            'vendor': self.vendor,
            'open_ports': self.open_ports,
            'os_info': self.os_info,
            'risk_score': self.risk_score,
            'is_gateway': self.is_gateway,
            'last_seen': self.last_seen.isoformat(),
        }
    
    @classmethod
    def from_dict(cls, data: Dict) -> 'NetworkDevice':
        """Создать из словаря"""
        device = cls(
            ip_address=data['ip_address'],
            mac_address=data.get('mac_address'),
            hostname=data.get('hostname'),
            device_type=DeviceType(data.get('device_type', 'unknown')),
            vendor=data.get('vendor'),
            open_ports=data.get('open_ports', []),
            os_info=data.get('os_info'),
            risk_score=data.get('risk_score', 0.5),
            is_gateway=data.get('is_gateway', False)
        )
        if 'last_seen' in data:
            device.last_seen = datetime.fromisoformat(data['last_seen'])
        return device

@dataclass
class SecurityZone:
    """Зона безопасности"""
    name: str
    zone_type: ZoneType
    description: str = ""
    devices: List[NetworkDevice] = field(default_factory=list)
    color: str = "#808080"  # Серый по умолчанию
    rules: Dict[str, ActionType] = field(default_factory=dict)
    
    def __post_init__(self):
        """Установить цвет в зависимости от типа зоны"""
        color_map = {
            ZoneType.TRUSTED: "#4CAF50",  # Зеленый
            ZoneType.IOT: "#FF9800",       # Оранжевый
            ZoneType.GUEST: "#9C27B0",     # Фиолетовый
            ZoneType.SERVER: "#2196F3",    # Синий
            ZoneType.DMZ: "#F44336",       # Красный
            ZoneType.CUSTOM: "#607D8B",    # Серый
        }
        self.color = color_map.get(self.zone_type, "#808080")
    
    def add_device(self, device: NetworkDevice):
        """Добавить устройство в зону"""
        if device not in self.devices:
            self.devices.append(device)
    
    def remove_device(self, device: NetworkDevice):
        """Удалить устройство из зоны"""
        if device in self.devices:
            self.devices.remove(device)
    
    @property
    def device_count(self) -> int:
        """Количество устройств в зоне"""
        return len(self.devices)
    
    @property
    def ip_addresses(self) -> List[str]:
        """Список IP-адресов устройств в зоне"""
        return [device.ip_address for device in self.devices]
    
    def set_rule(self, target_zone: 'SecurityZone', action: ActionType):
        """Установить правило для целевой зоны"""
        self.rules[target_zone.name] = action
    
    def get_rule(self, target_zone: 'SecurityZone') -> Optional[ActionType]:
        """Получить правило для целевой зоны"""
        return self.rules.get(target_zone.name)
    
    def to_dict(self) -> Dict:
        """Конвертировать в словарь"""
        return {
            'name': self.name,
            'zone_type': self.zone_type.value,
            'description': self.description,
            'devices': [device.to_dict() for device in self.devices],
            'color': self.color,
            'rules': {k: v.value for k, v in self.rules.items()},
        }
    
    @classmethod
    def from_dict(cls, data: Dict) -> 'SecurityZone':
        """Создать из словаря"""
        zone = cls(
            name=data['name'],
            zone_type=ZoneType(data['zone_type']),
            description=data.get('description', ''),
            color=data.get('color', '#808080')
        )
        
        # Восстанавливаем устройства
        for device_data in data.get('devices', []):
            zone.devices.append(NetworkDevice.from_dict(device_data))
        
        # Восстанавливаем правила
        for target_name, action_value in data.get('rules', {}).items():
            zone.rules[target_name] = ActionType(action_value)
        
        return zone

@dataclass
class Rule:
    """Правило безопасности"""
    source_zone: str
    destination_zone: str
    action: ActionType
    protocol: ProtocolType = ProtocolType.ANY
    port: Optional[int] = None
    description: str = ""
    enabled: bool = True
    
    def to_dict(self) -> Dict:
        """Конвертировать в словарь"""
        return {
            'source_zone': self.source_zone,
            'destination_zone': self.destination_zone,
            'action': self.action.value,
            'protocol': self.protocol.value,
            'port': self.port,
            'description': self.description,
            'enabled': self.enabled,
        }
    
    @classmethod
    def from_dict(cls, data: Dict) -> 'Rule':
        """Создать из словаря"""
        return cls(
            source_zone=data['source_zone'],
            destination_zone=data['destination_zone'],
            action=ActionType(data['action']),
            protocol=ProtocolType(data.get('protocol', 'any')),
            port=data.get('port'),
            description=data.get('description', ''),
            enabled=data.get('enabled', True)
        )

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
        if zone.name not in self.zones:
            self.zones[zone.name] = zone
            self.updated_at = datetime.now()
    
    def remove_zone(self, zone_name: str):
        """Удалить зону из политики"""
        if zone_name in self.zones:
            # Удаляем правила, связанные с этой зоной
            self.rules = [
                rule for rule in self.rules 
                if rule.source_zone != zone_name and rule.destination_zone != zone_name
            ]
            del self.zones[zone_name]
            self.updated_at = datetime.now()
    
    def add_rule(self, rule: Rule):
        """Добавить правило в политику"""
        if rule.source_zone in self.zones and rule.destination_zone in self.zones:
            self.rules.append(rule)
            self.updated_at = datetime.now()
    
    def remove_rule(self, rule_index: int):
        """Удалить правило из политики"""
        if 0 <= rule_index < len(self.rules):
            del self.rules[rule_index]
            self.updated_at = datetime.now()
    
    def get_rules_for_zone(self, zone_name: str) -> List[Rule]:
        """Получить все правила для указанной зоны"""
        return [
            rule for rule in self.rules 
            if rule.source_zone == zone_name or rule.destination_zone == zone_name
        ]
    
    def validate(self) -> List[str]:
        """Валидация политики"""
        errors = []
        
        # Проверка наличия зон
        if not self.zones:
            errors.append("Политика не содержит зон безопасности")
        
        # Проверка правил на наличие ссылок на несуществующие зоны
        for rule in self.rules:
            if rule.source_zone not in self.zones:
                errors.append(f"Правило ссылается на несуществующую исходную зону: {rule.source_zone}")
            if rule.destination_zone not in self.zones:
                errors.append(f"Правило ссылается на несуществующую целевую зону: {rule.destination_zone}")
        
        return errors
    
    def to_dict(self) -> Dict:
        """Конвертировать в словарь"""
        return {
            'name': self.name,
            'description': self.description,
            'zones': {name: zone.to_dict() for name, zone in self.zones.items()},
            'rules': [rule.to_dict() for rule in self.rules],
            'created_at': self.created_at.isoformat(),
            'updated_at': self.updated_at.isoformat(),
        }
    
    @classmethod
    def from_dict(cls, data: Dict) -> 'NetworkPolicy':
        """Создать из словаря"""
        policy = cls(
            name=data['name'],
            description=data.get('description', '')
        )
        
        # Восстанавливаем зоны
        for zone_name, zone_data in data.get('zones', {}).items():
            policy.zones[zone_name] = SecurityZone.from_dict(zone_data)
        
        # Восстанавливаем правила
        for rule_data in data.get('rules', []):
            policy.rules.append(Rule.from_dict(rule_data))
        
        if 'created_at' in data:
            policy.created_at = datetime.fromisoformat(data['created_at'])
        if 'updated_at' in data:
            policy.updated_at = datetime.fromisoformat(data['updated_at'])
        
        return policy
    
    def save_to_file(self, filepath: str):
        """Сохранить политику в файл"""
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(self.to_dict(), f, indent=2, ensure_ascii=False)
    
    @classmethod
    def load_from_file(cls, filepath: str) -> 'NetworkPolicy':
        """Загрузить политику из файла"""
        with open(filepath, 'r', encoding='utf-8') as f:
            data = json.load(f)
        return cls.from_dict(data)
