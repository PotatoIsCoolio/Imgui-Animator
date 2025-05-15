import math, os
# Imports everything you need
from PySide6.QtWidgets import *
from PySide6.QtCore import *
from PySide6.QtGui import *

class CustomGraphicsItem(QGraphicsItem):
    def __init__(self):
        super().__init__()
        self.setFlag(QGraphicsItem.ItemIsMovable)
        self.setFlag(QGraphicsItem.ItemIsSelectable)
        self.setFlag(QGraphicsItem.ItemSendsGeometryChanges)
        self.setAcceptHoverEvents(True)
        self.shapeType = "unknown"
        self.handles = []
        self.startPos = None
        self.startTransform = None
        
    def itemChange(self, change, value):
        if change == QGraphicsItem.ItemSelectedChange:
            if self.handles:
                for handle in self.handles:
                    handle.setVisible(bool(value))
            
            if value and self.scene():
                if hasattr(self.scene(), "parent") and self.scene().parent():
                    window = self.scene().parent()
                    if hasattr(window, "updatePropertyPanel"):
                        window.updatePropertyPanel(self)
        
        elif change == QGraphicsItem.ItemPositionChange:
            if self.scene() and hasattr(self.scene(), "parent") and self.scene().parent():
                window = self.scene().parent()
                if hasattr(window, "snapToGrid") and window.snapToGrid:
                    gridSize = window.gridSize
                    x = round(value.x() / gridSize) * gridSize
                    y = round(value.y() / gridSize) * gridSize
                    return QPointF(x, y)
        
        elif change == QGraphicsItem.ItemPositionHasChanged:
            if self.handles:
                for handle in self.handles:
                    handle.updatePosition()
        
        return super().itemChange(change, value)
    
    def mousePressEvent(self, event):
        self.startPos = self.pos()
        self.startTransform = self.transform()
        super().mousePressEvent(event)
    
    def mouseReleaseEvent(self, event):
        if self.startPos != self.pos():
            window = None
            for widget in QApplication.topLevelWidgets():
                if hasattr(widget, 'animatedItems'):  # God check for AnimatorMainWindow 
                    window = widget
                    break # SLAM ON THE BREAKS YO!
            
            if window:
                from animator.commands.undo_commands import ModifyItemCommand
                cmd = ModifyItemCommand(
                    self,
                    "position",
                    self.startPos,
                    self.pos()
                )
                window.undoStack.push(cmd)
        
        super().mouseReleaseEvent(event)
    
    def contextMenuEvent(self, event):
        menu = QMenu()
        menu.setStyleSheet("""
            QMenu {
                background-color: #2d2d2d;
                color: #f0f0f0;
                border: 1px solid #3d3d3d;
            }
            QMenu::item {
                padding: 5px 20px 5px 20px;
            }
            QMenu::item:selected {
                background-color: #0078d7;
            }
            QMenu::separator {
                height: 1px;
                background-color: #3d3d3d;
                margin: 5px 0px 5px 0px;
            }
        """)
        
        window = None
        for widget in QApplication.topLevelWidgets():
            if hasattr(widget, 'animatedItems'):  # Check for AnimatorMainWindow again >.<
                window = widget
                break
        
        if window:
            deleteAction = menu.addAction("Delete")
            deleteAction.triggered.connect(window.deleteSelectedItems)
            
            copyAction = menu.addAction("Copy")
            copyAction.triggered.connect(window.copySelectedItems)
            
            duplicateAction = menu.addAction("Duplicate")
            duplicateAction.triggered.connect(window.duplicateSelectedItems)
            
            menu.addSeparator()
            
            addKeyframeAction = menu.addAction("Add Keyframe")
            addKeyframeAction.triggered.connect(window.addKeyframeAtCurrentFrame)
            
            menu.addSeparator()
            
            bringToFrontAction = menu.addAction("Bring to Front")
            bringToFrontAction.triggered.connect(lambda: window.changeItemZOrder(self, 1))
            
            sendToBackAction = menu.addAction("Send to Back")
            sendToBackAction.triggered.connect(lambda: window.changeItemZOrder(self, -1))
            
            menu.exec(event.screenPos())
    
    def addResizeHandles(self):
        from animator.items.resize_handle import ResizeHandle # trying not to cause a circular import loop here
        positions = ["top-left", "top", "top-right", "right", "bottom-right", "bottom", "bottom-left", "left"]
        
        for position in positions:
            handle = ResizeHandle(self, position)
            self.handles.append(handle)
        
        for handle in self.handles:
            handle.setVisible(self.isSelected())
    
    def updateHandles(self):
        for handle in self.handles:
            handle.updatePosition()
