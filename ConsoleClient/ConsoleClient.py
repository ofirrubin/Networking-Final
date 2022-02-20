import os
from threading import Thread

from Client import ClientExceptions
from Client.client import Client
from time import sleep

downloads_path = ''


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
            sleep(1.5)
            self.client.list_files(self._set_list_files)
            sleep(1.5)

    def _set_list_files(self, files_):
        self.list_files = files_

    def __set_online_list(self, status_feedback):
        status, users = status_feedback
        if status is True:
            u = []
            for user in users:
                try:
                    u.append(user.decode())
                except UnicodeDecodeError:
                    pass
            self.online_users = u

    @classmethod
    def on_update(cls, updates, failed):
        for u in updates:
            try:
                src, msg = u.split(b"\n", maxsplit=2)
                print("<", src.decode(), "> says: ", msg.decode())
            except UnicodeDecodeError:
                pass

    def message(self, callback, dest, message):
        return self.client.send_msg(callback, dest, message)

    def download_file(self, filename, callback):
        self.client.download_file(filename, callback)

    def broadcast(self, callback, msg):
        return self.client.broadcast(callback, msg)

    def logout(self):
        return self.client.logout()


def help_():
    print("""Welcome!
    Syntax map:
    Message: msg <username> <message>
    Broadcast: broadcast <message>
    Check Online Users: list users
    Check Available Files To Download: list files
    Exit: exit
    Hit the enter to proceed & update the screen (for incoming messages etc.)
    Any other to print this help""")


def download_callback(ftc, status, resp):
    global downloads_path
    dest = os.path.join(downloads_path, ftc.filename)
    if status is True:
        print("\nThe file", dest, " completed downloading! ->", ftc)
    else:
        with open(dest, 'ab+') as f:
            f.write(resp.data)


def on_msg(verified, feedback, msg):
    if verified is False:
        if Client.USER_NOT_FOUND in feedback:
            print("User not found, failed to send the message")
        else:
            print("Failed to send the message")


def eval_input(client):
    inp = input('>')
    if inp == 'exit':
        client.logout()
        exit(0)
    if inp.startswith('msg '):
        inp = inp[len('msg '):]
        if ' ' not in inp:
            print("Invalid syntax, to message use: <msg> <dest> <msg_txt>")
            return True
        dest, msg = inp.split(' ', maxsplit=1)
        if dest not in client.online_users:
            print("User not online, check online list and try again")
        else:
            client.message(on_msg, dest, msg)
    elif inp.startswith('broadcast '):
        client.broadcast(None, inp[len('broadcast '):])
    elif inp.startswith('list users'):
        print(client.online_users)
    elif inp.startswith('list files'):
        print(client.list_files)
    elif inp.startswith('download '):
        filename = inp[len('download '):]
        print("The file ", filename, ' will be download shortly in Downloads folder.\n'
                                     'Warning, the download will override existing file if exists')
        try:
            dest = os.path.join(downloads_path, filename)
            if os.path.isfile(dest):
                os.remove(dest)
            client.download_file(filename, download_callback)
        except FileNotFoundError:

            print(filename, " was not found!")
    elif inp != '':
        help_()
    return True


def main():
    global downloads_path
    c = Chatter("127.0.0.1", 12333)
    logged_out = True
    while logged_out:
        try:
            c.login(input("Please enter your username: "))
            logged_out = False
        except ClientExceptions.UsernameInUse:
            print("Username is in use, please use another one.")
        except KeyboardInterrupt:
            print("\nGood bye!")
            exit(0)
        except (ConnectionError, ConnectionResetError, ConnectionRefusedError):
            print("Couldn't communicate with the server, make sure it's online and try again.")
            return

    downloads_path = os.path.join('.', 'Downloads')
    if os.path.isdir('Downloads') is False:
        os.mkdir('Downloads')
    try:
        while True:
            eval_input(c)
    except KeyboardInterrupt:
        print("Logging out.. Good bye!")
        c.logout()
        exit(0)


if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        pass
