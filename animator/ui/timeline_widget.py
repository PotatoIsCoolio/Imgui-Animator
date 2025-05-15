from PySide6.QtWidgets import *
from PySide6.QtCore import *
from PySide6.QtGui import *

# This file is just with the frames and shit
# Edit these if you need to please. this got to confusing to add settings and shit. 
# Should of tried to do it at the start of this project. Im sorry.

class TimelineWidget(QWidget):
    frameChanged = Signal(int)
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.currentFrame = 0
        self.totalFrames = 100
        self.isPlaying = False
        self.playTimer = QTimer()
        self.playTimer.timeout.connect(self.advanceFrame)
        self.fps = 24
        
        self.setupUI()
        
    def setupUI(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        
        controlsLayout = QHBoxLayout()
        
        self.playButton = QPushButton()
        self.playButton.setIcon(QIcon.fromTheme("media-playback-start"))
        self.playButton.setFixedSize(32, 32)
        self.playButton.clicked.connect(self.togglePlay)
        controlsLayout.addWidget(self.playButton)
        
        self.prevFrameButton = QPushButton()
        self.prevFrameButton.setIcon(QIcon.fromTheme("media-skip-backward"))
        self.prevFrameButton.setFixedSize(32, 32)
        self.prevFrameButton.clicked.connect(self.prevFrame)
        controlsLayout.addWidget(self.prevFrameButton)
        
        self.nextFrameButton = QPushButton()
        self.nextFrameButton.setIcon(QIcon.fromTheme("media-skip-forward"))
        self.nextFrameButton.setFixedSize(32, 32)
        self.nextFrameButton.clicked.connect(self.nextFrame)
        controlsLayout.addWidget(self.nextFrameButton)
        
        self.frameSpinbox = QSpinBox()
        self.frameSpinbox.setRange(0, self.totalFrames)
        self.frameSpinbox.setValue(self.currentFrame)
        self.frameSpinbox.valueChanged.connect(self.setCurrentFrame)
        controlsLayout.addWidget(self.frameSpinbox)
        
        controlsLayout.addWidget(QLabel("FPS:"))
        self.fpsSpinbox = QSpinBox()
        self.fpsSpinbox.setRange(1, 60)
        self.fpsSpinbox.setValue(self.fps)
        self.fpsSpinbox.valueChanged.connect(self.setFps)
        controlsLayout.addWidget(self.fpsSpinbox)
        
        controlsLayout.addWidget(QLabel("Duration:"))
        self.durationSpinbox = QSpinBox()
        self.durationSpinbox.setRange(10, 1000)
        self.durationSpinbox.setValue(self.totalFrames)
        self.durationSpinbox.valueChanged.connect(self.setDuration)
        controlsLayout.addWidget(self.durationSpinbox)
        
        self.addKeyframeButton = QPushButton("Add Keyframe")
        self.addKeyframeButton.clicked.connect(self.addKeyframe)
        controlsLayout.addWidget(self.addKeyframeButton)
        
        controlsLayout.addStretch()
        layout.addLayout(controlsLayout)
        
        self.timelineSlider = QSlider(Qt.Horizontal)
        self.timelineSlider.setRange(0, self.totalFrames)
        self.timelineSlider.setValue(self.currentFrame)
        self.timelineSlider.valueChanged.connect(self.setCurrentFrame)
        layout.addWidget(self.timelineSlider)
        
        self.tracksWidget = QWidget()
        self.tracksLayout = QVBoxLayout(self.tracksWidget)
        self.tracksLayout.setContentsMargins(0, 0, 0, 0)
        self.tracksLayout.setSpacing(1)
        
        scrollArea = QScrollArea()
        scrollArea.setWidgetResizable(True)
        scrollArea.setWidget(self.tracksWidget)
        layout.addWidget(scrollArea)
    
    def togglePlay(self):
        self.isPlaying = not self.isPlaying
        
        if self.isPlaying:
            self.playButton.setIcon(QIcon.fromTheme("media-playback-pause"))
            self.playTimer.start(1000 // self.fps)
        else:
            self.playButton.setIcon(QIcon.fromTheme("media-playback-start"))
            self.playTimer.stop()
    
    def advanceFrame(self):
        nextFrame = self.currentFrame + 1
        if nextFrame > self.totalFrames:
            nextFrame = 0
        
        self.setCurrentFrame(nextFrame)
    
    def prevFrame(self):
        self.setCurrentFrame(max(0, self.currentFrame - 1))
    
    def nextFrame(self):
        self.setCurrentFrame(min(self.totalFrames, self.currentFrame + 1))
    
    def setCurrentFrame(self, frame):
        if frame != self.currentFrame:
            self.currentFrame = frame
            self.frameSpinbox.setValue(frame)
            self.timelineSlider.setValue(frame)
            self.frameChanged.emit(frame)
    
    def setFps(self, fps):
        self.fps = fps
        if self.isPlaying:
            self.playTimer.start(1000 // self.fps)
    
    def setDuration(self, frames):
        self.totalFrames = frames
        self.timelineSlider.setRange(0, frames)
        self.frameSpinbox.setRange(0, frames)
    
    def addKeyframe(self):
        parent = self.parent()
        while parent:
            if hasattr(parent, "addKeyframeAtCurrentFrame"):
                parent.addKeyframeAtCurrentFrame()
                break
            parent = parent.parent()
