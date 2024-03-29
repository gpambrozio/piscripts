import datetime

from base import SenderReceiver, logger


class LogicManager(SenderReceiver):
    def __init__(self):
        SenderReceiver.__init__(self, 'Logic')
        self.current_state = {}
        self.properties = {
            'Moving': False,
            'Parked': True,
        }
        for (name, value) in self.properties.iteritems():
            self.add_broadcast(None, name, value)
        self.stopped_time = None
        self.moving_time = None
        self.devices = []


    def set_property(self, name, value):
        if name not in self.properties or self.properties[name] != value:
            self.properties[name] = value
            self.add_broadcast(None, name, value)


    def broadcast_received(self, broadcast):
        if broadcast.destination is None:
            self.current_state[broadcast.prop]= broadcast.value

        if broadcast.prop == 'Speed' and broadcast.value > 40:
            self.stopped_time = None
            if self.moving_time is None:
                self.moving_time = datetime.datetime.now()

        elif broadcast.prop == 'Speed' and broadcast.value < 5:
            self.moving_time = None
            if self.stopped_time is None:
                self.stopped_time = datetime.datetime.now()

        elif broadcast.prop == 'Devices':
            self.check_new_devices(broadcast.value)
            self.devices = broadcast.value


    def tick(self):
        if not self.properties['Parked'] and self.stopped_time is not None:
            elapsed = (datetime.datetime.now() - self.stopped_time).seconds
            if elapsed > 3 * 60:
                self.set_property('Moving', False)
                self.set_property('Parked', True)
                self.stopped_time = None

        elif not self.properties['Moving'] and self.moving_time is not None:
            elapsed = (datetime.datetime.now() - self.moving_time).seconds
            if elapsed > 60:
                self.set_property('Parked', False)
                self.set_property('Moving', True)
                self.moving_time = None


    def check_new_devices(self, new_devices):
        added = set(new_devices) - set(self.devices)
        removed = set(self.devices) - set(new_devices)
        # Do nothing for now...
