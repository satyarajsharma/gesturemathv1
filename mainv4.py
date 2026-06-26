import cvzone
import cv2
from cvzone.HandTrackingModule import HandDetector
import numpy as np
import os
from PIL import Image
from google import genai
import streamlit as st

# Configure the browser layout to use the full screen width
st.set_page_config(layout="wide")

# Optional: Here is your placeholder line to embed a banner image at the top
# st.image('MathGesturesBanner.png')

# Define layout split: 60% (0.6) for camera, 40% (0.4) for results
col1, col2 = st.columns([0.6, 0.4])

with col1:
    st.subheader("Live Air Canvas")
    run = st.checkbox('Toggle Webcam', value=True)
    FRAME_WINDOW = st.image([])  # Placeholder viewport for the live feed

with col2:
    st.title("Gemini Math Solver")
    output_text_area = st.empty()  # Placeholder for the streaming text output
    output_text_area.info("Write a math equation and hold up 4 fingers to solve it. (Thumb and 3 fingers, not pinky fingee)")

# Initialize HandDetector (maxHands=1)
detector = HandDetector(staticMode=False, maxHands=1, modelComplexity=1, detectionCon=0.7, minTrackCon=0.5)


# Initialize Gemini Client
def get_client():
    # You define your variable and give it the string value directly
    api_key = "WRITE API KEY HERE PLEASE"

    # You hand your local 'api_key' variable to Google's 'api_key' parameter
    return genai.Client(api_key=api_key)


client = get_client()


def getHandInfo(img):
    hands, img = detector.findHands(img, draw=True, flipType=True)
    if hands:
        hand = hands[0]
        fingers = detector.fingersUp(hand)
        lmList = hand["lmList"]
        return fingers, lmList
    return None


def draw(info, prev_pos, canvas):
    fingers, lmList = info
    current_pos = None

    # Draw Mode: Index finger only up
    if fingers == [0, 1, 0, 0, 0]:
        current_pos = lmList[8][0:2]
        if prev_pos is None:
            prev_pos = current_pos
        cv2.line(canvas, current_pos, prev_pos, (255, 0, 255), 10)

    return current_pos


def send_to_gemini(img_array, prompt="Solve this math problem"):
    img_rgb = cv2.cvtColor(img_array, cv2.COLOR_BGR2RGB)
    pil_image = Image.fromarray(img_rgb)

    response = client.models.generate_content(
        model="gemini-2.5-flash",
        contents=[prompt, pil_image]
    )
    return response.text


# State Variables
cap = cv2.VideoCapture(0)
cap.set(3, 1280)
cap.set(4, 720)

prev_pos = None
canvas = None
request_sent = False

# Streamlit Browser Loop
while run:
    success, img = cap.read()
    if not success:
        st.error("Webcam failed to start.")
        break

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
                output_text_area.warning("Thinking... Processing your math problem.")
                try:
                    # Send only the canvas drawing layer to keep the math clean for the AI
                    result = send_to_gemini(canvas, prompt="Solve this math problem step by step")
                    output_text_area.success(result)
                except Exception as e:
                    output_text_area.error(f"GenAI error: {e}")
                request_sent = True
        else:
            request_sent = False
    else:
        prev_pos = None  # Reset tracking if hand leaves the frame

    # Combine video feed and drawing overlay
    image_combined = cv2.addWeighted(img, 0.7, canvas, 0.3, 0)

    # Stream directly into the Streamlit Web UI frame-by-frame
    FRAME_WINDOW.image(image_combined, channels="BGR")

# Cleanup if webcam is toggled off
cap.release()