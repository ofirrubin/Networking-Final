import socket
from threading import Thread
from time import sleep


class UDPServer:
    def __init__(self, ip, port, client_handler, request_length):
        self.ip = ip
        self.port = port
        self.clh = client_handler
        self.req_len = request_length
        self.exit = False
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.thread = None

    def start(self):
        self.sock.bind((self.ip, self.port))
        self.thread = Thread(target=self.__background_worker).start()

    def stop(self):
        self.exit = True
        sleep(1)
        self.thread.kill()

    def __background_worker(self):
        # UDP is connection-less, the only reason I use threading for client handler is so
        # I can handle others - receives from other clients too at the background.
        while self.exit is False:
            data, addr = self.sock.recvfrom(self.req_len)
            Thread(target=self.clh, args=(data, addr), daemon=False).start()
