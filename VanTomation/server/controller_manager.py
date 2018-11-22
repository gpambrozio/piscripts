import json
import threading
import Queue as queue

from base import logger, SerialBuffer
from device_manager import DeviceManager, DeviceThread


class ControllerManager(DeviceManager):

    def __init__(self):
        SERVICE_UUID = '12345678-1234-5678-1234-56789abc0010'
        INPUT_CHAR_UUID = '12345679-1234-5678-1234-56789abc0010'
        OUTPUT_CHAR_UUID = '1234567a-1234-5678-1234-56789abc0010'

        DeviceManager.__init__(self, [[SERVICE_UUID, INPUT_CHAR_UUID, OUTPUT_CHAR_UUID]], ControllerThread)
        

class ControllerThread(DeviceThread):

    def before_thread(self):
        service_uuid = self.service_and_char_uuids[0][0]
        self.input_characteristic = self.characteristics[service_uuid][0]
        self.output_characteristic = self.characteristics[service_uuid][1]
        self.start_notifications(self.input_characteristic)
        self.received_data = SerialBuffer()
        self.last_sent_data = {}


    def received_data(self, cHandle, data):
        if cHandle == self.input_characteristic.getHandle():
            self.received_data.received(data)
            for line in self.received_data.pending_data():
                destination = line[0]
                if destination == "L":
                    strip = line[1]
                    value = line[2:]
                    self.add_broadcast("Light:%s" % strip, "Mode", value)
                elif destination == "P":
                    self.add_broadcast("Locks", "State", line[1])
                elif destination == "T":
                    self.add_broadcast("Thermostat", "On", int(line[2]))
                    self.add_broadcast("Thermostat", "Target", int(line[3:], 16))
                else:
                    logger.info("Unknown destination: %s" % line)


    def send_command(self, command):
        self.add_command(lambda: self.output_characteristic.write(command))


    def send(self, identifier, message):
        if identifier in self.last_sent_data and self.last_sent_data[identifier] == message:
            return

        self.last_sent_data[identifier] = message
        to_send = "%s%s\n" % (identifier, message)
        while to_send:
            self.send_command(to_send[:20])
            to_send = to_send[20:]


    def broadcast_received(self, broadcast):
        if broadcast.destination == None and broadcast.prop == "Devices":
            self.send("Dv", broadcast.value)

        elif broadcast.destination == None and broadcast.prop == "Temperature" and broadcast.source == "Thermostat":
            self.send("Ti", "%.0f" % (broadcast.value * 10))
        elif broadcast.destination == None and broadcast.prop == "Temperature" and broadcast.source == "AgnesOutside":
            self.send("To", "%.0f" % (broadcast.value * 10))

        elif broadcast.destination == None and broadcast.prop == "Humidity" and broadcast.source == "Thermostat":
            self.send("Hm", "%.0f" % (broadcast.value * 10))
        elif broadcast.destination == None and broadcast.prop == "On" and broadcast.source == "Thermostat":
            self.send("TO", "%d" % broadcast.value)
        elif broadcast.destination == None and broadcast.prop == "Target" and broadcast.source == "Thermostat":
            self.send("Tt", "%.0f" % (broadcast.value * 10))

        elif broadcast.destination == None and broadcast.prop == "SSID" and broadcast.source == "Wifi":
            self.send("Ws", "%s" % (broadcast.value or ""))
        elif broadcast.destination == None and broadcast.prop == "IP" and broadcast.source == "Wifi":
            self.send("Wi", "%s" % (broadcast.value or ""))
        elif broadcast.destination == None and broadcast.prop == "Scan" and broadcast.source == "Wifi":
            self.send("WS", "%s" % (json.dumps(broadcast.value) if broadcast.value else ""))
