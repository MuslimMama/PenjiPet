from machine import *
import sh1106
import framebuf
import time
import penjipal

pal = penjipal.penjiPal(20)
##make pal with 20 hp



i2c = I2C(0, scl=Pin(1), sda=Pin(0), freq=800000)
##display with higher frequency 
oled = sh1106.SH1106_I2C(128, 64, i2c, res=Pin(2), addr=0x3c, delay = 100)
##initialize display as oled
button = Pin(15, Pin.IN, Pin.PULL_UP)
##button object


kitty = framebuf.FrameBuffer(pal.get_cat(), 128, 64, framebuf.MONO_HLSB)

kittycough = framebuf.FrameBuffer(pal.get_cough(), 128, 64, framebuf.MONO_HLSB)

    
kittycough2 = framebuf.FrameBuffer(pal.get_cough2(), 128, 64, framebuf.MONO_HLSB)
##sprites for cat and cough animations

oled.fill(0)
counter = 0


life_bar = 128
init_life = pal.get_life()
while True:
    oled.hline(0,0,life_bar,1)
    oled.hline(0,1,life_bar,1)
    oled.hline(0,2,life_bar,1)
    ##displays life bar
    oled.text("boof",0,4)
    oled.text("bar",0,10)
    oled.show()
    
    #display boof bar, to be replaced eventually


    if button.value()== 0: #check for button press
        counter += 1 ## counter for cough animation
        pal.update_life() # decrease life when button is pressed
        life_bar = 128 * (pal.get_life() / init_life)
        life_bar = int(life_bar)
        
        if counter%2 == 0:
            
            oled.blit(kittycough, 0, 0)
            
            time.sleep(0.5)
            
        else:
            
            oled.blit(kittycough2, 0, 0)
            time.sleep(0.5)
            
    else:
        
        oled.blit(kitty, 0, 0)
    if pal.get_life() <= 0:
        break
oled.fill(0)
oled.text("kitty dead", 40, 32)
oled.show()
    

