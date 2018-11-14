#!/usr/bin/env python
import time
from samplebase import SampleBase
from PIL import Image, ImageDraw, ImageFont


class ImageScroller(SampleBase):
    def __init__(self, *args, **kwargs):
        super(ImageScroller, self).__init__(*args, **kwargs)

    def run(self):
        text = "Thank you!!!"
        font = ImageFont.truetype('test/test.ttf', 16)
        self.image = Image.new('RGB', (len(text) * 14 + self.matrix.width, self.matrix.height), color = (0, 0, 0))
        draw = ImageDraw.Draw(self.image)
        draw.text((0, 0), text, font=font, fill=(255, 255, 255))

        double_buffer = self.matrix.CreateFrameCanvas()
        img_width, img_height = self.image.size

        # let's scroll
        xpos = 0
        while True:
            xpos += 1
            if (xpos > img_width):
                xpos = 0

            double_buffer.SetImage(self.image, -xpos)
            double_buffer.SetImage(self.image, -xpos + img_width)

            double_buffer = self.matrix.SwapOnVSync(double_buffer)
            time.sleep(0.03)

# Main function
# e.g. call with
#  sudo ./image-scroller.py --chain=4
# if you have a chain of four
if __name__ == "__main__":
    image_scroller = ImageScroller()
    if (not image_scroller.process()):
        image_scroller.print_help()
