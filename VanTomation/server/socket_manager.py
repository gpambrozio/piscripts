import threading
import socket
import sys
import time
import Queue as queue

from base import SenderReceiver, SerialBuffer, logger


class SocketManagerConnectionHandler(SenderReceiver):
    def __init__(self, name):
        SenderReceiver.__init__(self, name)
        self.commands = queue.Queue()
        self.addr = name

    def handle(self, command):
        pass


    def disconnected(self):
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
            client.setsockopt(socket.SOL_SOCKET, socket.SO_KEEPALIVE, 1)
            client.setsockopt(socket.IPPROTO_TCP, socket.TCP_KEEPIDLE, 5)
            client.setsockopt(socket.IPPROTO_TCP, socket.TCP_KEEPINTVL, 5)
            client.setsockopt(socket.IPPROTO_TCP, socket.TCP_KEEPCNT, 3)
            threading.Thread(target=self.listenToClient, args=(client, address)).start()


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
                    logger.error("No data, breaking")
                    break

                past_data.received(data)
                lines = past_data.pending_data()
                if len(lines) == 0:
                    continue

                if handler is None:
                    handler_class_name = lines[0].strip(" \r\n") + "Handler"
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

        except Exception as e:
            logger.error("Error in loop: %s" % e)

        finally:
            # Clean up the connection
            logger.debug("Closed socket")
            if handler is not None:
                handler.disconnected()
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
        elif command[0] == "T":
            # Date format is 0603232819.58;America/Denver
            date_time_tz = command[1:].split(";", 1)
            self.add_broadcast("Pi", "TimeZone", date_time_tz[1])
            self.add_broadcast("Pi", "DateTime", date_time_tz[0])
        elif command[0] == "l":
            self.add_broadcast("Locks", "State", command[1])


    def broadcast_received(self, broadcast):
        if broadcast.destination is None and broadcast.prop == "Connected":
            self.add_command("C%s" % ("1" if broadcast.value is not None else "0"))


class PanelHandler(SocketManagerConnectionHandler):

    def __init__(self):
        SocketManagerConnectionHandler.__init__(self, 'panel')
        self.add_command("files")


    def handle(self, command):
        if command.startswith('files:'):
            files = command[6:].strip(" \r\n").split(',')
            self.add_broadcast(None, "Files", files)


    def broadcast_received(self, broadcast):
        if broadcast.destination == "Panel" and broadcast.prop == "Play":
            self.add_command("image/%s/1" % broadcast.value)


    def disconnected(self):
        SocketManagerConnectionHandler.disconnected(self)
        self.add_broadcast(None, "Files", [])


class KeypadHandler(SocketManagerConnectionHandler):

    def __init__(self):
        SocketManagerConnectionHandler.__init__(self, 'keypad')
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

        elif broadcast.destination is None and broadcast.prop == "Distance" and broadcast.source == "Parking":
            self.add_command("Ds%s" % (broadcast.value or ""))

        elif broadcast.prop == "Moving" and broadcast.value and (time.time() - broadcast.ts) < 5:
            self.add_command("Md")
        elif broadcast.prop == "Parked" and broadcast.value and (time.time() - broadcast.ts) < 5:
            self.add_command("Mh")

        elif broadcast.prop == "Files" and broadcast.source == "panel":
            self.add_command("Pf%s" % (','.join(sorted(broadcast.value))))

        elif broadcast.prop == "Position" and broadcast.source == "fan":
            self.add_command("Fp%d" % broadcast.value)

        elif broadcast.prop == "Position" and broadcast.source == "Couch":
            self.add_command("Cp%d" % broadcast.value)

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

        elif items[0] == "Fan":
            if items[1] == "C":
                self.add_broadcast("Fan", "Position", 0)
            elif items[1] == "U":
                self.add_broadcast("Fan", "Relative", 25)
            elif items[1] == "D":
                self.add_broadcast("Fan", "Relative", -25)

        elif items[0] == "Couch":
            if items[1] == "C":
                self.add_broadcast("Couch", "Position", 0)
            elif items[1] == "U":
                self.add_broadcast("Couch", "Relative", 25)
            elif items[1] == "D":
                self.add_broadcast("Couch", "Relative", -25)

        elif items[0] == "Light":
            stripId = "Light:%s" % items[1]
            state = self.current_state.get(stripId)
            if state is not None:
                state['brightness'] = int(items[3])
                if state['mode'] != items[2]:
                    state['mode'] = items[2]
                    state['color'] = 0xFFFFFF
                self.add_broadcast(None, stripId, state)


class FanHandler(SocketManagerConnectionHandler):

    def __init__(self):
        SocketManagerConnectionHandler.__init__(self, 'fan')


    def handle(self, command):
        if command.startswith('P:'):
            try:
                position = int(command[2:].strip(" \r\n"))
                self.add_broadcast(None, "Position", position)
            except Exception as e:
                logger.error("Error parsing command: %s" % command)


    def broadcast_received(self, broadcast):
        if broadcast.destination == "Fan" and broadcast.prop == "Relative":
            self.add_command("R%d" % broadcast.value)
        elif broadcast.destination == "Fan" and broadcast.prop == "Position":
            self.add_command("P%d" % broadcast.value)

        # Close/open fan when we start/stop moving
        elif broadcast.prop == "Moving" and broadcast.value:
            self.add_command("P40")
        elif broadcast.prop == "Parked" and broadcast.value:
            self.add_command("P100")


class ParkingHandler(SocketManagerConnectionHandler):

    def __init__(self):
        SocketManagerConnectionHandler.__init__(self, 'Parking')


    def handle(self, command):
        if command.startswith('D'):
            distance = int(command[1:].strip(" \r\n"))
            self.add_broadcast(None, "Distance", distance)


    def broadcast_received(self, broadcast):
        if broadcast.destination is None and broadcast.prop == "ParkingOnOff":
            self.add_command("+" if broadcast.value else "-")


class CouchHandler(SocketManagerConnectionHandler):

    def __init__(self):
        SocketManagerConnectionHandler.__init__(self, 'Couch')


    def handle(self, command):
        if command.startswith('P:'):
            try:
                position = int(command[2:].strip(" \r\n"))
                self.add_broadcast(None, "Position", position)
            except Exception as e:
                logger.error("Error parsing command: %s" % command)


    def broadcast_received(self, broadcast):
        if broadcast.destination == "Couch" and broadcast.prop == "Relative":
            self.add_command("R%d" % broadcast.value)
        elif broadcast.destination == "Couch" and broadcast.prop == "Position":
            self.add_command("P%d" % broadcast.value)

        # Lower couch when we start moving
        elif broadcast.prop == "Moving" and broadcast.value:
            self.add_command("P0")

