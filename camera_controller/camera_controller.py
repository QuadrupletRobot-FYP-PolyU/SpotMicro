import socket
import json
import utilities.queues as queues

class CameraController:
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

        try:
            while True:
                data, addr = self.sock.recvfrom(1024)  # Buffer size is 1024 bytes
                message = data.decode('utf-8')
                input_states = json.loads(message)

                print(f"Received message at {addr}: {input_states}")
                # Process the input states and put them into the appropriate queues
                for command, value in input_states.items():
                    print(f"Message, {command} with value {value}")
                    self.process_command(command, value)

        except KeyboardInterrupt:
            print("\nServer is shutting down.")
        finally:
            self.sock.close()
            print("Server has been closed.")

    def process_command(self, command, value):
        # Process the command and add it to the motion queue with the corresponding value
        # Assuming value is a float indicating the intensity or magnitude of the input
        todo = x