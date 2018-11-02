#!/usr/bin/env python

import os
import time
import threading
import sys
import BaseHTTPServer
from samplebase import SampleBase
from PIL import Image

HOST_NAME = ''
PORT_NUMBER = 8080

current_image = 'blank'

class ImageScroller(SampleBase):
    def __init__(self, *args, **kwargs):
        super(ImageScroller, self).__init__(*args, **kwargs)

    def run(self):
        self.images = {os.path.splitext(file_name)[0]: Image.open(os.path.join('images', file_name)).convert('RGB') 
            for file_name in os.listdir('images') if os.path.splitext(file_name)[1] == '.png'}
        self.double_buffer = self.matrix.CreateFrameCanvas()
        
        self.thread = threading.Thread(target=self.runLoop)
        self.thread.daemon = True
        self.thread.start()

    def runLoop(self):
        image_name = ''

        # let's scroll
        while True:
            if image_name != current_image:
                image_name = current_image
                if image_name in self.images:
                    image = self.images[image_name]
                    img_width, img_height = image.size
                    xpos = 0

            self.double_buffer.SetImage(image, -xpos)
            self.double_buffer.SetImage(image, -xpos + img_width)

            self.double_buffer = self.matrix.SwapOnVSync(self.double_buffer)
            xpos += 1
            if (xpos > img_width):
                xpos = 0

            time.sleep(0.03)


class MyHandler(BaseHTTPServer.BaseHTTPRequestHandler):
    def do_HEAD(s):
        s.send_response(200)
        s.send_header("Content-type", "text/plain")
        s.end_headers()

    def do_GET(s):
        global current_image
        
        """Respond to a GET request."""
        s.send_response(200)
        s.send_header("Content-type", "text/plain")
        s.end_headers()
        # If someone went to "http://something.somewhere.net/foo/bar/",
        # then s.path equals "/foo/bar/".
        current_image = s.path[1:]
        s.wfile.write("You accessed path: %s" % s.path)


if __name__ == '__main__':
    image_scroller = ImageScroller()
    if not image_scroller.process():
        image_scroller.print_help()
        sys.exit(1)

    httpd = BaseHTTPServer.HTTPServer((HOST_NAME, PORT_NUMBER), MyHandler)
    print time.asctime(), "Server Starts - %s:%s" % (HOST_NAME, PORT_NUMBER)
    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        pass
    httpd.server_close()
    print time.asctime(), "Server Stops - %s:%s" % (HOST_NAME, PORT_NUMBER)
