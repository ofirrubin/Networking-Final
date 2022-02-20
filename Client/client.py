from hashlib import md5, sha256
from datetime import datetime, timedelta
from threading import Thread

from Client import ClientExceptions
from Client.FTC import FTC
from Lib.SecurePipe import SecurePipe, salt


class Client:
    DAEMON = False

    def __init__(self, ip, port):
        self.ip = ip
        self.port = port
        self.connection = None

        self.username = b''

        self.requests = []
        self.get_updates = print
        self.logged_in = False
        self.be = Thread(target=self.__backend, daemon=self.DAEMON)
        self.stop_be = False

    def login(self, username):
        if self.stop_be is True:
            return

        if self.be.is_alive():
            self.stop_be = True
            self.be.join(timeout=0.2)
            self.stop_be = False
            self.be = Thread(target=self.__backend, daemon=self.DAEMON)

        if b"\n" in username:
            raise ValueError("Username nor password can include new line.")
        self.connection = SecurePipe.connect(self.ip, self.port)
        print("Established secure connection..")
        self.connection.send(b"\n".join([b"LOGIN", username, salt()]))
        status = self.connection.recv()
        if status == b'USERNAME_IN_USE':
            raise ClientExceptions.UsernameInUse()
        elif status == b'USER_REGISTERED':
            self.logged_in = True
            self.username = username
            print("Logged in!")
            self.be.start()  # Start backend worker

    def logout(self):
        self.stop_be = True
        self.logged_in = False

    def __backend(self):
        self.stop_be = False
        try:
            while self.stop_be is False:
                self.__call_updates()
                for r in self.requests:
                    if self.stop_be is True:
                        return
                    request_type, callback, request_args = r
                    if request_args is None:
                        request_args = b""
                    self.connection.send(b"\n".join([request_type.encode(), salt(), str(request_args).encode()]))
                    self.__call_req(request_type, callback, request_args, r)
                    self.requests.remove(r)
        except (ConnectionResetError, ConnectionError, BrokenPipeError):
            self.logout()

    def __call_req(self, request_type, callback, request_args, r):
        ans = self.connection.recv()
        if request_type == "GET_USERS":
            Thread(target=self.__get_online_list, args=(ans, callback, r), daemon=self.DAEMON).start()
        elif request_type == "GET_UPDATES":
            self.__get_updates(ans, callback)
        elif request_type == "SEND_MSG":
            Thread(target=self.__sent_msg, args=(ans, request_args, callback), daemon=self.DAEMON).start()
        elif request_type == 'LIST_FILES':
            Thread(target=self.__list_files, args=(ans, callback), daemon=self.DAEMON).start()

    def __call_updates(self):
        self.connection.send("USER_QUESTS".encode() + salt())
        ans = self.connection.recv()
        if ans.startswith(b"True"):
            self.requests.insert(0, ("GET_UPDATES", self.get_updates, None))

    def __get_online_list(self, ans, callback, req):
        if self.stop_be is True or not callable(callback):
            return
        if ans is None or ans == b'':
            callback(None)
            self.requests.append(req)
        else:
            s = ans.rsplit(b"\n", 1)
            if len(s) != 2:
                callback((False, TypeError("Returned invalid type answer format")))
                self.requests.append(req)
            elif md5(s[0]).hexdigest().encode() != s[1]:
                callback((False, ValueError("Couldn't validate recieved information"), s))
                self.requests.append(req)
            else:
                users = [user[2:-1] for user in s[0].split(b", ")]
                users.remove(self.username)
                callback((True, users))

    def __sent_msg(self, feedback, msg, callback):
        if self.stop_be is True or not callable(callback):
            return
        if feedback.startswith(b"TRUE"):
            callback(feedback, msg)
        else:
            m = feedback.split(b"\n")
            if m[0] == b"FALSE":
                print("Message not sent, error: ", m[1])
            else:
                print("Message not sent, recvd this feedback: ", feedback)
            callback(feedback, msg)

    def get_online_list(self, callback):
        if self.stop_be is True or callable(callback) is False:
            return
        if ("GET_USERS", callback, None) not in self.requests:
            self.requests.append(("GET_USERS", callback, None))

    def send_msg(self, callback, dest, msg):
        if dest.encode() == self.username:
            raise ValueError("Oops! you can't send message to your self.")
        if msg == '':
            raise ValueError("Oops! you can't send an empty message!")
        self.requests.insert(0, ("SEND_MSG", callback, dest + "\n" + msg))

    def broadcast(self, callback, msg):
        self.requests.insert(0, ("SEND_MSG", callback, "\n" + msg))

    def __get_updates(self, updates_count_bytes, callback, threshold=5):
        failed = 0
        updates = []
        updates_count = int.from_bytes(updates_count_bytes, "big")
        self.connection.send(updates_count_bytes)
        while updates_count > 0 and failed < threshold:
            update = self.connection.recv()
            h = md5(update).hexdigest().encode()
            self.connection.send(h)
            rh = self.connection.recv()
            if rh == h:
                updates.append(update)
            else:
                failed += 1
            updates_count -= 1
        Thread(target=callback, args=(updates, failed), daemon=self.DAEMON).start()

    def __list_files(self, list_files, callback):
        if self.stop_be is False and callable(callback):
            return callback(list_files.decode().split("\n"))

    def list_files(self, callback):
        if ("LIST_FILES", callback, None) not in self.requests:
            self.requests.append(("LIST_FILES", callback, None))

    def download_file(self, filename, callback, offset=0):
        if not callable(callback):
            raise TypeError("You must include callable callback, cancelling download.")
        if type(offset) is not int or offset < 0:
            raise ValueError("offset must be int >= 0")
        req = FTC((self.ip, self.port + 1), filename, offset)
        req.request(callback)