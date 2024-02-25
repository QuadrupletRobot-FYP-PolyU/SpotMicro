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

    def video_stream_server(self, video_path, port):
        # Open video file
        video = cv2.VideoCapture('./video.mp4')

        server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        server_socket.bind(('172.20.10.10', port))
        server_socket.listen(1)  # Listen for a single connection

        print(f"Server listening on port {port}")
        print("Waiting for client...")
        connection, client_address = server_socket.accept()
        print(f"Connection from {client_address}")

        try:
            while True:
                ret, frame = video.read()
                if not ret:
                    video.set(cv2.CAP_PROP_POS_FRAMES, 0)
                    continue

                ret, jpeg = cv2.imencode('.jpg', frame)
                if not ret:
                    continue

                jpeg_bytes = jpeg.tobytes()

                self.send_frame(connection, jpeg_bytes)
        except Exception as e:
            print(f"An error occurred: {e}")
        finally:
            connection.close()
            server_socket.close()
            video.release()

    # ... Include other methods here, adjusted for TCP ...

    def do_process_events_from_queues(self):
        video_path = 'video.mp4'

        if Config().get(Config.CAMERA_ACTIVATED) == 'True':
            # Camera streaming logic (omitted, but should be similar to video_stream_server with TCP adjustments)
            pass
        else:
            Thread(target=self.video_stream_server, args=(
                video_path, 6666)).start()  # Port for left eye
            Thread(target=self.video_stream_server, args=(
                video_path, 6667)).start()  # Port for right eye
