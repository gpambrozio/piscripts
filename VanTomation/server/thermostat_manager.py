import struct

from base import SenderReceiver, logger
from device_manager import DeviceManager, DeviceThread


class ThermostatManager(DeviceManager):

    def __init__(self):
        SERVICE_UUID = '1234'
        TEMP_CHAR_UUID = '1235'
        HUMID_CHAR_UUID = '1236'
        ONOFF_CHAR_UUID = '1237'
        TARGET_CHAR_UUID = '1238'

        DeviceManager.__init__(self, [[SERVICE_UUID, TEMP_CHAR_UUID, HUMID_CHAR_UUID, ONOFF_CHAR_UUID, TARGET_CHAR_UUID]], ThermostatThread)
        

class ThermostatThread(DeviceThread):

    def before_thread(self):
        service_uuid = self.service_and_char_uuids[0][0]
        self.temperature = None
        self.humidity = None
        self.onoff = None
        self.target = None
        self.temperature_characteristic = self.characteristics[service_uuid][0]
        self.humidity_characteristic = self.characteristics[service_uuid][1]
        self.onoff_characteristic = self.characteristics[service_uuid][2]
        self.target_characteristic = self.characteristics[service_uuid][3]
        self.start_notifications(self.temperature_characteristic)
        self.start_notifications(self.humidity_characteristic)
        self.start_notifications(self.onoff_characteristic)
        self.start_notifications(self.target_characteristic)
        self.onoff = int(struct.unpack('B', self.onoff_characteristic.read())[0])
        self.target = float(struct.unpack('<h', self.target_characteristic.read())[0]) / 10
        self.add_broadcast(None, "ThermostatTargetOnOff", self.onoff)
        self.add_broadcast(None, "ThermostatTarget", self.target)


    def received_data(self, cHandle, data):
        if cHandle == self.temperature_characteristic.getHandle():
            self.temperature = float(struct.unpack('<h', data)[0]) / 10
            self.add_broadcast(None, "Temperature", self.temperature)
        elif cHandle == self.humidity_characteristic.getHandle():
            self.humidity = float(struct.unpack('<h', data)[0]) / 10
            self.add_broadcast(None, "Humidity", self.humidity)
        elif cHandle == self.onoff_characteristic.getHandle():
            self.onoff = int(struct.unpack('B', data)[0])
            self.add_broadcast(None, "ThermostatOnOff", self.onoff)
        elif cHandle == self.target_characteristic.getHandle():
            self.target = float(struct.unpack('<h', data)[0]) / 10
            self.add_broadcast(None, "ThermostatTarget", self.target)
        else:
            logger.debug("Unknown handle %d", cHandle)


    def broadcast_received(self, broadcast):
        if broadcast.destination is None and broadcast.prop == "ThermostatOnOff":
            self.onoff = broadcast.value
            logger.debug("Setting onoff to %d", self.onoff)
            self.add_command(lambda: self.onoff_characteristic.write('\x01' if self.onoff else '\x00'))
        elif broadcast.destination is None and broadcast.prop == "ThermostatTarget":
            self.target = broadcast.value
            logger.debug("Setting temp to %d", self.target)
            self.add_command(lambda: self.target_characteristic.write(struct.pack('<h', self.target)))
        elif broadcast.prop == "Speed" and broadcast.source == "gps" and broadcast.value > 10:
            # Turn thermostat off
            self.onoff = 0
            self.add_command(lambda: self.onoff_characteristic.write('\x00'))
            self.add_broadcast(None, "ThermostatOnOff", 0)
