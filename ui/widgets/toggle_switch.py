from PyQt5.QtWidgets import QCheckBox
from PyQt5.QtCore import Qt, QSize, QPoint, QRectF
from PyQt5.QtGui import QPainter, QColor, QBrush, QPen

class ToggleSwitch(QCheckBox):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setCursor(Qt.PointingHandCursor)

    def sizeHint(self):
        return QSize(58, 28)

    def hitButton(self, pos: QPoint):
        return self.contentsRect().contains(pos)

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)

        # Set colors based on checked state
        if self.isChecked():
            bg_color = QColor("#6200ea")
            handle_color = QColor("#ffffff")
        else:
            bg_color = QColor("#4a4a6a")
            handle_color = QColor("#d0d0d0")
            
        painter.setPen(Qt.NoPen)
        
        # Draw background
        rect = QRectF(0, 0, self.width(), self.height())
        painter.setBrush(QBrush(bg_color))
        painter.drawRoundedRect(rect, self.height() / 2, self.height() / 2)
        
        # Draw handle
        handle_radius = (self.height() - 6) / 2
        handle_x = 3 if not self.isChecked() else self.width() - 3 - 2 * handle_radius
        
        painter.setBrush(QBrush(handle_color))
        painter.drawEllipse(QPoint(int(handle_x + handle_radius), int(self.height() / 2)), int(handle_radius), int(handle_radius))