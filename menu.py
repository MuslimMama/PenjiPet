import sh1106
from machine import Pin, I2C
import time

selectbutton = Pin(20, Pin.IN, Pin.PULL_UP)
menubutton = Pin(19, Pin.IN, Pin.PULL_UP)
i2c = I2C(0, scl=Pin(10), sda=Pin(9), freq=800_000)
oled = sh1106.SH1106_I2C(128, 64, i2c, res=Pin(2), addr=0x3C, delay=100)



def menu():
    
    checker = False
    
    
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
            if selectbutton.value() == 0 and counter == 3: #  3 is the position where it's at "exit"
                print("leave")
                break
            
            elif selectbutton.value() == 0 and counter == 1:
                oled.fill(0) #fills screen with black to go into temps screen
                oled.text("<", 63, 10) #first instance of the indicator
                while True:
                    oled.text("Low", 10, 10)
                    oled.text("Medium", 10, 20)
                    oled.text("High", 10, 30)
                    oled.text("Exit", 10, 40)
                    oled.show()
                    
                    if selectbutton.value() == 0 and counter == 4: #  3 is the position where it's at "exit"
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
 


