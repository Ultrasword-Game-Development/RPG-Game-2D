# ----------------------------------- #
# network object handler system

NETWORK_OBJECTS = {}

def register_object(name: str, handle_func, packer_func):
    NETWORK_OBJECTS[name] = [handle_func, packer_func]

def get_object(name):
    return NETWORK_OBJECTS[name]

def get_packer(name):
    return get_object(name)[1]

def get_handler(name):
    return get_object(name)[0]

# ----------------------------------- #
# methods
# HANDLER handles the message sent given a data: dict{}
# PACKER packs a message given an array of data []


