from jinja2 import Environment, FileSystemLoader
import os
from typing import Dict, List

class RuleGenerator:
    def __init__(self):
        # Загружаем шаблоны Jinja2
        template_dir = os.path.join(os.path.dirname(__file__), 'templates')
        self.env = Environment(loader=FileSystemLoader(template_dir))
        
    def generate_openwrt_config(self, zones: Dict, rules: List) -> str:
        """Сгенерировать конфигурацию для OpenWrt"""
        template = self.env.get_template('openwrt.conf.j2')
        
        # Подготовка данных для шаблона
        data = {
            'zones': zones,
            'rules': rules,
            'timestamp': '2025-12-25',
            'version': '1.0'
        }
        
        return template.render(data)
    
    def generate_windows_firewall_script(self, zones: Dict, rules: List) -> str:
        """Сгенерировать PowerShell скрипт для Windows"""
        template = self.env.get_template('windows_firewall.ps1.j2')
        
        data = {
            'zones': zones,
            'rules': rules,
            'timestamp': '2025-12-25'
        }
        
        return template.render(data)
    
    def generate_iptables_script(self, zones: Dict, rules: List) -> str:
        """Сгенерировать bash скрипт для iptables"""
        template = self.env.get_template('iptables.sh.j2')
        
        data = {
            'zones': zones,
            'rules': rules,
            'timestamp': '2025-12-25'
        }
        
        return template.render(data)

# Пример шаблона: src/engine/templates/openwrt.conf.j2
"""
# ZeroTrust Inspector - Конфигурация безопасности
# Сгенерировано: {{ timestamp }}
# Версия: {{ version }}

config defaults
    option syn_flood '1'
    option input 'ACCEPT'
    option output 'ACCEPT'
    option forward 'REJECT'

{% for zone in zones %}
config zone
    option name '{{ zone.name }}'
    list network 'lan'
    option input 'ACCEPT'
    option output 'ACCEPT'
    option forward 'ACCEPT'
    option masq '1'
{% endfor %}

{% for rule in rules %}
config rule
    option name '{{ rule.name }}'
    option src '{{ rule.src_zone }}'
    option dest '{{ rule.dst_zone }}'
    option proto '{{ rule.proto }}'
    option dest_port '{{ rule.port }}'
    option target '{{ rule.action }}'
{% endfor %}
"""
