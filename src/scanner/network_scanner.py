import nmap
import socket
import netifaces
from typing import List, Dict
from dataclasses import dataclass
from datetime import datetime

@dataclass
class NetworkDevice:
    ip: str
    mac: str = ""
    hostname: str = ""
    vendor: str = ""
    device_type: str = "unknown"
    open_ports: List[int] = None
    last_seen: datetime = None
    
    def __post_init__(self):
        if self.open_ports is None:
            self.open_ports = []

class NetworkScanner:
    def __init__(self):
        self.nm = nmap.PortScanner()
        self.devices = []
        
    def get_local_network(self) -> str:
        """Определить локальную сеть"""
        interfaces = netifaces.interfaces()
        for interface in interfaces:
            addrs = netifaces.ifaddresses(interface)
            if netifaces.AF_INET in addrs:
                ip_info = addrs[netifaces.AF_INET][0]
                ip = ip_info['addr']
                netmask = ip_info['netmask']
                # Преобразуем в CIDR
                cidr = sum(bin(int(x)).count('1') for x in netmask.split('.'))
                network = '.'.join(ip.split('.')[:3]) + '.0'
                return f"{network}/{cidr}"
        return "192.168.1.0/24"  # По умолчанию
    
    def scan_network(self, network_range: str = None) -> List[NetworkDevice]:
        """Основное сканирование сети"""
        if not network_range:
            network_range = self.get_local_network()
            
        print(f"Сканирую сеть: {network_range}")
        
        # Фаза 1: ARP-сканирование для быстрого обнаружения
        self.nm.scan(hosts=network_range, arguments='-sn -PR')
        
        devices = []
        for host in self.nm.all_hosts():
            if self.nm[host].state() == 'up':
                device = NetworkDevice(ip=host)
                
                # Получаем MAC-адрес
                if 'mac' in self.nm[host]['addresses']:
                    device.mac = self.nm[host]['addresses']['mac']
                    
                # Получаем hostname
                if 'hostname' in self.nm[host]:
                    device.hostname = self.nm[host]['hostname']
                
                devices.append(device)
        
        # Фаза 2: Детальное сканирование открытых портов
        for device in devices:
            self.scan_device_ports(device)
            
        self.devices = devices
        return devices
    
    def scan_device_ports(self, device: NetworkDevice):
        """Сканирование портов устройства"""
        try:
            # Быстрое сканирование основных портов
            self.nm.scan(hosts=device.ip, 
                        arguments='-T4 -F --top-ports 100')
            
            if 'tcp' in self.nm[device.ip]:
                device.open_ports = list(self.nm[device.ip]['tcp'].keys())
                
            device.last_seen = datetime.now()
            
        except Exception as e:
            print(f"Ошибка сканирования {device.ip}: {e}")
