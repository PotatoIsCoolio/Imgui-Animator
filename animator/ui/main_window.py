import sys, math, json, time, os
from enum import Enum
from typing import List, Dict, Any, Optional, Tuple, Union
from PySide6.QtWidgets import *
from PySide6.QtCore import *
from PySide6.QtGui import *

# All the damn files below
from animator.ui.graphics_view import CustomGraphicsView
from animator.ui.timeline_widget import TimelineWidget
from animator.animation.animated_item import AnimatedItem
from animator.animation.keyframe import AnimationKeyframe
from animator.items.text_item import CustomTextItem
from animator.items.shape_items import CustomRectItem, CustomEllipseItem, CustomPolygonItem
from animator.commands.undo_commands import (
    AddItemCommand, RemoveItemCommand, ModifyItemCommand, 
    AddKeyframeCommand, RemoveKeyframeCommand
)
from animator.utils.geometry import regularPolygon, starPolygon
from animator.utils.export import exportImguiCode

class AnimatorMainWindow(QMainWindow):
    def __init__(self):
        super().__init__()  # Gotta get the credits yk?
        self.setWindowTitle("ImGui Animator Tool (Made By PotatoIsCool)")
        self.setGeometry(100, 100, 1200, 800)
        
        self.animatedItems = []
        self.currentItem = None
        self.copiedItems = []
        self.snapToGrid = True
        self.gridSize = 10
        self.undoStack = QUndoStack(self)
        
        self.applyDarkTheme()
        self.setupScene()
        self.setupUI()
        self.setupShortcuts()
        
        self.addText()
    
    def applyDarkTheme(self): # Change this if you would like to use a different theme
        darkPalette = QPalette()
        
        darkBg = QColor(30, 30, 30)
        darkerBg = QColor(25, 25, 25)
        darkestBg = QColor(20, 20, 20)
        lightText = QColor(240, 240, 240)
        accent = QColor(0, 120, 215)
        
        darkPalette.setColor(QPalette.Window, darkBg)
        darkPalette.setColor(QPalette.WindowText, lightText)
        darkPalette.setColor(QPalette.Base, darkerBg)
        darkPalette.setColor(QPalette.AlternateBase, darkestBg)
        darkPalette.setColor(QPalette.ToolTipBase, darkBg)
        darkPalette.setColor(QPalette.ToolTipText, lightText)
        darkPalette.setColor(QPalette.Text, lightText)
        darkPalette.setColor(QPalette.Button, darkerBg)
        darkPalette.setColor(QPalette.ButtonText, lightText)
        darkPalette.setColor(QPalette.BrightText, Qt.white)
        darkPalette.setColor(QPalette.Highlight, accent)
        darkPalette.setColor(QPalette.HighlightedText, Qt.white)
        darkPalette.setColor(QPalette.Link, accent)
        
        QApplication.instance().setPalette(darkPalette)
        # Qcss BELOW
        stylesheet = """ 
        QMainWindow, QDialog {
            background-color: #1e1e1e;
        }
        
        QWidget {
            color: #f0f0f0;
            font-family: 'Segoe UI', Arial, sans-serif;
        }
        
        QToolBar {
            background-color: #252525;
            border: none;
            spacing: 3px;
        }
        
        QPushButton {
            background-color: #2d2d2d;
            border: 1px solid #3d3d3d;
            border-radius: 3px;
            padding: 5px;
            min-height: 20px;
        }
        
        QPushButton:hover {
            background-color: #3d3d3d;
        }
        
        QPushButton:pressed {
            background-color: #0078d7;
        }
        
        QLineEdit, QSpinBox, QDoubleSpinBox, QComboBox {
            background-color: #252525;
            border: 1px solid #3d3d3d;
            border-radius: 3px;
            padding: 3px;
            min-height: 20px;
        }
        
        QDockWidget {
            titlebar-close-icon: url(close.png);
            titlebar-normal-icon: url(undock.png);
        }
        
        QDockWidget::title {
            background-color: #2d2d2d;
            padding-left: 5px;
            padding-top: 3px;
            padding-bottom: 3px;
        }
        
        QTabWidget::pane {
            border: 1px solid #3d3d3d;
        }
        
        QTabBar::tab {
            background-color: #252525;
            border: 1px solid #3d3d3d;
            border-bottom: none;
            border-top-left-radius: 3px;
            border-top-right-radius: 3px;
            padding: 5px 10px;
        }
        
        QTabBar::tab:selected {
            background-color: #2d2d2d;
        }
        
        QTabBar::tab:hover {
            background-color: #3d3d3d;
        }
        
        QGraphicsView {
            background-color: #1a1a1a;
            border: 1px solid #3d3d3d;
        }
        
        QScrollBar:vertical {
            background-color: #252525;
            width: 12px;
            margin: 0px;
        }
        
        QScrollBar::handle:vertical {
            background-color: #3d3d3d;
            min-height: 20px;
            border-radius: 6px;
        }
        
        QScrollBar::handle:vertical:hover {
            background-color: #4d4d4d;
        }
        
        QScrollBar:horizontal {
            background-color: #252525;
            height: 12px;
            margin: 0px;
        }
        
        QScrollBar::handle:horizontal {
            background-color: #3d3d3d;
            min-width: 20px;
            border-radius: 6px;
        }
        
        QScrollBar::handle:horizontal:hover {
            background-color: #4d4d4d;
        }
        
        QGroupBox {
            border: 1px solid #3d3d3d;
            border-radius: 3px;
            margin-top: 10px;
            padding-top: 10px;
        }
        
        QGroupBox::title {
            subcontrol-origin: margin;
            subcontrol-position: top left;
            left: 10px;
            padding: 0 3px;
        }
        
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
        """
        
        QApplication.instance().setStyleSheet(stylesheet)
    
    def setupScene(self):
        self.view = CustomGraphicsView()
        
        self.scene = QGraphicsScene(self)
        self.scene.setSceneRect(QRectF(0, 0, 1000, 600))
        self.view.setScene(self.scene)
        
        self.drawGrid()
    
    def drawGrid(self):
        gridColor = QColor(60, 60, 60)
        gridPen = QPen(gridColor, 1, Qt.DotLine)
        
        majorGridColor = QColor(80, 80, 80)
        majorGridPen = QPen(majorGridColor, 1, Qt.DashLine)
        
        rect = self.scene.sceneRect()
        
        for y in range(0, int(rect.height()), self.gridSize):
            if y % (self.gridSize * 5) == 0:
                self.scene.addLine(rect.left(), y, rect.right(), y, majorGridPen)
            else:
                self.scene.addLine(rect.left(), y, rect.right(), y, gridPen)
        
        for x in range(0, int(rect.width()), self.gridSize):
            if x % (self.gridSize * 5) == 0:
                self.scene.addLine(x, rect.top(), x, rect.bottom(), majorGridPen)
            else:
                self.scene.addLine(x, rect.top(), x, rect.bottom(), gridPen)
    
    def setupUI(self):
        centralWidget = QWidget()
        mainLayout = QVBoxLayout(centralWidget)
        mainLayout.setContentsMargins(0, 0, 0, 0)
        
        toolbar = QToolBar("Main Toolbar")
        newAction = QAction("New", self)
        saveAction = QAction("Save", self)
        loadAction = QAction("Load", self)
        exportAction = QAction("Export ImGui", self)
        undoAction = self.undoStack.createUndoAction(self, "Undo")
        redoAction = self.undoStack.createRedoAction(self, "Redo")
        
        self.addToolBar(toolbar)
        toolbar.setMovable(True)
        toolbar.setIconSize(QSize(24, 24))
        
        newAction.triggered.connect(self.newProject)
        saveAction.triggered.connect(self.saveProject)
        loadAction.triggered.connect(self.loadProject)
        exportAction.triggered.connect(self.exportImgui)

        toolbar.addAction(newAction)
        toolbar.addAction(saveAction)
        toolbar.addAction(loadAction)
        toolbar.addAction(exportAction)
        
        toolbar.addSeparator()
        
        undoAction.setShortcut(QKeySequence.Undo)
        toolbar.addAction(undoAction)
        
        redoAction.setShortcut(QKeySequence.Redo)
        toolbar.addAction(redoAction)
        
        toolbar.addSeparator()
        
        self.snapAction = QAction("Snap to Grid", self)
        self.snapAction.setCheckable(True)
        self.snapAction.setChecked(self.snapToGrid)
        self.snapAction.triggered.connect(self.toggleSnapToGrid)
        toolbar.addAction(self.snapAction)
        
        self.setCentralWidget(centralWidget)
        mainLayout.addWidget(self.view)
        
        self.timeline = TimelineWidget()
        self.timeline.frameChanged.connect(self.updateAnimationFrame)
        mainLayout.addWidget(self.timeline)
        
        self.setupDocks()
    
    def setupDocks(self):
        self.toolDock = QDockWidget("Tools", self)
        self.toolDock.setAllowedAreas(Qt.AllDockWidgetAreas)
        self.toolDock.setFeatures(QDockWidget.DockWidgetMovable | QDockWidget.DockWidgetFloatable)
        
        toolWidget = QWidget()
        toolLayout = QVBoxLayout(toolWidget)
        toolLayout.setContentsMargins(5, 5, 5, 5)
        toolLayout.setSpacing(5)
        
        addTextButton = QPushButton("Add Text")
        addTextButton.setIcon(QIcon.fromTheme("insert-text"))
        addTextButton.clicked.connect(self.addText)
        toolLayout.addWidget(addTextButton)
        
        shapesGroup = QGroupBox("Shapes")
        shapesLayout = QVBoxLayout(shapesGroup)
        shapesLayout.setContentsMargins(5, 5, 5, 5)
        shapesLayout.setSpacing(5)
        
        for shape in ["Rectangle", "Square", "Circle", "Triangle", "Pentagon", "Hexagon", "Octagon", "Parallelogram", "Star"]:
            btn = QPushButton(f"Add {shape}")
            btn.clicked.connect(lambda checked, s=shape: self.addShape(s))
            shapesLayout.addWidget(btn)
        
        toolLayout.addWidget(shapesGroup)
        
        animGroup = QGroupBox("Animation")
        animLayout = QVBoxLayout(animGroup)
        animLayout.setContentsMargins(5, 5, 5, 5)
        animLayout.setSpacing(5)
        
        keyframeBtn = QPushButton("Add Keyframe")
        keyframeBtn.clicked.connect(self.addKeyframeAtCurrentFrame)
        animLayout.addWidget(keyframeBtn)
        
        previewBtn = QPushButton("Preview Animation")
        previewBtn.clicked.connect(lambda: self.timeline.togglePlay())
        animLayout.addWidget(previewBtn)
        
        toolLayout.addWidget(animGroup)
        
        importGroup = QGroupBox("Import")
        importLayout = QVBoxLayout(importGroup)
        importLayout.setContentsMargins(5, 5, 5, 5)
        importLayout.setSpacing(5)
        
        importImageBtn = QPushButton("Import Image")
        importImageBtn.clicked.connect(self.importImageDialog)
        importLayout.addWidget(importImageBtn)
        
        importFontBtn = QPushButton("Import Font")
        importFontBtn.clicked.connect(self.importFontDialog)
        importLayout.addWidget(importFontBtn)
        
        toolLayout.addWidget(importGroup)
        
        toolLayout.addStretch()
        
        self.toolDock.setWidget(toolWidget)
        self.addDockWidget(Qt.LeftDockWidgetArea, self.toolDock)
        
        self.propDock = QDockWidget("Properties", self)
        self.propDock.setAllowedAreas(Qt.AllDockWidgetAreas)
        self.propDock.setFeatures(QDockWidget.DockWidgetMovable | QDockWidget.DockWidgetFloatable)
        
        self.propWidget = QWidget()
        self.propLayout = QFormLayout(self.propWidget)
        self.propLayout.setContentsMargins(5, 5, 5, 5)
        self.propLayout.setSpacing(5)
        
        self.nameInput = QLineEdit("Item")
        self.nameInput.textChanged.connect(self.updateItemName)
        self.propLayout.addRow("Name:", self.nameInput)
        
        self.xInput = QDoubleSpinBox()
        self.xInput.setRange(-1000, 1000)
        self.xInput.valueChanged.connect(self.updateItemPosition)
        self.propLayout.addRow("X:", self.xInput)
        
        self.yInput = QDoubleSpinBox()
        self.yInput.setRange(-1000, 1000)
        self.yInput.valueChanged.connect(self.updateItemPosition)
        self.propLayout.addRow("Y:", self.yInput)
        
        self.rotationInput = QDoubleSpinBox()
        self.rotationInput.setRange(-360, 360)
        self.rotationInput.valueChanged.connect(self.updateItemTransform)
        self.propLayout.addRow("Rotation:", self.rotationInput)
        
        self.scaleInput = QDoubleSpinBox()
        self.scaleInput.setRange(0.1, 10)
        self.scaleInput.setSingleStep(0.1)
        self.scaleInput.setValue(1.0)
        self.scaleInput.valueChanged.connect(self.updateItemTransform)
        self.propLayout.addRow("Scale:", self.scaleInput)
        
        self.opacityInput = QDoubleSpinBox()
        self.opacityInput.setRange(0, 1)
        self.opacityInput.setSingleStep(0.1)
        self.opacityInput.setValue(1.0)
        self.opacityInput.valueChanged.connect(self.updateItemOpacity)
        self.propLayout.addRow("Opacity:", self.opacityInput)
        
        colorLayout = QHBoxLayout()
        self.colorButton = QPushButton()
        self.colorButton.setFixedSize(24, 24)
        self.colorButton.setStyleSheet("background-color: white;")
        self.colorButton.clicked.connect(self.pickColor)
        colorLayout.addWidget(self.colorButton)
        
        self.fillColorButton = QPushButton()
        self.fillColorButton.setFixedSize(24, 24)
        self.fillColorButton.setStyleSheet("background-color: #6464ff;")
        self.fillColorButton.clicked.connect(self.pickFillColor)
        colorLayout.addWidget(self.fillColorButton)
        
        self.propLayout.addRow("Colors:", colorLayout)
        
        self.textGroup = QGroupBox("Text Properties")
        self.textGroup.setVisible(False)
        textLayout = QFormLayout(self.textGroup)
        
        self.textInput = QLineEdit("Text")
        self.textInput.textChanged.connect(self.updateText)
        textLayout.addRow("Text:", self.textInput)
        
        self.fontSizeInput = QSpinBox()
        self.fontSizeInput.setRange(8, 72)
        self.fontSizeInput.setValue(16)
        self.fontSizeInput.valueChanged.connect(self.updateFont)
        textLayout.addRow("Font Size:", self.fontSizeInput)
        
        self.fontCombo = QComboBox()
        self.fontCombo.addItems(["Arial", "Times New Roman", "Courier New", "Verdana", "Tahoma"])
        self.fontCombo.currentTextChanged.connect(self.updateFont)
        textLayout.addRow("Font:", self.fontCombo)
        
        self.propLayout.addRow(self.textGroup)
        
        self.shapeGroup = QGroupBox("Shape Properties")
        self.shapeGroup.setVisible(False)
        shapeLayout = QFormLayout(self.shapeGroup)
        
        self.widthInput = QDoubleSpinBox()
        self.widthInput.setRange(1, 1000)
        self.widthInput.setValue(100)
        self.widthInput.valueChanged.connect(self.updateShapeSize)
        shapeLayout.addRow("Width:", self.widthInput)
        
        self.heightInput = QDoubleSpinBox()
        self.heightInput.setRange(1, 1000)
        self.heightInput.setValue(100)
        self.heightInput.valueChanged.connect(self.updateShapeSize)
        shapeLayout.addRow("Height:", self.heightInput)
        
        self.propLayout.addRow(self.shapeGroup)
        
        self.animGroup = QGroupBox("Animation")
        animLayout = QVBoxLayout(self.animGroup)
        
        self.smoothingCheck = QCheckBox("Enable Smoothing")
        self.smoothingCheck.setChecked(True)
        self.smoothingCheck.stateChanged.connect(self.toggleSmoothing)
        animLayout.addWidget(self.smoothingCheck)
        
        self.keyframesList = QListWidget()
        self.keyframesList.itemClicked.connect(self.keyframeSelected)
        animLayout.addWidget(self.keyframesList)
        
        keyframeButtonsLayout = QHBoxLayout()
        
        addKeyframeBtn = QPushButton("Add")
        addKeyframeBtn.clicked.connect(self.addKeyframeAtCurrentFrame)
        keyframeButtonsLayout.addWidget(addKeyframeBtn)
        
        removeKeyframeBtn = QPushButton("Remove")
        removeKeyframeBtn.clicked.connect(self.removeSelectedKeyframe)
        keyframeButtonsLayout.addWidget(removeKeyframeBtn)
        
        animLayout.addLayout(keyframeButtonsLayout)
        
        self.propLayout.addRow(self.animGroup)
        
        self.propDock.setWidget(self.propWidget)
        self.addDockWidget(Qt.RightDockWidgetArea, self.propDock)
        
        self.outputDock = QDockWidget("ImGui Output", self)
        self.outputDock.setAllowedAreas(Qt.AllDockWidgetAreas)
        
        self.outputText = QTextEdit()
        self.outputText.setReadOnly(True)
        self.outputText.setFont(QFont("Courier New", 10))
        
        self.outputDock.setWidget(self.outputText)
        self.addDockWidget(Qt.BottomDockWidgetArea, self.outputDock)
        self.outputDock.setVisible(False)
    
    def setupShortcuts(self):
        deleteShortcut = QShortcut(QKeySequence.Delete, self)
        deleteShortcut.activated.connect(self.deleteSelectedItems)
        
        copyShortcut = QShortcut(QKeySequence.Copy, self)
        copyShortcut.activated.connect(self.copySelectedItems)
        
        pasteShortcut = QShortcut(QKeySequence.Paste, self)
        pasteShortcut.activated.connect(self.pasteItems)
        
        duplicateShortcut = QShortcut(QKeySequence("Ctrl+D"), self)
        duplicateShortcut.activated.connect(self.duplicateSelectedItems)
        
        undoShortcut = QShortcut(QKeySequence.Undo, self)
        undoShortcut.activated.connect(self.undoStack.undo)
        
        redoShortcut = QShortcut(QKeySequence.Redo, self)
        redoShortcut.activated.connect(self.undoStack.redo)
    
    def addText(self):
        item = CustomTextItem("Text")
        self.scene.addItem(item)
        item.setPos(100, 100)
        
        animatedItem = AnimatedItem(item, "Text")
        self.animatedItems.append(animatedItem)
        
        cmd = AddItemCommand(self.scene, item, animatedItem)
        self.undoStack.push(cmd)
        
        self.scene.clearSelection()
        item.setSelected(True)
        self.updatePropertyPanel(item)
    
    def addShape(self, shape):
        pen = QPen(QColor("white"))
        brush = QBrush(QColor(100, 100, 255, 180))
        item = None
        
        if shape == "Rectangle":
            item = CustomRectItem(0, 0, 120, 60, pen, brush)
        elif shape == "Square":
            item = CustomRectItem(0, 0, 80, 80, pen, brush, True)
        elif shape == "Circle":
            item = CustomEllipseItem(0, 0, 80, 80, pen, brush)
        elif shape == "Triangle":
            poly = QPolygonF([QPointF(40, 0), QPointF(80, 80), QPointF(0, 80)])
            item = CustomPolygonItem(0, 0, poly, pen, brush, "Triangle")
        elif shape == "Pentagon":
            item = CustomPolygonItem(0, 0, regularPolygon(5, 50), pen, brush, "Pentagon")
        elif shape == "Hexagon":
            item = CustomPolygonItem(0, 0, regularPolygon(6, 50), pen, brush, "Hexagon")
        elif shape == "Octagon":
            item = CustomPolygonItem(0, 0, regularPolygon(8, 50), pen, brush, "Octagon")
        elif shape == "Parallelogram":
            poly = QPolygonF([QPointF(20, 0), QPointF(100, 0), QPointF(80, 60), QPointF(0, 60)])
            item = CustomPolygonItem(0, 0, poly, pen, brush, "Parallelogram")
        elif shape == "Star":
            item = CustomPolygonItem(0, 0, starPolygon(5, 50, 25), pen, brush, "Star")
        
        if item:
            self.scene.addItem(item)
            item.setPos(100, 100)
            
            animatedItem = AnimatedItem(item, shape)
            self.animatedItems.append(animatedItem)
            
            cmd = AddItemCommand(self.scene, item, animatedItem)
            self.undoStack.push(cmd)
            
            self.scene.clearSelection()
            item.setSelected(True)
            self.updatePropertyPanel(item)
    
    def updatePropertyPanel(self, item):
        self.currentItem = item
        
        animatedItem = None
        for ai in self.animatedItems:
            if ai.item == item:
                animatedItem = ai
                break
        
        if not animatedItem:
            return
        
        self.nameInput.blockSignals(True)
        self.nameInput.setText(animatedItem.name)
        self.nameInput.blockSignals(False)
        
        pos = item.pos()
        self.xInput.blockSignals(True)
        self.yInput.blockSignals(True)
        self.xInput.setValue(pos.x())
        self.yInput.setValue(pos.y())
        self.xInput.blockSignals(False)
        self.yInput.blockSignals(False)
        
        transform = item.transform()
        scale = math.sqrt(transform.m11() * transform.m11() + transform.m12() * transform.m12())
        rotation = math.degrees(math.atan2(transform.m12(), transform.m11()))
        
        self.rotationInput.blockSignals(True)
        self.scaleInput.blockSignals(True)
        self.rotationInput.setValue(rotation)
        self.scaleInput.setValue(scale)
        self.rotationInput.blockSignals(False)
        self.scaleInput.blockSignals(False)
        
        self.opacityInput.blockSignals(True)
        self.opacityInput.setValue(item.opacity())
        self.opacityInput.blockSignals(False)
        
        if hasattr(item, "pen") and hasattr(item, "brush"):
            self.colorButton.setStyleSheet(f"background-color: {item.pen.color().name()};")
            self.fillColorButton.setStyleSheet(f"background-color: {item.brush.color().name()};")
        elif hasattr(item, "defaultTextColor"):
            self.colorButton.setStyleSheet(f"background-color: {item.defaultTextColor().name()};")
        
        isText = hasattr(item, "toPlainText")
        self.textGroup.setVisible(isText)
        self.shapeGroup.setVisible(not isText)
        
        if isText:
            self.textInput.blockSignals(True)
            self.fontSizeInput.blockSignals(True)
            self.fontCombo.blockSignals(True)
            
            self.textInput.setText(item.toPlainText())
            self.fontSizeInput.setValue(item.font().pointSize())
            
            fontFamily = item.font().family()
            index = self.fontCombo.findText(fontFamily)
            if index >= 0:
                self.fontCombo.setCurrentIndex(index)
            
            self.textInput.blockSignals(False)
            self.fontSizeInput.blockSignals(False)
            self.fontCombo.blockSignals(False)
        
        if not isText and hasattr(item, "rect"):
            self.widthInput.blockSignals(True)
            self.heightInput.blockSignals(True)
            
            self.widthInput.setValue(item.rect.width())
            self.heightInput.setValue(item.rect.height())
            
            self.widthInput.blockSignals(False)
            self.heightInput.blockSignals(False)
        
        self.smoothingCheck.blockSignals(True)
        self.smoothingCheck.setChecked(animatedItem.useSmoothing)
        self.smoothingCheck.blockSignals(False)
        
        self.updateKeyframesList(animatedItem)
    
    def updateKeyframesList(self, animatedItem):
        self.keyframesList.clear()
        
        if not animatedItem:
            return
        
        for keyframe in animatedItem.keyframes:
            self.keyframesList.addItem(f"Frame {keyframe.frame}")
    
    def updateItemName(self):
        if not self.currentItem:
            return
        
        name = self.nameInput.text()
        
        for ai in self.animatedItems:
            if ai.item == self.currentItem:
                ai.name = name
                break
    
    def updateItemPosition(self):
        if not self.currentItem:
            return
        
        oldPos = self.currentItem.pos()
        x = self.xInput.value()
        y = self.yInput.value()
        
        cmd = ModifyItemCommand(
            self.currentItem,
            "position",
            oldPos,
            QPointF(x, y)
        )
        self.undoStack.push(cmd)
        
        self.currentItem.setPos(x, y)
    
    def updateItemTransform(self):
        if not self.currentItem:
            return
        
        oldTransform = self.currentItem.transform()
        rotation = self.rotationInput.value()
        scale = self.scaleInput.value()
        
        transform = QTransform()
        transform.rotate(rotation)
        transform.scale(scale, scale)
        
        cmd = ModifyItemCommand(
            self.currentItem,
            "transform",
            oldTransform,
            transform
        )
        self.undoStack.push(cmd)
        
        self.currentItem.setTransform(transform)
    
    def updateItemOpacity(self):
        if not self.currentItem:
            return
        
        oldOpacity = self.currentItem.opacity()
        opacity = self.opacityInput.value()
        
        cmd = ModifyItemCommand(
            self.currentItem,
            "opacity",
            oldOpacity,
            opacity
        )
        self.undoStack.push(cmd)
        
        self.currentItem.setOpacity(opacity)
    
    def updateText(self):
        if not self.currentItem or not hasattr(self.currentItem, "setPlainText"):
            return
        
        oldText = self.currentItem.toPlainText()
        text = self.textInput.text()
        
        cmd = ModifyItemCommand(
            self.currentItem,
            "text",
            oldText,
            text
        )
        self.undoStack.push(cmd)
        
        self.currentItem.setPlainText(text)
        
        for ai in self.animatedItems:
            if ai.item == self.currentItem:
                ai.properties["text"] = text
                break
    
    def updateFont(self):
        if not self.currentItem or not hasattr(self.currentItem, "setFont"):
            return
        
        oldFont = self.currentItem.font()
        size = self.fontSizeInput.value()
        family = self.fontCombo.currentText()
        
        font = QFont(family, size)
        
        cmd = ModifyItemCommand(
            self.currentItem,
            "font",
            oldFont,
            font
        )
        self.undoStack.push(cmd)
        
        self.currentItem.setFont(font)
        
        for ai in self.animatedItems:
            if ai.item == self.currentItem:
                ai.properties["fontSize"] = size
                ai.properties["fontFamily"] = family
                break
    
    def updateShapeSize(self):
        if not self.currentItem or not hasattr(self.currentItem, "rect"):
            return
        
        oldRect = QRectF(self.currentItem.rect)
        width = self.widthInput.value()
        height = self.heightInput.value()
        
        if hasattr(self.currentItem, "isSquare") and self.currentItem.isSquare:
            if self.sender() == self.widthInput:
                height = width
                self.heightInput.blockSignals(True)
                self.heightInput.setValue(height)
                self.heightInput.blockSignals(False)
            else:
                width = height
                self.widthInput.blockSignals(True)
                self.widthInput.setValue(width)
                self.widthInput.blockSignals(False)
        
        newRect = QRectF(0, 0, width, height)
        
        cmd = ModifyItemCommand(
            self.currentItem,
            "rect",
            oldRect,
            newRect
        )
        self.undoStack.push(cmd)
        
        self.currentItem.rect = newRect
        
        self.currentItem.update()
        
        if hasattr(self.currentItem, "updateHandles"):
            self.currentItem.updateHandles()
        
        for ai in self.animatedItems:
            if ai.item == self.currentItem:
                ai.properties["width"] = width
                ai.properties["height"] = height
                break
    
    def updateShapeSizeFromItem(self):
        if not self.currentItem or not hasattr(self.currentItem, "rect"):
            return
        
        self.widthInput.blockSignals(True)
        self.heightInput.blockSignals(True)
        
        self.widthInput.setValue(self.currentItem.rect.width())
        self.heightInput.setValue(self.currentItem.rect.height())
        
        self.widthInput.blockSignals(False)
        self.heightInput.blockSignals(False)
    
    def pickColor(self):
        if not self.currentItem:
            return
        
        currentColor = QColor("white")
        
        if hasattr(self.currentItem, "pen"):
            currentColor = self.currentItem.pen.color()
        elif hasattr(self.currentItem, "defaultTextColor"):
            currentColor = self.currentItem.defaultTextColor()
        
        color = QColorDialog.getColor(currentColor, self, "Select Color")
        
        if color.isValid():
            if hasattr(self.currentItem, "pen"):
                oldPen = QPen(self.currentItem.pen)
                newPen = QPen(self.currentItem.pen)
                newPen.setColor(color)
                
                cmd = ModifyItemCommand(
                    self.currentItem,
                    "pen",
                    oldPen,
                    newPen
                )
                self.undoStack.push(cmd)
                
                self.currentItem.pen = newPen
                self.currentItem.update()
            elif hasattr(self.currentItem, "setDefaultTextColor"):
                oldColor = self.currentItem.defaultTextColor()
                
                cmd = ModifyItemCommand(
                    self.currentItem,
                    "color",
                    oldColor,
                    color
                )
                self.undoStack.push(cmd)
                
                self.currentItem.setDefaultTextColor(color)
            
            self.colorButton.setStyleSheet(f"background-color: {color.name()};")
            
            for ai in self.animatedItems:
                if ai.item == self.currentItem:
                    ai.color = color
                    break
    
    def pickFillColor(self):
        if not self.currentItem or not hasattr(self.currentItem, "brush"):
            return
        
        currentColor = self.currentItem.brush.color()
        color = QColorDialog.getColor(currentColor, self, "Select Fill Color", QColorDialog.ShowAlphaChannel)
        
        if color.isValid():
            oldBrush = QBrush(self.currentItem.brush)
            newBrush = QBrush(self.currentItem.brush)
            newBrush.setColor(color)
            
            cmd = ModifyItemCommand(
                self.currentItem,
                "brush",
                oldBrush,
                newBrush
            )
            self.undoStack.push(cmd)
            
            self.currentItem.brush = newBrush
            self.currentItem.update()
            self.fillColorButton.setStyleSheet(f"background-color: {color.name()};")
            
            for ai in self.animatedItems:
                if ai.item == self.currentItem:
                    ai.fillColor = color
                    break
    
    def toggleSmoothing(self, state):
        if not self.currentItem:
            return
        
        for ai in self.animatedItems:
            if ai.item == self.currentItem:
                ai.useSmoothing = bool(state)
                break
    
    def addKeyframeAtCurrentFrame(self):
        if not self.currentItem:
            return
        
        animatedItem = None
        for ai in self.animatedItems:
            if ai.item == self.currentItem:
                animatedItem = ai
                break
        
        if not animatedItem:
            return
        
        currentFrame = self.timeline.currentFrame
        keyframe = animatedItem.addKeyframe(currentFrame)
        
        cmd = AddKeyframeCommand(animatedItem, keyframe)
        self.undoStack.push(cmd)
        
        self.updateKeyframesList(animatedItem)
        
        self.statusBar().showMessage(f"Keyframe added at frame {currentFrame}", 3000)
    
    def removeSelectedKeyframe(self):
        if not self.currentItem:
            return
        
        animatedItem = None
        for ai in self.animatedItems:
            if ai.item == self.currentItem:
                animatedItem = ai
                break
        
        if not animatedItem:
            return
        
        selectedItems = self.keyframesList.selectedItems()
        if not selectedItems:
            return
        
        selectedItem = selectedItems[0]
        frameText = selectedItem.text()
        frame = int(frameText.split(" ")[1])
        
        keyframe = None
        for kf in animatedItem.keyframes:
            if kf.frame == frame:
                keyframe = kf
                break
        
        if not keyframe:
            return
        
        cmd = RemoveKeyframeCommand(animatedItem, keyframe)
        self.undoStack.push(cmd)
        
        animatedItem.keyframes = [kf for kf in animatedItem.keyframes if kf.frame != frame]
        
        self.updateKeyframesList(animatedItem)
        
        self.statusBar().showMessage(f"Keyframe removed at frame {frame}", 3000)
    
    def keyframeSelected(self, item):
        if not self.currentItem:
            return
        
        animatedItem = None
        for ai in self.animatedItems:
            if ai.item == self.currentItem:
                animatedItem = ai
                break
        
        if not animatedItem:
            return
        
        frameText = item.text()
        frame = int(frameText.split(" ")[1])
        
        self.timeline.setCurrentFrame(frame)
    
    def updateAnimationFrame(self, frame):
        for animatedItem in self.animatedItems:
            keyframe = animatedItem.getKeyframe(frame)
            animatedItem.applyKeyframe(keyframe)
    
    def deleteSelectedItems(self):
        selectedItems = self.scene.selectedItems()
        
        if not selectedItems:
            return
        
        itemsToRemove = []
        animatedItemsToRemove = []
        
        for item in selectedItems:
            itemsToRemove.append(item)
            
            for ai in self.animatedItems:
                if ai.item == item:
                    animatedItemsToRemove.append(ai)
                    break
        
        cmd = RemoveItemCommand(self.scene, itemsToRemove, animatedItemsToRemove)
        self.undoStack.push(cmd)
        
        for item in itemsToRemove:
            self.scene.removeItem(item)
        
        self.animatedItems = [ai for ai in self.animatedItems if ai not in animatedItemsToRemove]
        
        self.currentItem = None
    
    def copySelectedItems(self):
        selectedItems = self.scene.selectedItems()
        
        if not selectedItems:
            return
        
        self.copiedItems = []
        
        for item in selectedItems:
            itemData = {
                "type": None,
                "pos": item.pos(),
                "transform": item.transform(),
                "opacity": item.opacity()
            }
            
            if hasattr(item, "shapeType"):
                itemData["type"] = item.shapeType
                
                if hasattr(item, "rect"):
                    itemData["rect"] = QRectF(item.rect)
                
                if hasattr(item, "pen"):
                    itemData["pen"] = QPen(item.pen)
                
                if hasattr(item, "brush"):
                    itemData["brush"] = QBrush(item.brush)
                
                if hasattr(item, "polygon"):
                    itemData["polygon"] = QPolygonF(item.polygon)
                
                if hasattr(item, "isSquare"):
                    itemData["isSquare"] = item.isSquare
            
            elif hasattr(item, "toPlainText"):
                itemData["type"] = "text"
                itemData["text"] = item.toPlainText()
                itemData["font"] = QFont(item.font())
                itemData["color"] = QColor(item.defaultTextColor())
            
            self.copiedItems.append(itemData)
        
        self.statusBar().showMessage(f"Copied {len(self.copiedItems)} item(s)", 3000)
    
    def pasteItems(self):
        if not self.copiedItems:
            return
        
        self.scene.clearSelection()
        
        offset = 20
        
        for itemData in self.copiedItems:
            item = None
            
            if itemData["type"] == "text":
                item = CustomTextItem(itemData["text"], itemData["font"])
                item.setDefaultTextColor(itemData["color"])
            
            elif itemData["type"] in ["Rectangle", "Square"]:
                item = CustomRectItem(
                    0, 0,
                    itemData["rect"].width(),
                    itemData["rect"].height(),
                    itemData["pen"],
                    itemData["brush"],
                    itemData.get("isSquare", False)
                )
            
            elif itemData["type"] == "Circle" or itemData["type"] == "Ellipse":
                item = CustomEllipseItem(
                    0, 0,
                    itemData["rect"].width(),
                    itemData["rect"].height(),
                    itemData["pen"],
                    itemData["brush"]
                )
            
            elif "polygon" in itemData:
                item = CustomPolygonItem(
                    0, 0,
                    itemData["polygon"],
                    itemData["pen"],
                    itemData["brush"],
                    itemData["type"]
                )
            
            if item:
                item.setPos(itemData["pos"].x() + offset, itemData["pos"].y() + offset)
                item.setTransform(itemData["transform"])
                item.setOpacity(itemData["opacity"])
                
                self.scene.addItem(item)
                
                animatedItem = AnimatedItem(item, itemData["type"])
                self.animatedItems.append(animatedItem)
                
                cmd = AddItemCommand(self.scene, item, animatedItem)
                self.undoStack.push(cmd)
                
                item.setSelected(True)
        
        self.statusBar().showMessage(f"Pasted {len(self.copiedItems)} item(s)", 3000)
    
    def duplicateSelectedItems(self):
        self.copySelectedItems()
        self.pasteItems()
    
    def changeItemZOrder(self, item, direction):
        if direction > 0:
            item.setZValue(item.zValue() + 1)
        else:
            item.setZValue(item.zValue() - 1)
    
    def toggleSnapToGrid(self, checked):
        self.snapToGrid = checked
    
    def editTextItem(self, item):
        if not hasattr(item, "toPlainText"):
            return
        
        text, ok = QInputDialog.getText(
            self, "Edit Text", "Text:", 
            text=item.toPlainText()
        )
        
        if ok and text:
            oldText = item.toPlainText()
            
            cmd = ModifyItemCommand(
                item,
                "text",
                oldText,
                text
            )
            self.undoStack.push(cmd)
            
            item.setPlainText(text)
            
            for ai in self.animatedItems:
                if ai.item == item:
                    ai.properties["text"] = text
                    break
            
            if self.currentItem == item:
                self.textInput.setText(text)
    
    def importImageDialog(self):
        filePath, _ = QFileDialog.getOpenFileName(
            self, "Import Image", "", "Images (*.png *.jpg *.jpeg *.bmp *.gif)"
        )
        
        if filePath:
            self.importImage(filePath)
    
    def importImage(self, filePath, pos=None): # Coming soon! (I hope)
        self.statusBar().showMessage(f"Image importing not implemented yet: {filePath}", 3000)
    
    def importImageData(self, imageData, pos=None):
        self.statusBar().showMessage("Image importing not implemented yet", 3000)
    
    def importFontDialog(self):
        filePath, _ = QFileDialog.getOpenFileName(
            self, "Import Font", "", "Fonts (*.ttf *.otf)"
        )
        
        if filePath:
            self.importFont(filePath)
    
    def importFont(self, filePath): # Coming soon! (I hope)
        self.statusBar().showMessage(f"Font importing not implemented yet: {filePath}", 3000)
    
    def newProject(self): # Clears the current project and resets the scene and changes the status bar :p
        self.scene.clear()
        
        self.animatedItems = []
        
        self.currentItem = None
        
        self.drawGrid()
        
        self.timeline.setCurrentFrame(0)
        
        self.statusBar().showMessage("New project created", 3000)
    
    def saveProject(self): # Saves your current project as a .ImguiAnimation file (Its really just a json file lol)
        filename, _ = QFileDialog.getSaveFileName(self, "Save Project", "", "ImGui Animator (*.ImguiAnimation)")
        
        if not filename:
            return
        
        projectData = {
            "version": "1.0",
            "timeline": {
                "duration": self.timeline.totalFrames,
                "fps": self.timeline.fps
            },
            "items": []
        }
        
        for animatedItem in self.animatedItems:
            projectData["items"].append(animatedItem.toDict())
        
        with open(filename, "w") as f:
            json.dump(projectData, f, indent=2)
        
        self.statusBar().showMessage(f"Project saved to {filename}", 3000)
    
    def loadProject(self): # Loads the .ImguiAnimation file
        filename, _ = QFileDialog.getOpenFileName(self, "Load Project", "", "ImGui Animator (*.ImguiAnimation)")
        
        if not filename:
            return
        
        try:
            with open(filename, "r") as f:
                projectData = json.load(f)
            
            self.newProject()
            
            if "timeline" in projectData:
                self.timeline.setDuration(projectData["timeline"].get("duration", 100))
                self.timeline.setFps(projectData["timeline"].get("fps", 24))
            
            for itemData in projectData.get("items", []):
                itemType = itemData.get("type", "unknown")
                
                if itemType == "text":
                    item = CustomTextItem(itemData.get("properties", {}).get("text", "Text"))
                    self.scene.addItem(item)
                    
                    fontSize = itemData.get("properties", {}).get("fontSize", 16)
                    fontFamily = itemData.get("properties", {}).get("fontFamily", "Arial")
                    item.setFont(QFont(fontFamily, fontSize))
                    
                    color = QColor(itemData.get("color", "#ffffff"))
                    item.setDefaultTextColor(color)
                    
                elif itemType in ["Rectangle", "Square"]:
                    pen = QPen(QColor(itemData.get("color", "#ffffff")))
                    brush = QBrush(QColor(itemData.get("fill_color", "#6464ff")))
                    
                    width = itemData.get("properties", {}).get("width", 100)
                    height = itemData.get("properties", {}).get("height", 100)
                    
                    item = CustomRectItem(0, 0, width, height, pen, brush, itemType == "Square")
                    self.scene.addItem(item)
                    
                elif itemType == "Circle":
                    pen = QPen(QColor(itemData.get("color", "#ffffff")))
                    brush = QBrush(QColor(itemData.get("fill_color", "#6464ff")))
                    
                    width = itemData.get("properties", {}).get("width", 80)
                    height = itemData.get("properties", {}).get("height", 80)
                    
                    item = CustomEllipseItem(0, 0, width, height, pen, brush)
                    self.scene.addItem(item)
                    
                else:
                    continue
                
                animatedItem = AnimatedItem(item, itemData.get("name", "Item"))
                animatedItem.properties = itemData.get("properties", {})
                animatedItem.useSmoothing = itemData.get("use_smoothing", True)
                
                for keyframeData in itemData.get("keyframes", []):
                    keyframe = AnimationKeyframe.fromDict(keyframeData)
                    animatedItem.keyframes.append(keyframe)
                
                if animatedItem.keyframes:
                    animatedItem.applyKeyframe(animatedItem.keyframes[0])
                
                self.animatedItems.append(animatedItem)
            
            self.statusBar().showMessage(f"Project loaded from {filename}", 3000)
            
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to load project: {str(e)}")
    
    def exportImgui(self):
        if not self.animatedItems:
            QMessageBox.warning(self, "Warning", "No items to export :(")
            return
        
        filename, _ = QFileDialog.getSaveFileName(self, "Export ImGui Code", "", "C++ Source (*.cpp);;C++ Header (*.h)")
        
        if not filename:
            return
        
        code = exportImguiCode(self.animatedItems)
        
        with open(filename, "w") as f:
            f.write(code)
        
        self.outputText.setText(code)
        self.outputDock.setVisible(True)
        
        self.statusBar().showMessage(f"ImGui code exported to {filename}", 3000)
