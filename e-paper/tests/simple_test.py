#!/usr/bin/python
# -*- coding:utf-8 -*-

import logging
from lib import epd2in13_V4
import time
from PIL import Image,ImageDraw,ImageFont
import traceback

logging.basicConfig(level=logging.DEBUG)

FONT_PATH = "./font/Font.ttc"

try:
    
    # Init edp.
    epd = epd2in13_V4.EPD()
    epd.init()
    epd.Clear(0xFF)

    # Define the fonts.
    font15 = ImageFont.truetype(FONT_PATH, 15)
    font24 = ImageFont.truetype(FONT_PATH, 24)
    
    # partial update
    time_image = Image.new('1', (epd.height, epd.width), 255)
    time_draw = ImageDraw.Draw(time_image)
    epd.displayPartBaseImage(epd.getbuffer(time_image))
    num = 0
    while (True):
        time_draw.rectangle((0, 0, 100, 25), fill = 255, outline=0, width=2)
        time_draw.text((0, 0), f"Last update: {time.strftime('%H:%M:%S')}", font = font24, fill = 0)
        epd.displayPartial(epd.getbuffer(time_image))
        num = num + 1
        if(num == 10):
            break
    
    logging.info("Clear...")
    epd.init()
    epd.Clear(0xFF)
    
    logging.info("Goto Sleep...")
    epd.sleep()
        
except IOError as e:
    logging.info(e)
    
except KeyboardInterrupt:    
    logging.info("ctrl + c:")
    epd2in13_V4.epdconfig.module_exit(cleanup=True)
    exit()
