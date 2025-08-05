from machine import Pin, I2C, PWM
import sh1106
import framebuf
import time
import penjipal
import gc
import menu
import blinker

pal = penjipal.penjiPal(26)
init_life = pal.get_life()
life_bar = 128

# Setup I2C for OLED display (SH1106)
i2c = I2C(0, scl=Pin(17), sda=Pin(16), freq=800_000)

# PWM setup, max duty cycle at 2^16 or 655356
volts = machine.Pin(0) # pin zero is on the very top left
volts_pwm = PWM(volts)
volts_pwm.freq(1000)
volts_pwm.duty_u16(65535) #100% duty cycle

# Initialize SH1106 OLED display (128x64), address 0x3C
oled = sh1106.SH1106_I2C(128, 64, i2c, res=Pin(2), addr=0x3C, delay=100)

# Setup button input on GPIO 18 with internal pull-up resistor
penbutton = Pin(18, Pin.IN, Pin.PULL_UP)
menubutton = Pin(19, Pin.IN, Pin.PULL_UP)
selectbutton = Pin(20, Pin.IN, Pin.PULL_UP)

# Load sprites into framebuffers
kitty = pal.get_cat_fb()
kittycough = pal.get_cough_fb()
kittycough2 = pal.get_cough2_fb()

# Clear OLED display and initialize counters
oled.fill(0)
counter = 0

# Main game loop
while True:
   
    # if we press the menu button, it loops us in the menu until we back out and break
    menu.menu()
    
    gc.collect()
    
    # if u hit a whole ass blinker it get a True result into result and shows the kitty dead screen
    result = blinker.blinker(kitty, kittycough, kittycough2, life_bar)

    if result == True:
        oled.fill(0)
        oled.text("kitty dead...", 3, 10)
        oled.text("shibal.", 3, 25)
        oled.show()
        time.sleep(4)

