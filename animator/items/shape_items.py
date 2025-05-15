from PySide6.QtWidgets import *
from PySide6.QtCore import *
from PySide6.QtGui import *

from animator.items.base_item import CustomGraphicsItem

class CustomRectItem(CustomGraphicsItem):
    def __init__(self, x, y, w, h, pen, brush, isSquare=False):
        super().__init__()
        self.rect = QRectF(0, 0, w, h)
        self.pen = pen
        self.brush = brush
        self.isSquare = isSquare
        self.shapeType = "Square" if isSquare else "Rectangle"
        self.setPos(x, y)
        self.addResizeHandles()
        
    def boundingRect(self):
        return self.rect
        
    def paint(self, painter, option, widget):
        painter.setPen(self.pen)
        painter.setBrush(self.brush)
        painter.drawRect(self.rect)
        
        if self.isSelected():
            painter.setPen(QPen(QColor(255, 255, 0), 1, Qt.DashLine))
            painter.setBrush(Qt.NoBrush)
            painter.drawRect(self.rect)

class CustomEllipseItem(CustomGraphicsItem):
    def __init__(self, x, y, w, h, pen, brush):
        super().__init__()
        self.rect = QRectF(0, 0, w, h)
        self.pen = pen
        self.brush = brush
        self.shapeType = "Circle" if w == h else "Ellipse"
        self.isSquare = (w == h)
        self.setPos(x, y)
        self.addResizeHandles()
        
    def boundingRect(self):
        return self.rect
        
    def paint(self, painter, option, widget):
        painter.setPen(self.pen)
        painter.setBrush(self.brush)
        painter.drawEllipse(self.rect)
        
        if self.isSelected():
            painter.setPen(QPen(QColor(255, 255, 0), 1, Qt.DashLine))
            painter.setBrush(Qt.NoBrush)
            painter.drawRect(self.rect)

class CustomPolygonItem(CustomGraphicsItem):
    def __init__(self, x, y, polygon, pen, brush, shapeType="Polygon"):
        super().__init__()
        self.polygon = polygon
        self.pen = pen
        self.brush = brush
        self.shapeType = shapeType
        self.setPos(x, y)
        self.addResizeHandles()
        
    def boundingRect(self):
        return self.polygon.boundingRect()
        
    def paint(self, painter, option, widget):
        painter.setPen(self.pen)
        painter.setBrush(self.brush)
        painter.drawPolygon(self.polygon)
        
        if self.isSelected():
            painter.setPen(QPen(QColor(255, 255, 0), 1, Qt.DashLine))
            painter.setBrush(Qt.NoBrush)
            painter.drawRect(self.boundingRect())
