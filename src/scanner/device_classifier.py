import re
from typing import Dict

class DeviceClassifier:
    def __init__(self):
        # База данных производителей по OUI
        self.oui_db = self.load_oui_database()
        
        # Правила классификации
        self.classification_rules = {
            'computer': [
                lambda d: any(p in [22, 3389, 445] for p in d.open_ports),
                lambda d: 'microsoft' in d.vendor.lower(),
                lambda d: 'apple' in d.vendor.lower(),
                lambda d: 'linux' in d.vendor.lower(),
            ],
            'phone': [
                lambda d: 'apple' in d.vendor.lower() and 'iphone' in d.vendor.lower(),
                lambda d: 'samsung' in d.vendor.lower(),
                lambda d: any(p in [62078, 5353] for p in d.open_ports),  # iOS/Android порты
            ],
            'iot': [
                lambda d: 'philips' in d.vendor.lower() and 80 in d.open_ports,
                lambda d: 'tp-link' in d.vendor.lower(),
                lambda d: 'xiaomi' in d.vendor.lower(),
                lambda d: 80 in d.open_ports and len(d.open_ports) < 3,
            ],
            'printer': [
                lambda d: 9100 in d.open_ports,
                lambda d: 'hp' in d.vendor.lower() and 631 in d.open_ports,
                lambda d: 'canon' in d.vendor.lower(),
            ],
            'router': [
                lambda d: d.ip.endswith('.1') or d.ip.endswith('.254'),
                lambda d: 53 in d.open_ports or 67 in d.open_ports,  # DNS/DHCP
            ]
        }
    
    def load_oui_database(self) -> Dict[str, str]:
        """Загрузить базу OUI из файла"""
        oui_db = {}
        try:
            with open('assets/oui.txt', 'r') as f:
                for line in f:
                    if '(base 16)' in line:
                        parts = line.split('(base 16)')
                        mac_prefix = parts[0].strip().replace('-', ':').upper()
                        vendor = parts[1].strip()
                        oui_db[mac_prefix] = vendor
        except:
            # Минимальная база для начала
            oui_db = {
                '00:11:22': 'Test Vendor',
                'AA:BB:CC': 'Test IoT Vendor'
            }
        return oui_db
    
    def get_vendor_from_mac(self, mac: str) -> str:
        """Определить производителя по MAC"""
        if not mac:
            return "Unknown"
        
        mac_prefix = ':'.join(mac.split(':')[:3]).upper()
        return self.oui_db.get(mac_prefix, "Unknown")
    
    def classify_device(self, device) -> str:
        """Классифицировать устройство"""
        # Определить производителя
        device.vendor = self.get_vendor_from_mac(device.mac)
        
        # Применить правила классификации
        for device_type, rules in self.classification_rules.items():
            for rule in rules:
                try:
                    if rule(device):
                        return device_type
                except:
                    continue
        
        # По умолчанию
        if device.open_ports:
            return "network_device"
        return "unknown"
