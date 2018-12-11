import binascii
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
        self.mode = m
        self.targetBrightness = int(b)     # uint8_t
        self.cycleDelay = int(d)           # uint8_t
        self.color = int(c)              # uint32_t
        logger.debug("Light: %s, %d", self.mode, self.color)


    def update(self):
        logger.debug("Updating Light: %s, %d %d %d", self.mode, self.targetBrightness, self.cycleDelay, self.color)
        self.characteristic.write(self.toData())


    def toData(self):
        # Last 1 is padding to make it 8 bytes (multiple of 4)
        return struct.pack('<cBBBI', self.mode, self.targetBrightness, self.cycleDelay, 0, self.color)


class LightsThread(DeviceThread):

    def before_thread(self):
        service_uuid = self.service_and_char_uuids[0][0]
        self.inside_characteristic = self.characteristics[service_uuid][0]
        self.outside_characteristic = self.characteristics[service_uuid][1]
        self.inside = Strip(self.inside_characteristic)
        self.outside = Strip(self.outside_characteristic)


    def write(self, strip):
        self.add_command(lambda: strip.update())


    def broadcast_received(self, broadcast):
        if broadcast.destination is not None and broadcast.destination.startswith("Light:") and broadcast.prop == "Mode":
            strip = self.inside if broadcast.destination[-1] == 'I' else self.outside
        
            mode = broadcast.value[0]
            if mode not in "CRT":
                logger.debug("Unknown mode: %s", mode)
                return

            strip.mode = mode
            strip.targetBrightness = ord(binascii.unhexlify(broadcast.value[1:3]))
            strip.cycleDelay = ord(binascii.unhexlify(broadcast.value[3:5]))
            strip.color = struct.unpack('<I', binascii.unhexlify(broadcast.value[5:]) + '\x00')[0]
            self.write(strip)

        elif broadcast.prop == "Speed" and broadcast.source == "gps" and broadcast.value > 10:
            # Turn light off
            self.inside.mode = 'C'
            self.inside.targetBrightness = 0;
            self.inside.color = 0
            self.outside.mode = 'C'
            self.outside.targetBrightness = 0;
            self.outside.color = 0
            self.write(self.inside)
            self.write(self.outside)
