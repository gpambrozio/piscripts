import threading
import Queue as queue

from base import logger
from device_manager import DeviceManager, DeviceThread


class ControllerManager(DeviceManager):

    def __init__(self):
        SERVICE_UUID = '12345678-1234-5678-1234-56789abc0010'
        COMMAND_CHAR_UUID = '12345679-1234-5678-1234-56789abc0010'
        DEVICES_CHAR_UUID = '1234567a-1234-5678-1234-56789abc0010'

        DeviceManager.__init__(self, [[SERVICE_UUID, COMMAND_CHAR_UUID, DEVICES_CHAR_UUID]], ControllerThread)
        

class ControllerThread(DeviceThread):

    def before_thread(self):
        service_uuid = self.service_and_char_uuids[0][0]
        self.command_characteristic = self.characteristics[service_uuid][0]
        self.devices_characteristic = self.characteristics[service_uuid][1]
        self.start_notifications(self.command_characteristic)


    def received_data(self, cHandle, data):
        if cHandle == self.command_characteristic.getHandle():
            destination = data[0]
            if destination == "L":
                strip = data[1]
                value = data[2:]
                self.add_broadcast("Light:%s" % strip, "Mode", value)
            elif destination == "P":
                self.add_broadcast("Locks", "State", data[1])
            elif destination == "T":
                self.add_broadcast("Thermostat", "On", int(data[2]))
                self.add_broadcast("Thermostat", "Target", int(data[3:], 16))
            else:
                logger.info("Unknown destination: %s" % data)


    def broadcast_received(self, broadcast):
        if broadcast.destination == None and broadcast.prop == "Devices":
            self.add_command(lambda: self.devices_characteristic.write("Dv" + broadcast.value))
        elif broadcast.destination == None and broadcast.prop == "Temperature" and broadcast.source == "Thermostat":
            self.add_command(lambda: self.devices_characteristic.write("Ti%.0f" % (broadcast.value * 10)))
        elif broadcast.destination == None and broadcast.prop == "Temperature" and broadcast.source == "AgnesOutside":
            self.add_command(lambda: self.devices_characteristic.write("To%.0f" % (broadcast.value * 10)))
        elif broadcast.destination == None and broadcast.prop == "Humidity" and broadcast.source == "Thermostat":
            self.add_command(lambda: self.devices_characteristic.write("Hm%.0f" % (broadcast.value * 10)))
        elif broadcast.destination == None and broadcast.prop == "On" and broadcast.source == "Thermostat":
            self.add_command(lambda: self.devices_characteristic.write("To%d" % broadcast.value))
        elif broadcast.destination == None and broadcast.prop == "Target" and broadcast.source == "Thermostat":
            self.add_command(lambda: self.devices_characteristic.write("Tt%.0f" % (broadcast.value * 10)))
