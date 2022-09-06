import socket

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

class Connection:
    def __init__(self, ip: str, port: int = 8081):
        self.link = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.address = (ip, port)

    def connect(self):
        # connect to teh server
        try:
            self.link.connect(self.address)
            print(f"[SOCKET] Connected to {self.address[0]}:{self.address[1]}")
            return True
        except socket.error as e:
            print(f"[SOCKET] Closing connection and closing program due to: {e}")
            return False

    def send(self, bytes):
        self.link.send(bytes)

    def recv(self, length):
        return self.link.recv(length)

    def close(self):
        self.link.close()


# ----------------------------------- #
# methods
# HANDLER handles the message sent given a data: dict{}
# PACKER packs a message given an array of data []


