import cv2

for i in range(5):
    cap = cv2.VideoCapture(i)
    success, img = cap.read()

    if success:
        print(f"Camera {i} works")

    cap.release()