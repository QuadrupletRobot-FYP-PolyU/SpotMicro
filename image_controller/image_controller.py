import spotmicroai.utilities.queues as queues
class ImageController:
    def __init__(self, communication_queues):
        self._abort_queue = communication_queues[queues.ABORT_CONTROLLER]
        self._network_queue = communication_queues[queues.NETWORK_CONTROLLER]
        self._image_queue = communication_queues[queues.IMAGE_CONTROLLER]
        self._lcd_screen_queue = communication_queues[queues.LCD_SCREEN_CONTROLLER]