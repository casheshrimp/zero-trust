"""
Сканер сети
"""

import nmap
import threading
from typing import List, Dict, Optional
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime

from ..core.models import NetworkDevice, DeviceType
from ..core.exceptions import ScanError
from .device_classifier import DeviceClassifier

class NetworkScanner:
    """Сканер сетевых устройств"""
    
    def __init__(self):
        self.nm = nmap.PortScanner()
        self.classifier = DeviceClassifier()
        self.scan_progress = 0
        self.is_scanning = False
        self.scan_results = []
    
    def scan_network(self, network_range: str = "192.168.1.0/24", 
                    ports: str = "22,80,443,3389,9100") -> List[NetworkDevice]:
        """
        Сканировать сеть для обнаружения устройств
        
        Args:
            network_range: Диапазон сети для сканирования
            ports: Порт для сканирования (через запятую)
        
        Returns:
            Список обнаруженных устройств
        """
        self.is_scanning = True
        self.scan_progress = 0
        self.scan_results = []
        
        try:
            print(f"🔍 Сканирование сети {network_range}...")
            
            # Выполняем сканирование
            self.nm.scan(hosts=network_range, ports=ports, 
                        arguments='-sS -O --host-timeout 30s')
            
            devices = []
            
            # Обрабатываем результаты
            for host in self.nm.all_hosts():
                if self.nm[host].state() == 'up':
                    device = self._create_device_from_scan(host, self.nm[host])
                    devices.append(device)
                
                self.scan_progress = int((len(devices) / len(self.nm.all_hosts())) * 100)
            
            self.scan_results = devices
            self.is_scanning = False
            self.scan_progress = 100
            
            print(f"✅ Найдено {len(devices)} устройств")
            return devices
            
        except Exception as e:
            self.is_scanning = False
            raise ScanError(f"Ошибка сканирования: {e}")
    
    def quick_scan(self, network_range: str = "192.168.1.0/24") -> List[NetworkDevice]:
        """Быстрое сканирование сети (только ping)"""
        try:
            print(f"⚡ Быстрое сканирование {network_range}...")
            
            self.nm.scan(hosts=network_range, arguments='-sn')
            
            devices = []
            for host in self.nm.all_hosts():
                if self.nm[host].state() == 'up':
                    device = NetworkDevice(
                        ip_address=host,
                        hostname=self.nm[host].hostname() if 'hostname' in self.nm[host] else None
                    )
                    devices.append(device)
            
            print(f"✅ Найдено {len(devices)} активных устройств")
            return devices
            
        except Exception as e:
            raise ScanError(f"Ошибка быстрого сканирования: {e}")
    
    def _create_device_from_scan(self, host: str, scan_data: Dict) -> NetworkDevice:
        """Создать объект устройства из данных сканирования"""
        # Получаем MAC-адрес
        mac_address = None
        if 'addresses' in scan_data and 'mac' in scan_data['addresses']:
            mac_address = scan_data['addresses']['mac']
        
        # Получаем открытые порты
        open_ports = []
        if 'tcp' in scan_data:
            for port, port_data in scan_data['tcp'].items():
                if port_data['state'] == 'open':
                    open_ports.append(port)
        
        # Получаем ОС
        os_info = None
        if 'osmatch' in scan_data and scan_data['osmatch']:
            os_info = scan_data['osmatch'][0]['name']
        
        # Создаем устройство
        device = NetworkDevice(
            ip_address=host,
            mac_address=mac_address,
            hostname=scan_data.get('hostname', ''),
            os=os_info,
            open_ports=open_ports
        )
        
        # Классифицируем устройство
        device.device_type = self.classifier.classify_device(device)
        
        # Получаем информацию о производителе
        if mac_address:
            vendor = self.classifier.get_vendor_from_mac(mac_address)
            if vendor:
                device.vendor = vendor
        
        return device
    
    def scan_single_device(self, ip_address: str) -> Optional[NetworkDevice]:
        """Сканировать одно устройство детально"""
        try:
            print(f"🔍 Детальное сканирование {ip_address}...")
            
            self.nm.scan(hosts=ip_address, 
                        ports="1-1000,3389,8080,8443,9100,515,631",
                        arguments='-sS -sV -O --script=banner')
            
            if ip_address in self.nm.all_hosts():
                return self._create_device_from_scan(ip_address, self.nm[ip_address])
            
            return None
            
        except Exception as e:
            raise ScanError(f"Ошибка сканирования устройства {ip_address}: {e}")
    
    def stop_scan(self):
        """Остановить текущее сканирование"""
        self.is_scanning = False
        print("⏹️ Сканирование остановлено")
    
    def get_scan_progress(self) -> int:
        """Получить прогресс сканирования"""
        return self.scan_progress
    
    def get_latest_results(self) -> List[NetworkDevice]:
        """Получить результаты последнего сканирования"""
        return self.scan_results.copy()
