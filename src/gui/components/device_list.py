"""
Виджет списка устройств с поддержкой drag-and-drop
"""

from PyQt6.QtWidgets import (
    QListWidget, QListWidgetItem, QMenu, QAbstractItemView
)
from PyQt6.QtCore import Qt, QMimeData, pyqtSignal
from PyQt6.QtGui import QDrag, QIcon, QPixmap, QColor
import json

from ...core.models import NetworkDevice, DeviceType
from ...core.constants import DEVICE_ICONS

class DeviceListWidget(QListWidget):
    """Виджет списка устройств с поддержкой drag-and-drop"""
    
    device_selected = pyqtSignal(NetworkDevice)
    device_dragged = pyqtSignal(str, str)  # device_id, zone_name
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setup_ui()
        self.devices = {}
        
    def setup_ui(self):
        """Настройка интерфейса виджета"""
        self.setDragEnabled(True)
        self.setAcceptDrops(False)  # Принимаем только исходящие drag
        self.setDragDropMode(QAbstractItemView.DragDropMode.DragOnly)
        self.setSelectionMode(QAbstractItemView.SelectionMode.SingleSelection)
        self.setMinimumWidth(200)
        
        # Контекстное меню
        self.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)
        self.customContextMenuRequested.connect(self.show_context_menu)
    
    def update_devices(self, devices: list):
        """Обновить список устройств"""
        self.clear()
        self.devices.clear()
        
        for device in devices:
            self.add_device(device)
    
    def add_device(self, device: NetworkDevice):
        """Добавить устройство в список"""
        item = QListWidgetItem(self)
        widget = DeviceItem(device)
        item.setSizeHint(widget.sizeHint())
        
        # Сохраняем данные устройства в item
        item.setData(Qt.ItemDataRole.UserRole, device.ip_address)
        self.devices[device.ip_address] = device
        
        self.addItem(item)
        self.setItemWidget(item, widget)
    
    def startDrag(self, supportedActions):
        """Начало операции drag-and-drop"""
        item = self.currentItem()
        if not item:
            return
        
        device_ip = item.data(Qt.ItemDataRole.UserRole)
        device = self.devices.get(device_ip)
        if not device:
            return
        
        # Создаем данные для перетаскивания
        mime_data = QMimeData()
        device_data = {
            'ip_address': device.ip_address,
            'device_type': device.device_type.value,
            'name': device.get_friendly_name()
        }
        mime_data.setText(json.dumps(device_data))
        
        # Создаем drag операцию
        drag = QDrag(self)
        drag.setMimeData(mime_data)
        
        # Устанавливаем иконку для перетаскивания
        icon_char = DEVICE_ICONS.get(device.device_type.value, "❓")
        pixmap = self.create_drag_pixmap(icon_char, device.get_friendly_name())
        drag.setPixmap(pixmap)
        drag.setHotSpot(pixmap.rect().center())
        
        # Запускаем drag
        drag.exec(Qt.DropAction.MoveAction)
        
        # Сигнал о начале перетаскивания
        self.device_dragged.emit(device.ip_address, "")
    
    def create_drag_pixmap(self, icon: str, text: str) -> QPixmap:
        """Создать изображение для перетаскивания"""
        from PyQt6.QtGui import QPainter, QFont, QBrush, QPen
        
        pixmap = QPixmap(100, 50)
        pixmap.fill(Qt.GlobalColor.transparent)
        
        painter = QPainter(pixmap)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        
        # Фон
        painter.setBrush(QBrush(QColor(70, 130, 180, 200)))  # Прозрачный синий
        painter.setPen(Qt.PenStyle.NoPen)
        painter.drawRoundedRect(0, 0, 100, 50, 10, 10)
        
        # Иконка
        painter.setFont(QFont("Arial", 20))
        painter.setPen(QPen(Qt.GlobalColor.white))
        painter.drawText(15, 30, icon)
        
        # Текст (обрезаем если длинный)
        if len(text) > 10:
            text = text[:8] + "..."
        painter.setFont(QFont("Arial", 8))
        painter.drawText(40, 20, text)
        
        painter.end()
        return pixmap
    
    def show_context_menu(self, position):
        """Показать контекстное меню для устройства"""
        item = self.itemAt(position)
        if not item:
            return
        
        device_ip = item.data(Qt.ItemDataRole.UserRole)
        device = self.devices.get(device_ip)
        if not device:
            return
        
        menu = QMenu(self)
        
        # Действия меню
        scan_action = menu.addAction("🔍 Сканировать порты")
        info_action = menu.addAction("📋 Информация")
        menu.addSeparator()
        classify_action = menu.addAction("🏷️ Классифицировать")
        menu.addSeparator()
        isolate_action = menu.addAction("🔒 Изолировать")
        
        action = menu.exec(self.viewport().mapToGlobal(position))
        
        if action == scan_action:
            self.scan_device_ports(device)
        elif action == info_action:
            self.show_device_info(device)
        elif action == classify_action:
            self.reclassify_device(device)
        elif action == isolate_action:
            self.isolate_device(device)
    
    def scan_device_ports(self, device: NetworkDevice):
        """Сканировать порты устройства"""
        print(f"Сканирую порты устройства {device.ip_address}")
        # Здесь будет вызов модуля сканирования
    
    def show_device_info(self, device: NetworkDevice):
        """Показать информацию об устройстве"""
        from PyQt6.QtWidgets import QMessageBox
        
        info_text = f"""
        <b>Устройство:</b> {device.get_friendly_name()}<br>
        <b>IP-адрес:</b> {device.ip_address}<br>
        <b>MAC-адрес:</b> {device.mac_address or 'Неизвестно'}<br>
        <b>Производитель:</b> {device.vendor or 'Неизвестно'}<br>
        <b>Тип:</b> {device.device_type.value}<br>
        <b>Открытые порты:</b> {', '.join(map(str, device.open_ports)) or 'Нет'}<br>
        <b>Последний раз online:</b> {device.last_seen.strftime('%Y-%m-%d %H:%M:%S')}<br>
        <b>Оценка риска:</b> {device.risk_score:.1f}/10
        """
        
        QMessageBox.information(self, "Информация об устройстве", info_text)
    
    def reclassify_device(self, device: NetworkDevice):
        """Переклассифицировать устройство"""
        print(f"Переклассифицирую устройство {device.ip_address}")
        # Здесь будет вызов классификатора
    
    def isolate_device(self, device: NetworkDevice):
        """Изолировать устройство"""
        from PyQt6.QtWidgets import QMessageBox
        
        reply = QMessageBox.question(
            self,
            "Изолировать устройство",
            f"Вы уверены, что хотите изолировать устройство {device.get_friendly_name()}?\n"
            "Оно будет помещено в отдельную зону без доступа к другим устройствам.",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )
        
        if reply == QMessageBox.StandardButton.Yes:
            print(f"Изолирую устройство {device.ip_address}")
