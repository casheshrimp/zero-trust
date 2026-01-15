from PyQt6.QtWidgets import (QGraphicsView, QGraphicsScene, 
                             QGraphicsRectItem, QGraphicsTextItem)
from PyQt6.QtCore import Qt, QPointF, QRectF
from PyQt6.QtGui import QBrush, QPen, QColor, QFont

class SecurityZone(QGraphicsRectItem):
    def __init__(self, name, color, x, y, width=200, height=150):
        super().__init__(x, y, width, height)
        
        self.name = name
        self.devices = []
        
        # Настройка внешнего вида
        self.setBrush(QBrush(color))
        self.setPen(QPen(Qt.GlobalColor.black, 2))
        
        # Добавляем текст с названием зоны
        self.text_item = QGraphicsTextItem(name, self)
        self.text_item.setFont(QFont("Arial", 12, QFont.Weight.Bold))
        self.text_item.setPos(10, 10)
        
    def add_device(self, device_item):
        """Добавить устройство в зону"""
        device_item.setParentItem(self)
        self.devices.append(device_item)
        self.arrange_devices()
        
    def arrange_devices(self):
        """Расположить устройства внутри зоны"""
        x, y = 20, 40
        for device in self.devices:
            device.setPos(x, y)
            x += 60
            if x > 150:  # Перенос на следующую строку
                x = 20
                y += 60

class NetworkCanvas(QGraphicsView):
    def __init__(self):
        super().__init__()
        
        self.scene = QGraphicsScene()
        self.setScene(self.scene)
        
        self.setRenderHint(QPainter.RenderHint.Antialiasing)
        self.setDragMode(QGraphicsView.DragMode.RubberBandDrag)
        
        # Создаем зоны по умолчанию
        self.create_default_zones()
        
    def create_default_zones(self):
        """Создать стандартные зоны безопасности"""
        zones = [
            ("Доверенные", QColor(144, 238, 144), 50, 50),
            ("Умный дом", QColor(255, 255, 153), 300, 50),
            ("Гости", QColor(211, 211, 211), 550, 50),
        ]
        
        self.zones = {}
        for name, color, x, y in zones:
            zone = SecurityZone(name, color, x, y)
            self.scene.addItem(zone)
            self.zones[name] = zone
