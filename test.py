import cv2

# Initialize the two cameras using their respective device files
cap0 = cv2.VideoCapture('/dev/video0')
cap1 = cv2.VideoCapture('/dev/video2', cv2.CAP_V4L)
cap1.set(cv2.CAP_PROP_FOURCC, cv2.VideoWriter_fourcc(*'MJPG'))

if not cap0.isOpened():
    print("Cannot open camera 0")
    exit()

if not cap1.isOpened():
    print("Cannot open camera 1")
    exit()

# Capture a frame from the first camera
ret0, frame0 = cap0.read()
if ret0:
    cv2.imwrite('camera0_frame.jpg', frame0)
    print("Image saved for camera 0")
else:
    print("Failed to capture frame from camera 0")

# Capture a frame from the second camera
ret1, frame1 = cap1.read()
if ret1:
    cv2.imwrite('camera1_frame.jpg', frame1)
    print("Image saved for camera 1")
else:
    print("Failed to capture frame from camera 1")

# Release the cameras
cap0.release()
cap1.release()
