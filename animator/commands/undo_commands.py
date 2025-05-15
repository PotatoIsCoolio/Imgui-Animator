from PySide6.QtWidgets import *
from PySide6.QtCore import *
from PySide6.QtGui import *

class AddItemCommand(QUndoCommand):
    def __init__(self, scene, item, animatedItem, parent=None):
        super().__init__(parent)
        self.scene = scene
        self.item = item
        self.animatedItem = animatedItem
        self.setText(f"Add {animatedItem.name}")
    
    def undo(self):
        self.scene.removeItem(self.item)
        window = None
        for widget in QApplication.topLevelWidgets():
            if hasattr(widget, 'animatedItems'): # Checkmate
                window = widget
                break
        
        if window:
            window.animatedItems = [ai for ai in window.animatedItems if ai != self.animatedItem]
    
    def redo(self):
        self.scene.addItem(self.item)
        window = None
        for widget in QApplication.topLevelWidgets():
            if hasattr(widget, 'animatedItems'): # Checkmates
                window = widget
                break
        
        if window and self.animatedItem not in window.animatedItems:
            window.animatedItems.append(self.animatedItem)

class RemoveItemCommand(QUndoCommand):
    def __init__(self, scene, items, animatedItems, parent=None):
        super().__init__(parent)
        self.scene = scene
        self.items = items.copy()
        self.animatedItems = animatedItems.copy()
        self.setText(f"Remove {len(items)} item(s)")
    
    def undo(self):
        window = None
        for widget in QApplication.topLevelWidgets():
            if hasattr(widget, 'animatedItems'): # Checkmtae
                window = widget
                break
        
        for item in self.items:
            self.scene.addItem(item)
        
        if window:
            for ai in self.animatedItems:
                if ai not in window.animatedItems:
                    window.animatedItems.append(ai)
    
    def redo(self):
        window = None
        for widget in QApplication.topLevelWidgets():
            if hasattr(widget, 'animatedItems'):
                window = widget
                break
        
        for item in self.items:
            self.scene.removeItem(item)
        
        if window:
            for ai in self.animatedItems:
                if ai in window.animatedItems:
                    window.animatedItems.remove(ai)

class ModifyItemCommand(QUndoCommand):
    def __init__(self, item, propertyName, oldValue, newValue, parent=None):
        super().__init__(parent)
        self.item = item
        self.propertyName = propertyName
        self.oldValue = oldValue
        self.newValue = newValue
        self.setText(f"Modify {propertyName}")
    
    def undo(self):
        self._setProperty(self.oldValue)
    
    def redo(self):
        self._setProperty(self.newValue)
    
    def _setProperty(self, value):
        if self.propertyName == "position":
            self.item.setPos(value)
        elif self.propertyName == "transform":
            self.item.setTransform(value)
        elif self.propertyName == "opacity":
            self.item.setOpacity(value)
        elif self.propertyName == "text" and hasattr(self.item, "setPlainText"):
            self.item.setPlainText(value)
        elif self.propertyName == "font" and hasattr(self.item, "setFont"):
            self.item.setFont(value)
        elif self.propertyName == "color" and hasattr(self.item, "setDefaultTextColor"):
            self.item.setDefaultTextColor(value)
        elif self.propertyName == "pen" and hasattr(self.item, "pen"):
            self.item.pen = value
            self.item.update()
        elif self.propertyName == "brush" and hasattr(self.item, "brush"):
            self.item.brush = value
            self.item.update()
        elif self.propertyName == "rect" and hasattr(self.item, "rect"):
            self.item.rect = value
            self.item.update()

class AddKeyframeCommand(QUndoCommand):
    def __init__(self, animatedItem, keyframe, parent=None):
        super().__init__(parent)
        self.animatedItem = animatedItem
        self.keyframe = keyframe
        self.setText(f"Add keyframe at frame {keyframe.frame}")
    
    def undo(self):
        self.animatedItem.keyframes = [kf for kf in self.animatedItem.keyframes if kf.frame != self.keyframe.frame]
    
    def redo(self):
        for i, kf in enumerate(self.animatedItem.keyframes):
            if kf.frame == self.keyframe.frame:
                self.animatedItem.keyframes[i] = self.keyframe
                return
        
        self.animatedItem.keyframes.append(self.keyframe)
        self.animatedItem.keyframes.sort(key=lambda kf: kf.frame)

class RemoveKeyframeCommand(QUndoCommand):
    def __init__(self, animatedItem, keyframe, parent=None):
        super().__init__(parent)
        self.animatedItem = animatedItem
        self.keyframe = keyframe
        self.keyframeIndex = -1
        self.setText(f"Remove keyframe at frame {keyframe.frame}")
    
    def undo(self):
        for i, kf in enumerate(self.animatedItem.keyframes):
            if kf.frame > self.keyframe.frame:
                self.animatedItem.keyframes.insert(i, self.keyframe)
                return
        
        self.animatedItem.keyframes.append(self.keyframe)
    
    def redo(self):
        for i, kf in enumerate(self.animatedItem.keyframes):
            if kf.frame == self.keyframe.frame:
                self.keyframeIndex = i
                self.animatedItem.keyframes.pop(i)
                break
