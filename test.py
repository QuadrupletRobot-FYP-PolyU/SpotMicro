import cv2
import time

# The device number might be 0 or any other integer, depending on your system
# If you have one camera, it is likely to be 0
cap = cv2.VideoCapture(0)

if not cap.isOpened():
    print("Cannot open camera")
    exit()

# Set a filename
filename = "captured_frame.jpg"

try:
    # Capture a single frame
    ret, frame = cap.read()
    if ret:
        # If the frame is captured correctly, save it
        cv2.imwrite(filename, frame)
        print(f"Image saved as {filename}")
    else:
        print("Can't receive frame (stream end?). Exiting ...")
finally:
    # When everything done, release the capture
    cap.release()

# Optional: If you want to set a delay between captures, use time.sleep
# time.sleep(2)
