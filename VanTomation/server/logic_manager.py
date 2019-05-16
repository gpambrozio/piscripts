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


    def set_property(self, name, value):
        if name not in self.properties or self.properties[name] != value:
            self.properties[name] = value
            self.add_broadcast(None, name, value)


    def broadcast_received(self, broadcast):
        if broadcast.destination is None:
            self.current_state[broadcast.prop]= broadcast.value

        if broadcast.prop == 'Speed' and broadcast.value > 10 and not self.properties['Moving']:
            self.set_property('Moving', True)
            self.set_property('Parked', False)
            self.stopped_time = None

        elif broadcast.prop == "Speed" and broadcast.value < 3:
            self.set_property('Moving', False)
            if self.stopped_time is None:
                self.stopped_time = datetime.datetime.now()

        if not self.properties['Moving'] and self.stopped_time is not None:
            elapsed = (datetime.datetime.now() - self.stopped_time).seconds
            if elapsed > 2 * 60:
                self.set_property('Parked', True)
                self.stopped_time = None

