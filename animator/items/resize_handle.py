from PySide6.QtWidgets import *
from PySide6.QtCore import *
from PySide6.QtGui import *

class ResizeHandle(QGraphicsRectItem):
    def __init__(self, parent, position):
        super().__init__(0, 0, 5, 5, parent) # Change the vector scales to change the scale button sir!
        self.position = position # I recommend around 0,0,5,5 or 0,0,8,8
        self.setFlag(QGraphicsItem.ItemIsMovable, False)
        self.setFlag(QGraphicsItem.ItemIsSelectable, False)
        self.setFlag(QGraphicsItem.ItemSendsGeometryChanges, False)
        self.setAcceptHoverEvents(True)
        self.setBrush(QBrush(QColor(255, 255, 0)))
        self.setPen(QPen(QColor(0, 0, 0)))
        self.setCursor(self._getCursor())
        self.setZValue(1)
        self.setVisible(False)
        self.updatePosition()
    
    def _getCursor(self):
        if self.position in ["top-left", "bottom-right"]:
            return Qt.SizeFDiagCursor
        elif self.position in ["top-right", "bottom-left"]:
            return Qt.SizeBDiagCursor
        elif self.position in ["top", "bottom"]:
            return Qt.SizeVerCursor
        elif self.position in ["left", "right"]:
            return Qt.SizeHorCursor
        return Qt.SizeAllCursor
    
    def updatePosition(self):
        if not self.parentItem():
            return
        
        parentRect = self.parentItem().boundingRect()
        x, y = 0, 0
        
        if "left" in self.position:
            x = parentRect.left() - 4
        elif "right" in self.position:
            x = parentRect.right() - 4
        else:
            x = parentRect.left() + parentRect.width() / 2 - 4
        
        if "top" in self.position:
            y = parentRect.top() - 4
        elif "bottom" in self.position:
            y = parentRect.bottom() - 4
        else:
            y = parentRect.top() + parentRect.height() / 2 - 4
        
        self.setPos(x, y)
    
    def mousePressEvent(self, event):
        self.startPos = event.pos()
        self.startParentRect = self.parentItem().boundingRect()
        self.startParentPos = self.parentItem().pos()
        event.accept()
    
    def mouseMoveEvent(self, event):
        if not self.parentItem():
            return
        
        delta = event.pos() - self.startPos
        parent = self.parentItem()
        
        window = None
        for widget in QApplication.topLevelWidgets():
            if hasattr(widget, 'animatedItems'):  # I really need to make a more simple way to check this ugh
                window = widget
                break
        
        if hasattr(parent, "rect"):
            originalRect = QRectF(parent.rect)
        
        if hasattr(parent, "rect"):
            newRect = QRectF(parent.rect)
            
            if "left" in self.position:
                newWidth = self.startParentRect.width() - delta.x()
                if newWidth > 10:
                    newRect.setLeft(newRect.right() - newWidth)
                    parent.setPos(self.startParentPos.x() + delta.x(), parent.pos().y())
            
            if "right" in self.position:
                newWidth = self.startParentRect.width() + delta.x()
                if newWidth > 10:
                    newRect.setWidth(newWidth)
            
            if "top" in self.position:
                newHeight = self.startParentRect.height() - delta.y()
                if newHeight > 10:
                    newRect.setTop(newRect.bottom() - newHeight)
                    parent.setPos(parent.pos().x(), self.startParentPos.y() + delta.y())
            
            if "bottom" in self.position:
                newHeight = self.startParentRect.height() + delta.y()
                if newHeight > 10:
                    newRect.setHeight(newHeight)
            
            if hasattr(parent, "isSquare") and parent.isSquare:
                size = max(newRect.width(), newRect.height())
                newRect.setWidth(size)
                newRect.setHeight(size)
            
            parent.rect = newRect
            parent.update()
            
            if hasattr(parent, "updateHandles"):
                parent.updateHandles()
            
            if window and hasattr(window, "currentItem") and window.currentItem == parent:
                if hasattr(window, "updateShapeSizeFromItem"):
                    window.updateShapeSizeFromItem()
            
            event.accept()
    
    def mouseReleaseEvent(self, event):
        if hasattr(self.parentItem(), "rect"):
            window = None
            for widget in QApplication.topLevelWidgets():
                if hasattr(widget, 'animatedItems'):  # Checkmate
                    window = widget
                    break
            
            if window and hasattr(self, "startParentRect"):
                from animator.commands.undo_commands import ModifyItemCommand
                cmd = ModifyItemCommand(
                    self.parentItem(),
                    "rect",
                    self.startParentRect,
                    QRectF(self.parentItem().rect)
                )
                if hasattr(window, "undoStack"):
                    window.undoStack.push(cmd)
        
        event.accept()
