from hashlib import md5
from time import sleep
from datetime import datetime, timedelta
from threading import Thread
from random import random

from Server import SecurePipe
import ClientExceptions


class Client:
    delta = timedelta(seconds=10)

    def __init__(self, ip, port):
        self.ip = ip
        self.port = port
        self.connection = None

        self.username = b''
        self.credentials = b''

        self.requests = []
        self.logged_in = datetime.fromisocalendar(1990, 1, 1)
        self.be = Thread(target=self.backend)
        self.stop_be = False

    def login(self, username, password):
        if self.stop_be is True:
            return

        if self.be.is_alive():
            self.stop_be = True
            self.be.join(timeout=0.2)
            self.stop_be = False
            self.be = Thread(target=self.backend)

        if "\n" in username or "\n" in password:
            raise ValueError("Username nor password can include new line.")
        self.connection = SecurePipe.connect(self.ip, self.port)
        dt = datetime.now()
        self.connection.send(b"LOGIN\n" + username.encode() + b"\n" + password.encode())
        status = self.connection.recv()
        if status == b'USERNAME_IN_USE':
            raise ClientExceptions.UsernameInUse()
        elif status == b"INVALID_CREDENTIAL":
            raise ClientExceptions.InvalidCredentials()
        elif status == b'USER_REGISTERED':
            self.logged_in = dt
            self.username = username.encode()
            self.credentials = username.encode() + b"\n" + password.encode()
            print("Logged in")

            self.be.start()  # Start backend worker

    def __tick(self):
        now = datetime.now()
        if now - self.logged_in > self.delta or self.stop_be is True:
            print("IM OUT")
            self.stop_be = True
            return
        self.connection.send(b"TICK\n" + self.credentials + b"\n" + str(random()).encode())
        if self.connection.recv().startswith(b"TRUE"):
            self.requests.append(("UPDATES", ()))
        self.logged_in = now

    def backend(self):
        self.stop_be = False
        while self.stop_be is False:
            for r in self.requests:
                self.__ticker()
                request_type, request_args = r
                self.connection.send(request_type.encode() + str(random()).encode())
                ans = self.connection.recv()
                if request_type == "GET_USERS":
                    Thread(target=self.__get_online_list, args=(ans, request_args[0]), daemon=False).start()
                    self.requests.remove(r)
            self.__ticker()

    def __ticker(self):
        if self.stop_be is False:
            self.__tick()
            print("TICKED")
            sleep(0.1)

    def __get_online_list(self, ans, callback):
        if self.stop_be is True or callback is None:
            return
        if ans is None or ans == b'':
            callback(None)
        else:

            s = ans.rsplit(b"\n", 1)
            if len(s) != 2:
                callback((False, TypeError("Returned invalid type answer format")))
            elif md5(s[0]).hexdigest().encode() != s[1]:
                callback((False, ValueError("Couldn't validate recieved information"), s))
            else:
                users = [x[2:-1] for x in s[0].split(b", ")]
                users.remove(self.username)
                callback((True, users))

    def get_online_list(self, callback):
        self.requests.append(("GET_USERS", (callback,)))


c = Client("127.0.0.1", 5551)
c.login("username" + "e", "password")
c.get_online_list(print)
