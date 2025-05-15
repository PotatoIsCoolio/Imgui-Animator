import sys, os
from PySide6.QtWidgets import *
from PySide6.QtCore import *
from PySide6.QtGui import *
os.chdir(os.path.dirname(os.path.abspath(__file__)))
from animator.ui.main_window import AnimatorMainWindow

# Made by PotatoIsCool
# Someone please fix the bugs I am overwhelm by this
# Also please do not clown on me about how much checks I have in my code
# I was to lazy to write a func that checks it for me :p

app = QApplication(sys.argv)
win = AnimatorMainWindow()
win.show()
sys.exit(app.exec())