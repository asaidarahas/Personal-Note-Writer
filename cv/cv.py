import time

import cv2
import imutils
import numpy as np
import pyautogui
from imutils.video import WebcamVideoStream

from .finger_tracking import HandDetector


class FingerDetector:
    def __init__(self, cam, smooth=9):
        self.cam = cam
        self.width = 640
        self.height = 480
        self.screen_size = pyautogui.size()
        self.detector = HandDetector(detectionCon=0.8)
        self.clocX = 0
        self.clocY = 0
        self.plocX = 0
        self.plocY = 0
        self.smooth = smooth
        self.noFinger = False
        self.clear = False

    def get_finger(self):
        img = self.cam.read()
        img = imutils.resize(img, width=self.width, height=self.height)
        hands, img = self.detector.detect_hands(img)
        if hands:
            hand = hands[-1]

            landmarks = hand["marks"]  # landmarks

            fingers = self.detector.find_fingers(hand)
            if len(landmarks) != 0:
                posx, posy = landmarks[8]
                posx1, posy1 = landmarks[12]
                self.noFinger = False
                self.clear = False
            if sum(fingers) == 5:
                self.clear = True
            else:
                self.clear = False
                if fingers[1] == 1 and fingers[2] == 0:
                    img = self.fingers_move(img, posx, posy)
                elif fingers[1] == 1 and fingers[2] == 1:
                    length, info, img = self.detector.compute_dist((posx, posy), (posx1, posy1), img)
                    if length < 40:
                        cv2.circle(img, (info[4], info[5]), 10, (0, 255, 0), cv2.FILLED)
                        pyautogui.click(button='left')
                    else:
                        self.noFinger = True
                        img = self.fingers_move(img, posx, posy)

        return img

    def fingers_move(self, img, posx, posy, offset=0):
        mousex = np.interp(posx, (0, self.width), (0, self.screen_size[0]))
        mousey = np.interp(posy, (0, self.height), (0, self.screen_size[1]))

        self.clocX = self.plocX + (mousex - self.plocX) / self.smooth
        self.clocY = self.plocY + (mousey - self.plocY) / self.smooth

        if mousex < self.screen_size[0] and mousey < self.screen_size[1]:
            if offset == 0:
                pyautogui.moveTo(self.screen_size[0] - self.clocX, self.clocY, _pause=False)
            else:
                pyautogui.moveTo(self.screen_size[0] - self.clocX, self.clocY - offset, _pause=False)
            cv2.circle(img, (posx, posy), 10, (255, 0, 0), cv2.FILLED)
            self.plocX, self.plocY = self.clocX, self.clocY
        return img

    def fingers_click(self, img, finger1, finger2):
        (posx, posy) = finger1
        (posx1, posy1) = finger2
        length, info, img = self.detector.compute_dist((posx, posy), (posx1, posy1), img)
        if length < 40:
            cv2.circle(img, (info[4], info[5]), 10, (0, 255, 0), cv2.FILLED)
            pyautogui.click(button="left")
        return img

    def show(self, img):
        cv2.namedWindow("Personal Note Writer")  # Create a named window
        cv2.moveWindow("Personal Note Writer", self.screen_size[0] // 3, 0)
        cv2.imshow("Personal Note Writer", img)
        cv2.waitKey(1)

    def run(self):
        start = time.time()
        while True:
            img = self.get_finger()
            end = time.time()
            fps = 1 / (end - start)
            img = cv2.flip(img, 1)
            cv2.putText(img, str(int(fps)), (20, 50), cv2.FONT_HERSHEY_PLAIN, 3, (255, 0, 0), 3)
            self.show(img)
            start = end


def main():
    cam = WebcamVideoStream(src=0).start()
    detector = FingerDetector(cam)
    detector.run()


if __name__ == '__main__':
    main()
