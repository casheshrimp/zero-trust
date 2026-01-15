"""
Сканер сети на основе Nmap
"""

import nmap
import socket
import netifaces
import threading
from typing import List, Dict, Optional
from datetime import datetime
import time

from ..core.models import NetworkDevice, DeviceType
from ..core.exceptions import NetworkScanError

class NetworkScanner:
    """Сканер сети"""
    
    def __init__(self):
        self.nm = nmap.PortScanner()
        self.scanning = False
        self.progress = 0
        self.current_scan = None
        self.devices_found = []
        
    def get_local_network(self) -> str:
        """
        Определить локальную сеть автоматически
        Возвращает строку в формате CIDR (например, '192.168.1.0/24')
        """
        try:
            interfaces = netifaces.interfaces()
            for interface in interfaces:
                # Пропускаем локальные интерфейсы
                if interface.startswith('lo'):
                    continue
                    
                addrs = netifaces.ifaddresses(interface)
                if netifaces.AF_INET in addrs:
                    ip_info = addrs[netifaces.AF_INET][0]
                    ip = ip_info['addr']
                    netmask = ip_info['netmask']
                    
                    # Преобразуем в CIDR
                    netmask_bits = sum(bin(int(x)).count('1') for x in netmask.split('.'))
                    network_parts = ip.split('.')
                    network_parts[-1] = '0'  # Последний октет обнуляем
                    network = '.'.join(network_parts)
                    
                    return f"{network}/{netmask_bits}"
                    
        except Exception as e:
            raise NetworkScanError(f"Не удалось определить сеть: {e}")
        
        # Если не удалось определить, возвращаем по умолчанию
        return "192.168.1.0/24"
    
    def scan_network_async(self, network_range: str = None, callback=None):
        """
        Асинхронное сканирование сети
        """
        if self.scanning:
            raise NetworkScanError("Сканирование уже выполняется")
        
        if not network_range:
            network_range = self.get_local_network()
        
        self.scanning = True
        self.progress = 0
        self.devices_found = []
        
        # Запускаем в отдельном потоке
        scan_thread = threading.Thread(
            target=self._scan_thread,
            args=(network_range, callback),
            daemon=True
        )
        scan_thread.start()
        
        return scan_thread
    
    def _scan_thread(self, network_range: str, callback=None):
        """
        Поток для сканирования сети
        """
        try:
            # Фаза 1: ARP сканирование для быстрого обнаружения
            self.progress = 10
            if callback:
                callback("phase1", "ARP сканирование...", self.progress)
            
            self.nm.scan(hosts=network_range, arguments='-sn -PR --max-rtt-timeout 100ms')
            
            discovered_hosts = []
            for host in self.nm.all_hosts():
                if self.nm[host].state() == 'up':
                    discovered_hosts.append(host)
            
            self.progress = 30
            if callback:
                callback("phase1_done", f"Найдено хостов: {len(discovered_hosts)}", self.progress)
            
            # Фаза 2: Детальное сканирование каждого хоста
            self.progress = 40
            if callback:
                callback("phase2", "Детальное сканирование...", self.progress)
            
            devices = []
            total_hosts = len(discovered_hosts)
            
            for i, host in enumerate(discovered_hosts):
                device = self._scan_single_host(host)
                if device:
                    devices.append(device)
                
                # Обновляем прогресс
                self.progress = 40 + int((i / total_hosts) * 40)
                if callback:
                    callback("host_scanned", f"Сканирован {host}", self.progress)
            
            self.devices_found = devices
            self.progress = 100
            
            if callback:
                callback("complete", f"Сканирование завершено. Найдено {len(devices)} устройств", self.progress)
            
        except Exception as e:
            error_msg = f"Ошибка сканирования: {str(e)}"
            if callback:
                callback("error", error_msg, 0)
            raise NetworkScanError(error_msg)
        finally:
            self.scanning = False
    
    def _scan_single_host(self, host: str) -> Optional[NetworkDevice]:
        """
        Сканирование отдельного хоста
        """
        try:
            device = NetworkDevice(ip_address=host)
            
            # Получаем MAC-адрес и hostname
            if 'addresses' in self.nm[host]:
                addresses = self.nm[host]['addresses']
                if 'mac' in addresses:
                    device.mac_address = addresses['mac']
            
            if 'hostnames' in self.nm[host] and self.nm[host]['hostnames']:
                device.hostname = self.nm[host]['hostnames'][0]['name']
            
            # Сканируем порты
            self.nm.scan(
                hosts=host,
                arguments='-T4 -F --top-ports 100'  # Быстрое сканирование 100 популярных портов
            )
            
            if 'tcp' in self.nm[host]:
                device.open_ports = list(self.nm[host]['tcp'].keys())
                
                # Определяем сервисы
                for port, info in self.nm[host]['tcp'].items():
                    if 'name' in info and info['name'] != 'unknown':
                        device.services[port] = info['name']
            
            # Определяем тип устройства на основе открытых портов
            device.device_type = self._guess_device_type(device)
            
            return device
            
        except Exception:
            # Если не удалось просканировать, все равно возвращаем базовое устройство
            return NetworkDevice(ip_address=host, device_type=DeviceType.UNKNOWN)
    
    def _guess_device_type(self, device: NetworkDevice) -> DeviceType:
        """
        Определить тип устройства на основе открытых портов
        """
        if not device.open_ports:
            return DeviceType.UNKNOWN
        
        # Проверяем специфичные порты
        ports = set(device.open_ports)
        
        if 9100 in ports:  # Printer
            return DeviceType.PRINTER
        elif 3389 in ports:  # RDP
            return DeviceType.COMPUTER
        elif 22 in ports and 445 in ports:  # SSH + SMB
            return DeviceType.COMPUTER
        elif 80 in ports and len(ports) < 3:  # Только HTTP и мало портов
            return DeviceType.IOT
        elif 53 in ports or 67 in ports:  # DNS или DHCP
            return DeviceType.ROUTER
        
        return DeviceType.UNKNOWN
    
    def stop_scan(self):
        """Остановить текущее сканирование"""
        self.scanning = False
        # Nmap не поддерживает graceful stop, но мы можем прекратить обработку
    
    def get_scan_results(self) -> List[NetworkDevice]:
        """Получить результаты последнего сканирования"""
        return self.devices_found.copy()
    
    def get_scan_progress(self) -> int:
        """Получить текущий прогресс сканирования"""
        return self.progress
