import os
import json

from base import SenderReceiver, logger


class StateManager(SenderReceiver):
    def __init__(self):
        SenderReceiver.__init__(self, "StateManager")
        self.current_state = {}
        self.latest_commands = {}


    def broadcast_received(self, broadcast):
        if broadcast.destination is None:
            self.current_state = self.coordinator.current_state
            self.dump_state()
        self.latest_commands["%s:%s" % (broadcast.destination, broadcast.prop)] = {"source": broadcast.source, "value": broadcast.value, "ts": broadcast.ts}
        self.dump_commands()


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


    def dump_commands(self):
        state_file = open("/tmp/vantomation.commands.json", "w+")
        state_file.write(json.dumps(self.latest_commands, indent=2))
        state_file.close()
