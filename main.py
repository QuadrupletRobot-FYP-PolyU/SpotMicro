from spot.spot import Spot
import argparse


parser = argparse.ArgumentParser()
parser.add_argument("-m", "--mode", type=int, default=1,
                    required=True, help="Go into debug mode (1) or production mode (0)")


args = parser.parse_args()


def debug_mode():
    while True:
        uInput = int(input("enter a number between 0-11, enter -1 to exit"))

        if uInput <= 11 and uInput >= 0:
            print("ready for calibration")
            angleInput = int(input("enter in an angle"))
            if angleInput >= 0 and angleInput <= 180:
                spot.calibrate_angle(spot.servoDictionary[uInput], angleInput)
            else:
                print("the angle chosen is not correct")
        elif uInput == -1:
            return
        elif uInput > 11 or uInput < 0:
            print("invalid number choice")


if __name__ == "__main__":
    spot = Spot()
    if args.mode == 1:
        debug_mode()
    elif args.mode == 0:
        while True:
            uInput = int(
                input("Press 1 for rest, 2 for standing, 3 for walking, -1"))
            if uInput == 1:
                spot.rest()
            elif uInput == 2:
                spot.standing()
    else:
        print("Theres been an error")
