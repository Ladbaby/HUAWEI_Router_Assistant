# coding:utf-8
from PyQt5.QtCore import Qt, QRectF, QSize
from PyQt5.QtGui import QPixmap, QPainter, QBrush, QPainterPath
from PyQt5.QtWidgets import QWidget

class Backdrop(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setObjectName('backdrop')
        self.banner = QPixmap(':/gallery/images/background.jpg')

    def paintEvent(self, e) -> None:
        super().paintEvent(e)
        painter = QPainter(self)
        painter.setRenderHints(
            QPainter.SmoothPixmapTransform | QPainter.Antialiasing)
        painter.setPen(Qt.NoPen)

        path = QPainterPath()
        path.setFillRule(Qt.WindingFill)
        w, h = self.width(), 200
        path.addRoundedRect(QRectF(0, 0, w, h), 10, 10)
        path.addRect(QRectF(0, h-50, 50, 50))
        path.addRect(QRectF(w-50, 0, 50, 50))
        path.addRect(QRectF(w-50, h-50, 50, 50))
        path = path.simplified()

        # draw background color
        # if not isDarkTheme():
        #     painter.fillPath(path, QColor(206, 216, 228))
        # else:
        #     # painter.fillPath(path, QColor(39, 39, 39))
        #     painter.fillPath(path, QColor(255, 0, 0))
            # painter.fillPath(path, Qt.transparent)

        # draw banner image
        pixmap = self.banner.scaled(
            QSize(self.width(), self.height()), transformMode=Qt.SmoothTransformation, aspectRatioMode=Qt.KeepAspectRatioByExpanding)
        path.addRect(QRectF(0, h, w, self.height() - h))
        painter.fillPath(path, QBrush(pixmap))
