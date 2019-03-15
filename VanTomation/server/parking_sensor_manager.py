import Queue as queue
import binascii
import datetime
import struct

from base import logger
from device_manager import DeviceManager, DeviceThread


class ParkingSensorManager(DeviceManager):

    def __init__(self):
        SERVICE_UUID = '8242'
        TX_CHAR_UUID = '4242'

        DeviceManager.__init__(self, [[SERVICE_UUID, TX_CHAR_UUID]], ParkingSensorThread)


class ParkingSensorThread(DeviceThread):

    def before_thread(self):
        service_uuid = self.service_and_char_uuids[0][0]
        self.tx_characteristic = self.characteristics[service_uuid][0]
        self.next_temp_read = datetime.datetime.now()
        self.on_off = False
        
        
    def read_distance(self):
        data = self.tx_characteristic.read()
        distance = struct.unpack('f', data)[0]
        self.add_broadcast(None, "Distance", distance)


    def no_data_received(self):
        if datetime.datetime.now() > self.next_temp_read and self.on_off:
            self.next_temp_read = datetime.datetime.now() + datetime.timedelta(milliseconds=200)
            self.add_command(lambda: self.read_distance())


    def broadcast_received(self, broadcast):
        if broadcast.destination is None and broadcast.prop == "ParkingOnOff":
            self.on_off = broadcast.value
            self.next_temp_read = datetime.datetime.now()
