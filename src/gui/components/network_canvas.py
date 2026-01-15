"""
Холст для визуального проектирования зон безопасности
"""

from PyQt6.QtWidgets import (
    QGraphicsView, QGraphicsScene, QGraphicsRectItem,
    QGraphicsTextItem, QGraphicsItem, QMenu, QInputDialog,
    QColorDialog
)
from PyQt6.QtCore import Qt, QPointF, QRectF, pyqtSignal
from PyQt6.QtGui import (
    QBrush, QPen, QColor, QFont, QPainter, QDragEnterEvent,
    QDropEvent, QMouseEvent
)
import json

from ...core.models import SecurityZone, ZoneType, NetworkDevice
from ...core.constants import ZONE_COLORS

class ZoneItem(QGraphicsRectItem):
    """Элемент зоны на холсте"""
    
    zone_changed = pyqtSignal(str)  # zone_name
    
    def __init__(self, zone: SecurityZone, x: float, y: float):
        super().__init__(x, y, 200, 150)
        
        self.zone = zone
        self.device_items = []
        
        self.setup_appearance()
        self.setFlag(QGraphicsItem.GraphicsItemFlag.ItemIsMovable, True)
        self.setFlag(QGraphicsItem.GraphicsItemFlag.ItemIsSelectable, True)
        self.setFlag(QGraphicsItem.GraphicsItemFlag.ItemSendsGeometryChanges, True)
    
    def setup_appearance(self):
        """Настройка внешнего вида зоны"""
        color = QColor(self.zone.color)
        
        # Основной прямоугольник
        self.setBrush(QBrush(color.lighter(130)))  # Светлее на 30%
        self.setPen(QPen(Qt.GlobalColor.black, 2))
        
        # Заголовок зоны
        self.title_item = QGraphicsTextItem(self.zone.name, self)
        self.title_item.setFont(QFont("Arial", 12, QFont.Weight.Bold))
        self.title_item.setDefaultTextColor(Qt.GlobalColor.black)
        self.title_item.setPos(10, 5)
        
        # Счетчик устройств
        device_count = len(self.zone.devices)
        self.count_item = QGraphicsTextItem(f"Устройств: {device_count}", self)
        self.count_item.setFont(QFont("Arial", 9))
        self.count_item.setDefaultTextColor(Qt.GlobalColor.darkGray)
        self.count_item.setPos(10, 30)
    
    def add_device_item(self, device_item):
        """Добавить элемент устройства в зону"""
        device_item.setParentItem(self)
        self.device_items.append(device_item)
        self.arrange_devices()
        self.update_count()
    
    def remove_device_item(self, device_item):
        """Удалить элемент устройства из зоны"""
        if device_item in self.device_items:
            self.device_items.remove(device_item)
            device_item.setParentItem(None)
            self.arrange_devices()
            self.update_count()
    
    def arrange_devices(self):
        """Расположить устройства внутри зоны"""
        x, y = 20, 50  # Начальная позиция
        item_size = 40
        
        for i, device_item in enumerate(self.device_items):
            device_item.setPos(x, y)
            
            x += item_size + 10
            if x + item_size > 180:  # Перенос на следующую строку
                x = 20
                y += item_size + 5
    
    def update_count(self):
        """Обновить счетчик устройств"""
        self.count_item.setPlainText(f"Устройств: {len(self.device_items)}")
    
    def mouseDoubleClickEvent(self, event):
        """Обработка двойного клика для редактирования"""
        self.edit_zone()
        super().mouseDoubleClickEvent(event)
    
    def contextMenuEvent(self, event):
        """Контекстное меню для зоны"""
        menu = QMenu()
        
        edit_action = menu.addAction("✏️ Переименовать")
        color_action = menu.addAction("🎨 Изменить цвет")
        menu.addSeparator()
        delete_action = menu.addAction("🗑️ Удалить зону")
        menu.addSeparator()
        add_device_action = menu.addAction("➕ Добавить устройство")
        
        action = menu.exec(event.screenPos())
        
        if action == edit_action:
            self.edit_zone()
        elif action == color_action:
            self.change_color()
        elif action == delete_action:
            self.delete_zone()
        elif action == add_device_action:
            self.add_device_dialog()
    
    def edit_zone(self):
        """Редактировать название зоны"""
        from PyQt6.QtWidgets import QInputDialog
        
        new_name, ok = QInputDialog.getText(
            None,
            "Переименовать зону",
            "Введите новое название:",
            text=self.zone.name
        )
        
        if ok and new_name:
            self.zone.name = new_name
            self.title_item.setPlainText(new_name)
            self.zone_changed.emit(new_name)
    
    def change_color(self):
        """Изменить цвет зоны"""
        color = QColorDialog.getColor(
            QColor(self.zone.color),
            None,
            "Выберите цвет зоны"
        )
        
        if color.isValid():
            self.zone.color = color.name()
            self.setBrush(QBrush(color.lighter(130)))
    
    def delete_zone(self):
        """Удалить зону"""
        from PyQt6.QtWidgets import QMessageBox
        
        reply = QMessageBox.question(
            None,
            "Удалить зону",
            f"Вы уверены, что хотите удалить зону '{self.zone.name}'?\n"
            "Все устройства будут возвращены в список.",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )
        
        if reply == QMessageBox.StandardButton.Yes:
            # Возвращаем устройства
            for device_item in self.device_items[:]:
                self.remove_device_item(device_item)
            
            # Удаляем зону
            scene = self.scene()
            if scene:
                scene.removeItem(self)
    
    def add_device_dialog(self):
        """Диалог добавления устройства"""
        print("Открываю диалог добавления устройства")
        # Здесь будет диалог выбора устройства

