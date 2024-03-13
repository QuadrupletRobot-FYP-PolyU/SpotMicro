import busio
import queue
from board import SCL, SDA
from adafruit_pca9685 import PCA9685
from adafruit_motor import servo
from adafruit_servokit import ServoKit
import time
import sys
import traceback
from utilities.general import General
from utilities.log import Logger
from utilities.config import Config
import utilities.queues as queues
from kinematics.kinematics import ikine


log = Logger().setup_logger('Motion controller')


class MotionController:
    boards = 1
    is_activated = False
    i2c = None
    pca9685_1 = None

    pca9685_address = None
    pca9685_reference_clock_speed = None
    pca9685_frequency = None

    rear_shoulder_left = None
    rear_shoulder_left_pca9685 = None
    rear_shoulder_left_channel = None
    rear_shoulder_left_min_pulse = None
    rear_shoulder_left_max_pulse = None
    rear_shoulder_left_rest_angle = None

    rear_leg_left = None
    rear_leg_left_pca9685 = None
    rear_leg_left_channel = None
    rear_leg_left_min_pulse = None
    rear_leg_left_max_pulse = None
    rear_leg_left_rest_angle = None

    rear_feet_left = None
    rear_feet_left_pca9685 = None
    rear_feet_left_channel = None
    rear_feet_left_min_pulse = None
    rear_feet_left_max_pulse = None
    rear_feet_left_rest_angle = None

    rear_shoulder_right = None
    rear_shoulder_right_pca9685 = None
    rear_shoulder_right_channel = None
    rear_shoulder_right_min_pulse = None
    rear_shoulder_right_max_pulse = None
    rear_shoulder_right_rest_angle = None

    rear_leg_right = None
    rear_leg_right_pca9685 = None
    rear_leg_right_channel = None
    rear_leg_right_min_pulse = None
    rear_leg_right_max_pulse = None
    rear_leg_right_rest_angle = None

    rear_feet_right = None
    rear_feet_right_pca9685 = None
    rear_feet_right_channel = None
    rear_feet_right_min_pulse = None
    rear_feet_right_max_pulse = None
    rear_feet_right_rest_angle = None

    front_shoulder_left = None
    front_shoulder_left_pca9685 = None
    front_shoulder_left_channel = None
    front_shoulder_left_min_pulse = None
    front_shoulder_left_max_pulse = None
    front_shoulder_left_rest_angle = None

    front_leg_left = None
    front_leg_left_pca9685 = None
    front_leg_left_channel = None
    front_leg_left_min_pulse = None
    front_leg_left_max_pulse = None
    front_leg_left_rest_angle = None

    front_feet_left = None
    front_feet_left_pca9685 = None
    front_feet_left_channel = None
    front_feet_left_min_pulse = None
    front_feet_left_max_pulse = None
    front_feet_left_rest_angle = None

    front_shoulder_right = None
    front_shoulder_right_pca9685 = None
    front_shoulder_right_channel = None
    front_shoulder_right_min_pulse = None
    front_shoulder_right_max_pulse = None
    front_shoulder_right_rest_angle = None

    front_leg_right = None
    front_leg_right_pca9685 = None
    front_leg_right_channel = None
    front_leg_right_min_pulse = None
    front_leg_right_max_pulse = None
    front_leg_right_rest_angle = None

    front_feet_right = None
    front_feet_right_pca9685 = None
    front_feet_right_channel = None
    front_feet_right_min_pulse = None
    front_feet_right_max_pulse = None
    front_feet_right_rest_angle = None

    def __init__(self, communication_queues):
        try:

            log.debug('Starting controller...')

            self.i2c = busio.I2C(SCL, SDA)
            self.load_pca9685_boards_configuration()
            self.load_servos_configuration()
            self.is_activated = False
            self._abort_queue = communication_queues[queues.ABORT_CONTROLLER]
            self._motion_queue = communication_queues[queues.MOTION_CONTROLLER]
            self._lcd_screen_queue = communication_queues[queues.LCD_SCREEN_CONTROLLER]
            self._video_queue = communication_queues[queues.VIDEO_SERVER_CONTROLLER]
            self._server_controller = communication_queues[queues.REMOTE_CONTROLLER_CONTROLLER]

            self._previous_event = {}

        except Exception as e:
            log.error('Motion controller initialization problem', e)

            try:
                self.pca9685_1.deinit()
            finally:
                try:
                    if self.boards == 2:
                        self.pca9685_2.deinit()
                finally:
                    sys.exit(1)

    def exit_gracefully(self):
        try:
            self.pca9685_1.deinit()
        finally:
            try:
                if self.boards == 2:
                    self.pca9685_2.deinit()
            finally:
                log.info('Terminated')
                sys.exit(0)

    def do_process_events_from_queues(self):

        while True:

            try:

                event = self._motion_queue.get(block=True, timeout=60)
                print(event)
                # log.debug(event)

                if event['start']:
                    if self.is_activated:
                        self.rest_position()
                        time.sleep(0.5)
                        self.deactivate_pca9685_boards()
                        self._abort_queue.put(
                            queues.ABORT_CONTROLLER_ACTION_ABORT)
                    else:
                        self.activate_pca9685_boards()
                        self.activate_servos()
                        self.rest_position()

                if not self.is_activated:
                    log.info('Press START/OPTIONS to enable the servos')
                    continue

                if event['a']:
                    self.rest_position()

                if event['y']:
                    self.standing_position()

                if event['b']:
                    self.walk_forward(1, 0.1, 0.186, 0.078,
                                      0.055, 0.1075, 0.130)

                time.sleep(2)
                self.move()
            except queue.Empty as e:
                log.info('Inactivity lasted 60 seconds, shutting down the servos, '
                         'press start to reactivate')
                if self.is_activated:
                    self.rest_position()
                    time.sleep(0.5)
                    self.deactivate_pca9685_boards()

            except Exception as e:
                traceback.print_exc()

                # If you want to capture the traceback as a string, you can use traceback.format_exc()
                exception_traceback = traceback.format_exc()
                print(exception_traceback)
                log.error(
                    'Unknown problem while processing the queue of the motion controller')
                log.error(
                    ' - Most likely a servo is not able to get to the assigned position')

    def walk_forward(self, steps, distance, body_length, body_width, l1, l2, l3):

        # Define the height of the step and the leg lifting sequence
        step_height = 0.3
        sequence = ['RearRight', 'FrontLeft', 'RearLeft', 'FrontRight']

        for _ in range(steps):
            for leg_name in sequence:
                # Lift the leg
                x_lift, y_lift, z_lift = l1, 0, step_height
                theta1, theta2, theta3 = ikine(x_lift, y_lift, z_lift, l1, l2, l3, leg_name in [
                                               'FrontLeft', 'FrontRight'])

                # Update the leg joint angles to lift the leg
                self.move_leg(leg_name, theta1, theta2, theta3)

                # Move the leg forward
                x_forward, y_forward, z_forward = distance, 0, step_height
                theta1, theta2, theta3 = ikine(
                    x_forward, y_forward, z_forward, l1, l2, l3, leg_name in ['FrontLeft', 'FrontRight'])

                # Update the leg joint angles to position the leg forward
                self.move_leg(leg_name, theta1, theta2, theta3)

                # Lower the leg
                x_down, y_down, z_down = distance, 0, 0
                theta1, theta2, theta3 = ikine(x_down, y_down, z_down, l1, l2, l3, leg_name in [
                                               'FrontLeft', 'FrontRight'])

                # Update the leg joint angles to lower the leg
                self.move_leg(leg_name, theta1, theta2, theta3)

    def load_pca9685_boards_configuration(self):
        self.pca9685_address = int(Config().get(
            Config.MOTION_CONTROLLER_BOARDS_PCA9685_1_ADDRESS), 0)
        if self.pca9685_address != 40:
            self.pca9685_address = 0x40
        self.pca9685_reference_clock_speed = int(Config().get(
            Config.MOTION_CONTROLLER_BOARDS_PCA9685_1_REFERENCE_CLOCK_SPEED))
        self.pca9685_frequency = int(Config().get(
            Config.MOTION_CONTROLLER_BOARDS_PCA9685_1_FREQUENCY))

        print(f"address: {self.pca9685_address}, reference clock speed: {self.pca9685_reference_clock_speed}, frequency:{self.pca9685_frequency}")

    def activate_pca9685_boards(self):

        self.pca9685 = PCA9685(self.i2c, address=self.pca9685_address,
                               reference_clock_speed=self.pca9685_reference_clock_speed)
        self.pca9685.frequency = self.pca9685_frequency

        self.is_activated = True
        print(f"Activated: {self.is_activated}")
        log.debug(str(self.boards) + ' PCA9685 board(s) activated')

    def deactivate_pca9685_boards(self):

        try:
            if self.pca9685:
                self.pca9685.deinit()
        except Exception as e:
            log.debug(str(e) + 'Could not de initialize the board')

        log.debug(str(self.boards) + ' PCA9685 board(s) deactivated')

    def load_servos_configuration(self):

        self.servo_rear_shoulder_left_pca9685 = Config().get(
            Config.MOTION_CONTROLLER_SERVOS_REAR_SHOULDER_LEFT_PCA9685)
        self.servo_rear_shoulder_left_channel = Config().get(
            Config.MOTION_CONTROLLER_SERVOS_REAR_SHOULDER_LEFT_CHANNEL)
        self.servo_rear_shoulder_left_min_pulse = Config().get(
            Config.MOTION_CONTROLLER_SERVOS_REAR_SHOULDER_LEFT_MIN_PULSE)
        self.servo_rear_shoulder_left_max_pulse = Config().get(
            Config.MOTION_CONTROLLER_SERVOS_REAR_SHOULDER_LEFT_MAX_PULSE)
        self.servo_rear_shoulder_left_rest_angle = Config().get(
            Config.MOTION_CONTROLLER_SERVOS_REAR_SHOULDER_LEFT_REST_ANGLE)

        print(f"rl_shoulder_servo: {self.servo_rear_shoulder_left_pca9685}, channel: {self.servo_rear_shoulder_left_channel},min_pulse: {self.servo_rear_shoulder_left_min_pulse},  max_pulse: {self.servo_rear_shoulder_left_max_pulse},rest: {self.servo_rear_shoulder_left_rest_angle}")

        self.servo_rear_leg_left_pca9685 = Config().get(
            Config.MOTION_CONTROLLER_SERVOS_REAR_LEG_LEFT_PCA9685)
        self.servo_rear_leg_left_channel = Config().get(
            Config.MOTION_CONTROLLER_SERVOS_REAR_LEG_LEFT_CHANNEL)
        self.servo_rear_leg_left_min_pulse = Config().get(
            Config.MOTION_CONTROLLER_SERVOS_REAR_LEG_LEFT_MIN_PULSE)
        self.servo_rear_leg_left_max_pulse = Config().get(
            Config.MOTION_CONTROLLER_SERVOS_REAR_LEG_LEFT_MAX_PULSE)
        self.servo_rear_leg_left_rest_angle = Config().get(
            Config.MOTION_CONTROLLER_SERVOS_REAR_LEG_LEFT_REST_ANGLE)

        print(f"rl_leg_servo: {self.servo_rear_leg_left_pca9685}, channel: {self.servo_rear_leg_left_channel}, min_pulse: {self.servo_rear_leg_left_min_pulse},  max_pulse: {self.servo_rear_leg_left_max_pulse},rest: {self.servo_rear_leg_left_rest_angle}")

        self.servo_rear_feet_left_pca9685 = Config().get(
            Config.MOTION_CONTROLLER_SERVOS_REAR_FEET_LEFT_PCA9685)
        self.servo_rear_feet_left_channel = Config().get(
            Config.MOTION_CONTROLLER_SERVOS_REAR_FEET_LEFT_CHANNEL)
        self.servo_rear_feet_left_min_pulse = Config().get(
            Config.MOTION_CONTROLLER_SERVOS_REAR_FEET_LEFT_MIN_PULSE)
        self.servo_rear_feet_left_max_pulse = Config().get(
            Config.MOTION_CONTROLLER_SERVOS_REAR_FEET_LEFT_MAX_PULSE)
        self.servo_rear_feet_left_rest_angle = Config().get(
            Config.MOTION_CONTROLLER_SERVOS_REAR_FEET_LEFT_REST_ANGLE)

        print(f"rl_feet_servo: {self.servo_rear_feet_left_pca9685}, channel: {self.servo_rear_feet_left_channel},min_pulse: {self.servo_rear_feet_left_min_pulse},  max_pulse: {self.servo_rear_feet_left_max_pulse},rest: {self.servo_rear_feet_left_rest_angle}")

        self.servo_rear_shoulder_right_pca9685 = Config().get(
            Config.MOTION_CONTROLLER_SERVOS_REAR_SHOULDER_RIGHT_PCA9685)
        self.servo_rear_shoulder_right_channel = Config().get(
            Config.MOTION_CONTROLLER_SERVOS_REAR_SHOULDER_RIGHT_CHANNEL)
        self.servo_rear_shoulder_right_min_pulse = Config().get(
            Config.MOTION_CONTROLLER_SERVOS_REAR_SHOULDER_RIGHT_MIN_PULSE)
        self.servo_rear_shoulder_right_max_pulse = Config().get(
            Config.MOTION_CONTROLLER_SERVOS_REAR_SHOULDER_RIGHT_MAX_PULSE)
        self.servo_rear_shoulder_right_rest_angle = Config().get(

            Config.MOTION_CONTROLLER_SERVOS_REAR_SHOULDER_RIGHT_REST_ANGLE)
        print(f"rr_shoulder_servo: {self.servo_rear_shoulder_right_pca9685}, channel: {self.servo_rear_shoulder_right_channel},min_pulse: {self.servo_rear_shoulder_right_min_pulse},  max_pulse: {self.servo_rear_shoulder_right_max_pulse},rest: {self.servo_rear_shoulder_right_rest_angle}")

        self.servo_rear_leg_right_pca9685 = Config().get(
            Config.MOTION_CONTROLLER_SERVOS_REAR_LEG_RIGHT_PCA9685)
        self.servo_rear_leg_right_channel = Config().get(
            Config.MOTION_CONTROLLER_SERVOS_REAR_LEG_RIGHT_CHANNEL)
        self.servo_rear_leg_right_min_pulse = Config().get(
            Config.MOTION_CONTROLLER_SERVOS_REAR_LEG_RIGHT_MIN_PULSE)
        self.servo_rear_leg_right_max_pulse = Config().get(
            Config.MOTION_CONTROLLER_SERVOS_REAR_LEG_RIGHT_MAX_PULSE)
        self.servo_rear_leg_right_rest_angle = Config().get(
            Config.MOTION_CONTROLLER_SERVOS_REAR_LEG_RIGHT_REST_ANGLE)

        print(f"rr_leg_servo: {self.servo_rear_leg_right_pca9685}, channel: {self.servo_rear_leg_right_channel}, min_pulse: {self.servo_rear_leg_right_min_pulse},  max_pulse: {self.servo_rear_leg_right_max_pulse}, rest: {self.servo_rear_leg_right_rest_angle}")

        self.servo_rear_feet_right_pca9685 = Config().get(
            Config.MOTION_CONTROLLER_SERVOS_REAR_FEET_RIGHT_PCA9685)
        self.servo_rear_feet_right_channel = Config().get(
            Config.MOTION_CONTROLLER_SERVOS_REAR_FEET_RIGHT_CHANNEL)
        self.servo_rear_feet_right_min_pulse = Config().get(
            Config.MOTION_CONTROLLER_SERVOS_REAR_FEET_RIGHT_MIN_PULSE)
        self.servo_rear_feet_right_max_pulse = Config().get(
            Config.MOTION_CONTROLLER_SERVOS_REAR_FEET_RIGHT_MAX_PULSE)
        self.servo_rear_feet_right_rest_angle = Config().get(
            Config.MOTION_CONTROLLER_SERVOS_REAR_FEET_RIGHT_REST_ANGLE)

        print(f"rr_feet_servo: {self.servo_rear_feet_right_pca9685}, channel: {self.servo_rear_feet_right_channel},min_pulse: {self.servo_rear_feet_right_min_pulse},  max_pulse: {self.servo_rear_feet_right_max_pulse},rest: {self.servo_rear_feet_right_rest_angle}")

        self.servo_front_shoulder_left_pca9685 = Config().get(
            Config.MOTION_CONTROLLER_SERVOS_FRONT_SHOULDER_LEFT_PCA9685)
        self.servo_front_shoulder_left_channel = Config().get(
            Config.MOTION_CONTROLLER_SERVOS_FRONT_SHOULDER_LEFT_CHANNEL)
        self.servo_front_shoulder_left_min_pulse = Config().get(
            Config.MOTION_CONTROLLER_SERVOS_FRONT_SHOULDER_LEFT_MIN_PULSE)
        self.servo_front_shoulder_left_max_pulse = Config().get(
            Config.MOTION_CONTROLLER_SERVOS_FRONT_SHOULDER_LEFT_MAX_PULSE)
        self.servo_front_shoulder_left_rest_angle = Config().get(
            Config.MOTION_CONTROLLER_SERVOS_FRONT_SHOULDER_LEFT_REST_ANGLE)
        print(f"fl_shoulder_servo: {self.servo_front_shoulder_left_pca9685}, channel: {self.servo_front_shoulder_left_channel}, min_pulse: {self.servo_front_shoulder_left_min_pulse},  max_pulse: {self.servo_front_shoulder_left_max_pulse},rest: {self.servo_front_shoulder_left_rest_angle}")

        self.servo_front_leg_left_pca9685 = Config().get(
            Config.MOTION_CONTROLLER_SERVOS_FRONT_LEG_LEFT_PCA9685)
        self.servo_front_leg_left_channel = Config().get(
            Config.MOTION_CONTROLLER_SERVOS_FRONT_LEG_LEFT_CHANNEL)
        self.servo_front_leg_left_min_pulse = Config().get(
            Config.MOTION_CONTROLLER_SERVOS_FRONT_LEG_LEFT_MIN_PULSE)
        self.servo_front_leg_left_max_pulse = Config().get(
            Config.MOTION_CONTROLLER_SERVOS_FRONT_LEG_LEFT_MAX_PULSE)
        self.servo_front_leg_left_rest_angle = Config().get(
            Config.MOTION_CONTROLLER_SERVOS_FRONT_LEG_LEFT_REST_ANGLE)

        print(f"fl_leg_servo: {self.servo_front_leg_left_pca9685}, channel: {self.servo_front_leg_left_channel}, min_pulse: {self.servo_front_leg_left_min_pulse},  max_pulse: {self.servo_front_leg_left_max_pulse}, rest: {self.servo_front_leg_left_rest_angle}")

        self.servo_front_feet_left_pca9685 = Config().get(
            Config.MOTION_CONTROLLER_SERVOS_FRONT_FEET_LEFT_PCA9685)
        self.servo_front_feet_left_channel = Config().get(
            Config.MOTION_CONTROLLER_SERVOS_FRONT_FEET_LEFT_CHANNEL)
        self.servo_front_feet_left_min_pulse = Config().get(
            Config.MOTION_CONTROLLER_SERVOS_FRONT_FEET_LEFT_MIN_PULSE)
        self.servo_front_feet_left_max_pulse = Config().get(
            Config.MOTION_CONTROLLER_SERVOS_FRONT_FEET_LEFT_MAX_PULSE)
        self.servo_front_feet_left_rest_angle = Config().get(
            Config.MOTION_CONTROLLER_SERVOS_FRONT_FEET_LEFT_REST_ANGLE)
        print(f"fl_feet_servo: {self.servo_front_feet_left_pca9685}, channel: {self.servo_front_feet_left_channel},min_pulse: {self.servo_front_feet_left_min_pulse},  max_pulse: {self.servo_front_feet_left_max_pulse}, rest: {self.servo_front_feet_left_rest_angle}")

        self.servo_front_shoulder_right_pca9685 = Config().get(
            Config.MOTION_CONTROLLER_SERVOS_FRONT_SHOULDER_RIGHT_PCA9685)
        self.servo_front_shoulder_right_channel = Config().get(
            Config.MOTION_CONTROLLER_SERVOS_FRONT_SHOULDER_RIGHT_CHANNEL)
        self.servo_front_shoulder_right_min_pulse = Config().get(
            Config.MOTION_CONTROLLER_SERVOS_FRONT_SHOULDER_RIGHT_MIN_PULSE)
        self.servo_front_shoulder_right_max_pulse = Config().get(
            Config.MOTION_CONTROLLER_SERVOS_FRONT_SHOULDER_RIGHT_MAX_PULSE)
        self.servo_front_shoulder_right_rest_angle = Config().get(
            Config.MOTION_CONTROLLER_SERVOS_FRONT_SHOULDER_RIGHT_REST_ANGLE)

        print(f"fr_shoulder_servo: {self.servo_front_shoulder_right_pca9685}, channel: {self.servo_front_shoulder_right_channel}, min_pulse: {self.servo_front_shoulder_right_min_pulse},  max_pulse: {self.servo_front_shoulder_right_max_pulse}, rest: {self.servo_front_shoulder_right_rest_angle}")

        self.servo_front_leg_right_pca9685 = Config().get(
            Config.MOTION_CONTROLLER_SERVOS_FRONT_LEG_RIGHT_PCA9685)
        self.servo_front_leg_right_channel = Config().get(
            Config.MOTION_CONTROLLER_SERVOS_FRONT_LEG_RIGHT_CHANNEL)
        self.servo_front_leg_right_min_pulse = Config().get(
            Config.MOTION_CONTROLLER_SERVOS_FRONT_LEG_RIGHT_MIN_PULSE)
        self.servo_front_leg_right_max_pulse = Config().get(
            Config.MOTION_CONTROLLER_SERVOS_FRONT_LEG_RIGHT_MAX_PULSE)
        self.servo_front_leg_right_rest_angle = Config().get(
            Config.MOTION_CONTROLLER_SERVOS_FRONT_LEG_RIGHT_REST_ANGLE)
        print(f"fr_leg_servo: {self.servo_front_leg_right_pca9685}, channel: {self.servo_front_leg_right_channel}, min_pulse: {self.servo_front_leg_right_min_pulse},  max_pulse: {self.servo_front_leg_right_max_pulse}, rest: {self.servo_front_leg_right_rest_angle}")

        self.servo_front_feet_right_pca9685 = Config().get(
            Config.MOTION_CONTROLLER_SERVOS_FRONT_FEET_RIGHT_PCA9685)
        self.servo_front_feet_right_channel = Config().get(
            Config.MOTION_CONTROLLER_SERVOS_FRONT_FEET_RIGHT_CHANNEL)
        self.servo_front_feet_right_min_pulse = Config().get(
            Config.MOTION_CONTROLLER_SERVOS_FRONT_FEET_RIGHT_MIN_PULSE)
        self.servo_front_feet_right_max_pulse = Config().get(
            Config.MOTION_CONTROLLER_SERVOS_FRONT_FEET_RIGHT_MAX_PULSE)
        self.servo_front_feet_right_rest_angle = Config().get(
            Config.MOTION_CONTROLLER_SERVOS_FRONT_FEET_RIGHT_REST_ANGLE)

        print(f"fr_feet_servo: {self.servo_front_feet_right_pca9685}, channel: {self.servo_front_feet_right_channel}, min_pulse: {self.servo_front_feet_right_min_pulse},  max_pulse: {self.servo_front_feet_right_max_pulse}, rest: {self.servo_front_feet_right_rest_angle}")

    def activate_servos(self):

        if self.servo_rear_shoulder_left_pca9685 == 1:
            self.servo_rear_shoulder_left = servo.Servo(
                self.pca9685.channels[self.servo_rear_shoulder_left_channel])
        else:
            self.servo_rear_shoulder_left = servo.Servo(
                self.pca9685_2.channels[self.servo_rear_shoulder_left_channel])
        self.servo_rear_shoulder_left.set_pulse_width_range(
            min_pulse=self.servo_rear_shoulder_left_min_pulse, max_pulse=self.servo_rear_shoulder_left_max_pulse)

        if self.servo_rear_leg_left_pca9685 == 1:
            self.servo_rear_leg_left = servo.Servo(
                self.pca9685.channels[self.servo_rear_leg_left_channel])
        else:
            self.servo_rear_leg_left = servo.Servo(
                self.pca9685_2.channels[self.servo_rear_leg_left_channel])
        self.servo_rear_leg_left.set_pulse_width_range(
            min_pulse=self.servo_rear_leg_left_min_pulse, max_pulse=self.servo_rear_leg_left_max_pulse)

        if self.servo_rear_feet_left_pca9685 == 1:
            self.servo_rear_feet_left = servo.Servo(
                self.pca9685.channels[self.servo_rear_feet_left_channel])
        else:
            self.servo_rear_feet_left = servo.Servo(
                self.pca9685_2.channels[self.servo_rear_feet_left_channel])
        self.servo_rear_feet_left.set_pulse_width_range(
            min_pulse=self.servo_rear_feet_left_min_pulse, max_pulse=self.servo_rear_feet_left_max_pulse)

        if self.servo_rear_shoulder_right_pca9685 == 1:
            self.servo_rear_shoulder_right = servo.Servo(
                self.pca9685.channels[self.servo_rear_shoulder_right_channel])
        else:
            self.servo_rear_shoulder_right = servo.Servo(
                self.pca9685_2.channels[self.servo_rear_shoulder_right_channel])
        self.servo_rear_shoulder_right.set_pulse_width_range(
            min_pulse=self.servo_rear_shoulder_right_min_pulse, max_pulse=self.servo_rear_shoulder_right_max_pulse)

        if self.servo_rear_leg_right_pca9685 == 1:
            self.servo_rear_leg_right = servo.Servo(
                self.pca9685.channels[self.servo_rear_leg_right_channel])
        else:
            self.servo_rear_leg_right = servo.Servo(
                self.pca9685_2.channels[self.servo_rear_leg_right_channel])
        self.servo_rear_leg_right.set_pulse_width_range(
            min_pulse=self.servo_rear_leg_right_min_pulse, max_pulse=self.servo_rear_leg_right_max_pulse)

        if self.servo_rear_feet_right_pca9685 == 1:
            self.servo_rear_feet_right = servo.Servo(
                self.pca9685.channels[self.servo_rear_feet_right_channel])
        else:
            self.servo_rear_feet_right = servo.Servo(
                self.pca9685_2.channels[self.servo_rear_feet_right_channel])
        self.servo_rear_feet_right.set_pulse_width_range(
            min_pulse=self.servo_rear_feet_right_min_pulse, max_pulse=self.servo_rear_feet_right_max_pulse)

        if self.servo_front_shoulder_left_pca9685 == 1:
            self.servo_front_shoulder_left = servo.Servo(
                self.pca9685.channels[self.servo_front_shoulder_left_channel])
        else:
            self.servo_front_shoulder_left = servo.Servo(
                self.pca9685_2.channels[self.servo_front_shoulder_left_channel])
        self.servo_front_shoulder_left.set_pulse_width_range(
            min_pulse=self.servo_front_shoulder_left_min_pulse, max_pulse=self.servo_front_shoulder_left_max_pulse)

        if self.servo_front_leg_left_pca9685 == 1:
            self.servo_front_leg_left = servo.Servo(
                self.pca9685.channels[self.servo_front_leg_left_channel])
        else:
            self.servo_front_leg_left = servo.Servo(
                self.pca9685_2.channels[self.servo_front_leg_left_channel])
        self.servo_front_leg_left.set_pulse_width_range(
            min_pulse=self.servo_front_leg_left_min_pulse, max_pulse=self.servo_front_leg_left_max_pulse)

        if self.servo_front_feet_left_pca9685 == 1:
            self.servo_front_feet_left = servo.Servo(
                self.pca9685.channels[self.servo_front_feet_left_channel])
        else:
            self.servo_front_feet_left = servo.Servo(
                self.pca9685_2.channels[self.servo_front_feet_left_channel])
        self.servo_front_feet_left.set_pulse_width_range(
            min_pulse=self.servo_front_feet_left_min_pulse, max_pulse=self.servo_front_feet_left_max_pulse)

        if self.servo_front_shoulder_right_pca9685 == 1:
            self.servo_front_shoulder_right = servo.Servo(
                self.pca9685.channels[self.servo_front_shoulder_right_channel])
        else:
            self.servo_front_shoulder_right = servo.Servo(
                self.pca9685_2.channels[self.servo_front_shoulder_right_channel])
        self.servo_front_shoulder_right.set_pulse_width_range(
            min_pulse=self.servo_front_shoulder_right_min_pulse, max_pulse=self.servo_front_shoulder_right_max_pulse)

        if self.servo_front_leg_right_pca9685 == 1:
            self.servo_front_leg_right = servo.Servo(
                self.pca9685.channels[self.servo_front_leg_right_channel])
        else:
            self.servo_front_leg_right = servo.Servo(
                self.pca9685_2.channels[self.servo_front_leg_right_channel])
        self.servo_front_leg_right.set_pulse_width_range(
            min_pulse=self.servo_front_leg_right_min_pulse, max_pulse=self.servo_front_leg_right_max_pulse)

        if self.servo_front_feet_right_pca9685 == 1:
            self.servo_front_feet_right = servo.Servo(
                self.pca9685.channels[self.servo_front_feet_right_channel])
        else:
            self.servo_front_feet_right = servo.Servo(
                self.pca9685_2.channels[self.servo_front_feet_right_channel])
        self.servo_front_feet_right.set_pulse_width_range(
            min_pulse=self.servo_front_feet_right_min_pulse, max_pulse=self.servo_front_feet_right_max_pulse)

    def move(self):

        try:
            self.servo_rear_shoulder_left.angle = self.servo_rear_shoulder_left_rest_angle
        except ValueError as e:
            log.error('Impossible servo_rear_shoulder_left angle requested')

        try:
            self.servo_rear_leg_left.angle = self.servo_rear_leg_left_rest_angle
        except ValueError as e:
            log.error('Impossible servo_rear_leg_left angle requested')

        try:
            self.servo_rear_feet_left.angle = self.servo_rear_feet_left_rest_angle
        except ValueError as e:
            log.error('Impossible servo_rear_feet_left angle requested')

        try:
            self.servo_rear_shoulder_right.angle = self.servo_rear_shoulder_right_rest_angle
        except ValueError as e:
            log.error('Impossible servo_rear_shoulder_right angle requested')

        try:
            self.servo_rear_leg_right.angle = self.servo_rear_leg_right_rest_angle
        except ValueError as e:
            log.error('Impossible servo_rear_leg_right angle requested')

        try:
            self.servo_rear_feet_right.angle = self.servo_rear_feet_right_rest_angle
        except ValueError as e:
            log.error('Impossible servo_rear_feet_right angle requested')

        try:
            self.servo_front_shoulder_left.angle = self.servo_front_shoulder_left_rest_angle
        except ValueError as e:
            log.error('Impossible servo_front_shoulder_left angle requested')

        try:
            self.servo_front_leg_left.angle = self.servo_front_leg_left_rest_angle
        except ValueError as e:
            log.error('Impossible servo_front_leg_left angle requested')

        try:
            self.servo_front_feet_left.angle = self.servo_front_feet_left_rest_angle
        except ValueError as e:
            log.error('Impossible servo_front_feet_left angle requested')

        try:
            self.servo_front_shoulder_right.angle = self.servo_front_shoulder_right_rest_angle
        except ValueError as e:
            log.error('Impossible servo_front_shoulder_right angle requested')

        try:
            self.servo_front_leg_right.angle = self.servo_front_leg_right_rest_angle
        except ValueError as e:
            log.error('Impossible servo_front_leg_right angle requested')

        try:
            self.servo_front_feet_right.angle = self.servo_front_feet_right_rest_angle
        except ValueError as e:
            log.error('Impossible servo_front_feet_right angle requested')

    def rest_position(self):

        self.servo_rear_shoulder_left_rest_angle = Config().get(
            Config.MOTION_CONTROLLER_SERVOS_REAR_SHOULDER_LEFT_REST_ANGLE)
        self.servo_rear_leg_left_rest_angle = Config().get(
            Config.MOTION_CONTROLLER_SERVOS_REAR_LEG_LEFT_REST_ANGLE)
        self.servo_rear_feet_left_rest_angle = Config().get(
            Config.MOTION_CONTROLLER_SERVOS_REAR_FEET_LEFT_REST_ANGLE)
        self.servo_rear_shoulder_right_rest_angle = Config().get(
            Config.MOTION_CONTROLLER_SERVOS_REAR_SHOULDER_RIGHT_REST_ANGLE)
        self.servo_rear_leg_right_rest_angle = Config().get(
            Config.MOTION_CONTROLLER_SERVOS_REAR_LEG_RIGHT_REST_ANGLE)
        self.servo_rear_feet_right_rest_angle = Config().get(
            Config.MOTION_CONTROLLER_SERVOS_REAR_FEET_RIGHT_REST_ANGLE)
        self.servo_front_shoulder_left_rest_angle = Config().get(
            Config.MOTION_CONTROLLER_SERVOS_FRONT_SHOULDER_LEFT_REST_ANGLE)
        self.servo_front_leg_left_rest_angle = Config().get(
            Config.MOTION_CONTROLLER_SERVOS_FRONT_LEG_LEFT_REST_ANGLE)
        self.servo_front_feet_left_rest_angle = Config().get(
            Config.MOTION_CONTROLLER_SERVOS_FRONT_FEET_LEFT_REST_ANGLE)
        self.servo_front_shoulder_right_rest_angle = Config().get(
            Config.MOTION_CONTROLLER_SERVOS_FRONT_SHOULDER_RIGHT_REST_ANGLE)
        self.servo_front_leg_right_rest_angle = Config().get(
            Config.MOTION_CONTROLLER_SERVOS_FRONT_LEG_RIGHT_REST_ANGLE)
        self.servo_front_feet_right_rest_angle = Config().get(
            Config.MOTION_CONTROLLER_SERVOS_FRONT_FEET_RIGHT_REST_ANGLE)

    def standing_position(self):

        variation_leg = 50
        variation_feet = 70

        self.servo_rear_shoulder_left.angle = self.servo_rear_shoulder_left_rest_angle + 10
        self.servo_rear_leg_left.angle = self.servo_rear_leg_left_rest_angle - variation_leg
        self.servo_rear_feet_left.angle = self.servo_rear_feet_left_rest_angle + variation_feet

        self.servo_rear_shoulder_right.angle = self.servo_rear_shoulder_right_rest_angle - 10
        self.servo_rear_leg_right.angle = self.servo_rear_leg_right_rest_angle + variation_leg
        self.servo_rear_feet_right.angle = self.servo_rear_feet_right_rest_angle - variation_feet

        time.sleep(0.05)

        self.servo_front_shoulder_left.angle = self.servo_front_shoulder_left_rest_angle - 10
        self.servo_front_leg_left.angle = self.servo_front_leg_left_rest_angle - variation_leg + 5
        self.servo_front_feet_left.angle = self.servo_front_feet_left_rest_angle + \
            variation_feet - 5

        self.servo_front_shoulder_right.angle = self.servo_front_shoulder_right_rest_angle + 10
        self.servo_front_leg_right.angle = self.servo_front_leg_right_rest_angle + variation_leg - 5
        self.servo_front_feet_right.angle = self.servo_front_feet_right_rest_angle - \
            variation_feet + 5

        time.sleep(0.05)

    def body_move_position_right(self):

        move = 20

        variation_leg = 50
        variation_feet = 70

        self.servo_rear_shoulder_left.angle = self.servo_rear_shoulder_left_rest_angle + 10 + move
        self.servo_rear_leg_left.angle = self.servo_rear_leg_left_rest_angle - variation_leg
        self.servo_rear_feet_left.angle = self.servo_rear_feet_left_rest_angle + variation_feet

        self.servo_rear_shoulder_right.angle = self.servo_rear_shoulder_right_rest_angle - 10 + move
        self.servo_rear_leg_right.angle = self.servo_rear_leg_right_rest_angle + variation_leg
        self.servo_rear_feet_right.angle = self.servo_rear_feet_right_rest_angle - variation_feet

        time.sleep(0.05)

        self.servo_front_shoulder_left.angle = self.servo_front_shoulder_left_rest_angle - 10 - move
        self.servo_front_leg_left.angle = self.servo_front_leg_left_rest_angle - variation_leg + 5
        self.servo_front_feet_left.angle = self.servo_front_feet_left_rest_angle + \
            variation_feet - 5

        self.servo_front_shoulder_right.angle = self.servo_front_shoulder_right_rest_angle + 10 - move
        self.servo_front_leg_right.angle = self.servo_front_leg_right_rest_angle + variation_leg - 5
        self.servo_front_feet_right.angle = self.servo_front_feet_right_rest_angle - \
            variation_feet + 5

    def move_leg(self, leg, theta0, theta1, theta2):
        if leg == "FrontLeft":
            self.servo_front_shoulder_left.angle = theta0
            self.servo_front_leg_left.angle = theta1
            self.servo_front_feet_left.angle = theta2
        elif leg == "FrontRight":
            self.servo_front_shoulder_right.angle = theta0
            self.servo_front_leg_right.angle = theta1
            self.servo_front_feet_right.angle = theta2
        elif leg == "RearLeft":
            self.servo_rear_shoulder_left.angle = theta0
            self.servo_rear_leg_left.angle = theta1
            self.servo_rear_feet_left.angle = theta2
        elif leg == "RearRight":
            self.servo_rear_shoulder_right.angle = theta0
            self.servo_rear_leg_right.angle = theta1
            self.servo_rear_feet_right.angle = theta2
