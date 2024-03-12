import socket
import busio
import busio
from board import SCL, SDA
import json
from adafruit_motor import servo
import utilities.queues as queues
from adafruit_pca9685 import PCA9685


class CameraController:
    def __init__(self, communication_queues):
        self.i2c = busio.I2C(SCL, SDA)
        pca9685_address = 0x40
        pca9685_reference_clock_speed = 25000000
        pca9685_frequency = 50
        self.pca9685 = PCA9685(self.i2c, address=pca9685_address,
                               reference_clock_speed=pca9685_reference_clock_speed)
        self.pca9685.frequency = pca9685_frequency
        # Set up the UDP server
        self.udp_ip = "172.20.10.10"
        self.udp_port = 8888
        # Create a UDP socket
        self.horizontalServo = servo.Servo(self.pca9685.channels[15])
        self.horizontalServo.angle = 90
        self.verticalServo = servo.Servo(self.pca9685.channels[14])
        self.verticalServo.angle = 90
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
                data, addr = self.sock.recvfrom(
                    1024)  # Buffer size is 1024 bytes
                message = data.decode('utf-8')
                input_states = json.loads(message)

                # print(f"Received message at {addr}: {input_states}")
                # Process the input states and put them into the appropriate queues
                for command, value in input_states.items():
                 #   print(f"Message, {command} with value {value}")
                    self.process_command(command, value)

        except KeyboardInterrupt:
            print("\nServer is shutting down.")
        finally:
            self.sock.close()
            print("Server has been closed.")

    def process_command(self, command, value):
        x = 10
        # Process the command and add it to the motion queue with the corresponding value
        # Assuming value is a float indicating the intensity or magnitude of the input
        # if command == "horizontal":
        # Calculate potential new angle based on current angle and value
        # newAngle = self.horizontalServo.angle + (3 * int(value))
        # Clamp the new angle to the servo's safe operating range
        # newAngle = max(0, min(180, newAngle))

        # Set the servo to the new angle if it's within the valid range
        # if 0 <= newAngle <= 180:
        # print(
        # f"Setting horizontal servo from angle {self.horizontalServo.angle} to {newAngle}")
        # self.horizontalServo.angle = newAngle
        # else:
        # print(f"Horizontal servo command out of range: {newAngle}")

        # elif command == "vertical":
        # Calculate potential new angle based on current angle and value
        # newAngle = self.verticalServo.angle + (3 * int(value))
        # Clamp the new angle to the servo's safe operating range
        # newAngle = max(0, min(180, newAngle))

        # Set the servo to the new angle if it's within the valid range
        # if 0 <= newAngle <= 180:
        # print(
        #       f"Setting vertical servo from angle {self.verticalServo.angle} to {newAngle}")
        # self.verticalServo.angle = newAngle
        # else:
        # print(f"Vertical servo command out of range: {newAngle}")
