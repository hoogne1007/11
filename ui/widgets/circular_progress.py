from PyQt5.QtWidgets import QWidget
from PyQt5.QtCore import Qt, QRectF
from PyQt5.QtGui import QPainter, QColor, QPen, QFont

class CircularProgressBar(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.value = 0
        self.progress_color = QColor("#03dac6")
        self.background_color = QColor("#4a4a6a")
        self.text_color = QColor("#ffffff")
        self.font_size = 30
        self.progress_width = 15

    def setValue(self, value):
        self.value = value
        self.update() # Trigger a repaint

    def paintEvent(self, event):
        width = self.width()
        height = self.height()
        side = min(width, height)

        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)

        rect = QRectF(
            (width - side) / 2 + self.progress_width / 2,
            (height - side) / 2 + self.progress_width / 2,
            side - self.progress_width,
            side - self.progress_width
        )

        # Background arc
        pen = QPen(self.background_color, self.progress_width, Qt.SolidLine)
        pen.setCapStyle(Qt.RoundCap)
        painter.setPen(pen)
        painter.drawArc(rect, 0, 360 * 16)

        # Progress arc
        pen.setColor(self.progress_color)
        painter.setPen(pen)
        # Angle is degrees * 16 for QPainter
        angle = int(self.value * 3.6 * 16)
        painter.drawArc(rect, 90 * 16, -angle)

        # Text
        pen.setColor(self.text_color)
        painter.setPen(pen)
        font = QFont("Arial", self.font_size, QFont.Bold)
        painter.setFont(font)
        painter.drawText(rect, Qt.AlignCenter, f"{int(self.value)}%")