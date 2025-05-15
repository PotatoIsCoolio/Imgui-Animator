from PySide6.QtWidgets import *
from PySide6.QtCore import *
from PySide6.QtGui import *

class CustomTextItem(QGraphicsTextItem):
    def __init__(self, text="Text", font=None):
        super().__init__(text)
        self.setFlag(QGraphicsTextItem.ItemIsMovable)
        self.setFlag(QGraphicsTextItem.ItemIsSelectable)
        self.setFlag(QGraphicsTextItem.ItemSendsGeometryChanges)
        self.setAcceptHoverEvents(True)
        self.shapeType = "text"
        self.handles = []
        self.startPos = None
        
        if font:
            self.setFont(font)
        else:
            self.setFont(QFont("Arial", 16))
            
        self.setDefaultTextColor(QColor("white"))
        self.addResizeHandles()
    
    def addResizeHandles(self):
        from animator.items.resize_handle import ResizeHandle
        positions = ["top-left", "top-right", "bottom-right", "bottom-left"]
        
        for position in positions:
            handle = ResizeHandle(self, position)
            self.handles.append(handle)
        
        for handle in self.handles:
            handle.setVisible(self.isSelected())
    
    def updateHandles(self):
        for handle in self.handles:
            handle.updatePosition()
    
    def itemChange(self, change, value):
        if change == QGraphicsTextItem.ItemSelectedChange:
            if self.handles:
                for handle in self.handles:
                    handle.setVisible(bool(value))
            
            if value and self.scene():
                if hasattr(self.scene(), "parent") and self.scene().parent():
                    window = self.scene().parent()
                    if hasattr(window, "updatePropertyPanel"):
                        window.updatePropertyPanel(self)
        
        elif change == QGraphicsTextItem.ItemPositionChange:
            if self.scene() and hasattr(self.scene(), "parent") and self.scene().parent():
                window = self.scene().parent()
                if hasattr(window, "snapToGrid") and window.snapToGrid:
                    gridSize = window.gridSize
                    x = round(value.x() / gridSize) * gridSize
                    y = round(value.y() / gridSize) * gridSize
                    return QPointF(x, y)
        
        elif change == QGraphicsTextItem.ItemPositionHasChanged:
            if self.handles:
                for handle in self.handles:
                    handle.updatePosition()
        
        return super().itemChange(change, value)
    
    def mousePressEvent(self, event):
        self.startPos = self.pos()
        super().mousePressEvent(event)
    
    def mouseReleaseEvent(self, event):
        if self.startPos != self.pos():
            window = None
            for widget in QApplication.topLevelWidgets():
                if hasattr(widget, 'animatedItems'):
                    window = widget
                    break
            
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
    # Goth mommy's or femboys?
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
            if hasattr(widget, 'animatedItems'):
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
            
            editTextAction = menu.addAction("Edit Text")
            editTextAction.triggered.connect(lambda: window.editTextItem(self))
            
            menu.addSeparator()
            
            addKeyframeAction = menu.addAction("Add Keyframe")
            addKeyframeAction.triggered.connect(window.addKeyframeAtCurrentFrame)
            
            menu.addSeparator()
            
            bringToFrontAction = menu.addAction("Bring to Front")
            bringToFrontAction.triggered.connect(lambda: window.changeItemZOrder(self, 1))
            
            sendToBackAction = menu.addAction("Send to Back")
            sendToBackAction.triggered.connect(lambda: window.changeItemZOrder(self, -1))
            
            menu.exec(event.screenPos())
