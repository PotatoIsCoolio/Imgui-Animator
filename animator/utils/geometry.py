import math
from PySide6.QtWidgets import *
from PySide6.QtCore import *
from PySide6.QtGui import *

# had my bestie Cannibal do this math yap :p

def regularPolygon(sides, radius):
    angle = 2 * math.pi / sides
    points = [QPointF(radius + math.cos(i * angle) * radius, 
                     radius + math.sin(i * angle) * radius) 
             for i in range(sides)]
    return QPolygonF(points)

def starPolygon(points, outerRadius, innerRadius):
    polygon = QPolygonF()
    centerX = outerRadius
    centerY = outerRadius
    
    for i in range(points * 2):
        angle = math.pi * i / points
        radius = innerRadius if i % 2 else outerRadius
        x = centerX + radius * math.sin(angle)
        y = centerY + radius * math.cos(angle)
        polygon.append(QPointF(x, y))
    
    return polygon
