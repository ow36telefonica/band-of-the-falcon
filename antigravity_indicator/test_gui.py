import sys
from PyQt6.QtWidgets import QApplication, QWidget
from PyQt6.QtCore import Qt

app = QApplication(sys.argv)

screens = app.screens()
windows = []

print(f"Detected {len(screens)} screens.")

for i, s in enumerate(screens):
    geom = s.geometry()
    print(f"Screen {i}: {geom.x()}, {geom.y()}, {geom.width()}x{geom.height()}")
    
    w = QWidget()
    w.setWindowFlags(
        Qt.WindowType.FramelessWindowHint |
        Qt.WindowType.WindowStaysOnTopHint |
        Qt.WindowType.Tool
    )
    # Red bar at the bottom (Height 40px)
    w.setGeometry(geom.x(), geom.y() + geom.height() - 40, geom.width(), 40)
    w.setStyleSheet("background-color: red;")
    w.show()
    w.raise_()
    windows.append(w)

print("Test windows initialized successfully. Keeping app open...")
sys.exit(app.exec())
