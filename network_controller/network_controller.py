import spotmicroai.utilities.queues as queues
import paho.mqtt.publish as publish
import paho.mqtt.client as mqtt

#PUBLIC INFORMATION, CHANGE IF CONFIDENTIAL
#HOST NAME === broker.emqx.io
#PORT === 1883
class NetworkController:
    def __init__(self,communication_queues):
        self._abort_queue = communication_queues[queues.ABORT_CONTROLLER]
        self._network_queue = communication_queues[queues.NETWORK_CONTROLLER]
        self._image_queue = communication_queues[queues.IMAGE_CONTROLLER]
        self._lcd_screen_queue = communication_queues[queues.LCD_SCREEN_CONTROLLER]

    def do_process_events_from_queues(self):