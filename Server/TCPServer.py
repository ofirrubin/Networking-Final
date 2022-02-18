import socket
import threading


class Server:
    def __init__(self, ip, port):
        self.ip = ip
        self.port = port
        self.sock = socket.socket()
        self.__running = False
        self.on_stop = None

    def start(self, user_handler):
        self.sock.bind((self.ip, self.port))
        self.sock.listen(100)  # How many clients to listen, queue size.
        self.__running = True
        while self.__running is True:
            try:
                data, caddr = self.sock.accept()
                print("Client accepted")
                threading.Thread(target=user_handler, args=(data, caddr), daemon=False).start()
            except KeyboardInterrupt:
                self.stop()

    def stop(self):
        self.__running = False
        if callable(self.on_stop):
            self.on_stop()
