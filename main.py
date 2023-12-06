#!/usr/bin/env python3

import sys
from utilities.log import Logger
import multiprocessing
from motion_controller.motion_controller import MotionController
from abort_controller.abort_controller import AbortController
from lcd_screen_controller.lcd_screen_controller import LCDScreenController
from remote_controller.remote_controller import RemoteControllerController
from image_controller.image_controller import ImageController
from network_controller.network_controller import NetworkController

log = Logger().setup_logger()

def process_abort_controller(communication_queues):
    abort = AbortController(communication_queues)
    abort.do_process_events_from_queue()

def process_motion_controller(communication_queues):
    motion = MotionController(communication_queues)
    motion.do_process_events_from_queues()

def process_network_controller(communication_queues):
    network = NetworkController(communication_queues)
    network.do_process_events_from_queues()

def process_image_controller(communication_queues):
    image = ImageController(communication_queues)
    image.do_process_events_from_queues()

def create_controllers_queues():
    communication_queues = {'abort_controller': multiprocessing.Queue(10),
                            'network_controller': multiprocessing.Queue(1),
                            'image_controller': multiprocessing.Queue(1),
                            'lcd_screen_controller': multiprocessing.Queue(10)}

    log.info('Created the communication queues: ' + ', '.join(communication_queues.keys()))

    return communication_queues


def close_controllers_queues(communication_queues):
    log.info('Closing controller queues')

    for queue in communication_queues.items():
        queue.close()
        queue.join_thread()


def main():
    communication_queues = create_controllers_queues()

    # Abort controller
    # Controls the 0E port from PCA9685 to cut the power to the servos conveniently if needed.
    abort_controller = multiprocessing.Process(target=process_abort_controller, args=(communication_queues,))
    abort_controller.daemon = True  # The daemon dies if the parent process dies

    # Start the motion controller
    # Moves the servos
    motion_controller = multiprocessing.Process(target=process_motion_controller, args=(communication_queues,))
    motion_controller.daemon = True

    #Start the network controller
    #In charge of communication with MQTT server and Computer
    network_controller =multiprocessing.Process(target=process_network_controller, args=(communication_queues,))
    network_controller.daemon = True

    image_controller = multiprocessing.Process(target=process_image_controller, args=(communication_queues,))
    image_controller.daemon = True
    # Start the threads, queues messages are produced and consumed in those
    abort_controller.start()
    motion_controller.start()
    network_controller.start()
    image_controller.start()

    if not abort_controller.is_alive():
        log.error("SpotMicro can't work without abort_controller")
        sys.exit(1)

    if not motion_controller.is_alive():
        log.error("SpotMicro can't work without motion_controller")
        sys.exit(1)

    # Make sure the thread/process ends
    abort_controller.join()
    motion_controller.join()
    network_controller.join()
    image_controller.join()

    close_controllers_queues(communication_queues)


if __name__ == '__main__':
    log.info('SpotMicro starting...')

    try:
        main()

    except KeyboardInterrupt:
        log.info('Terminated due Control+C was pressed')

    else:
        log.info('Normal termination')
