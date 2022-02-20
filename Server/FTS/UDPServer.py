import socket
from threading import Thread
from time import sleep


class UDPServer:
    DAEMON = True

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
        try:
            self.thread = Thread(target=self.__background_worker, daemon=self.DAEMON).start()
        except KeyboardInterrupt:
            pass

    def stop(self):
        self.exit = True
        sleep(1)
        try:
            if self.thread is not None:
                self.thread.kill()
        except KeyboardInterrupt:
            pass

    def __background_worker(self):
        # UDP is connection-less, the only reason I use threading for client handler is so
        # I can handle others - receives from other clients too at the background.
        try:
            while self.exit is False:
                data, addr = self.sock.recvfrom(self.req_len)
                print("Sending to: ", self.clh, " the following: ", (data, addr))
                Thread(target=self.clh, args=(data, addr), daemon=self.DAEMON).start()
        except KeyboardInterrupt:
            pass
