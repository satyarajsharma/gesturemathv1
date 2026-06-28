import cvzone
import cv2
from cvzone.HandTrackingModule import HandDetector
import numpy as np
import os
from PIL import Image
from google import genai
import streamlit as st

st.set_page_config(layout="wide")

# --- Initialize Session State Memory ---
# This ensures our drawing doesn't vanish when we click a button!
if 'canvas' not in st.session_state:
    st.session_state.canvas = None


# Initialize Gemini Client HARDCODED HARDCODED HARDCODED
def get_client():
    # You define your variable and give it the string value directly
    api_key = "WRITE THE API HERE"

    # You hand your local 'api_key' variable to Google's 'api_key' parameter
    return genai.Client(api_key=api_key)


client = get_client()



def send_to_gemini(img_array, prompt="Solve this math problem step by step"):
    img_rgb = cv2.cvtColor(img_array, cv2.COLOR_BGR2RGB)
    pil_image = Image.fromarray(img_rgb)
    response = client.models.generate_content(
        model="gemini-2.5-flash",
        contents=[prompt, pil_image]
    )
    return response.text


# --- Computer Vision Setup ---
detector = HandDetector(staticMode=False, maxHands=1, modelComplexity=1, detectionCon=0.7, minTrackCon=0.5)


def getHandInfo(img):
    hands, img = detector.findHands(img, draw=True, flipType=True)
    if hands:
        hand = hands[0]
        fingers = detector.fingersUp(hand)
        lmList = hand["lmList"]
        return fingers, lmList
    return None


def draw(info, prev_pos, canvas, is_eraser):
    fingers, lmList = info
    current_pos = None

    # Draw Mode: Index finger only up [0, 1, 0, 0, 0]
    if fingers == [0, 1, 0, 0, 0]:
        current_pos = lmList[8][0:2]
        if prev_pos is None:
            prev_pos = current_pos

        # Determine color and thickness based on the checkbox
        if is_eraser:
            color = (0, 0, 0)  # Black (Acts as an eraser)
            thickness = 60  # Super thick for easy erasing
        else:
            color = (255, 0, 255)  # Purple ink
            thickness = 10  # Normal pen size

        cv2.line(canvas, current_pos, prev_pos, color, thickness)

    return current_pos


# --- Streamlit Web UI Layout ---
col1, col2 = st.columns([0.6, 0.4])

with col2:
    st.title("Control Panel")

    # 1. The Eraser Toggle
    eraser_mode = st.checkbox("Eraser Mode (Use index finger to erase)", value=False)

    # 2. The Clear Board Button
    if st.button("Clear Board"):
        if st.session_state.canvas is not None:
            # Wipe it back to pure black
            st.session_state.canvas = np.zeros_like(st.session_state.canvas)

            # --- NEW FEATURE: CUSTOM PROMPT ---
    # st.text_input creates a text box on the website.
    # The 'value' is the default text, but you can delete it and type anything live.
    # Whatever is typed in this box gets saved to the 'custom_prompt' variable.
    custom_prompt = st.text_input("Tell Gemini what to do:", value="Solve this math problem step by step")

    # 3. The Get Answer Button (Updated)
    if st.button("Get Answer", type="primary"):
        if st.session_state.canvas is not None:
            with st.spinner("Thinking..."):
                try:
                    # UPDATED LINE: We pass the text from 'custom_prompt' to Gemini
                    result = send_to_gemini(st.session_state.canvas, prompt=custom_prompt)
                    st.success("Got it!")
                    st.write(result)
                except Exception as e:
                    st.error(f"Error: {e}")
        else:
            st.warning("Draw something first!")

with col1:
    st.subheader("Live Air Canvas")
    run = st.checkbox('Toggle Webcam', value=True)
    FRAME_WINDOW = st.image([])

# --- Webcam Loop ---
# This runs constantly while the webcam is checked
if run:
    cap = cv2.VideoCapture(0)
    cap.set(3, 1280)
    cap.set(4, 720)

    prev_pos = None

    while run:
        success, img = cap.read()
        if not success:
            st.error("Webcam failed to start.")
            break

        img = cv2.flip(img, 1)

        # Initialize the memory canvas if it's the first frame
        if st.session_state.canvas is None:
            st.session_state.canvas = np.zeros_like(img)

        info = getHandInfo(img)
        if info:
            # Pass the eraser checkbox state into our draw function
            prev_pos = draw(info, prev_pos, st.session_state.canvas, eraser_mode)
        else:
            prev_pos = None  # Reset if hand leaves frame

        # Combine video and our memory canvas
        image_combined = cv2.addWeighted(img, 0.7, st.session_state.canvas, 0.3, 0)

        # Display to the webpage
        FRAME_WINDOW.image(image_combined, channels="BGR")

    cap.release()