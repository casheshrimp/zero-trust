"""
Модели данных приложения
"""

from dataclasses import dataclass, field
from typing import List, Dict, Optional, Set
from enum import Enum
from datetime import datetime
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
    COMPUTER = "computer"
    PHONE = "phone"
    TABLET = "tablet"
    IOT = "iot"
    PRINTER = "printer"
    ROUTER = "router"
    SWITCH = "switch"
    CAMERA = "camera"
    UNKNOWN = "unknown"

class ActionType(Enum):
    """Типы действий для правил"""
    ALLOW = "allow"
    DENY = "deny"
    REJECT = "reject"
    LOG = "log"

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
    risk_score: float = 0.0
    last_seen: datetime = field(default_factory=datetime.now)
    description: str = ""
    
    def __post_init__(self):
        """Валидация IP-адреса"""
        try:
            ipaddress.ip_address(self.ip_address)
        except ValueError:
            raise ValueError(f"Некорректный IP-адрес: {self.ip_address}")
    
    @property
    def is_online(self) -> bool:
        """Устройство онлайн, если видели недавно"""
        return (datetime.now() - self.last_seen).seconds < 300  # 5 минут
    
    def get_friendly_name(self) -> str:
        """Получить понятное имя устройства"""
        if self.hostname and self.hostname != self.ip_address:
            return self.hostname
        elif self.vendor and self.device_type != DeviceType.UNKNOWN:
            return f"{self.vendor} {self.device_type.value}"
        else:
            return self.ip_address

@dataclass
class SecurityZone:
    """Зона безопасности"""
    name: str
    zone_type: ZoneType
    description: str = ""
    devices: List[NetworkDevice] = field(default_factory=list)
    color: str = "#FFFFFF"  # Цвет по умолчанию
    default_policy: ActionType = ActionType.DENY
    
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

@dataclass
class Rule:
    """Правило фильтрации"""
    source_zone: SecurityZone
    destination_zone: SecurityZone
    action: ActionType
    protocol: str = "any"  # tcp, udp, icmp, any
    port: Optional[int] = None
    description: str = ""
    enabled: bool = True
    
    def __str__(self) -> str:
        """Строковое представление правила"""
        base = f"{self.source_zone.name} -> {self.destination_zone.name}: {self.action.value}"
        if self.protocol != "any":
            base += f" ({self.protocol}"
            if self.port:
                base += f":{self.port}"
            base += ")"
        return base

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
    
    def remove_zone(self, zone_name: str):
        """Удалить зону из политики"""
        if zone_name in self.zones:
            del self.zones[zone_name]
            # Удаляем связанные правила
            self.rules = [
                rule for rule in self.rules 
                if rule.source_zone.name != zone_name and rule.destination_zone.name != zone_name
            ]
            self.updated_at = datetime.now()
    
    def add_rule(self, rule: Rule):
        """Добавить правило в политику"""
        self.rules.append(rule)
        self.updated_at = datetime.now()
    
    def get_rules_between(self, zone1: str, zone2: str) -> List[Rule]:
        """Получить правила между двумя зонами"""
        return [
            rule for rule in self.rules
            if (rule.source_zone.name == zone1 and rule.destination_zone.name == zone2) or
               (rule.source_zone.name == zone2 and rule.destination_zone.name == zone1)
        ]
    
    def validate(self) -> bool:
        """Проверить валидность политики"""
        # Проверка наличия всех зон, упомянутых в правилах
        for rule in self.rules:
            if rule.source_zone.name not in self.zones:
                return False
            if rule.destination_zone.name not in self.zones:
                return False
        return True
