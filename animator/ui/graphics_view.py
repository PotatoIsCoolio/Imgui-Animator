from PySide6.QtWidgets import *
from PySide6.QtCore import *
from PySide6.QtGui import *
# ck = check btw im just using slang :rollingeyes:
class CustomGraphicsView(QGraphicsView):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setRenderHint(QPainter.Antialiasing)
        self.setRenderHint(QPainter.TextAntialiasing)
        self.setRenderHint(QPainter.SmoothPixmapTransform)
        self.setViewportUpdateMode(QGraphicsView.FullViewportUpdate)
        self.setDragMode(QGraphicsView.RubberBandDrag)
        self.setAcceptDrops(True)
        self.scaleFactor = 1.0
    
    def wheelEvent(self, event):
        if event.modifiers() & Qt.ControlModifier:
            zoomInFactor = 1.15
            zoomOutFactor = 1 / zoomInFactor
            
            oldPos = self.mapToScene(event.position().toPoint())
            
            if event.angleDelta().y() > 0:
                zoomFactor = zoomInFactor
                self.scaleFactor *= zoomFactor
            else:
                zoomFactor = zoomOutFactor
                self.scaleFactor *= zoomFactor
            
            self.scale(zoomFactor, zoomFactor)
            
            newPos = self.mapToScene(event.position().toPoint())
            
            delta = newPos - oldPos
            self.translate(delta.x(), delta.y())
            
            event.accept()
        else:
            super().wheelEvent(event)
    
    def keyPressEvent(self, event):
        if event.key() == Qt.Key_Delete:
            window = self.window()
            if hasattr(window, 'deleteSelectedItems'): #ck
                window.deleteSelectedItems()
                event.accept()
                return
        
        if event.key() == Qt.Key_C and event.modifiers() & Qt.ControlModifier:
            window = self.window()
            if hasattr(window, 'copySelectedItems'): #ck
                window.copySelectedItems()
                event.accept()
                return
        
        if event.key() == Qt.Key_V and event.modifiers() & Qt.ControlModifier:
            window = self.window()
            if hasattr(window, 'pasteItems'): #ck
                window.pasteItems()
                event.accept()
                return
        
        if event.key() == Qt.Key_D and event.modifiers() & Qt.ControlModifier:
            window = self.window()
            if hasattr(window, 'duplicateSelectedItems'): #ck
                window.duplicateSelectedItems()
                event.accept()
                return
        
        if event.key() == Qt.Key_Z and event.modifiers() & Qt.ControlModifier:
            window = self.window()
            if hasattr(window, 'undoStack'):#ck
                window.undoStack.undo()
                event.accept()
                return
        
        if event.key() == Qt.Key_Y and event.modifiers() & Qt.ControlModifier:
            window = self.window()
            if hasattr(window, 'undoStack'):#ckk
                window.undoStack.redo()
                event.accept()
                return
        
        if event.key() in [Qt.Key_Left, Qt.Key_Right, Qt.Key_Up, Qt.Key_Down]:
            window = self.window()
            if hasattr(window, 'snapToGrid'):#ck
                deltaX = 0
                deltaY = 0
                
                if event.key() == Qt.Key_Left:
                    deltaX = -1
                elif event.key() == Qt.Key_Right:
                    deltaX = 1
                elif event.key() == Qt.Key_Up:
                    deltaY = -1
                elif event.key() == Qt.Key_Down:
                    deltaY = 1
                
                if hasattr(window, "snapToGrid") and window.snapToGrid:
                    deltaX *= window.gridSize
                    deltaY *= window.gridSize
                
                for item in self.scene().selectedItems():
                    item.setPos(item.pos().x() + deltaX, item.pos().y() + deltaY)
                
                event.accept()
                return
        
        super().keyPressEvent(event)
    
    def dragEnterEvent(self, event):
        if event.mimeData().hasUrls() or event.mimeData().hasImage():
            event.acceptProposedAction()
        else:
            super().dragEnterEvent(event)
    
    def dragMoveEvent(self, event):
        if event.mimeData().hasUrls() or event.mimeData().hasImage():
            event.acceptProposedAction()
        else:
            super().dragMoveEvent(event)
    
    def dropEvent(self, event):
        if event.mimeData().hasUrls():
            window = self.window()
            if hasattr(window, 'importImage'):#ck
                for url in event.mimeData().urls():
                    filePath = url.toLocalFile()
                    if filePath.lower().endswith(('.png', '.jpg', '.jpeg', '.gif', '.bmp')):
                        window.importImage(filePath, self.mapToScene(event.pos().toPoint()))
                    elif filePath.lower().endswith(('.ttf', '.otf')):
                        window.importFont(filePath)
                
                event.acceptProposedAction()
        elif event.mimeData().hasImage():
            window = self.window()
            if hasattr(window, 'importImageData'): #ck
                image = QImage(event.mimeData().imageData())
                if not image.isNull():
                    tempFile = QBuffer()
                    tempFile.open(QIODevice.WriteOnly)
                    image.save(tempFile, "PNG")
                    
                    window.importImageData(tempFile.data(), self.mapToScene(event.pos().toPoint()))
                
                event.acceptProposedAction()
        else:
            super().dropEvent(event)
# dont make your code compicated
#NoComplicatedCode2025!