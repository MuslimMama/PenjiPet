from machine import Pin, I2C, PWM
import time
import penjipal
import sh1106


def init():
    # Setup I2C for OLED display (SH1106)
    i2c = I2C(0, scl=Pin(5), sda=Pin(4), freq=800_000)

    # Setup button input with internal pull-up resistor
    penbutton = Pin(6, Pin.IN, Pin.PULL_UP)
    menubutton = Pin(7, Pin.IN, Pin.PULL_UP)
    selectbutton = Pin(8, Pin.IN, Pin.PULL_UP)

    # Initialize SH1106 OLED display (128x64), address 0x3C
    oled = sh1106.SH1106_I2C(128, 64, i2c, res=Pin(2), addr=0x3C, delay=100)

    pal = penjipal.penjiPal(26)

    return i2c, penbutton, menubutton, selectbutton, oled, pal
