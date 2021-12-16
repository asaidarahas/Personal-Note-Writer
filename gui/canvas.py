import sys

import cv2
import numpy as np
from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *


class Canvas(QWidget):
    newPoint = pyqtSignal(QPoint)

    def __init__(self, parent=None):
        QWidget.__init__(self, parent)
        self.path = QPainterPath()
        self.plain_image = QImage(self.size(), QImage.Format_RGB888)  # TODO: change it to RGB888?
        self.plain_image.fill(QColor('white'))
        self.setCursor(QCursor(Qt.PointingHandCursor))
        self.drawing = False
        self.brushSize = 7
        self.brushColor = Qt.black
        self.lastPoint = QPoint()
        self.setMouseTracking(True)
        self.startPoint = QPoint()

    def paintEvent(self, event):
        writer = QPainter(self)
        writer.drawImage(self.rect(), self.plain_image, self.plain_image.rect())
        # writer.end()

    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            self.drawing = True
            self.lastPoint = event.pos()

    def mouseMoveEvent(self, event):
        if not self.drawing:
            self.lastPoint = QPoint()
        else:
            painter = QPainter(self.plain_image)
            painter.setPen(QPen(self.brushColor, self.brushSize, Qt.SolidLine, Qt.RoundCap, Qt.RoundJoin))
            if self.lastPoint == QPoint():
                pass
            else:
                painter.drawLine(self.lastPoint, event.pos())
            self.lastPoint = event.pos()
            self.update()

    def mouseReleaseEvent(self, event):
        if event.button() == Qt.LeftButton:
            self.drawing = False

    def sizeHint(self):
        return self.size()

    def write_back(self):
        self.setCursor(QCursor(Qt.PointingHandCursor))
        self.drawing = True
        self.brushSize = 7
        self.brushColor = Qt.black

    def draw_bounding_box(self, begin, end, width, height, conf):
        writer = QPainter(self.plain_image)
        writer.setPen(Qt.red)
        writer.drawRect(begin, end, width, height)
        writer.setFont(QFont("times", 22))
        writer.drawText(begin, end, str(conf))
        self.update()

    def write_stop(self):
        self.drawing = False

    def get_array(self, incomingImage=None):
        if not incomingImage:
            incomingImage = self.plain_image
        incomingImage = incomingImage.convertToFormat(4)

        width = incomingImage.width()
        height = incomingImage.height()

        ptr = incomingImage.bits()
        ptr.setsize(incomingImage.byteCount())
        arr = np.array(ptr).reshape(height, width, 4)  # Copies the data
        return arr

    def open_image(self, filename):
        with open(filename, 'rb') as f:
            content = f.read()
        # w = QLabel()
        self.plain_image.loadFromData(content)
        # w.setPixmap(QPixmap.fromImage())
        self.update()

    def save_image(self, filename):
        image = self.get_array()
        cv2.imwrite(filename, image)

    def set_pen(self):
        self.setCursor(QCursor(Qt.PointingHandCursor))
        self.brushSize = 7
        self.brushColor = Qt.black

    def set_erase(self):
        self.setCursor(QCursor(Qt.OpenHandCursor))
        self.brushSize = 15
        self.brushColor = Qt.white

    def clear(self, trigger=True):
        if trigger:
            self.plain_image.fill(Qt.white)
            self.update()


if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = Canvas()
    window.show()
    app.exec()
