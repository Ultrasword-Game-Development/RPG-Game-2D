import socket
import pickle
import sys
import os

from queue import deque

import pygame

from . import network_obj

# ----------------------------------- #
# constants
HEADER = 16
FORMAT = 'utf-8'
MAX_SEND = 2048
MAX_RECEIVE = 2048

CLOSING_CALL = "!CLOSING!"


# ----------------------------------- #
# client
class Client:
    """Connects to servers"""
    def __init__(self, ip: str, port: int = 8081):
        # ----------------------------------- #
        # create internet objects
        self.address = (ip, port)

        # create connection
        self.link = network_obj.Connection(ip, port)
        
        # receive queue
        self.recieved = deque()
    
    def connect(self):
        # ----------------------------------- #
        # connect to the server
        if not self.link.connect():
            pygame.event.post(pygame.event.Event(pygame.QUIT))
    
    # ----------------------------------- #
    # to send data
    def send(self, unpickled_obj: dict):
        # ----------------------------------- #
        # pickle unpiockled object
        bytedata = pickle.dumps(unpickled_obj)
        # size data
        length = len(bytedata)
        first = str(length).encode(FORMAT)
        # send first
        first += b' ' * (HEADER-len(first))
        print(first)
        # send
        self.link.send(first)

        # send object
        self.link.send(bytedata)
    
    def recieve(self):
        # ----------------------------------- #
        # recieve pickled data
        length = int(self.link.recv(HEADER).decode(FORMAT))
        # logging
        print(f"Decoded length: {length}")
        # store in recieved array
        rec = self.link.recv(length)
        # unload with pickle
        obj = pickle.loads(rec)
        print(obj)
        self.recieved.append(obj)
    
    def close(self):
        self.send(CLOSING_CALL)
        self.link.close()
        print("closed connection")
    

