import busio
from board import SCL, SDA
from adafruit_pca9685 import PCA9685
from adafruit_motor import servo
from adafruit_servokit import ServoKit
import time

from spotmicroai.utilities.general import General

i2c = busio.I2C(SCL, SDA)


class SpotMicro:
    def __init__(self):
        self.pca_2 = PCA9685(i2c, address=0x40, reference_clock_speed=25000000)
        self.pca_2.frequency = 50
        # shoulder
        # lr
        self.lrShoulder = servo.Servo(self.pca_2.channels[6])

        self.lrShoulder.set_pulse_width_range(500, 2500)
        # rr
        self.rrShoulder = servo.Servo(self.pca_2.channels[9])
        self.rrShoulder.set_pulse_width_range(500, 2500)
        # lf

        # leg
        # lr
        self.lrLeg = servo.Servo(self.pca_2.channels[7])
        self.lrLeg.set_pulse_width_range(500, 2500)
        # rr
        self.rrLeg = servo.Servo(self.pca_2.channels[10])
        self.rrLeg.set_pulse_width_range(500, 2500)
        # feet
        # lr
        self.lrFeet = servo.Servo(self.pca_2.channels[8])
        self.lrFeet.set_pulse_width_range(500, 2500)
        # rr
        self.rrFeet = servo.Servo(self.pca_2.channels[11])
        self.rrFeet.set_pulse_width_range(500, 2500)

        self.lfShoulder = servo.Servo(self.pca_2.channels[0])
        self.lfShoulder.set_pulse_width_range(500, 2500)
        # rf
        self.rfShoulder = servo.Servo(self.pca_2.channels[3])
        self.rfShoulder.set_pulse_width_range(500, 2500)
        # lf
        self.lfLeg = servo.Servo(self.pca_2.channels[1])
        self.lfLeg.set_pulse_width_range(500, 2500)
        # rf
        self.rfLeg = servo.Servo(self.pca_2.channels[4])
        self.rfLeg.set_pulse_width_range(500, 2500)
        # lf
        self.lfFeet = servo.Servo(self.pca_2.channels[2])
        self.lfFeet.set_pulse_width_range(500, 2500)
        # rf
        self.rfFeet = servo.Servo(self.pca_2.channels[5])
        self.rfFeet.set_pulse_width_range(500, 2500)


spot = SpotMicro()


def standing():
    variation_leg = 50
    variation_feet = 70
    time.sleep(1)

    spot.lrShoulder.angle = 85
    spot.lrLeg.angle = 90 - variation_leg - 10
    spot.lrFeet.angle = 0 + variation_feet

    spot.rrShoulder.angle = 95
    spot.rrLeg.angle = 90 + variation_leg + 10
    spot.rrFeet.angle = 180 - variation_feet

    time.sleep(0.05)

    spot.lfShoulder.angle = 90
    spot.lfLeg.angle = 90 - variation_leg - 10
    spot.lfFeet.angle = 0 + variation_feet

    spot.rfShoulder.angle = 90
    spot.rfLeg.angle = 90 + variation_leg + 10
    spot.rfFeet.angle = 180 - variation_feet + 5


def rest():

    spot.lrShoulder.angle = 90
    spot.lrLeg.angle = 90
    spot.lrFeet.angle = 0

    spot.rrShoulder.angle = 90
    spot.rrLeg.angle = 90
    spot.rrFeet.angle = 180

    time.sleep(0.05)

    spot.lfShoulder.angle = 90
    spot.lfLeg.angle = 90
    spot.lfFeet.angle = 0

    spot.rfShoulder.angle = 90
    spot.rfLeg.angle = 90
    spot.rfFeet.angle = 180


def body_move_body_left_right(raw_value):
    range = 5

    if raw_value < 0:
        spot.lrShoulder -= range
        spot.rrShoulder -= range
        spot.lfShoulder += range
        spot.rfShoulder += range

    elif raw_value > 0:
        spot.lrShoulder += range
        spot.rrShoulder += range
        spot.lfShoulder -= range
        spot.rfShoulder -= range

    else:
        rest()


def body_move_body_left_right_analog(raw_value):

    delta_a = int(General().maprange((-1, 1), (30, 150), raw_value))
    delta_b = int(General().maprange((-1, 1), (150, 30), raw_value))

    spot.lrShoulder = delta_a
    spot.rrShoulder = delta_a
    spot.lfShoulder = delta_b
    spot.rfShoulder = delta_b


body_move_body_left_right_analog(10)
rest()
