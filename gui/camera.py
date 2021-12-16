import cv2
from PyQt5.QtCore import *
from imutils.video import WebcamVideoStream
from numpy import ndarray

from cv.cv import FingerDetector


class Worker(QThread):
    # Data signals
    frameData = pyqtSignal(ndarray)
    noFinger = pyqtSignal(bool)
    clearGesture = pyqtSignal(bool)

    def __init__(self):
        QThread.__init__(self)
        self.detector = None
        self.active = None

    def run(self):
        self.active = True
        cam = WebcamVideoStream(src=0).start()
        self.detector = FingerDetector(cam)
        while True:
            image = self.detector.get_finger()
            self.noFinger.emit(self.detector.noFinger)
            self.clearGesture.emit(self.detector.clear)
            if self.active:
                image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
                image = cv2.flip(image, 1)
                self.frameData.emit(image)

    def stop(self):
        self.active = False
        self.quit()
