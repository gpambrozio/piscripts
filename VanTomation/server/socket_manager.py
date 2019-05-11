import threading
import socket
import sys
import Queue as queue

from base import SenderReceiver, SerialBuffer, logger


class SocketManagerConnectionHandler(SenderReceiver):
    def __init__(self, name):
        SenderReceiver.__init__(self, name)
        self.commands = queue.Queue()
        self.addr = name

    def handle(self, command):
        pass


    def add_command(self, command):
        self.commands.put(command)


class SocketManager(SenderReceiver):
    def __init__(self):
        SenderReceiver.__init__(self, "Socket")
        server_port = 5000

        # Create a UDS socket
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.sock.bind(('', server_port))
        
        self.handlers = []

        # Listen for incoming connections
        self.sock.listen(5)
        self.thread = threading.Thread(target=self.listen)
        self.thread.daemon = True                            # Daemonize thread
        self.thread.start()                                  # Start the execution


    def all_broadcasters(self):
        return self.handlers


    def listen(self):
        """ Method that runs forever """
        while True:
            client, address = self.sock.accept()
            client.settimeout(60)
            threading.Thread(target=self.listenToClient, args=(client,address)).start()


    def listenToClient(self, connection, client_address):
        # Receive the data in small chunks and retransmit it
        handler = None
        try:
            logger.debug("connection from %s", client_address)
            connection.setblocking(0)
            past_data = SerialBuffer()
            while True:
                try:
                    data = connection.recv(256)
                except socket.error:
                    # No data received but still connected
                    if handler is not None:
                        try:
                            command = handler.commands.get(False)
                            connection.sendall(command + "\n")
                            handler.commands.task_done()
                        except queue.Empty:
                            pass

                    continue

                if data == '':   # connection closed
                    break

                past_data.received(data)
                lines = past_data.pending_data()
                if len(lines) == 0:
                    continue

                if handler is None:
                    handler_class_name = lines[0] + "Handler"
                    handler_class = getattr(sys.modules[__name__], handler_class_name)
                    handler = handler_class()
                    lines = lines[1:]
                    self.handlers.append(handler)
                    if self.coordinator is not None:
                        self.coordinator.device_connected(handler)

                        # Send all currently known states
                        for s in self.coordinator.current_state.values():
                            handler.broadcast_received(s)

                for line in lines:
                    handler.handle(line)
        finally:
            # Clean up the connection
            logger.debug("Closed socket")
            if handler is not None:
                self.handlers.remove(handler)
                self.coordinator.device_disconnected(handler)


class PhoneGPSHandler(SocketManagerConnectionHandler):

    def __init__(self):
        SocketManagerConnectionHandler.__init__(self, 'gps')


    def handle(self, command):
        if command[0] == "L":
            components = command[1:].split(',')
            self.add_broadcast(None, "Location", (float(components[0]) / 10000, float(components[1]) / 10000))
        elif command[0] == "A":
            components = command[1:].split(',')
            self.add_broadcast(None, "Altitude", int(components[0]))
            self.add_broadcast(None, "Speed", int(components[1]))
            self.add_broadcast(None, "Heading", int(components[2]))


class KeypadHandler(SocketManagerConnectionHandler):

    def __init__(self):
        SocketManagerConnectionHandler.__init__(self, 'panel')
        self.current_state = {}


    def broadcast_received(self, broadcast):
        if broadcast.destination is None:
            self.current_state[broadcast.prop]= broadcast.value

        if broadcast.destination is None and broadcast.prop == "Temperature" and broadcast.source == "Thermostat":
            self.add_command("Ti%.0f" % (broadcast.value * 10))
        elif broadcast.destination is None and broadcast.prop == "Temperature" and broadcast.source == "Pi":
            self.add_command("To%.0f" % (broadcast.value * 10))

        elif broadcast.destination is None and broadcast.prop == "Humidity" and broadcast.source == "Thermostat":
            self.add_command("Hm%.0f" % (broadcast.value * 10))
        elif broadcast.destination is None and broadcast.prop == "ThermostatOnOff":
            self.add_command("TO%d" % broadcast.value)
        elif broadcast.destination is None and broadcast.prop == "ThermostatTarget":
            self.add_command("Tt%.0f" % (broadcast.value))

        elif broadcast.destination is None and broadcast.prop == "SSID" and broadcast.source == "WiFi":
            self.add_command("Ws%s" % (broadcast.value or ""))
        elif broadcast.destination is None and broadcast.prop == "IP" and broadcast.source == "WiFi":
            self.add_command("WI%s" % (broadcast.value or ""))

        elif broadcast.destination is None and broadcast.prop == "Distance" and broadcast.source == "Behinds":
            self.add_command("Ds%s" % (broadcast.value or ""))

        elif broadcast.destination is None and broadcast.prop.startswith("Light:"):
            stripId = broadcast.prop[-1]
            brightness = broadcast.value['brightness']
            if broadcast.value['mode'] == 'C' and broadcast.value['color'] == 0:
                brightness = 0
            self.add_command("L%s%s%d" % (stripId, broadcast.value['mode'], brightness))


    def handle(self, command):
        logger.debug("Received command: %s", command)
        items = command.split(':')
        if items[0] == "ParkingSensor":
            self.add_broadcast(None, "ParkingOnOff", int(items[1]) != 0)

        elif items[0] == "ThermostatOnOff":
            self.add_broadcast(None, "ThermostatOnOff", int(items[1]))
        elif items[0] == "ThermostatTarget":
            self.add_broadcast(None, "ThermostatTarget", int(items[1]))

        elif items[0] == "Locks":
            self.add_broadcast("Locks", "State", "L" if items[1] == "lock" else "U")

        elif items[0] == "Light":
            stripId = "Light:%s" % items[1]
            state = self.current_state.get(stripId)
            if state is not None:
                state['brightness'] = int(items[3])
                if state['mode'] != items[2]:
                    state['mode'] = items[2]
                    state['color'] = 0xFFFFFF
                self.add_broadcast(None, stripId, state)
