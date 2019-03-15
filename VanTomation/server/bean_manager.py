import Queue as queue
import binascii
import datetime
import struct

from base import logger
from device_manager import DeviceManager, DeviceThread


class BeanManager(DeviceManager):

    def __init__(self):
        SERVICE_UUID = 'a495ff10-c5b1-4b44-b512-1370f02d74de'
        TX_CHAR_UUID = 'a495ff11-c5b1-4b44-b512-1370f02d74de'

        DeviceManager.__init__(self, [[SERVICE_UUID, TX_CHAR_UUID]], BeanThread)


    def should_connect_to(self, device, device_name):
        return device_name != "AgnesInside"


class BeanThread(DeviceThread):

    def before_thread(self):
        BATTERY_SERVICE_UUID = '180F'
        BATTERY_CHAR_UUID = '2A19'

        self.received_uart_data = queue.Queue()
        service_uuid = self.service_and_char_uuids[0][0]
        self.tx_characteristic = self.characteristics[service_uuid][0]
        self.start_notifications(self.tx_characteristic)
        self.next_temp_read = datetime.datetime.now()
        
        self.battery_service = self.peripheral.getServiceByUUID(BATTERY_SERVICE_UUID)
        self.battery_characteristic = self.battery_service.getCharacteristics(BATTERY_CHAR_UUID)[0]


    def no_data_received(self):
        if datetime.datetime.now() > self.next_temp_read:
            self.next_temp_read = datetime.datetime.now() + datetime.timedelta(seconds=30)
            # Ask for temperature
            self.add_command(lambda: self.tx_characteristic.write(binascii.unhexlify("a0020020115e6d")))


    def received_data(self, cHandle, data):
        data_type = ord(data[4])
        if data_type == 0x91:
            temperature = 32.0 + float(ord(data[5])) * 9.0 / 5.0
            # Now ask for accelerometer
            self.add_command(lambda: self.tx_characteristic.write(binascii.unhexlify("a0020020107f7d")))
            self.add_broadcast(None, "Temperature", temperature)
        elif data_type == 0x90:
            x = struct.unpack('<h', data[5:7])[0]
            y = struct.unpack('<h', data[7:9])[0]
            z = struct.unpack('<h', data[9:11])[0]
            self.add_broadcast(None, "Accelerometer", (x, y, z))
            battery = ord(self.battery_characteristic.read()[0])
            self.add_broadcast(None, "Battery", battery)
        else:
            logger.error("Unkown type: %d (%s)" % (data_type, binascii.hexlify(data)))
