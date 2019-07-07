import os
import json
import logging

from base import SenderReceiver, logger
from logging.handlers import TimedRotatingFileHandler


# create logger
logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)

# create console handler and set level to debug
ch = TimedRotatingFileHandler('/tmp/vantomation.commands.log', when='midnight', backupCount=5)
ch.setLevel(logging.DEBUG)

# create formatter
formatter = logging.Formatter('%(asctime)s - %(message)s')

# add formatter to ch
ch.setFormatter(formatter)

# add ch to logger
logger.addHandler(ch)


class StateManager(SenderReceiver):
    def __init__(self):
        SenderReceiver.__init__(self, "StateManager")
        self.current_state = {}


    def broadcast_received(self, broadcast):
        if broadcast.destination is None:
            self.current_state = self.coordinator.current_state
            self.dump_state()
        logger.debug("%s", broadcast)


    def set_coordinator(self, coordinator):
        SenderReceiver.set_coordinator(self, coordinator)
        self.current_state = self.coordinator.current_state
        self.dump_state()


    def dump_state(self):
        state = {k: {'ts': v.ts, 'value': v.value} for (k, v) in self.current_state.iteritems()}
        state_file = open("/tmp/vantomation.state.json.temp", "w+")
        state_file.write(json.dumps(state))
        state_file.close()
        os.rename("/tmp/vantomation.state.json.temp", "/tmp/vantomation.state.json")
