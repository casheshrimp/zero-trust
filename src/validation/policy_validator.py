import subprocess
import socket
import time
from typing import List, Dict

class PolicyValidator:
    def __init__(self):
        self.test_results = []
        
    def ping_test(self, source_ip: str, target_ip: str) -> bool:
        """Проверка ping между устройствами"""
        try:
            # Для Windows
            param = '-n' if platform.system().lower() == 'windows' else '-c'
            command = ['ping', param, '2', '-W', '1', target_ip]
            
            result = subprocess.run(command, 
                                  capture_output=True, 
                                  text=True, 
                                  timeout=5)
            
            return result.returncode == 0
            
        except (subprocess.TimeoutExpired, Exception) as e:
            return False
    
    def port_test(self, source_ip: str, target_ip: str, port: int) -> bool:
        """Проверка доступности порта"""
        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(2)
            
            result = sock.connect_ex((target_ip, port))
            sock.close()
            
            return result == 0
            
        except Exception:
            return False
    
    def validate_zone_isolation(self, zones: Dict) -> List[Dict]:
        """Проверить изоляцию между зонами"""
        results = []
        
        zone_names = list(zones.keys())
        
        for i, zone1_name in enumerate(zone_names):
            for j, zone2_name in enumerate(zone_names):
                if i >= j:  # Чтобы не дублировать тесты
                    continue
                    
                zone1 = zones[zone1_name]
                zone2 = zones[zone2_name]
                
                if not zone1.devices or not zone2.devices:
                    continue
                
                # Берем первое устройство из каждой зоны для теста
                test_device1 = zone1.devices[0]
                test_device2 = zone2.devices[0]
                
                # Тест 1: Ping
                ping_result = self.ping_test(
                    test_device1.ip, 
                    test_device2.ip
                )
                
                # Тест 2: HTTP порт
                http_result = self.port_test(
                    test_device1.ip,
                    test_device2.ip,
                    80
                )
                
                results.append({
                    'test': f"{zone1_name} → {zone2_name}",
                    'ping': ping_result,
                    'http': http_result,
                    'expected': False,  # Ожидаем, что трафик заблокирован
                    'passed': not (ping_result or http_result)
                })
        
        return results
    
    def generate_report(self, test_results: List[Dict]) -> str:
        """Сгенерировать отчет о валидации"""
        total = len(test_results)
        passed = sum(1 for r in test_results if r['passed'])
        score = (passed / total) * 100 if total > 0 else 0
        
        report = f"""
        ОТЧЕТ О ВАЛИДАЦИИ ПОЛИТИК БЕЗОПАСНОСТИ
        ======================================
        
        Всего тестов: {total}
        Успешно: {passed}
        С ошибками: {total - passed}
        Оценка: {score:.1f}%
        
        Детальные результаты:
        """
        
        for result in test_results:
            status = "✅ УСПЕХ" if result['passed'] else "❌ ОШИБКА"
            report += f"\n{result['test']}: {status}"
            if not result['passed']:
                report += f"\n  Ping: {'доступен' if result['ping'] else 'блокирован'}"
                report += f"\n  HTTP: {'доступен' if result['http'] else 'блокирован'}"
        
        return report
