#!/usr/bin/python

from bluepy.btle import Scanner
import threading
import Queue as queue
import time
import traceback
import subprocess

from state_manager import StateManager
from wifi_manager import WiFiManager
from controller_manager import ControllerManager
from bean_manager import BeanManager
from lights_manager import LightsManager
from thermostat_manager import ThermostatManager
from pi_manager import PIManager
from socket_manager import SocketManager
from parking_sensor_manager import ParkingSensorManager

from base import SenderReceiver
from base import logger


class Coordinator(SenderReceiver):

    def __init__(self, device_managers):
        SenderReceiver.__init__(self, "Coordinator")
        self.connected_devices = set()

        self.devices = {
            'Lights'    : 'fd:6e:55:f0:de:06',
            'Thermostat': 'eb:cc:ee:35:55:c0',
            'Inside'    : '98:7b:f3:59:1e:d4',
            'Outside'   : '98:7b:f3:5a:d2:3f',
            'Parking'   : '24:0a:c4:00:a0:2c',
            'GPS'       : 'gps',
            'Keypad'    : 'keypad',
            'Panel'     : 'panel',
        }
        
        self.devices_by_addr = {v: k for (k, v) in self.devices.iteritems()}
        
        self.current_state = {}
        
        self.device_managers = device_managers
        for manager in device_managers:
            manager.set_coordinator(self)

        self.thread = threading.Thread(target=self.run)
        self.thread.daemon = True                            # Daemonize thread
        self.thread.start()                                  # Start the execution
        

    def device_connected(self, thread):
        self.connected_devices.add(thread.addr)
        self.update_connected_devices()


    def device_disconnected(self, thread):
        if thread.addr in self.connected_devices:
            self.connected_devices.remove(thread.addr)
            self.update_connected_devices()


    def update_connected_devices(self):
        connected = ", ".join(sorted([self.devices_by_addr[addr] for addr in self.connected_devices if addr in self.devices_by_addr]))
        self.add_broadcast(None, "Devices", connected)


    def run(self):
        """ Method that runs forever """

        while True:
            broadcasters = [self]
            for manager in self.device_managers:
                broadcasters += manager.all_broadcasters()
            
            for broadcaster in broadcasters:
                while True:
                    try:
                        broadcast = broadcaster.broadcast_messages.get(False)
                        broadcaster.broadcast_messages.task_done()

                        logger.debug("Got %s", broadcast)
                        if broadcast.destination is None:
                            self.current_state[broadcast.key] = broadcast

                        # Don't send the broadcast to whoever sent it.
                        for receiver in [b for b in broadcasters if b.name != broadcaster.name]:
                            receiver.broadcast_received(broadcast)
                        
                    except queue.Empty:
                        # Nothing available, just move on...
                        break
                    
                    except Exception, e:
                        logger.debug("Exception: %s\n%s", e, traceback.format_exc())

            time.sleep(0.2)


subprocess.call("hciconfig hci0 up", shell=True)
subprocess.call("hciconfig hci1 up", shell=True)
scanner = Scanner()
managers = [
    LightsManager(),
    PIManager(),
    ThermostatManager(),
    BeanManager(),
    ControllerManager(),
    SocketManager(),
    StateManager(),
    WiFiManager(),
    ParkingSensorManager(),
]
coordinator = Coordinator(managers)

logger.debug("Starting scan")
while True:
    try:
        devices = scanner.scan(2)
        for manager in managers:
            manager.found_devices(devices)
    except Exception, e:
        logger.debug("Exception on main loop: %s\n%s", e, traceback.format_exc())
        subprocess.call("hciconfig hci0 up", shell=True)
        subprocess.call("hciconfig hci1 up", shell=True)
        scanner = Scanner()
