import Queue as queue
import binascii

from base import SenderReceiver, logger
from device_manager import DeviceManager, DeviceThread


class UARTManager(DeviceManager):

    def __init__(self):
        SERVICE_UUID = '6E400001-B5A3-F393-E0A9-E50E24DCCA9E'
        TX_CHAR_UUID = '6E400002-B5A3-F393-E0A9-E50E24DCCA9E'
        RX_CHAR_UUID = '6E400003-B5A3-F393-E0A9-E50E24DCCA9E'

        DeviceManager.__init__(self, [[SERVICE_UUID, TX_CHAR_UUID, RX_CHAR_UUID]], UARTThread)
        

class UARTThread(DeviceThread):

    def before_thread(self):
        self.received_uart_data = queue.Queue()
        service_uuid = self.service_and_char_uuids[0][0]
        self.tx_characteristic = self.characteristics[service_uuid][0]
        self.rx_characteristic = self.characteristics[service_uuid][1]
        self.start_notifications(self.rx_characteristic)


    def received_data(self, cHandle, data):
        # Maybe use this for something..
        # self.received_uart_data.put(data)
        pass

        
    def write(self, data):
        """Write a string of data to the UART device."""
        self.add_command(lambda: self.tx_characteristic.write(data))


    def send_command(self, command):
        logger.debug("Sending command %s to %s", binascii.hexlify(command), self.name)
        full_command = "!" + chr(len(command) + 3) + command
        checksum = 0
        for c in full_command:
            checksum += ord(c)
        checksum = (checksum & 0xFF) ^ 0xFF
        full_command += chr(checksum)
        self.write(full_command)


    def broadcast_received(self, broadcast):
        if broadcast.destination is not None and broadcast.destination.startswith("Light:") and broadcast.prop == "Mode":
            strip = broadcast.destination[-1]
        
            mode = broadcast.value[0]
            if mode not in "CRT":
                logger.debug("Unknown mode: %s", mode)
                return

            color = binascii.unhexlify(broadcast.value[1:])
            self.send_command(mode + strip + color)
        elif broadcast.prop == "Speed" and broadcast.source == "gps" and broadcast.value > 10:
            # Turn light off
            self.send_command("CI\x00\x00\x00\x00")
            self.send_command("CO\x00\x00\x00\x00")


    def read(self, timeout_sec=None):
        """Block until data is available to read from the UART.  Will return a
        string of data that has been received.  Timeout_sec specifies how many
        seconds to wait for data to be available and will block forever if None
        (the default).  If the timeout is exceeded and no data is found then
        None is returned.
        """
        try:
            read_data = self.received_uart_data.get(timeout=timeout_sec)
            self.received_uart_data.task_done()
            return read_data
        except queue.Empty:
            # Timeout exceeded, return None to signify no data received.
            return None
