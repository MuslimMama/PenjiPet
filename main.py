from machine import Pin, I2C, PWM
import sh1106
import framebuf
import time
import penjipal

def init():
    pal = penjipal.penjiPal(26) #sets health points to 20, kitty will die in 26/2 or 13 seconds after holding button down
    init_life = pal.get_life()  # Starting HP for scaling
    life_bar = 128  # Full width of display
    return pal, init_life, life_bar

pal, init_life, life_bar = init()

def blinker(kitty, kittycough, kittycough2, life_bar):
    result = False
    oled.hline(0, 0, life_bar, 1)
    oled.hline(0, 1, life_bar, 1)
    oled.hline(0, 2, life_bar, 1)
    counter = 0
    # Placeholder text (optional: update with game info later)
    oled.text("boof", 0, 6)
    oled.text("bar", 0, 14)

    oled.show()
    while button.value() == 0:  # Button is pressed (active low)
        counter += 1  # Toggle animation frame
        pal.update_life()  # Reduce HP
        life = pal.get_life()
        # Update life bar proportionally
        life_bar = int(128 * (pal.get_life() / init_life))
        
        # Update life bar on screen
        oled.hline(0, 0, life_bar, 1)
        oled.hline(0, 1, life_bar, 1)
        oled.hline(0, 2, life_bar, 1)
        oled.text("boof", 0, 6)
        oled.text("bar", 0, 14)
        oled.show()
        
        # Alternate cough animation frames
        if counter % 2 == 0:
            oled.blit(kittycough, 0, 0)
            time.sleep(0.5)
        else:
            oled.blit(kittycough2, 0, 0)
            time.sleep(0.5)
        
        if life_bar == 0:
            result = True
    return result
pal, init_life, life_bar = init()
### end of functions

# Setup I2C for OLED display (SH1106)
i2c = I2C(0, scl=Pin(17), sda=Pin(16), freq=800_000)
volts = machine.Pin(0)
volts_pwm = PWM(volts)
volts_pwm.freq(1000)
volts_pwm.duty_u16(65335)

# Initialize SH1106 OLED display (128x64), address 0x3C
oled = sh1106.SH1106_I2C(128, 64, i2c, res=Pin(2), addr=0x3C, delay=100)

# Setup button input on GPIO 18 with internal pull-up resistor
button = Pin(18, Pin.IN, Pin.PULL_UP)

# Load sprites into framebuffers
kitty = framebuf.FrameBuffer(pal.get_cat(), 128, 64, framebuf.MONO_HLSB)
kittycough = framebuf.FrameBuffer(pal.get_cough(), 128, 64, framebuf.MONO_HLSB)
kittycough2 = framebuf.FrameBuffer(pal.get_cough2(), 128, 64, framebuf.MONO_HLSB)

# Clear OLED display and initialize counters
oled.fill(0)
counter = 0

# Main game loop
while True:
    pal, init_life, life_bar = init()
    
    oled.blit(kitty, 0, 0)  # Idle cat sprite
    
    result = blinker(kitty, kittycough, kittycough2, life_bar)
    
    if result == True:
        oled.fill(0)
        oled.text("kitty dead...", 3, 10)
        oled.text("wtf...", 3, 25)
        oled.show()
        time.sleep(4)
