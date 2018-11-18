import threading
import socket
import sys
import Queue as queue

from base import SenderReceiver, logger


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
        try:
            logger.debug("connection from %s", client_address)
            connection.setblocking(0)
            past_data = ""
            handler = None
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

                past_data += data
                lines = past_data.split("\n")
                past_data = lines[-1]
                lines = lines[0:-1]
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


class PanelHandler(SocketManagerConnectionHandler):

    def __init__(self):
        SocketManagerConnectionHandler.__init__(self, 'panel')


    def broadcast_received(self, broadcast):
        if broadcast.destination == None and broadcast.prop == "Temperature" and broadcast.source == "Thermostat":
            self.add_command("Ti%.0f" % (broadcast.value * 10))
        elif broadcast.destination == None and broadcast.prop == "Temperature" and broadcast.source == "AgnesOutside":
            self.add_command("To%.0f" % (broadcast.value * 10))
        elif broadcast.destination == None and broadcast.prop == "Humidity" and broadcast.source == "Thermostat":
            self.add_command("Hm%.0f" % (broadcast.value * 10))
        elif broadcast.destination == None and broadcast.prop == "On" and broadcast.source == "Thermostat":
            self.add_command("To%d" % broadcast.value)
        elif broadcast.destination == None and broadcast.prop == "Target" and broadcast.source == "Thermostat":
            self.add_command("Tt%.0f" % (broadcast.value * 10))
