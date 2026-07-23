#!/usr/bin/python3

import logging
import time
import datetime

# Dht22 (internal data).
import adafruit_dht
import board

# External data.
import requests
from bs4 import BeautifulSoup

# E-paper.
from lib import epd2in13_V4
from PIL import Image, ImageDraw, ImageFont

# in seconds
REFRESH_RATE = 30
FONT_PATH = "/home/luca/Desktop/thermometer/e-paper/font/MonospaceBold.ttf"

def internal_data(dht):
    t, h = None, None
    try:
        t = dht.temperature
        h = dht.humidity
    except RuntimeError as e:
        logging.error(e)
    except Exception as e:
        logging.error(e)
    return t, h


def external_data():
    try:
        t = ''
        h = ''
        resp = requests.get("http://stazioni2.soluzionimeteo.it/conegliano/index.php", timeout=10)
        soup = BeautifulSoup(resp.text, "html.parser")
        tmp = soup.find(id="ajaxtemp")
        if tmp is not None and tmp.string:
            t = tmp.string.strip().replace('°C', '').replace('°', '').strip()
        hum = soup.find(id="ajaxhumidity")
        if hum is not None and hum.string:
            h = hum.string.strip()
        return t, h
    except Exception as e:
        logging.error(f"External data fetch error: {e}")
    return None, None


def main():
    # init e-paper
    epd = epd2in13_V4.EPD()
    # init dht22
    dht = adafruit_dht.DHT22(board.D21)

    # init epd
    epd.init()
    epd.Clear(0xFF)

    # Define the fonts.
    font15 = ImageFont.truetype(FONT_PATH, 15)
    font24 = ImageFont.truetype(FONT_PATH, 24)

    # create image
    image = Image.new('1', (epd.height, epd.width), 255)
    draw = ImageDraw.Draw(image)
    epd.displayPartBaseImage(epd.getbuffer(image))

    last_ti, last_hi = "--", "--"
    last_te, last_he = "--", "--"

    # start thermometer
    try:
        while True:
            try: 
                ti, hi = internal_data(dht)
                if ti is not None: last_ti = str(ti)
                if hi is not None: last_hi = str(hi)

                te, he = external_data()
                if te is not None: last_te = str(te)
                if he is not None: last_he = str(he)

                # update internal
                text_in = f"Ti: {last_ti} Hi: {last_hi}"
                lu = f"Last update: {time.strftime('%H:%M')}"
                draw.rectangle((0, 0, epd.height-2, 40), fill = 255, outline=0, width=2)
                draw.text((4, 2), text_in, font = font24, fill = 0)
                draw.text((4, 22), lu, font = font15, fill = 0)

                # update external
                text_ext = f"Te: {last_te} He: {last_he}"
                draw.rectangle((0, 48, epd.height-2, 88), fill = 255, outline=0, width=2)
                draw.text((4, 50), text_ext, font = font24, fill = 0)
                draw.text((4, 70), lu, font = font15, fill = 0)

                # display time
                tm = f"{time.strftime('%H:%M')}"
                draw.rectangle((0, 95, epd.height-2, 120), fill = 0)
                draw.text((4, 96), tm, font = font24, fill = 255)
                epd.displayPartial(epd.getbuffer(image))

            except Exception as e:
                logging.error(f"Loop error: {e}")

            # wait
            time.sleep(REFRESH_RATE)
    except KeyboardInterrupt:
        logging.info("Stopping thermometer...")
    finally:
        try:
            dht.exit()
        except Exception:
            pass
        try:
            epd.sleep()
        except Exception:
            pass


if __name__ == '__main__':
    logging.basicConfig(format='%(asctime)s %(levelname)s - %(message)s', level=logging.INFO, datefmt='%d-%b-%y %H:%M:%S')
    main()
