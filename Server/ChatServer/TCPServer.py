import socket
from threading import Thread


class Server:
    DAEMON = True

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
        try:
            Thread(target=self.__background_worker, args=(user_handler,), daemon=self.DAEMON).start()
        except KeyboardInterrupt:
            pass

    def __background_worker(self, user_handler):
        while self.__running is True:
            try:
                data, caddr = self.sock.accept()
                print("Client accepted")
                Thread(target=user_handler, args=(data, caddr), daemon=self.DAEMON).start()
            except (KeyboardInterrupt, OSError):
                self.stop()

    def stopped(self):
        if callable(self.on_stop):
            self.on_stop()

    def stop(self):
        self.__running = False
        try:
            self.sock.shutdown(0)
        except OSError:
            pass
