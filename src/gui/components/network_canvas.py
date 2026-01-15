"""
Холст для визуализации сети
"""

from PyQt6.QtWidgets import (
    QGraphicsView, QGraphicsScene, QMenu, QGraphicsItem
)
from PyQt6.QtCore import Qt, QRectF, pyqtSignal
from PyQt6.QtGui import (
    QPainter, QBrush, QPen, QColor, QMouseEvent
)

from ...core.models import NetworkDevice, SecurityZone
from .device_item import DeviceItem

class NetworkCanvas(QGraphicsView):
    """Холст для отображения сети"""
    
    device_dropped = pyqtSignal(str, str)  # device_id, zone_name
    selection_changed = pyqtSignal(list)
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.scene = QGraphicsScene(self)
        self.setScene(self.scene)
        
        self.setup_ui()
        self.zones = {}
        self.device_items = {}
        
    def setup_ui(self):
        """Настройка интерфейса холста"""
        self.setRenderHint(QPainter.RenderHint.Antialiasing)
        self.setViewportUpdateMode(QGraphicsView.ViewportUpdateMode.FullViewportUpdate)
        self.setAcceptDrops(True)
        
        # Настройка сцены
        self.scene.setSceneRect(-500, -500, 1000, 1000)
        self.setSceneRect(-500, -500, 1000, 1000)
        
        # Включаем масштабирование колесом мыши
        self.setTransformationAnchor(QGraphicsView.ViewportAnchor.AnchorUnderMouse)
        self.setResizeAnchor(QGraphicsView.ViewportAnchor.AnchorViewCenter)
        
        # Фон
        self.setBackgroundBrush(QBrush(QColor(245, 245, 245)))
    
    def add_zone(self, zone: SecurityZone, position=None):
        """Добавить зону на холст"""
        from .zone_widget import ZoneWidget
        
        if position is None:
            position = self._calculate_zone_position(len(self.zones))
        
        zone_item = ZoneWidget(zone, position[0], position[1])
        self.scene.addItem(zone_item)
        self.zones[zone.name] = zone_item
        
        return zone_item
    
    def _calculate_zone_position(self, index: int):
        """Рассчитать позицию для новой зоны"""
        positions = [
            (-300, -300), (300, -300),
            (-300, 300), (300, 300),
            (0, -300), (0, 300),
            (-300, 0), (300, 0),
        ]
        
        if index < len(positions):
            return positions[index]
        else:
            x = ((index * 250) % 1000) - 500
            y = ((index * 250) // 1000 * 250) - 500
            return (x, y)
    
    def remove_zone(self, zone_name: str):
        """Удалить зону с холста"""
        if zone_name in self.zones:
            zone_item = self.zones[zone_name]
            self.scene.removeItem(zone_item)
            del self.zones[zone_name]
    
    def add_device_to_zone(self, device: NetworkDevice, zone_name: str):
        """Добавить устройство в зону"""
        if zone_name not in self.zones:
            return
        
        zone_item = self.zones[zone_name]
        device_item = zone_item.add_device(device)
        
        if device_item:
            self.device_items[device.ip_address] = (device_item, zone_item)
    
    def remove_device(self, device_ip: str):
        """Удалить устройство с холста"""
        if device_ip in self.device_items:
            device_item, zone_item = self.device_items[device_ip]
            zone_item.remove_device_item(device_item)
            del self.device_items[device_ip]
    
    def clear_canvas(self):
        """Очистить холст"""
        self.zones.clear()
        self.device_items.clear()
        self.scene.clear()
    
    def get_selected_devices(self):
        """Получить выделенные устройства"""
        selected = []
        for item in self.scene.selectedItems():
            if hasattr(item, 'device'):
                selected.append(item.device)
        return selected
    
    def wheelEvent(self, event):
        """Обработка колеса мыши для масштабирования"""
        zoom_factor = 1.15
        if event.angleDelta().y() > 0:
            self.scale(zoom_factor, zoom_factor)
        else:
            self.scale(1.0 / zoom_factor, 1.0 / zoom_factor)
    
    def mousePressEvent(self, event: QMouseEvent):
        """Обработка нажатия мыши"""
        if event.button() == Qt.MouseButton.RightButton:
            self.show_context_menu(event.pos())
        else:
            super().mousePressEvent(event)
    
    def show_context_menu(self, position):
        """Показать контекстное меню холста"""
        menu = QMenu(self)
        
        menu.addAction("📐 Автоматически расположить")
        menu.addSeparator()
        menu.addAction("🗑️ Очистить холст")
        menu.addSeparator()
        menu.addAction("💾 Сохранить схему...")
        
        action = menu.exec(self.mapToGlobal(position))
        
        if action:
            if action.text() == "📐 Автоматически расположить":
                self.auto_arrange()
            elif action.text() == "🗑️ Очистить холст":
                self.clear_canvas()
            elif action.text() == "💾 Сохранить схему...":
                self.export_scheme()
    
    def auto_arrange(self):
        """Автоматически расположить зоны"""
        zones = list(self.zones.values())
        for i, zone in enumerate(zones):
            x, y = self._calculate_zone_position(i)
            zone.setPos(x, y)
    
    def export_scheme(self):
        """Экспортировать схему в изображение"""
        from PyQt6.QtWidgets import QFileDialog
        
        filepath, _ = QFileDialog.getSaveFileName(
            self, "Сохранить схему", "", "PNG (*.png);;JPEG (*.jpg)"
        )
        
        if filepath:
            # Создаем изображение всей сцены
            from PyQt6.QtGui import QImage, QPainter
            
            rect = self.scene.itemsBoundingRect()
            image = QImage(rect.width(), rect.height(), QImage.Format.Format_ARGB32)
            image.fill(Qt.GlobalColor.white)
            
            painter = QPainter(image)
            self.scene.render(painter)
            painter.end()
            
            image.save(filepath)
