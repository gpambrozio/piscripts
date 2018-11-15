#!/usr/bin/env python
import time
from samplebase import SampleBase
from PIL import Image, ImageDraw, ImageFont


class ImageScroller(SampleBase):
    def __init__(self, *args, **kwargs):
        super(ImageScroller, self).__init__(*args, **kwargs)

    def run(self):
        double_buffer = self.matrix.CreateFrameCanvas()
        text = ""
        font = ImageFont.truetype('test/test.ttf', 16)
        image = Image.new('RGB', (len(text) * 14 + self.matrix.width, self.matrix.height), color = (0, 0, 0))
        draw = ImageDraw.Draw(image)
        draw.text((0, 0), text, font=font, fill=(255, 255, 255))

        img_width, img_height = image.size

        # let's scroll
        width = self.matrix.width
        xpos = -width
        while True:
            print "%s, %d, %d" % (image, xpos, img_width)
            double_buffer.SetImage(image, -xpos)
            double_buffer = self.matrix.SwapOnVSync(double_buffer)

            xpos += 1
            if (xpos > img_width):
                xpos = -32

            time.sleep(0.03)

# Main function
# e.g. call with
#  sudo ./image-scroller.py --chain=4
# if you have a chain of four
if __name__ == "__main__":
    image_scroller = ImageScroller()
    if (not image_scroller.process()):
        image_scroller.print_help()