class NetworkCanvas(QGraphicsView):
    """Холст для проектирования зон безопасности"""
    
    zone_created = pyqtSignal(str)  # zone_name
    zone_deleted = pyqtSignal(str)  # zone_name
    device_dropped = pyqtSignal(str, str)  # device_id, zone_name
    
    def __init__(self, parent=None):
        super().__init__(parent)
        
        self.scene = QGraphicsScene()
        self.setScene(self.scene)
        
        self.setup_ui()
        self.zones = {}  # name -> ZoneItem
        self.create_default_zones()
    
    def setup_ui(self):
        """Настройка интерфейса холста"""
        self.setRenderHint(QPainter.RenderHint.Antialiasing)
        self.setDragMode(QGraphicsView.DragMode.RubberBandDrag)
        self.setAcceptDrops(True)
        
        # Фон
        self.scene.setBackgroundBrush(QBrush(QColor(240, 240, 240)))
        
        # Контекстное меню холста
        self.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)
        self.customContextMenuRequested.connect(self.show_canvas_menu)
    
    def create_default_zones(self):
        """Создать зоны по умолчанию"""
        default_zones = [
            SecurityZone("Доверенные", ZoneType.TRUSTED, color=ZONE_COLORS["trusted"]),
            SecurityZone("Умный дом", ZoneType.IOT, color=ZONE_COLORS["iot"]),
            SecurityZone("Гости", ZoneType.GUEST, color=ZONE_COLORS["guest"]),
        ]
        
        x, y = 50, 50
        for zone in default_zones:
            self.add_zone(zone, x, y)
            x += 250
    
    def add_zone(self, zone: SecurityZone, x: float, y: float):
        """Добавить зону на холст"""
        zone_item = ZoneItem(zone, x, y)
        self.scene.addItem(zone_item)
        self.zones[zone.name] = zone_item
        
        # Подключаем сигналы
        zone_item.zone_changed.connect(self.on_zone_changed)
        
        self.zone_created.emit(zone.name)
        return zone_item
    
    def dragEnterEvent(self, event: QDragEnterEvent):
        """Обработка входа перетаскиваемого объекта"""
        if event.mimeData().hasText():
            event.acceptProposedAction()
    
    def dragMoveEvent(self, event):
        """Обработка перемещения перетаскиваемого объекта"""
        event.acceptProposedAction()
    
    def dropEvent(self, event: QDropEvent):
        """Обработка отпускания перетаскиваемого объекта"""
        try:
            # Получаем данные устройства
            device_data = json.loads(event.mimeData().text())
            device_ip = device_data['ip_address']
            
            # Находим зону, куда бросили устройство
            pos = self.mapToScene(event.position().toPoint())
            items = self.scene.items(pos)
            
            for item in items:
                if isinstance(item, ZoneItem):
                    # Создаем элемент устройства
                    from .device_item import DeviceItem
                    device_item = DeviceItem(
                        NetworkDevice(ip_address=device_ip)
                    )
                    device_item.setPos(item.mapFromScene(pos))
                    
                    # Добавляем устройство в зону
                    item.add_device_item(device_item)
                    
                    # Сигнал о добавлении устройства
                    self.device_dropped.emit(device_ip, item.zone.name)
                    event.acceptProposedAction()
                    return
            
            # Если не попали в зону, создаем новую
            self.create_zone_at(pos, device_ip)
            
        except (json.JSONDecodeError, KeyError) as e:
            print(f"Ошибка обработки drop: {e}")
        
        event.acceptProposedAction()
    
    def create_zone_at(self, pos: QPointF, first_device_ip: str = None):
        """Создать новую зону в указанной позиции"""
        from PyQt6.QtWidgets import QInputDialog
        
        zone_name, ok = QInputDialog.getText(
            None,
            "Новая зона",
            "Введите название зоны:",
            text="Новая зона"
        )
        
        if ok and zone_name:
            # Создаем зону
            zone = SecurityZone(
                zone_name,
                ZoneType.CUSTOM,
                color=ZONE_COLORS["custom"]
            )
            
            zone_item = self.add_zone(zone, pos.x(), pos.y())
            
            # Если есть устройство, добавляем его
            if first_device_ip:
                from .device_item import DeviceItem
                device_item = DeviceItem(
                    NetworkDevice(ip_address=first_device_ip)
                )
                zone_item.add_device_item(device_item)
                self.device_dropped.emit(first_device_ip, zone_name)
    
    def show_canvas_menu(self, position):
        """Показать контекстное меню холста"""
        menu = QMenu(self)
        
        create_zone_action = menu.addAction("➕ Создать зону")
        menu.addSeparator()
        arrange_zones_action = menu.addAction("🔧 Упорядочить зоны")
        clear_action = menu.addAction("🗑️ Очистить холст")
        
        action = menu.exec(self.mapToGlobal(position))
        
        if action == create_zone_action:
            self.create_zone_at(self.mapToScene(position))
        elif action == arrange_zones_action:
            self.arrange_zones()
        elif action == clear_action:
            self.clear_canvas()
    
    def arrange_zones(self):
        """Упорядочить зоны на холсте"""
        zone_items = list(self.zones.values())
        x, y = 50, 50
        
        for zone_item in zone_items:
            zone_item.setPos(x, y)
            x += 250
            
            if x > 800:  # Перенос на следующую строку
                x = 50
                y += 200
    
    def clear_canvas(self):
        """Очистить холст"""
        from PyQt6.QtWidgets import QMessageBox
        
        reply = QMessageBox.question(
            None,
            "Очистить холст",
            "Вы уверены, что хотите очистить холст?\n"
            "Все зоны и устройства будут удалены.",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )
        
        if reply == QMessageBox.StandardButton.Yes:
            for zone_item in list(self.zones.values()):
                self.scene.removeItem(zone_item)
            self.zones.clear()
    
    def on_zone_changed(self, zone_name: str):
        """Обработка изменения зоны"""
        print(f"Зона изменена: {zone_name}")
        # Здесь можно обновить что-то в модели данных
