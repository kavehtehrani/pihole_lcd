#!/usr/bin/env python3

from PCF8574 import PCF8574_GPIO
from Adafruit_LCD1602 import Adafruit_CharLCD
from time import sleep, strftime
from datetime import datetime
import requests
import json


def get_cpu_temp():  # get CPU temperature and store it into file "/sys/class/thermal/thermal_zone0/temp"
    tmp = open('/sys/class/thermal/thermal_zone0/temp')
    cpu_temp = float(tmp.read())/1e3
    tmp.close()
    return f"{cpu_temp:.0f}C"


def loop():
    mcp.output(3, 1)  # turn on LCD backlight
    lcd.begin(16, 2)  # set number of LCD lines and columns
    while (True):
        # lcd.clear()
        lcd.setCursor(0, 0)  # set cursor position
        j_pihole = get_pihole_data()
        lcd.message(f"#{j_pihole['unique_clients']} | {j_pihole['ads_percentage_today']:.0f}% |" \
                    f" {j_pihole['ads_blocked_today']} \n" \
                    f" {datetime.now().strftime('%H:%M')} | {get_cpu_temp()} ")
        sleep(5)


def destroy():
    lcd.clear()


def get_pihole_data():
    response = requests.get('http://127.0.0.1/admin/api.php')
    # response = requests.get('http://pi.hole/admin/api.php')
    parsed_json = json.loads(response.content)
    return parsed_json


if __name__ == '__main__':
    PCF8574_address = 0x27  # I2C address of the PCF8574 chip.
    PCF8574A_address = 0x3F  # I2C address of the PCF8574A chip.

    try:
        mcp = PCF8574_GPIO(PCF8574_address)
    except Exception:
        try:
            mcp = PCF8574_GPIO(PCF8574A_address)
        except Exception:
            print('I2C Address Error !')
            exit(1)

    # Create LCD, passing in MCP GPIO adapter.
    lcd = Adafruit_CharLCD(pin_rs=0, pin_e=2, pins_db=[4, 5, 6, 7], GPIO=mcp)

    print('Program is starting ... ')
    try:
        loop()
    except KeyboardInterrupt:
        destroy()

    print('Exiting.')
