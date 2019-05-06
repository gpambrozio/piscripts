#!/usr/bin/env python

import os
import socket
import sys
import threading
import time
import BaseHTTPServer
from rgbmatrix import graphics
from rgbmatrix import RGBMatrix, RGBMatrixOptions
from PIL import Image, ImageDraw, ImageFont, ImageChops

HOST_NAME = ''
PORT_NUMBER = 8080

# Fonts from https://fonts2u.com/font-vendors/the-grandoplex-project.html

current_command = ['text', 'Have a good day!', 1]

def trim(im):
    bg = Image.new(im.mode, im.size, color = (0, 0, 0))
    diff = ImageChops.difference(im, bg)
    bbox = diff.getbbox()
    if bbox:
        return im.crop(bbox)
    return im


class ImageScroller:
    def __init__(self):
        options = RGBMatrixOptions()

        options.rows = 16
        options.cols = 32
        options.chain_length = 1
        options.parallel = 1
        options.pixel_mapper_config = "Rotate:180"

        self.matrix = RGBMatrix(options = options)

    def process(self):
        try:
            # Start loop
            print("Press CTRL-C to stop sample")
            self.run()
        except KeyboardInterrupt:
            print("Exiting\n")
            sys.exit(0)

        return True

    def run(self):
        self.images = {os.path.splitext(file_name)[0]: Image.open(os.path.join('images', file_name)).convert('RGB') 
            for file_name in os.listdir('images') if file_name[0] != '.' and os.path.splitext(file_name)[1] == '.png'}

        self.thread = threading.Thread(target=self.runLoop)
        self.thread.daemon = True
        self.thread.start()

    def runLoop(self):
        global current_command
        
        # font = ImageFont.truetype('fonts/PixelOperator8.ttf', 16)
        font = ImageFont.load_path('fonts/9x15.pil')
        textColor = (255, 255, 255)
        
        double_buffer = self.matrix.CreateFrameCanvas()
        command = ['', '', '']
        drawing_count = 0
        image = None
        img_width = 0
        width = self.matrix.width
        xpos = -width

        # let's scroll
        while True:
            if command != current_command:
                command = current_command
                drawing_count = command[2]
                
                if command[0] == 'image':
                    if command[1] in self.images:
                        image = self.images[command[1]]
                else:
                    text = command[1]
                    image = Image.new('RGB', (len(text) * 14 + width, self.matrix.height), color = (0, 0, 0))
                    draw = ImageDraw.Draw(image)
                    draw.text((0, 0), text, font = font, fill = textColor)
                    image = trim(image)

                img_width, _ = image.size
                xpos = -width

            double_buffer.Clear()
            double_buffer.SetImage(image, -xpos, unsafe = False)
            double_buffer = self.matrix.SwapOnVSync(double_buffer)
            xpos += 1
            if xpos > img_width + width:
                xpos = -width
                if drawing_count > 0:
                    drawing_count -= 1
                    if drawing_count == 0:
                        current_command = ['text', '', 0]

            time.sleep(0.015)


class SocketServer(object):
    def __init__(self, host, port):
        self.host = host
        self.port = port
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.sock.bind((self.host, self.port))
        self.thread = threading.Thread(target=self.listen)
        self.thread.daemon = True
        self.thread.start()


    def listen(self):
        self.sock.listen(5)
        while True:
            client, address = self.sock.accept()
            client.settimeout(60)
            threading.Thread(target=self.listenToClient, args=(client,address)).start()


    def listenToClient(self, client, address):
        global current_command

        size = 1024
        while True:
            try:
                data = client.recv(size)
                if data:
                    components = data.strip(" \r\n").split('/')
                    if components[0] == 'ping':
                        client.send("Pong\n")
                    elif len(components) < 3:
                        client.send("Need 3 components: %s\n" % data)
                    else:
                        command = components[:3]
                        try:
                            command[2] = int(command[2])
                        except:
                            command[2] = 0
                        current_command = command
                        client.send("OK\n")
                else:
                    raise error('Client disconnected')
            except:
                client.close()


class HTTPHandler(BaseHTTPServer.BaseHTTPRequestHandler):
    def do_HEAD(s):
        s.send_response(200)
        s.send_header("Content-type", "text/plain")
        s.end_headers()

    def do_GET(s):
        global current_command
        
        """Respond to a GET request."""
        s.send_response(200)
        s.send_header("Content-type", "text/plain")
        s.end_headers()
        
        # If someone went to "http://something.somewhere.net/foo/bar/",
        # then s.path equals "/foo/bar/".
        components = s.path[1:].split('/')
        if components[0] == 'ping':
            s.wfile.write('pong')
        elif len(components) < 3:
            s.wfile.write("Need 3 components: %s" % s.path)
        else:
            command = components[:3]
            try:
                command[2] = int(command[2])
            except:
                command[2] = 0
            current_command = command
            
            s.wfile.write("You accessed path: %s" % s.path)


if __name__ == '__main__':
    socket_server = SocketServer('', 10000)
    image_scroller = ImageScroller()
    if not image_scroller.process():
        image_scroller.print_help()
        sys.exit(1)

    httpd = BaseHTTPServer.HTTPServer((HOST_NAME, PORT_NUMBER), HTTPHandler)
    print time.asctime(), "Server Starts - %s:%s" % (HOST_NAME, PORT_NUMBER)
    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        pass
    httpd.server_close()
    print time.asctime(), "Server Stops - %s:%s" % (HOST_NAME, PORT_NUMBER)
