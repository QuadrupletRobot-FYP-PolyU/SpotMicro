import socket
import json
import utilities.queues as queues


class ServerController:
    def __init__(self, communication_queues):
        # Set up the UDP server
        self.udp_ip = "172.20.10.10"
        self.udp_port = 7777
        # Create a UDP socket
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

        self._abort_queue = communication_queues[queues.ABORT_CONTROLLER]
        self._motion_queue = communication_queues[queues.MOTION_CONTROLLER]
        self._lcd_screen_queue = communication_queues[queues.LCD_SCREEN_CONTROLLER]
        self._video_queue = communication_queues[queues.VIDEO_SERVER_CONTROLLER]
        self._server_controller = communication_queues[queues.REMOTE_CONTROLLER_CONTROLLER]

    def do_process_events_from_queues(self):
        # Bind the socket to the IP and port
        self.sock.bind((self.udp_ip, self.udp_port))
        print(f"UDP server up and listening at {self.udp_ip}:{self.udp_port}")
        self._motion_queue.put('a')
        try:
            while True:
                data, addr = self.sock.recvfrom(
                    1024)  # Buffer size is 1024 bytes

                message = data.decode('utf-8')
                input_states = json.loads(message)
                
                print(f"Received message from {addr}: {input_states}")

        except KeyboardInterrupt:
            print("\nServer is shutting down.")

        finally:
            # Close the socket
            self.sock.close()
            print("Server has been closed.")
