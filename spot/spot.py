import busio
from board import SCL, SDA
from adafruit_pca9685 import PCA9685
from adafruit_motor import servo
from adafruit_servokit import ServoKit
import time

from spotmicroai.utilities.general import General

i2c = busio.I2C(SCL, SDA)


class Spot:

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

        self.servoDictionary = {0: self.lrShoulder, 1: self.lrLeg, 2: self.lrFeet, 3: self.rrShoulder, 4: self.rrLeg,
                                5: self.rrFeet, 6: self.rfShoulder, 7: self.rfLeg, 8: self.rfFeet, 9: self.lfShoulder, 10: self.lfLeg, 11: self.lfFeet}

    def standing(self):
        variation_leg = 50
        variation_feet = 70
        time.sleep(1)

        self.lrShoulder.angle = 85
        self.lrLeg.angle = 90 - variation_leg - 10
        self.lrFeet.angle = 0 + variation_feet

        self.rrShoulder.angle = 95
        self.rrLeg.angle = 90 + variation_leg + 10
        self.rrFeet.angle = 180 - variation_feet

        time.sleep(0.05)

        self.lfShoulder.angle = 90
        self.lfLeg.angle = 90 - variation_leg - 10
        self.lfFeet.angle = 0 + variation_feet

        self.rfShoulder.angle = 90
        self.rfLeg.angle = 90 + variation_leg + 10
        self.rfFeet.angle = 180 - variation_feet + 5

    def rest(self):

        self.lrShoulder.angle = 90
        self.lrLeg.angle = 90
        self.lrFeet.angle = 0

        self.rrShoulder.angle = 90
        self.rrLeg.angle = 90
        self.rrFeet.angle = 180

        time.sleep(0.05)

        self.lfShoulder.angle = 90
        self.lfLeg.angle = 90
        self.lfFeet.angle = 0

        self.rfShoulder.angle = 90
        self.rfLeg.angle = 90
        self.rfFeet.angle = 180

    def calibrate_angle(self, servo, angle):
        servo.angle = angle
        print(f"calibrated to angle {angle}")

    def body_move_body_left_right(self, raw_value):
        range = 5

        if raw_value < 0:
            self.lrShoulder -= range
            self.rrShoulder -= range
            self.lfShoulder += range
            self.rfShoulder += range

        elif raw_value > 0:
            self.lrShoulder += range
            self.rrShoulder += range
            self.lfShoulder -= range
            self.rfShoulder -= range

        else:
            self.rest()

    def body_move_body_left_right_analog(self, raw_value):

        delta_a = int(General().maprange((-1, 1), (30, 150), raw_value))
        delta_b = int(General().maprange((-1, 1), (150, 30), raw_value))

        self.lrShoulder = delta_a
        self.rrShoulder = delta_a
        self.lfShoulder = delta_b
        self.rfShoulder = delta_b
