import busio
from board import SCL, SDA
from adafruit_pca9685 import PCA9685
from adafruit_motor import servo
from adafruit_servokit import ServoKit
import time

i2c = busio.I2C(SCL, SDA)

pca_2 = PCA9685(i2c, address=0x40,reference_clock_speed=25000000)
pca_2.frequency = 50
#shoulder
#lr
lrShoulder = servo.Servo(pca_2.channels[6])

lrShoulder.set_pulse_width_range(500,2500)
#rr
rrShoulder = servo.Servo(pca_2.channels[9])
rrShoulder.set_pulse_width_range(500,2500)
#lf

#leg
#lr
lrLeg = servo.Servo(pca_2.channels[7])
lrLeg.set_pulse_width_range(500,2500)
#rr
rrLeg = servo.Servo(pca_2.channels[10])
rrLeg.set_pulse_width_range(500,2500)
#feet
#lr
lrFeet = servo.Servo(pca_2.channels[8])
lrFeet.set_pulse_width_range(500,2500)
#rr
rrFeet = servo.Servo(pca_2.channels[11])
rrFeet.set_pulse_width_range(500,2500)



lfShoulder = servo.Servo(pca_2.channels[0])
lfShoulder.set_pulse_width_range(500,2500)
#rf
rfShoulder= servo.Servo(pca_2.channels[3])
rfShoulder.set_pulse_width_range(500,2500)
#lf
lfLeg = servo.Servo(pca_2.channels[1])
lfLeg.set_pulse_width_range(500,2500)
#rf
rfLeg= servo.Servo(pca_2.channels[4])
rfLeg.set_pulse_width_range(500,2500)
#lf
lfFeet = servo.Servo(pca_2.channels[2])
lfFeet.set_pulse_width_range(500,2500)
#rf
rfFeet= servo.Servo(pca_2.channels[5])
rfFeet.set_pulse_width_range(500,2500)

def standing():
    variation_leg = 50
    variation_feet = 70
    time.sleep(1)

    lrShoulder.angle = 85
    lrLeg.angle = 90 - variation_leg - 10
    lrFeet.angle = 0 + variation_feet

    rrShoulder.angle = 95
    rrLeg.angle = 90 + variation_leg + 10
    rrFeet.angle = 180 - variation_feet

    time.sleep(0.05)

    lfShoulder.angle = 90
    lfLeg.angle = 90 - variation_leg  -10
    lfFeet.angle = 0 + variation_feet  

    rfShoulder.angle = 90
    rfLeg.angle = 90 + variation_leg + 10
    rfFeet.angle = 180 - variation_feet + 5

def rest():

    lrShoulder.angle = 90 
    lrLeg.angle = 90
    lrFeet.angle = 0

    rrShoulder.angle = 90
    rrLeg.angle = 90
    rrFeet.angle = 180

    time.sleep(0.05)

    lfShoulder.angle = 90
    lfLeg.angle = 90
    lfFeet.angle = 0 

    rfShoulder.angle = 90 
    rfLeg.angle = 90
    rfFeet.angle = 180



rest()
