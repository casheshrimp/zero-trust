"""
Генератор конфигурационных файлов для разных платформ
"""

from jinja2 import Environment, FileSystemLoader, TemplateNotFound
from typing import Dict, List, Optional
import os
from pathlib import Path

from ..core.models import NetworkPolicy, Rule, ActionType
from ..core.constants import TEMPLATES_DIR
from ..core.exceptions import RuleGenerationError

class RuleGenerator:
    """Генератор правил для разных сетевых устройств"""
    
    SUPPORTED_PLATFORMS = {
        'openwrt': 'OpenWrt / LEDE',
        'windows': 'Windows Firewall',
        'iptables': 'IPTables (Linux)',
        'mikrotik': 'MikroTik RouterOS',
        'asuswrt': 'ASUSWRT',
        'pfsense': 'pfSense / OPNsense',
    }
    
    def __init__(self):
        self.env = Environment(
            loader=FileSystemLoader(TEMPLATES_DIR),
            trim_blocks=True,
            lstrip_blocks=True
        )
        
        # Регистрируем фильтры для Jinja2
        self.env.filters['ip_to_int'] = self._ip_to_int
        self.env.filters['cidr_mask'] = self._cidr_mask
    
    def generate_config(self, policy: NetworkPolicy, platform: str, 
                       options: Dict = None) -> str:
        """
        Сгенерировать конфигурацию для указанной платформы
        """
        if platform not in self.SUPPORTED_PLATFORMS:
            raise RuleGenerationError(f"Неподдерживаемая платформа: {platform}")
        
        if options is None:
            options = {}
        
        try:
            # Загружаем шаблон
            template_name = f"{platform}.j2"
            template = self.env.get_template(template_name)
            
            # Подготавливаем данные для шаблона
            template_data = self._prepare_template_data(policy, platform, options)
            
            # Генерируем конфигурацию
            config = template.render(**template_data)
            
            return config
            
        except TemplateNotFound:
            raise RuleGenerationError(f"Шаблон для {platform} не найден")
        except Exception as e:
            raise RuleGenerationError(f"Ошибка генерации конфигурации: {e}")
    
    def _prepare_template_data(self, policy: NetworkPolicy, platform: str, 
                              options: Dict) -> Dict:
        """Подготовить данные для шаблона"""
        import datetime
        
        data = {
            'policy': policy,
            'platform': platform,
            'platform_name': self.SUPPORTED_PLATFORMS[platform],
            'options': options,
            'timestamp': datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            'generator': 'ZeroTrust Inspector',
            'version': '1.0.0',
        }
        
        # Добавляем платформ-специфичные данные
        if platform == 'openwrt':
            data.update(self._prepare_openwrt_data(policy))
        elif platform == 'windows':
            data.update(self._prepare_windows_data(policy))
        elif platform == 'iptables':
            data.update(self._prepare_iptables_data(policy))
        
        return data
    
    def _prepare_openwrt_data(self, policy: NetworkPolicy) -> Dict:
        """Подготовить данные для OpenWrt"""
        zones_data = []
        rules_data = []
        
        for zone in policy.zones.values():
            zone_data = {
                'name': zone.name.lower().replace(' ', '_'),
                'display_name': zone.name,
                'devices': [d.ip_address for d in zone.devices],
                'color': zone.color,
            }
            zones_data.append(zone_data)
        
        for rule in policy.rules:
            if not rule.enabled:
                continue
                
            rule_data = {
                'src_zone': rule.source_zone.name.lower().replace(' ', '_'),
                'dst_zone': rule.destination_zone.name.lower().replace(' ', '_'),
                'action': rule.action.value.upper(),
                'protocol': rule.protocol,
                'port': rule.port,
                'description': rule.description,
            }
            rules_data.append(rule_data)
        
        return {
            'zones': zones_data,
            'rules': rules_data,
        }
    
    def _prepare_windows_data(self, policy: NetworkPolicy) -> Dict:
        """Подготовить данные для Windows Firewall"""
        rules_data = []
        
        for rule in policy.rules:
            if not rule.enabled:
                continue
            
            # Для Windows нужно преобразовать правила в формат PowerShell
            rule_data = {
                'name': f"ZeroTrust_{rule.source_zone.name}_to_{rule.destination_zone.name}",
                'display_name': rule.description or f"{rule.source_zone.name} to {rule.destination_zone.name}",
                'direction': 'Outbound',  # Можно определить по контексту
                'action': 'Block' if rule.action == ActionType.DENY else 'Allow',
                'protocol': rule.protocol.upper() if rule.protocol != 'any' else 'Any',
                'local_ports': rule.port if rule.port else 'Any',
                'remote_addresses': [d.ip_address for d in rule.destination_zone.devices],
            }
            rules_data.append(rule_data)
        
        return {
            'rules': rules_data,
            'profile': 'Domain,Private,Public',
        }
    
    def _prepare_iptables_data(self, policy: NetworkPolicy) -> Dict:
        """Подготовить данные для IPTables"""
        chains_data = {}
        rules_data = []
        
        # Создаем цепочки для каждой зоны
        for zone in policy.zones.values():
            chain_name = f"ZONE_{zone.name.upper().replace(' ', '_')}"
            chains_data[zone.name] = {
                'chain': chain_name,
                'devices': [d.ip_address for d in zone.devices],
            }
        
        # Создаем правила
        for rule in policy.rules:
            if not rule.enabled:
                continue
            
            src_chain = chains_data[rule.source_zone.name]['chain']
            dst_chain = chains_data[rule.destination_zone.name]['chain']
            
            rule_data = {
                'src_chain': src_chain,
                'dst_chain': dst_chain,
                'action': rule.action.value.upper(),
                'protocol': rule.protocol,
                'dport': f'--dport {rule.port}' if rule.port else '',
                'comment': f'-m comment --comment "{rule.description}"' if rule.description else '',
            }
            rules_data.append(rule_data)
        
        return {
            'chains': chains_data,
            'rules': rules_data,
        }
    
    def _ip_to_int(self, ip_address: str) -> int:
        """Конвертировать IP-адрес в целое число"""
        parts = ip_address.split('.')
        return (int(parts[0]) << 24) + (int(parts[1]) << 16) + (int(parts[2]) << 8) + int(parts[3])
    
    def _cidr_mask(self, prefix_length: int) -> str:
        """Конвертировать длину префикса в маску сети"""
        mask = (0xffffffff << (32 - prefix_length)) & 0xffffffff
        return '.'.join([str(mask >> (i << 3) & 0xff) for i in range(3, -1, -1)])
    
    def get_platform_instructions(self, platform: str) -> str:
        """Получить инструкции по применению для платформы"""
        instructions = {
            'openwrt': """
            1. Скопируйте конфигурацию выше
            2. Откройте веб-интерфейс роутера (обычно 192.168.1.1)
            3. Перейдите в раздел Network → Firewall
            4. Нажмите "Edit" для конфигурации брандмауэра
            5. Вставьте конфигурацию и сохраните
            6. Перезагрузите брандмауэр или роутер
            """,
            
            'windows': """
            1. Сохраните скрипт как .ps1 файл
            2. Запустите PowerShell от имени администратора
            3. Перейдите в папку со скриптом: cd C:\путь\к\скрипту
            4. Разрешите выполнение скриптов: Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
            5. Запустите скрипт: .\\имя_скрипта.ps1
            6. Проверьте правила: Get-NetFirewallRule | Where-Object {$_.DisplayName -like "ZeroTrust*"}
            """,
            
            'iptables': """
            1. Сохраните скрипт как .sh файл
            2. Сделайте его исполняемым: chmod +x имя_скрипта.sh
            3. Запустите от root: sudo ./имя_скрипта.sh
            4. Чтобы сохранить правила после перезагрузки:
               - Для Ubuntu/Debian: iptables-save > /etc/iptables/rules.v4
               - Для CentOS/RHEL: service iptables save
            """,
        }
        
        return instructions.get(platform, "Инструкции для этой платформы пока недоступны.")
