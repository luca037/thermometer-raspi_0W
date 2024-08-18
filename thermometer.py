#!/usr/bin/python3

from rpi_lcd import LCD
import adafruit_dht
import board
import time
import datetime
import requests
from bs4 import BeautifulSoup
import logging

# in seconds
REFRESH_RATE = 30


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
        soup = BeautifulSoup(requests.get("http://stazioni2.soluzionimeteo.it/conegliano/index.php").text, "html.parser")
        tmp = soup.find(id="ajaxtemp")
        if tmp is not None:
            t = tmp.string.strip()
        tmp = soup.find(id="ajaxhumidity")
        if tmp is not None:
            h = tmp.string.strip()
        return t[:-2], h
    except requests.exceptions.ConnectionError as e:
        logging.error(e)
    except  NewConnectionError as e:
        logging.error(e)
    return None, None


def print_current_time():
    now = datetime.datetime.now()
    return now.strftime("%H:%M")


def clear_line(lcd, n):
    lcd.text(' ' * 8, n)


def main():
    # init lcd
    lcd = LCD(width=16, rows=2)
    # init dht22
    dht = adafruit_dht.DHT22(board.D21)

    lcd.text("Welcome back!", 1)
    time.sleep(3)
    lcd.clear()

    # start thermometer
    while True:
        try: 
            #print("INFO - Reading internal data.")
            ti, hi = internal_data(dht)

            #print("INFO - Reading external data.")
            te, he = external_data()

            # update internal
            if ti is not None and hi is not None:
                clear_line(lcd, 1)
                lcd.text(f"Ti:{ti}  Hi:{hi}", 1)

            # update external
            if te is not None and he is not None:
                clear_line(lcd, 2)
                space = 8 - len(te) - len(he)
                lcd.text(f"Te:{te}{' ' * space}He:{he}", 2)

            # wait
            time.sleep(REFRESH_RATE)
        except Exception as e:
            logging.error(e)
            lcd.clear()
            dht.exit()
            break


if __name__ == '__main__':
    logging.basicConfig(format='%(asctime)s %(levelname)s - %(message)s', datefmt='%d-%b-%y %H:%M:%S')
    main()
