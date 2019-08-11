import binascii
import json
import struct
import time

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
        self.serial_buffer = SerialBuffer()
        self.last_sent_data = {}
        self.waiting_to_send_data = []


    def received_data(self, cHandle, data):
        if cHandle == self.input_characteristic.getHandle():
            self.serial_buffer.received(data)
            for line in self.serial_buffer.pending_data():
                destination = line[0]
                if destination == "L":
                    strip = line[1]
                    value = line[2:]

                    state = {
                        'mode': value[0],
                        'brightness': ord(binascii.unhexlify(value[1:3])),
                        'cycleDelay': 2 * ord(binascii.unhexlify(value[3:5])),
                        'color': struct.unpack('>I', binascii.unhexlify(value[5:]) + '\x00')[0] / 256,
                    }

                    self.add_broadcast(None, "Light:%s" % strip, state)
                elif destination == "P":
                    self.add_broadcast("Locks", "State", line[1])
                elif destination == "T":
                    self.add_broadcast(None, "ThermostatOnOff", int(line[2]))
                    self.add_broadcast(None, "ThermostatTarget", int(line[3:], 16))
                elif destination == "D":
                    self.add_broadcast("Panel", "Play", line[2:])
                else:
                    logger.info("Unknown destination: %s" % line)


    def send_command(self, command):
        self.add_command(lambda: self.output_characteristic.write(command))


    def will_check_commands(self):
        if self.waiting_to_send_data:
            identifier, message = self.waiting_to_send_data.pop(0)
            to_send = "%s%s\n" % (identifier, message)
            while to_send:
                self.send_command(to_send[:20])
                to_send = to_send[20:]


    # For commands that the controller can change we need to force sending it again
    # because the value we have cached might not be the latest one.
    def send(self, identifier, message, force = False):
        if not force and identifier in self.last_sent_data and self.last_sent_data[identifier] == message:
            return

        self.last_sent_data[identifier] = message
        for i, identifierAndMessage in enumerate(self.waiting_to_send_data):
            if identifierAndMessage[0] == identifier:
                del self.waiting_to_send_data[i]
                break
        self.waiting_to_send_data.append((identifier, message))


    def broadcast_received(self, broadcast):
        if broadcast.destination is None and broadcast.prop == "Devices":
            self.send("Dv", ", ".join(sorted(broadcast.value)))

        elif broadcast.destination is None and broadcast.prop == "Temperature" and broadcast.source == "Thermostat":
            self.send("Ti", "%.0f" % (broadcast.value * 10))
        elif broadcast.destination is None and broadcast.prop == "Temperature" and broadcast.source == "Pi":
            self.send("To", "%.0f" % (broadcast.value * 10))

        elif broadcast.destination is None and broadcast.prop == "Humidity" and broadcast.source == "Thermostat":
            self.send("Hm", "%.0f" % (broadcast.value * 10))
        elif broadcast.destination is None and broadcast.prop == "ThermostatOnOff":
            self.send("TO", "%d" % broadcast.value, True)
        elif broadcast.destination is None and broadcast.prop == "ThermostatTarget":
            self.send("Tt", "%.0f" % (broadcast.value), True)

        elif broadcast.prop == "Files" and broadcast.source == "panel":
            self.send("Pf", json.dumps(broadcast.value))

        elif broadcast.prop == "Moving" and broadcast.value and (time.time() - broadcast.ts) < 5:
            self.send("Mv", "1")

        elif broadcast.prop == "Parked" and broadcast.value and (time.time() - broadcast.ts) < 5:
            self.send("Mv", "0")

        elif broadcast.destination is None and broadcast.prop == "Connected":
            self.send("Cs", "1" if broadcast.value is not None else "0")

        elif broadcast.destination is None and broadcast.prop.startswith("Light:"):
            stripId = broadcast.prop[-1]
            brightness = broadcast.value['brightness']
            if broadcast.value['mode'] == 'C' and broadcast.value['color'] == 0:
                brightness = 0
            self.send("L%s" % stripId, "%s%d,%d,%d" % (broadcast.value['mode'], brightness, broadcast.value['cycleDelay'], broadcast.value['color']))
