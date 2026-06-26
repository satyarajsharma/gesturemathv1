import cvzone
import cv2
from cvzone.HandTrackingModule import HandDetector
import numpy as np
import os
from PIL import Image
from google import genai

# Initialize the webcam to capture video
cap = cv2.VideoCapture(0)
cap.set(3, 1280)
cap.set(4, 720)

# Initialize HandDetector (Changed maxHands to 1 as requested)
detector = HandDetector(staticMode=False, maxHands=1, modelComplexity=1, detectionCon=0.7, minTrackCon=0.5)


# Initialize Gemini Client
def get_client():
    # Python asks your operating system: "Hey, do you have a hidden variable named 'API_KEY'?"
    # If set up correctly, your OS hands back "YAHAHAHAHA" (YAHAHAHA being the api key)
    api_key = os.environ.get("API_KEY")

    # A quick safety check: if the OS didn't find it, stop the program and warn you.
    if not api_key:
        raise RuntimeError("Set API_KEY env var")

    # You hand the successfully retrieved string to Google
    return genai.Client(api_key=api_key)


client = get_client()


def getHandInfo(img):
    hands, img = detector.findHands(img, draw=True, flipType=True)
    if hands:
        hand = hands[0]
        lmList = hand["lmList"]
        fingers = detector.fingersUp(hand)
        return fingers, lmList
    else:
        return None


def draw(info, prev_pos, canvas):
    fingers, lmList = info
    current_pos = None

    # Draw mode: Index finger only
    if fingers == [0, 1, 0, 0, 0]:
        current_pos = lmList[8][0:2]
        if prev_pos is None:
            prev_pos = current_pos
        cv2.line(canvas, current_pos, prev_pos, (255, 0, 255), 10)

    return current_pos


def send_to_gemini(img_array, prompt="Solve this math problem"):
    # Convert OpenCV BGR to RGB, then to PIL
    img_rgb = cv2.cvtColor(img_array, cv2.COLOR_BGR2RGB)
    pil_image = Image.fromarray(img_rgb)

    # Send to the Gemini model
    response = client.models.generate_content(
        model="gemini-2.5-flash",
        contents=[prompt, pil_image]
    )
    return response.text


# Variables
prev_pos = None
canvas = None
image_combined = None
request_sent = False

while True:
    success, img = cap.read()
    img = cv2.flip(img, 1)

    if canvas is None:
        canvas = np.zeros_like(img)

    info = getHandInfo(img)
    if info:
        fingers, lmList = info
        prev_pos = draw(info, prev_pos, canvas)

        # Trigger API: 4 fingers up
        if fingers == [1, 1, 1, 1, 0]:
            if not request_sent:
                print("Sending to Gemini 3.5 Flash... Please wait.")
                try:
                    result = send_to_gemini(canvas, prompt="Write about how meaningful this is")
                    print("Gemini Answer:\n", result)
                except Exception as e:
                    print("GenAI error:", e)
                request_sent = True
        else:
            request_sent = False

            # Combine webcam feed and canvas
    image_combined = cv2.addWeighted(img, 0.7, canvas, 0.3, 0)

    # Display windows
    cv2.imshow("Image Combined", image_combined)

    # Press 'q' to quit
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()