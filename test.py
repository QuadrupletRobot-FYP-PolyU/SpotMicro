import busio
from board import SCL, SDA
from adafruit_pca9685 import PCA9685
from adafruit_motor import servo
from adafruit_servokit import ServoKit
import time

i2c = busio.I2C(SCL, SDA)
pca_1 = PCA9685(i2c, address=0x40,reference_clock_speed=25000000)
pca_1.frequency = 50
pca_2 = PCA9685(i2c, address=0x60,reference_clock_speed=25000000)
pca_2.frequency = 50
#shoulder
#lr
lrShoulder = servo.Servo(pca_1.channels[0])
lrShoulder.set_pulse_width_range(500,2500)

while True:
    ui = input("enter angle")
    lrShoulder.angle = int(ui)