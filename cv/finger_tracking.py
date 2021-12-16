import math

import cv2
import mediapipe as mp


class HandDetector:
    def __init__(self, detectionCon=0.5, minTrackCon=0.5):
        """
        :param detectionCon: Minimum Detection Confidence Threshold
        :param minTrackCon: Minimum Tracking Confidence Threshold
        """
        self.detectionCon = detectionCon
        self.minTrackCon = minTrackCon

        self.mpHands = mp.solutions.hands
        self.model = self.mpHands.Hands(static_image_mode=False, max_num_hands=2,
                                        min_detection_confidence=self.detectionCon,
                                        min_tracking_confidence=self.minTrackCon)
        self.draw_util = mp.solutions.drawing_utils
        self.num = [4, 8, 12, 16, 20]

    def detect_hands(self, img, draw=True):
        """
        Finds hands in a BGR image.
        :param img: Image to find the hands in.
        :param draw: Flag to draw the output on the image.
        :return: Image with or without drawings
        """
        image = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
        self.output = self.model.process(image)
        my_hands = []
        height, width, channels = img.shape
        if self.output.multi_hand_landmarks:
            for type, keypoints in zip(self.output.multi_handedness, self.output.multi_hand_landmarks):
                features = {}
                landmarks = []
                posx = []
                posy = []
                for id, pos in enumerate(keypoints.landmark):
                    px, py = int(pos.x * width), int(pos.y * height)
                    landmarks.append([px, py])
                    posx.append(px)
                    posy.append(py)

                # Bounding Box
                xmin, xmax = min(posx), max(posx)
                ymin, ymax = min(posy), max(posy)
                boxW, boxH = xmax - xmin, ymax - ymin
                bbox = xmin, ymin, boxW, boxH
                cx, cy = bbox[0] + (bbox[2] // 2), \
                         bbox[1] + (bbox[3] // 2)

                features["marks"] = landmarks
                features["bbox"] = bbox
                features["center"] = (cx, cy)

                if type.classification[0].label == "Right":
                    features["type"] = "Left"
                else:
                    features["type"] = "Right"

                my_hands.append(features)

                # draw
                if draw:
                    self.draw_util.draw_landmarks(img, keypoints,
                                                  self.mpHands.HAND_CONNECTIONS)
                    cv2.rectangle(img, (bbox[0] - 20, bbox[1] - 20),
                                  (bbox[0] + bbox[2] + 20, bbox[1] + bbox[3] + 20),
                                  (0, 255, 0), 2)
        if draw:
            return my_hands, img
        else:
            return my_hands

    def find_fingers(self, features):
        """
        Finds how many fingers are open and returns in a list.
        Considers left and right hands separately
        :return: List of which fingers are up
        """
        type = features["type"]
        landmarks = features["marks"]
        if self.output.multi_hand_landmarks:
            fingers = []
            # Thumb
            if type == "Right":
                if landmarks[self.num[0]][0] > landmarks[self.num[0] - 1][0]:
                    fingers.append(1)
                else:
                    fingers.append(0)
            else:
                if landmarks[self.num[0]][0] < landmarks[self.num[0] - 1][0]:
                    fingers.append(1)
                else:
                    fingers.append(0)

            for id in range(1, 5):
                if landmarks[self.num[id]][1] < landmarks[self.num[id] - 2][1]:
                    fingers.append(1)
                else:
                    fingers.append(0)
        return fingers

    def compute_dist(self, p1, p2, img=None):
        """
        Find the distance between two landmarks based on their
        index numbers.
        :param p1: Point1
        :param p2: Point2
        :param img: Image to draw on.
        :param draw: Flag to draw the output on the image.
        :return: Distance between the points
                 Image with output drawn
                 Line information
        """

        x1, y1 = p1
        x2, y2 = p2
        cx, cy = (x1 + x2) // 2, (y1 + y2) // 2
        length = math.hypot(x2 - x1, y2 - y1)
        info = (x1, y1, x2, y2, cx, cy)
        if img is not None:
            cv2.circle(img, (x1, y1), 8, (255, 0, 0), cv2.FILLED)
            cv2.circle(img, (x2, y2), 8, (255, 0, 0), cv2.FILLED)
            cv2.line(img, (x1, y1), (x2, y2), (255, 0, 0), 3)
            cv2.circle(img, (cx, cy), 8, (255, 0, 0), cv2.FILLED)
            return length, info, img
        else:
            return length, info


def main():
    cap = cv2.VideoCapture(0)
    detector = HandDetector(detectionCon=0.8)
    while True:
        # Get image frame
        success, img = cap.read()
        # Find the hand and its landmarks
        hands, img = detector.detect_hands(img)

        if hands:
            # Hand 1
            hand1 = hands[0]
            marks1 = hand1["marks"]

            if len(hands) == 2:
                # Hand 2
                hand2 = hands[1]
                marks2 = hand2["marks"]

                # Find Distance between two Landmarks. Could be same hand or different hands
                length, info, img = detector.compute_dist(marks1[8], marks2[8], img)
        # Display
        cv2.imshow("Image", img)
        cv2.waitKey(1)


if __name__ == "__main__":
    main()
