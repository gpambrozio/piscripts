import struct

from base import logger
from device_manager import DeviceManager, DeviceThread


class LightsManager(DeviceManager):

    def __init__(self):
        SERVICE_UUID = '2234'
        INSIDE_CHAR_UUID = '2235'
        OUTSIDE_CHAR_UUID = '2236'

        DeviceManager.__init__(self, [[SERVICE_UUID, INSIDE_CHAR_UUID, OUTSIDE_CHAR_UUID]], LightsThread)


class Strip:
    
    def __init__(self, characteristic):
        data = characteristic.read()
        self.characteristic = characteristic
        (m, b, d, _, c) = struct.unpack('<cBBBI', data)
        self.state = {
            'mode': m,
            'brightness': int(b),
            'cycleDelay': int(d),
            'color': int(c),
        }
        logger.debug("Light: %s", self.state)


    def update(self):
        logger.debug("Updating Light: %s", self.state)
        self.characteristic.write(self.toData())


    def toData(self):
        # Last 1 is padding to make it 8 bytes (multiple of 4)
        return struct.pack('<cBBBI', self.state['mode'], self.state['brightness'], self.state['cycleDelay'], 0, self.state['color'])


    def parseState(self, state):
        for k in self.state.keys():
            if k in state:
                self.state[k] = state[k]


class LightsThread(DeviceThread):

    def before_thread(self):
        service_uuid = self.service_and_char_uuids[0][0]
        self.inside_characteristic = self.characteristics[service_uuid][0]
        self.outside_characteristic = self.characteristics[service_uuid][1]
        self.strips = {
            'I': Strip(self.inside_characteristic),
            'O': Strip(self.outside_characteristic),
        }
        for stripId in self.strips:
            strip = self.strips[stripId]
            self.add_broadcast(None, "Light:%s" % stripId, strip.state)


    def write(self, strip):
        self.add_command(lambda: strip.update())


    def broadcast_received(self, broadcast):
        if broadcast.prop.startswith("Light:"):
            stripId = broadcast.prop[-1]
            if not stripId in self.strips:
                logger.debug("Unknown strip: %s" % stripId)
                return

            strip = self.strips[stripId]
            strip.parseState(broadcast.value)
            self.write(strip)

        elif broadcast.prop == "Speed" and broadcast.value > 10:
            # Turn lights off
            for stripId in self.strips:
                strip = self.strips[stripId]
                strip.state['mode'] = 'C'
                strip.state['brightness'] = 0;
                self.write(strip)
                self.add_broadcast(None, "Light:%s" % stripId, strip.state)
