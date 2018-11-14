#!/usr/bin/env python

from PIL import Image, ImageDraw, ImageFont
import sys

text = "88888888888888-"
font = ImageFont.truetype('test.ttf', int(sys.argv[1]))
image = Image.new('RGB', (len(text) * 14, 16), color = (0, 0, 0))
draw = ImageDraw.Draw(image)
draw.text((0, 0), text, font=font, fill=(255, 255, 255))
image.save('test.png')
