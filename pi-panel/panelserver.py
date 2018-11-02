#!/usr/bin/env python

import time
import threading
import sys
import BaseHTTPServer
from samplebase import SampleBase
from PIL import Image

HOST_NAME = ''
PORT_NUMBER = 8080

class ImageScroller(SampleBase):
    def __init__(self, *args, **kwargs):
        super(ImageScroller, self).__init__(*args, **kwargs)
        self.parser.add_argument("-i", "--image", help="The image to display", default="runtext16.ppm")

    def run(self):
        self.image = Image.open(self.args.image).convert('RGB')
        self.double_buffer = self.matrix.CreateFrameCanvas()

        self.thread = threading.Thread(target=self.runLoop)
        self.thread.daemon = True
        self.thread.start()

    def runLoop(self):
        img_width, img_height = self.image.size

        # let's scroll
        xpos = 0
        while True:
            xpos += 1
            if (xpos > img_width):
                xpos = 0

            self.double_buffer.SetImage(self.image, -xpos)
            self.double_buffer.SetImage(self.image, -xpos + img_width)

            self.double_buffer = self.matrix.SwapOnVSync(self.double_buffer)
            time.sleep(0.03)


class MyHandler(BaseHTTPServer.BaseHTTPRequestHandler):
    def do_HEAD(s):
        s.send_response(200)
        s.send_header("Content-type", "text/plain")
        s.end_headers()

    def do_GET(s):
        """Respond to a GET request."""
        s.send_response(200)
        s.send_header("Content-type", "text/plain")
        s.end_headers()
        # If someone went to "http://something.somewhere.net/foo/bar/",
        # then s.path equals "/foo/bar/".
        s.wfile.write("You accessed path: %s" % s.path)


if __name__ == '__main__':
    image_scroller = ImageScroller()
    if not image_scroller.process():
        image_scroller.print_help()
        sys.exit(1)

    server_class = BaseHTTPServer.HTTPServer
    httpd = server_class((HOST_NAME, PORT_NUMBER), MyHandler)
    print time.asctime(), "Server Starts - %s:%s" % (HOST_NAME, PORT_NUMBER)
    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        pass
    httpd.server_close()
    print time.asctime(), "Server Stops - %s:%s" % (HOST_NAME, PORT_NUMBER)
