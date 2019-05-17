import Queue as queue
import time
import logging


FORMAT = '%(asctime)-15s %(message)s'
logging.basicConfig(format=FORMAT)
logger = logging.getLogger()
logger.setLevel(logging.DEBUG)


class BroadcastMessage(object):
    def __init__(self, source, destination, prop, value):
        self.source = source
        self.destination = destination
        self.prop = prop
        self.value = value
        self.key = "%s:%s" % (prop, source)
        self.ts = time.time()


    def __str__(self):
        return "Broadcast from %s to %s, %s = %s" % (self.source, self.destination, self.prop, self.value)

        

class SenderReceiver(object):
    def __init__(self, name):
        self.name = name
        self.broadcast_messages = queue.Queue()


    def found_devices(self, devices):
        pass


    def broadcast_received(self, broadcast):
        pass


    # Happens periodically regardless of having broadcasts or not.
    def tick(self):
        pass


    def add_broadcast(self, destination, prop, value):
        self.broadcast_messages.put(BroadcastMessage(self.name, destination, prop, value))


    def all_broadcasters(self):
        return [self]


    def set_coordinator(self, coordinator):
        self.coordinator = coordinator


class SerialBuffer:
    def __init__(self, separator = "\n"):
        self.separator = separator
        self.past_data = ""


    def received(self, data):
        self.past_data += data


    def pending_data(self):
        lines = self.past_data.split(self.separator)
        self.past_data = lines[-1]
        return lines[0:-1]
