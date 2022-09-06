import socket
import threading
import sys
import pickle
import os

from . import client
from . import network_obj

# ----------------------------------- #

class Server:
    """Hosts clients"""
    def __init__(self, port = 8081, max_conn = 10):
        self.address = (socket.gethostbyname(socket.gethostname()), port)

        self.link = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

        self.main_thread = None
        self.clients = {}
        self.max_conn = max_conn

        self.data_queue = []
        self.running = True

    def run(self, main_thread):
        # ----------------------------------- #
        # bind server to the connection
        try:
            self.link.bind(self.address)
            self.link.listen(self.max_conn)
            print(f"Server has started at {self.address[0]}:{self.address[1]}")
        except socket.error as e:
            exc_type, exc_obj, exc_tb = sys.exc_info()
            fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
            print(exc_type, fname, exc_tb.tb_lineno, "\n\n")
            # output error
            print(str(e))
        result = network_obj.Connection(self.address[0], self.address[1])
        result.link = self.link
        self.link = result
        # ----------------------------------- #
        # running
        print("Connected!")
        self.running = True
        # ----------------------------------- #
        # setup main thread
        self.main_thread = threading.Thread(target=main_thread, args=(self,), daemon=True)

        # ----------------------------------- # 
        # loop
        while self.running:
            # ----------------------------------- #
            # accept connections
            try:
                conn, addr = self.link.link.accept()
                # create a new thread
                thread = threading.Thread(target=self.handle_client, args=(conn, addr,))
                # add client to database
                self.clients[addr[0]] = {
                    "conn": conn,
                    "active": True,
                    "thread": thread
                }
                print(f"Accepted client from: {addr[0]}")
                # ----------------------------------- #
                # send object back
                thread.start()
            except Exception as e:
                # ----------------------------------- #
                # get error data
                exc_type, exc_obj, exc_tb = sys.exc_info()
                fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
                print(exc_type, fname, exc_tb.tb_lineno, "\n\n", e)
        self.main_thread.kill()

    def send(self, conn, data):
        bytedata = pickle.dumps(data)
        length = len(bytedata)
        first = str(length).encode(client.FORMAT)
        first += b' ' * (client.HEADAER-len(first))
        conn.send(first)
        conn.send(bytedata)

    def recieve(self, conn):
        # ----------------------------------- #
        # recieve data
        length = conn.recv(client.HEADER).decode(client.FORMAT)
        length = int(length)
        rec = conn.recv(length)
        obj = pickle.loads(rec)
        return (length, obj)

    def handle_client(self, conn, addr):
        # ----------------------------------- #
        # send initial data to client

        # ----------------------------------- #
        # handle client
        while self.clients[addr[0]]["active"]:
            # ----------------------------------- #
            # while active -- recieve client data
            try:
                # receive
                rec = self.recieve(conn)
                # debugging
                print(f"[Message] {addr[0]} | {rec[1]}")

                # quitting
                if rec[1] == client.CLOSING_CALL:
                    self.clients[addr[0]]["active"] = False
            except socket.error as e:
                # when there is an error, output it
                exc_type, exc_obj, exc_tb = sys.exc_info()
                fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
                print(exc_type, fname, exc_tb.tb_lineno, "\n\n", e)
                print(str(e))
                # ----------------------------------- #
        self.clients.pop(addr[0])
        conn.close()
        print(f"Closed connection and thread to: {addr[0]}")

    def send_to_all(self, data):
        # ----------------------------------- #
        # sending data to all entities
        for pair in self.clients:
            self.send(self.clients[pair]["conn"], data)

    def close(self):
        self.running = False
        self.link.close()
        print("ended connection")







