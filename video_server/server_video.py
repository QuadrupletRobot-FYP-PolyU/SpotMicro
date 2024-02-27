import io
import socket
import struct
# from picamera import PiCamera
from threading import Thread
import cv2
import os
from utilities.config import Config
import utilities.queues as queues


class ServerVideo:
    camera_resolution = (1920, 1080)
    camera_framerate = 60
    # Maximum size for TCP packet, can be set to a higher number than UDP
    max_packet_size = 65536

    def __init__(self, communication_queues):
        self._abort_queue = communication_queues[queues.ABORT_CONTROLLER]
        self._motion_queue = communication_queues[queues.MOTION_CONTROLLER]
        self._lcd_screen_queue = communication_queues[queues.LCD_SCREEN_CONTROLLER]
        self._video_queue = communication_queues[queues.VIDEO_SERVER_CONTROLLER]
        self._server_controller = communication_queues[queues.REMOTE_CONTROLLER_CONTROLLER]

    def send_frame(self, connection, frame_data):
        # Send the length of the frame data
        connection.sendall(struct.pack('<L', len(frame_data)))

        # Send the frame data
        connection.sendall(frame_data)

    def video_stream_server(self, port, camera_index_left, camera_index_right):
        camera_left = cv2.VideoCapture(camera_index_left)
        camera_right = cv2.VideoCapture(camera_index_right)

        camera_right.set(cv2.CAP_PROP_FOURCC, cv2.VideoWriter_fourcc(*'MJPG'))
        camera_left.set(cv2.CAP_PROP_FRAME_WIDTH, self.camera_resolution[0])
        camera_left.set(cv2.CAP_PROP_FRAME_HEIGHT, self.camera_resolution[1])
        camera_right.set(cv2.CAP_PROP_FRAME_WIDTH, self.camera_resolution[0])
        camera_right.set(cv2.CAP_PROP_FRAME_HEIGHT, self.camera_resolution[1])

        server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        server_socket.bind(('172.20.10.10', port))
        server_socket.listen(1)
        print(f"Server listening on port {port}")
        print("Waiting for client...")
        connection, client_address = server_socket.accept()
        print(f"Connection from {client_address}")

        try:
            while True:
                ret_left, frame_left = camera_left.read()
                ret_right, frame_right = camera_right.read()

                if not ret_left or not ret_right:
                    print("Failed to grab frame")
                    break

                # Stitch the frames side by side
                stitched_frame = np.hstack((frame_left, frame_right))

                ret, jpeg = cv2.imencode('.jpg', stitched_frame)
                if not ret:
                    print("Failed to encode frame")
                    continue

                jpeg_bytes = jpeg.tobytes()
                self.send_frame(connection, jpeg_bytes)

        except Exception as e:
            print(f"An error occurred: {e}")
        finally:
            connection.close()
            server_socket.close()
            camera_left.release()
            camera_right.release()

    # ... Include other methods here, adjusted for TCP ...

    def do_process_events_from_queues(self):
        camera_index_left = 0
        camera_index_right = 1
        Thread(target=self.video_stream_server, args=(
            6666, camera_index_left, camera_index_right)).start()  # Port for right eye
