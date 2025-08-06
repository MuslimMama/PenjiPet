import machine
import time
import init
import config_settings


i2c, penbutton, menubutton, selectbutton, oled, pal = init.init()


config = config_settings.load_settings()

#pwm initialization
volts = machine.Pin(0) #assign to pin zero
volts_pwm = PWM(volts)
volts_pwm.freq(1000)

if config is None:
    config = {"current_temp": "med"}

              
temp_levels = {
    "low": int(2**16 * 0.6),
    "med": int(2**16 * 0.75),
    "high": int(2**16 * 0.9)
    }

temp = temp_levels[config["current_temp"]]

#pwm initialization
volts = machine.Pin(0) #assign to pin zero
volts_pwm = PWM(volts)
volts_pwm.freq(1000)
volts_pwm.duty_u16(temp)

def menu():
    
    if menubutton.value() == 0:
        oled.fill(0) #fills screen with black to go into menu screen
        counter = 0 #used just to keep track of what row we're on
        
        while True:
            # continues to show the options you can choose
            print("main menu")
            oled.text("Temp", 10, 10)
            oled.text("Games", 10, 20)
            oled.text("Exit", 10, 30)
            oled.show()
# Main menu            
            #breaks while loop if cursor is next to exit, making us go back to the default kitty
            if selectbutton.value() == 0 and counter == 3: #  3 is the position where it's at "exit"
                print("leave")
                break
            
            elif selectbutton.value() == 0 and counter == 1:
                oled.fill(0) #fills screen with black to go into temps screen
                oled.text("<", 63, 10) #first instance of the indicator
                time.sleep(0.2)
                
                while True:
                    
                    print("temp menu")
                    oled.text("Low", 10, 10)
                    oled.text("Medium", 10, 20)
                    oled.text("High", 10, 30)
                    oled.text("Exit", 10, 40)
                    oled.show()
# Temp menu
                    
                    if selectbutton.value() == 0 and counter == 1: #low setting
                        config["current_temp"] = "low"
                        config_settings.update_settings(config)
                        temp = temp_levels["low"]
                        volts_pwm.duty_u16(temp)
                        oled.fill(0)
                        oled.text("<", 55, 10)
                        time.sleep(0.2)
                        break
                    
                    elif selectbutton.value() == 0 and counter == 2: # medium setting
                        config["current_temp"] = "med"
                        config_settings.update_settings(config)
                        temp = temp_levels["med"]
                        volts_pwm.duty_u16(temp)
                        oled.fill(0)
                        oled.text("<", 55, 10)
                        time.sleep(0.2)
                        break
                    
                    elif selectbutton.value() == 0 and counter == 3: # high setting
                        config["current_temp"] = "high"
                        config_settings.update_settings(config)
                        temp = temp_levels["high"]
                        volts_pwm.duty_u16(temp)
                        oled.fill(0)
                        oled.text("<", 55, 10)
                        time.sleep(0.2)
                        break
                    
                    elif selectbutton.value() == 0 and counter == 4: #  3 is the position where it's at "exit"
                        print("leave")
                        oled.fill(0)
                        oled.text("<", 55, 10) # needs a first instance of the indicator
                        time.sleep(0.2)
                        break
                    
                        
                        
                    if menubutton.value() == 0:
                        oled.fill_rect(63, 0, 20, 64, 0)
                        counter = counter %4
                        oled.text("<", 63, 10 + (counter * 10)) #position indicator
                        counter += 1
                        print(counter)
                        oled.show()
                        time.sleep(0.2) #debouncing
                        
            if menubutton.value() == 0:
                oled.fill_rect(55, 0, 20, 64, 0)
                
                counter = counter %3 #loops into being either 1, 2, 3 b/c 3 positions available
                oled.text("<", 55, 10 + (counter * 10)) #position indicator
                counter += 1
                print(counter)
                time.sleep(0.2) #debouncing
    return None
