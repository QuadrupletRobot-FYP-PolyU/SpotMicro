import io
import socket
import struct
# from picamera import PiCamera
from threading import Thread
import cv2
import sys
from utilities.config import Config
import utilities.queues as queues


class ServerVideo:
    camera_resolution = (1280, 720)
    camera_framerate = 24

    def __init__(self, communication_queues):
        self._abort_queue = communication_queues[queues.ABORT_CONTROLLER]
        self._motion_queue = communication_queues[queues.MOTION_CONTROLLER]
        self._lcd_screen_queue = communication_queues[queues.LCD_SCREEN_CONTROLLER]
        self._video_queue = communication_queues[queues.VIDEO_SERVER_CONTROLLER]
        self._server_controller = communication_queues[queues.REMOTE_CONTROLLER_CONTROLLER]

    def video_stream_server(self, video_path, port):
        # Open video file
        video = cv2.VideoCapture('./video.mp4')
        server_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        server_socket.bind(('', port))  # Listen on all interfaces

        print(f"Server listening on port {port}")
        # Wait for a client to send a message to get their address
        print("Waiting for client...")
        message, client_address = server_socket.recvfrom(1024)
        print(f"Connection from {client_address}")

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

                # Send the length of the JPEG data
                num_packets = len(jpeg_bytes) // self.max_packet_size + 1

                # Send the number of packets to expect
                server_socket.sendto(struct.pack(
                    '<L', num_packets), client_address)

                # Split data into packets and send each one
                for i in range(num_packets):
                    start = i * self.max_packet_size
                    end = start + self.max_packet_size
                    packet = jpeg_bytes[start:end]
                    server_socket.sendto(packet, client_address)
        except Exception as e:
            print(f"An error occurred: {e}")
        finally:
            server_socket.close()
            video.release()

    def camera_stream_server(self, camera_index, port):
        with PiCamera() as camera:
            camera.resolution = self.camera_resolution
            camera.framerate = self.camera_framerate
            server_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
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

    def do_process_events_from_queues(self):
        # Path to your MP4 file
        video_path = 'video.mp4'

        if Config().get(Config.CAMERA_ACTIVATED) == 'True':
            Thread(target=self.camera_stream_server, args=(
                0, 6666)).start()  # Port for left eye
            Thread(target=self.camera_stream_server, args=(
                1, 6667)).start()  # Port for right eye
        else:
            # Start two threads for the two video streams (simulating two cameras)
            Thread(target=self.video_stream_server, args=(
                video_path, 6666)).start()  # Port for left eye
            Thread(target=self.video_stream_server, args=(
                video_path, 6667)).start()  # Port for right eye
