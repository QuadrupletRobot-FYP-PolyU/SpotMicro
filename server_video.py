import io
import socket
import struct
# from picamera import PiCamera
from threading import Thread
import cv2
# Camera setup
camera_resolution = (1280, 720)
camera_framerate = 24


def video_stream_server(video_path, port):
    # Open video file
    video = cv2.VideoCapture(video_path)

    server_socket = socket.socket()
    server_socket.bind(('172.20.10.10', port))
    server_socket.listen(0)
    print("listening")
    # Accept a single connection
    connection = server_socket.accept()[0].makefile('wb')
    try:
        while True:
            # Read video frame
            ret, frame = video.read()
            if not ret:
                # Restart video if at the end
                video.set(cv2.CAP_PROP_POS_FRAMES, 0)
                continue

            # Encode frame as JPEG
            ret, jpeg = cv2.imencode('.jpg', frame)
            if not ret:
                continue

            # Convert JPEG to bytes
            jpeg_bytes = jpeg.tobytes()
            print(jpeg_bytes)
            # Send the length of the JPEG data
            connection.write(struct.pack('<L', len(jpeg_bytes)))
            connection.flush()

            # Send JPEG data
            connection.write(jpeg_bytes)

    finally:
        connection.close()
        server_socket.close()
        video.release()


def camera_stream_server(camera_index, port):
    with PiCamera() as camera:
        camera.resolution = camera_resolution
        camera.framerate = camera_framerate

        server_socket = socket.socket()
        server_socket.bind(('172.20.10.10', port))
        server_socket.listen(0)

        # Accept a single connection and make a file-like object out of it
        connection = server_socket.accept()[0].makefile('wb')
        try:
            stream = io.BytesIO()
            for _ in camera.capture_continuous(stream, 'jpeg', use_video_port=True):
                # Write the length of the capture to the stream and flush to
                # ensure it actually gets sent
                connection.write(struct.pack('<L', stream.tell()))
                connection.flush()

                # Rewind the stream and send the image data over the wire
                stream.seek(0)
                connection.write(stream.read())

                # Reset the stream for the next capture
                stream.seek(0)
                stream.truncate()
        finally:
            connection.close()
            server_socket.close()


# Path to your MP4 file
video_path = 'video.mp4'

# Start two threads for the two video streams (simulating two cameras)
Thread(target=video_stream_server, args=(
    video_path, 6666)).start()  # Port for left eye
Thread(target=video_stream_server, args=(
    video_path, 6667)).start()  # Port for right eye

# Start two threads for the two camera streams
# Thread(target=camera_stream_server, args=(0, 6666)).start()  # Port for left eye
# Thread(target=camera_stream_server, args=(1, 6667)).start()  # Port for right eye
