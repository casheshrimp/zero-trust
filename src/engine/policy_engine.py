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
