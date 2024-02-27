import cv2
import time

# Initialize the two cameras
cap0 = cv2.VideoCapture(0)
cap1 = cv2.VideoCapture(1)

if not cap0.isOpened() or not cap1.isOpened():
    print("Cannot open one or both cameras")
    exit()

# Set filenames for the captured images
filename0 = "camera0_frame.jpg"
filename1 = "camera1_frame.jpg"

try:
    # Capture a frame from the first camera
    ret0, frame0 = cap0.read()
    if ret0:
        cv2.imwrite(filename0, frame0)
        print(f"Image saved as {filename0}")
    else:
        print("Can't receive frame from camera 0 (stream end?). Exiting ...")

    # Capture a frame from the second camera
    ret1, frame1 = cap1.read()
    if ret1:
        cv2.imwrite(filename1, frame1)
        print(f"Image saved as {filename1}")
    else:
        print("Can't receive frame from camera 1 (stream end?). Exiting ...")
finally:
    # When everything is done, release the captures
    cap0.release()
    cap1.release()

# Optional: If you want to set a delay between captures, use time.sleep
# time.sleep(2)
