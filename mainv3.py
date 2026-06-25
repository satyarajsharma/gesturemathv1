import cvzone
import cv2
from cvzone.HandTrackingModule import HandDetector
import numpy as np

# Initialize the webcam to capture video
# The '2' indicates the third camera connected to your computer; '0' would usually refer to the built-in camera
cap = cv2.VideoCapture(0)
cap.set(3, 1280)
cap.set(4, 720)

# Initialize the HandDetector class with the given parameters
detector = HandDetector(staticMode=False, maxHands=2, modelComplexity=1, detectionCon=0.7, minTrackCon=0.5)

def getHandInfo(img):

    # Find hands in the current frame
    # The 'draw' parameter draws landmarks and hand outlines on the image if set to True
    # The 'flipType' parameter flips the image, making it easier for some detections
    hands, img = detector.findHands(img, draw=True, flipType=True)

    # Check if any hands are detected
    if hands:
        # Information for the first hand detected
        hand = hands[0]  # Get the first hand detected
        lmList = hand["lmList"]  # List of 21 landmarks for the first hand
                # Count the number of fingers up for the first hand
        fingers = detector.fingersUp(hand)
        print(fingers)
        return fingers, lmList
    else:
        return None

def draw(info, prev_pos, canvas):
    fingers, lmList = info
    curent_pos= None
    if fingers == [0, 1, 0, 0, 0]:

        current_pos = lmList[8][0:2]
        if prev_pos is None: prev_pos = current_pos
        cv2.line(canvas,current_pos,prev_pos,(255,0,255),10)


        return current_pos

prev_pos= None
canvas=None

# Continuously get frames from the webcam
while True:
    # Capture each frame from the webcam
    # 'success' will be True if the frame is successfully captured, 'img' will contain the frame
    success, img = cap.read()
    img = cv2.flip(img, 1)

    #video completed successfully till 24.12 here

    if canvas is None:
        canvas = np.zeros_like(img)

    info = getHandInfo(img)
    if info:
        fingers, lmList = info
        print(fingers)
        prev_pos = draw(info, prev_pos, canvas)

#video timestamp 12:39

    # Display the image in a window
    cv2.imshow("Image", img)
    cv2.imshow("Canvas", canvas)

    # Keep the window open and update it for each frame; wait for 1 millisecond between frames
    cv2.waitKey(1)