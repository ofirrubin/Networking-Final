from hashlib import md5, sha256
from time import sleep
from datetime import datetime, timedelta
from threading import Thread

from Lib.SecurePipe import SecurePipe, salt
import ClientExceptions


class Client:
    delta = timedelta(seconds=10)

    def __init__(self, ip, port):
        self.ip = ip
        self.port = port
        self.connection = None

        self.username = b''

        self.requests = []
        self.get_updates = print
        self.logged_in = datetime.fromisocalendar(1990, 1, 1)
        self.be = Thread(target=self.__backend)
        self.stop_be = False

    def login(self, username):
        if self.stop_be is True:
            return

        if self.be.is_alive():
            self.stop_be = True
            self.be.join(timeout=0.2)
            self.stop_be = False
            self.be = Thread(target=self.__backend)

        if b"\n" in username:
            raise ValueError("Username nor password can include new line.")
        self.connection = SecurePipe.connect(self.ip, self.port)
        print("Established secure connection, sending login request")
        self.connection.send(b"\n".join([b"LOGIN", username, salt()]))
        status = self.connection.recv()
        print("Recieved login response; ", str(status))
        if status == b'USERNAME_IN_USE':
            raise ClientExceptions.UsernameInUse()
        elif status == b'USER_REGISTERED':
            self.logged_in = True
            self.username = username
            print("Logged in")

            self.be.start()  # Start backend worker

    def __backend(self):
        self.stop_be = False
        while self.stop_be is False:
            self.connection.send("USER_QUESTS".encode() + salt())
            ans = self.connection.recv()
            if ans.startswith(b"True"):
                self.requests.insert(0, ("GET_UPDATES", self.get_updates, None))
            for r in self.requests:
                request = r
                request_type, callback, request_args = r
                if request_args is None:
                    request_args = b""
                self.connection.send(b"\n".join([request_type.encode(), salt(), str(request_args).encode()]))
                # request_type.encode() + "\n" + str(random()).encode() + "\n" + request_args)
                ans = self.connection.recv()
                self.requests.remove(r)
                if request_type == "GET_USERS":
                    Thread(target=self.__get_online_list, args=(ans, callback, request), daemon=False).start()
                elif request_type == "GET_UPDATES":
                    self.__get_updates(ans, callback)
                elif request_type == "SEND_MSG":
                    Thread(target=self.__sent_msg, args=(ans, request_args, callback), daemon=False).start()

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
            print("Message sent: ", msg)
            # callback(feedback, msg)
        else:
            m = feedback.split(b"\n")
            if m[0] == b"FALSE":
                print("Message not sent, error: ", m[1])
            else:
                print("Message not sent, recvd this feedback: ", feedback)
            # callback(feedback, msg)
            # self.requests.insert(0, request)

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
        self.requests.append(("SEND_MSG", callback, dest + "\n" + msg))

    def broadcast(self, callback, msg):
        self.requests.append(("SEND_MSG", callback, "\n" + msg))

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
        Thread(target=callback, args=(updates, failed)).start()

    def __list_files(self, list_files, callback):
        if self.stop_be is False and callable(callback):
            return callback(list_files.decode().split("\n"))

    def list_files(self, callback):
        if ("LIST_FILES", callback, None) not in self.requests:
            self.requests.append(("LIST_FILES", callback, None))

    def send_file(self, filename):
        pass

    def recv_file(self, filename):
        pass


class Chatter:
    def __init__(self, ip, port):
        self.ip = ip
        self.port = port
        self.client = Client(self.ip, self.port)
        self.client.get_updates = self.on_update
        self.online_users = []
        self.list_files = []
        self.chats = {}

    def login(self, username):
        self.online_users = []
        self.list_files = []
        self.chats = {}
        self.client.login(username.encode())
        Thread(target=self.update_online_list, daemon=False).start()

    def update_online_list(self):
        while self.client.logged_in:
            self.client.get_online_list(self.__set_online_list)
            sleep(1)
            self.client.list_files(self._set_list_files)

    def _set_list_files(self, files_):
        self.list_files = files_

    def __set_online_list(self, status_feedback):
        status, users = status_feedback
        if status is True:
            self.online_users = users

    def on_update(self, updates, failed):
        for u in updates:
            src, msg = u.split(b"\n", maxsplit=2)
            print("<", src.decode(), "> says: ", msg.decode())

    def message(self, callback, dest, message):
        return self.client.send_msg(callback, dest, message)

    def broadcast(self, callback, msg):
        return self.client.broadcast(callback, msg)


def help():
    print("""Welcome!
    Syntax map:
    Message: msg <username> <message>
    Broadcast: broadcast <message>
    Check Online Users: list users
    Check Available Files To Download: list files
    Exit: exit
    
    Any other to print this help""")


def eval_commands(client, inp):
    if inp == 'exit':
        return False
    if inp.startswith('msg '):
        dest, msg = inp[len('msg '):].split(' ', maxsplit=1)
        client.message(None, dest, msg)
    elif inp.startswith('broadcast '):
        client.broadcast(None, inp[len('broadcast '):])
    elif inp.startswith('list users'):
        print(client.online_users)
    elif inp.startswith('list files'):
        print(client.list_files)
    else:
        help()
    return True


def main():
    c = Chatter("127.0.0.1", 54321)
    logged_out = True
    while logged_out:
        try:
            c.login(input("Please enter your username: "))
            logged_out = False
        except ClientExceptions.UsernameInUse:
            print("Username is in use, please use another one.")

    while eval_commands(c, input()):
        continue


if __name__ == '__main__':
    main()
