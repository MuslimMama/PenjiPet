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


def menu():
    if menubutton.value() == 0:
        oled.fill(0) #fills screen with black to go into menu screen
        counter = 0 #used just to keep track of what row we're on
        
        while True:
            # continues to show the options you can choose
            oled.text("Temp", 10, 10)
            oled.text("Games", 10, 20)
            oled.text("Exit", 10, 30)
            oled.show()
            
            #breaks while loop if cursor is next to exit, making us go back to the default kitty
            if button.value() == 0 and counter == 3: #  3 is the position where it's at "exit"
                print("leave")
                break
            
            elif button.value() == 0 and counter == 1:
                counter = 0
                oled.fill(0) #fills screen with black to go into temps screen
                oled.text("<", 63, 10) #first instance of the indicator
                while True:
                    oled.text("Low", 10, 10)
                    oled.text("Medium", 10, 20)
                    oled.text("High", 10, 30)
                    oled.text("Exit", 10, 40)
                    oled.show()
                    
                    if button.value() == 0 and counter == 4: #  3 is the position where it's at "exit"
                        print("leave")
                        oled.fill(0)
                        oled.text("<", 55, 10) # needs a first instance of the indicator
                        break
                    
                    if menubutton.value() == 0:
                        oled.fill_rect(63, 0, 20, 64, 0)
                        counter = counter %4
                        oled.text("<", 63, 10 + (counter * 10)) #position indicator
                        counter += 1
                        print(counter)
                        oled.show()
                        time.sleep(0.15) #debouncing
                        
            if menubutton.value() == 0:
                oled.fill_rect(55, 0, 20, 64, 0)
                
                counter = counter %3 #loops into being either 1, 2, 3 b/c 3 positions available
                oled.text("<", 55, 10 + (counter * 10)) #position indicator
                counter += 1
                print(counter)
                time.sleep(0.15) #debouncing
    return None
 

def blinker(kitty, kittycough, kittycough2, life_bar):
    result = False
    oled.fill_rect(0, 0, life_bar, 3, 1)
    counter = 0
    # Placeholder text (optional: update with game info later)
    oled.text("boof", 0, 6)
    oled.text("bar", 0, 14)

    oled.show()
    # need to add third button, when button1 pressed, goes through while statement and reaches the 0.5s time sleep when exiting menu
    while button.value() == 0:  # Button is pressed (active low)
        counter += 1  # Toggle animation frame
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

# PWM setup, max duty cycle at 2^16 or 655356
volts = machine.Pin(0) # pin zero is on the very top left
volts_pwm = PWM(volts)
volts_pwm.freq(1000)
volts_pwm.duty_u16(65535) #100% duty cycle

# Initialize SH1106 OLED display (128x64), address 0x3C
oled = sh1106.SH1106_I2C(128, 64, i2c, res=Pin(2), addr=0x3C, delay=100)

# Setup button input on GPIO 18 with internal pull-up resistor
button = Pin(18, Pin.IN, Pin.PULL_UP)
menubutton = Pin(19, Pin.IN, Pin.PULL_UP)

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
    
    # if we press the menu button, it loops us in the menu until we back out and break
    menu()
    
    # if u hit a whole ass blinker it get a True result into result and shows the kitty dead screen
    result = blinker(kitty, kittycough, kittycough2, life_bar)

    if result == True:
        oled.fill(0)
        oled.text("kitty dead...", 3, 10)
        oled.text("shibal.", 3, 25)
        oled.show()
        time.sleep(4)

