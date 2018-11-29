from bluepy.btle import DefaultDelegate, BTLEException
from bluepy import btle
import threading
import Queue as queue
import uuid
import traceback

from base import SenderReceiver, logger


def reverse_uuid(service_uuid):
    if len(service_uuid) == 4:
        return service_uuid[2:4] + service_uuid[0:2]
    return uuid.UUID(bytes="".join([uuid.UUID(service_uuid).bytes[15-i] for i in range(16)])).hex

# Define service and characteristic UUIDs.

class DeviceManager(object):
    def __init__(self, service_and_char_uuids, thread_class):
        self.threads_by_addr = {}
        self.threads_by_name = {}
        self.service_and_char_uuids = service_and_char_uuids
        self.required_services = set([reverse_uuid(s[0]) for s in service_and_char_uuids])
        self.thread_class = thread_class
        self.coordinator = None


    def all_broadcasters(self):
        return self.threads_by_addr.values()


    def set_coordinator(self, coordinator):
        self.coordinator = coordinator


    def should_connect_to(self, device, device_name):
        return True


    def found_devices(self, devices):
        # Check if everything is OK
        for addr in self.threads_by_addr.keys():   # .keys() creates a copy and avoids error due to removing key
            t = self.threads_by_addr[addr]
            if not t.is_alive():
                if self.coordinator is not None:
                    self.coordinator.device_disconnected(t)
                del self.threads_by_name[t.name]
                del self.threads_by_addr[addr]
                logger.debug("Device %s thread died... Removing", t.name)

        for dev in devices:
            scan_data = dev.getScanData()
            services = set([s[2] for s in scan_data if s[0] in [3, 6, 7]])

            name = dev.getValueText(9) or dev.getValueText(8)
            if (name is not None and
                self.should_connect_to(dev, name) and
                self.required_services <= services and
                dev.addr not in self.threads_by_addr and 
                name not in self.threads_by_name):
                try:
                    logger.debug("Found device %s type %s", dev.addr, type(self))
                    t = self.thread_class(self, dev, name, self.service_and_char_uuids)
                    logger.debug("Connected to %s (%s)", dev.addr, t.name)
                    self.threads_by_addr[dev.addr] = t
                    self.threads_by_name[name] = t
                    if self.coordinator is not None:
                        self.coordinator.device_connected(t)
                        # Send all currently known states
                        for s in self.coordinator.current_state.values():
                            t.broadcast_received(s)

                except Exception, e:
                    logger.debug("Exception connecting to %s: %s", dev.addr, e)


class NotificationDelegate(DefaultDelegate):
    def __init__(self):
        DefaultDelegate.__init__(self)
        self.last_data = None


    def handleNotification(self, cHandle, data):
        self.last_data = (cHandle, data)


class DeviceThread(SenderReceiver):
    def __init__(self, manager, dev, name, service_and_char_uuids):
        """ Constructor
        """
        SenderReceiver.__init__(self, name)

        self.manager = manager
        self.dev = dev
        self.service_and_char_uuids = service_and_char_uuids

        self.addr = dev.addr
        self.name = name

        self.delegate = NotificationDelegate()
        self.peripheral = btle.Peripheral()
        self.peripheral.setDelegate(self.delegate)
        self.peripheral.connect(self.dev)

        # logger.debug("services %s", [s.uuid.getCommonName() for s in self.peripheral.getServices()])
        self.services = [self.peripheral.getServiceByUUID(s[0]) for s in service_and_char_uuids]
        self.characteristics = {}
        for i, s in enumerate(service_and_char_uuids):
            service_uuid = s[0]
            service = self.services[i]
            self.characteristics[service_uuid] = [service.getCharacteristics(uuid)[0] for uuid in s[1:]]
        
        self.commands = queue.Queue()
        
        self.before_thread()
    
        self.thread = threading.Thread(target=self.run)
        self.thread.daemon = True                            # Daemonize thread
        self.thread.start()                                  # Start the execution

        
    def run(self):
        """ Method that runs forever """

        while True:
            try:
                if self.peripheral.waitForNotifications(0.1):
                    # handleNotification() was called
                    self.received_data(self.delegate.last_data[0], self.delegate.last_data[1])
                else:
                    self.no_data_received()

            except BTLEException, e:
                if e.code == BTLEException.DISCONNECTED:
                    self.peripheral.disconnect()
                    logger.debug("%s disconnected", self.name)
                else:
                    logger.debug("BTLEException: %s\n%s", e, traceback.format_exc())
                break

            except Exception, e:
                logger.debug("Exception: %s\n%s", e, traceback.format_exc())
                break

            try:
                command = self.commands.get(False)
                command()
                self.commands.task_done()
            except queue.Empty:
                pass
            except Exception, e:
                logger.debug("Exception: %s\n%s", e, traceback.format_exc())


    def start_notifications(self, characteristic):
        # From https://stackoverflow.com/a/42703501/754013
        self.peripheral.writeCharacteristic(characteristic.valHandle + 1, "\x01\x00")


    def is_alive(self):
        return self.thread.is_alive()
        
        
    def before_thread(self):
        # Do something in subclasses
        pass
    
    
    def received_data(self, cHandle, data):
        # Do something in subclasses
        pass

        
    def no_data_received(self):
        # Just in case a subclass wants to do something about it.
        pass
        
        
    def add_command(self, command):
        self.commands.put(command)
