from machine import Pin, I2C
import time
import sh1106

x = "yogurt"
y = "gurt: yo...."
button = Pin(15, Pin.IN, Pin.PULL_UP)
def display(input):
    i2c = I2C(0, scl=Pin(1), sda=Pin(0), freq = 200000)  # Example for Raspberry Pi Pico
    display = sh1106.SH1106_I2C(128, 64, i2c, res=Pin(2), addr=0x3c, delay=100)
    display.text(str(input), 10, 32)
    display.show()


display(x)
i = int(0)

while True:
    if button.value() == 0:
        i += 1
        '''
       if i%2 == 0:
            display(x)
            
        else:
            display(y)
            '''
        
        display(i)
        time.sleep(0.2)
