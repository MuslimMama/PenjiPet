from machine import Pin, I2C
import sh1106
import framebuf
import time
import penjipal

penbutton = Pin(18, Pin.IN, Pin.PULL_UP)
i2c = I2C(0, scl=Pin(17), sda=Pin(16), freq=800_000)
oled = sh1106.SH1106_I2C(128, 64, i2c, res=Pin(2), addr=0x3C, delay=100)
pal = penjipal.penjiPal(26)

kitty = pal.get_cat_fb()
kittycough = pal.get_cough_fb()
kittycough2 = pal.get_cough2_fb()

def blinker(kitty, kittycough, kittycough2, life_bar):
    #show default kitty, always reset life to 26, set init_life to 26, set default result to false
    oled.blit(kitty, 0, 0)
    pal.set_life(26)
    init_life = pal.get_life()
    result = False # result true after hp goes to zero, meaning the death screen comes up
    sprite = False # toggles between the two frames
    
    #health bar and text
    oled.fill_rect(0, 0, life_bar, 3, 1)
    oled.text("boof", 0, 6)
    oled.text("bar", 0, 14)

    oled.show()
    # need to add third button, when button1 pressed, goes through while statement and reaches the 0.5s time sleep when exiting menu
    while button.value() == 0:  # Button is pressed (active low)
        sprite = not sprite  # Toggle animation frame
        pal.update_life()  # Reduce HP
        life = pal.get_life()
        # Update life bar proportionally
        life_bar = int(128 * (pal.get_life() / init_life))
        
        # Update life bar on screen
        oled.fill_rect(0, 0, life_bar, 3, 1) #solid rectangle from x = 0, y = 0, life bar length, 3 pixels high
        oled.text("boof", 0, 6)
        oled.text("bar", 0, 14)
        oled.show()
        
        # Alternate cough animation frames
        if sprite:
            oled.blit(kittycough, 0, 0)
            time.sleep(0.5)
        else:
            oled.blit(kittycough2, 0, 0)
            time.sleep(0.5)
        
        if life_bar == 0:
            result = True
            
    #reset all values after each press        
    init_life = pal.set_life(26)
    life_bar = 128  # Full width of display
    
    return result
