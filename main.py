import sys
import multiprocessing

from motion_controller.motion_controller import MotionController
from controller_server.server_controller import ServerController
from abort_controller.abort_controller import AbortController
from camera_controller.camera_controller import CameraController
from video_server.server_video import ServerVideo
from utilities.log import Logger


def process_abort_controller(communication_queues):
    abort = AbortController(communication_queues)
    abort.do_process_events_from_queue()


def process_video_controller(communication_queues):
    video = ServerVideo(communication_queues)
    video.do_process_events_from_queues()


def process_motion_controller(communication_queues):
    motion = MotionController(communication_queues)
    motion.do_process_events_from_queues()

def process_camera_controller(communication_queues):
    motion = CameraController(communication_queues)
    motion.do_process_events_from_queues()


def process_remote_controller_controller(communication_queues):
    remote_controller = ServerController(communication_queues)
    remote_controller.do_process_events_from_queues()


log = Logger().setup_logger()


def create_controllers_queues():
    communication_queues = {'video_controller': multiprocessing.Queue(1),
                            'abort_controller': multiprocessing.Queue(10),
                            'motion_controller': multiprocessing.Queue(10),
                            'remote_controller': multiprocessing.Queue(10),
                            'lcd_screen_controller': multiprocessing.Queue(10)}

    log.info('Created the communication queues: ' +
             ', '.join(communication_queues.keys()))

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
    abort_controller = multiprocessing.Process(
        target=process_abort_controller, args=(communication_queues,))
    abort_controller.daemon = True  # The daemon dies if the parent process dies

    # Start the motion controller
    # Moves the servos
    motion_controller = multiprocessing.Process(
        target=process_motion_controller, args=(communication_queues,))
    motion_controller.daemon = True

    # Activate Bluetooth controller
    # Let you move the dog using the bluetooth paired device
    remote_controller_controller = multiprocessing.Process(target=process_remote_controller_controller,
                                                           args=(communication_queues,))
    remote_controller_controller.daemon = True

    video_controller = multiprocessing.Process(target=process_video_controller,
                                               args=(communication_queues,))
    video_controller.daemon = True

    camera_controller = multiprocessing.Process(target=process_camera_controller,
                                               args=(communication_queues,))
    camera_controller.daemon = True
    # Start the threads, queues messages are produced and consumed in those
    abort_controller.start()
    motion_controller.start()
    remote_controller_controller.start()
    video_controller.start()
    camera_controller.start()

    if not abort_controller.is_alive():
        log.error("SpotMicro can't work without abort_controller")
        sys.exit(1)

    if not motion_controller.is_alive():
        log.error("SpotMicro can't work without motion_controller")
        sys.exit(1)

    if not remote_controller_controller:
        log.error("SpotMicro can't work without remote_controller_controller")
        sys.exit(1)

    if not video_controller:
        log.error("SpotMicro can't work without video_controller")
        sys.exit(1)
    # Make sure the thread/process ends
    abort_controller.join()
    motion_controller.join()
    remote_controller_controller.join()
    video_controller.join()
    camera_controller.join()

    close_controllers_queues(communication_queues)


if __name__ == '__main__':
    log.info('SpotMicro starting...')

    try:
        main()

    except KeyboardInterrupt:
        log.info('Terminated due Control+C was pressed')

    else:
        log.info('Normal termination')
