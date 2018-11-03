#!/usr/bin/env python

import os
import time
import threading
import sys
import BaseHTTPServer
from samplebase import SampleBase
from rgbmatrix import graphics
from PIL import Image

HOST_NAME = ''
PORT_NUMBER = 8080

current_image = 'blank'
current_text = ''
current_times = 0

class ImageScroller(SampleBase):
    def __init__(self, *args, **kwargs):
        super(ImageScroller, self).__init__(*args, **kwargs)

    def run(self):
        self.images = {os.path.splitext(file_name)[0]: Image.open(os.path.join('images', file_name)).convert('RGB') 
            for file_name in os.listdir('images') if file_name[0] != '.' and os.path.splitext(file_name)[1] == '.png'}
        self.double_buffer = self.matrix.CreateFrameCanvas()

        self.font = graphics.Font()
        self.font.LoadFont("9x15.bdf")
        self.textColor = graphics.Color(255, 255, 255)
        
        self.thread = threading.Thread(target=self.runLoop)
        self.thread.daemon = True
        self.thread.start()

    def runLoop(self):
        global current_image, current_text
        image_name = ''
        image_text = ''
        is_drawing_image = True
        drawing_count = 0
        width = self.matrix.width

        # let's scroll
        while True:
            if image_name != current_image:
                image_name = current_image
                if image_name in self.images:
                    image = self.images[image_name]
                    img_width, img_height = image.size
                    xpos = -width
                    is_drawing_image = True
                    drawing_count = current_times
            elif image_text != current_text:
                image_text = current_text
                xpos = -width
                is_drawing_image = False
                drawing_count = current_times

            if is_drawing_image:
                self.double_buffer.SetImage(image, -xpos)
            else:
                self.double_buffer.Clear()
                img_width = graphics.DrawText(self.double_buffer, self.font, -xpos, 12, self.textColor, image_text)

            self.double_buffer = self.matrix.SwapOnVSync(self.double_buffer)
            xpos += 1
            if xpos > img_width + width:
                xpos = -width
                if drawing_count > 0:
                    drawing_count -= 1
                    if drawing_count == 0:
                        image_text = current_text = ''
                        image_name = current_image = ''
                        is_drawing_image = False

            time.sleep(0.03)


class MyHandler(BaseHTTPServer.BaseHTTPRequestHandler):
    def do_HEAD(s):
        s.send_response(200)
        s.send_header("Content-type", "text/plain")
        s.end_headers()

    def do_GET(s):
        global current_image, current_text, current_times
        
        """Respond to a GET request."""
        s.send_response(200)
        s.send_header("Content-type", "text/plain")
        s.end_headers()
        # If someone went to "http://something.somewhere.net/foo/bar/",
        # then s.path equals "/foo/bar/".
        components = s.path[1:].split('/')
        if len(components) < 3:
            s.wfile.write("Need 3 components: %s" % s.path)
        else:
            s.wfile.write("You accessed path: %s" % s.path)
            if components[0] == "image":
                current_image = components[1]
            else:
                current_text = components[1]
            try:
                current_times = int(components[2])
            except:
                current_times = 0
            print "setting %d" % current_times


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
