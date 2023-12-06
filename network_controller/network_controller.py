#import utilities.queues as queues
import paho.mqtt.publish as publish
import paho.mqtt.client as mqtt
import yaml
class NetworkController:
    def __init__(self,communication_queues):
        with open("./../config.yml", "r") as yamlfile:
            self.cfg = yaml.safe_load(yamlfile)

        #if self.cfg['development'].dev_status == False:
            #self._abort_queue = communication_queues[queues.ABORT_CONTROLLER]
            #self._network_queue = communication_queues[queues.NETWORK_CONTROLLER]
            #self._image_queue = communication_queues[queues.IMAGE_CONTROLLER]
            #self._lcd_screen_queue = communication_queues[queues.LCD_SCREEN_CONTROLLER]
        self.client = mqtt.Client()
        self.do_process_events_from_queues()

    def do_process_events_from_queues(self):

        def on_connect(client, userdata, flags, rc):
            if rc == 0:
                print("Connected to MQTT Broker!")
            else:
                print("Failed to connect, return code %d\n", rc)

            # Subscribing to multiple topics
            client.subscribe("topic/movement")

        def on_message(client, userdata, message):
            print(f"Message received: {message.payload.decode()}")
            if message.topic == "topic/movement":
                print("Handling message from first topic")
                try:
                    states = message.states
                    self._motion_queue.put(states)
                except Exception:
                    print("There seems to be an error")
                # Handle the message for the first topic

        self.client.on_connect = on_connect
        self.client.on_message = on_message

        self.client.connect(self.cfg['network']['host'], self.cfg['network']['port'], 60)
        self.client.loop_forever()





NetworkController('')