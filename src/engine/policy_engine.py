"""
Движок для работы с политиками безопасности
"""

import json
from typing import Dict, List, Optional
from datetime import datetime
from pathlib import Path

from ..core.models import (
    NetworkPolicy, SecurityZone, Rule, ActionType,
    NetworkDevice
)
from ..core.exceptions import PolicyValidationError

class PolicyEngine:
    """Движок для управления политиками безопасности"""
    
    def __init__(self):
        self.current_policy = None
        self.policies = {}  # name -> NetworkPolicy
        self.templates = {}
        
    def create_policy(self, name: str, description: str = "") -> NetworkPolicy:
        """Создать новую политику"""
        policy = NetworkPolicy(name, description)
        self.current_policy = policy
        self.policies[name] = policy
        return policy
    
    def load_policy(self, filepath: Path) -> NetworkPolicy:
        """Загрузить политику из файла"""
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            policy = NetworkPolicy(
                name=data['name'],
                description=data.get('description', '')
            )
            
            # Восстанавливаем зоны
            for zone_data in data.get('zones', []):
                zone = SecurityZone(
                    name=zone_data['name'],
                    zone_type=zone_data['zone_type'],
                    description=zone_data.get('description', ''),
                    color=zone_data.get('color', '#FFFFFF'),
                    default_policy=ActionType(zone_data.get('default_policy', 'deny'))
                )
                policy.add_zone(zone)
            
            # Восстанавливаем правила
            for rule_data in data.get('rules', []):
                source_zone = policy.zones[rule_data['source_zone']]
                dest_zone = policy.zones[rule_data['dest_zone']]
                
                rule = Rule(
                    source_zone=source_zone,
                    destination_zone=dest_zone,
                    action=ActionType(rule_data['action']),
                    protocol=rule_data.get('protocol', 'any'),
                    port=rule_data.get('port'),
                    description=rule_data.get('description', ''),
                    enabled=rule_data.get('enabled', True)
                )
                policy.add_rule(rule)
            
            self.current_policy = policy
            self.policies[policy.name] = policy
            
            return policy
            
        except Exception as e:
            raise PolicyValidationError(f"Ошибка загрузки политики: {e}")
    
    def save_policy(self, policy: NetworkPolicy, filepath: Path):
        """Сохранить политику в файл"""
        try:
            data = {
                'name': policy.name,
                'description': policy.description,
                'created_at': policy.created_at.isoformat(),
                'updated_at': policy.updated_at.isoformat(),
                'zones': [],
                'rules': []
            }
            
            # Сохраняем зоны
            for zone in policy.zones.values():
                zone_data = {
                    'name': zone.name,
                    'zone_type': zone.zone_type.value,
                    'description': zone.description,
                    'color': zone.color,
                    'default_policy': zone.default_policy.value,
                    'device_count': zone.device_count
                }
                data['zones'].append(zone_data)
            
            # Сохраняем правила
            for rule in policy.rules:
                rule_data = {
                    'source_zone': rule.source_zone.name,
                    'dest_zone': rule.destination_zone.name,
                    'action': rule.action.value,
                    'protocol': rule.protocol,
                    'port': rule.port,
                    'description': rule.description,
                    'enabled': rule.enabled
                }
                data['rules'].append(rule_data)
            
            with open(filepath, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
            
        except Exception as e:
            raise PolicyValidationError(f"Ошибка сохранения политики: {e}")
    
    def validate_policy(self, policy: NetworkPolicy) -> List[str]:
        """
        Валидация политики безопасности
        Возвращает список предупреждений и ошибок
        """
        warnings = []
        
        # Проверка пустых зон
        for zone_name, zone in policy.zones.items():
            if zone.device_count == 0:
                warnings.append(f"Зона '{zone_name}' пуста")
        
        # Проверка правил для несуществующих зон
        for rule in policy.rules:
            if rule.source_zone.name not in policy.zones:
                warnings.append(f"Правило ссылается на несуществующую зону: {rule.source_zone.name}")
            if rule.destination_zone.name not in policy.zones:
                warnings.append(f"Правило ссылается на несуществующую зону: {rule.destination_zone.name}")
        
        # Проверка циклических разрешений
        # (упрощенная проверка - в реальном проекте нужен анализ графа)
        
        return warnings
    
    def generate_default_rules(self, policy: NetworkPolicy):
        """Сгенерировать правила по умолчанию для политики"""
        policy.rules.clear()
        
        zone_names = list(policy.zones.keys())
        
        # Создаем правила "запретить все" между всеми зонами
        for i, zone1_name in enumerate(zone_names):
            for j, zone2_name in enumerate(zone_names):
                if i != j:  # Не создаем правила для одной и той же зоны
                    rule = Rule(
                        source_zone=policy.zones[zone1_name],
                        destination_zone=policy.zones[zone2_name],
                        action=ActionType.DENY,
                        description=f"По умолчанию: {zone1_name} -> {zone2_name}"
                    )
                    policy.add_rule(rule)
        
        # Добавляем разрешение внутри зон
        for zone in policy.zones.values():
            rule = Rule(
                source_zone=zone,
                destination_zone=zone,
                action=ActionType.ALLOW,
                description=f"Внутренний трафик зоны {zone.name}"
            )
            policy.add_rule(rule)
    
    def optimize_rules(self, policy: NetworkPolicy):
        """Оптимизировать правила (удалить дубликаты, объединить похожие)"""
        # Удаляем дубликаты
        unique_rules = []
        seen_rules = set()
        
        for rule in policy.rules:
            rule_key = (
                rule.source_zone.name,
                rule.destination_zone.name,
                rule.action.value,
                rule.protocol,
                rule.port
            )
            
            if rule_key not in seen_rules:
                seen_rules.add(rule_key)
                unique_rules.append(rule)
        
        policy.rules = unique_rules
        
        # Сортируем правила для производительности
        # Более специфичные правила должны идти первыми
        policy.rules.sort(key=lambda r: (
            r.protocol != 'any',  # Сначала специфичные протоколы
            r.port is not None,   # Затем правила с портами
            r.action.value == 'allow'  # Разрешающие правила после запрещающих
        ))
    
    def find_conflicts(self, policy: NetworkPolicy) -> List[str]:
        """Найти конфликты в правилах"""
        conflicts = []
        
        # Группируем правила по парам зон
        rules_by_pair = {}
        for rule in policy.rules:
            key = (rule.source_zone.name, rule.destination_zone.name)
            if key not in rules_by_pair:
                rules_by_pair[key] = []
            rules_by_pair[key].append(rule)
        
        # Ищем конфликты в каждой паре
        for (src, dst), rules in rules_by_pair.items():
            if len(rules) > 1:
                # Проверяем на противоречивые правила
                has_allow = any(r.action == ActionType.ALLOW for r in rules)
                has_deny = any(r.action == ActionType.DENY for r in rules)
                
                if has_allow and has_deny:
                    conflicts.append(
                        f"Конфликт правил между {src} и {dst}: "
                        f"есть как разрешающие, так и запрещающие правила"
                    )
        
        return conflicts
