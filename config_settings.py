import ujson

# where we store settings

settings = "settings.json"

#loading from json
def load_settings():
    try:
        with open(settings,"r") as file:
            return ujson.load(file)
        
    except:
        return None
    
#writing into json
def update_settings(config):
    try:
        with open(settings, "w") as file:
            ujson.dump(config, file)
    except:        
        return None
