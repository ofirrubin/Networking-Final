import os

from Client import ClientExceptions
from Client import Chatter
from Client.QClient import USER_NOT_FOUND


class ConsoleClient(Chatter.Chatter):
    def __init__(self, ip, port, downloads_path=''):
        self.downloads_path = downloads_path
        super().__init__(ip, port,
                         on_update=self.console_on_update,
                         on_users_changed=self.console_users_changed,
                         on_msg=self.console_on_message,
                         on_download=self.console_download_callback)

    @classmethod
    def console_users_changed(cls, logged_in, logged_out):
        if logged_out:
            print(">> Bye to: ", ", ".join(logged_out))
        if logged_in:
            print(">> Say hi to: ", ', '.join(logged_in))

    @classmethod
    def console_on_update(cls, updates, failed):
        for u in updates:
            try:
                src, msg = u.decode().split("\n", maxsplit=2)
                if src == '':
                    print(">>", msg)
                else:
                    print("<", src, "> says: ", msg)
            except UnicodeDecodeError:
                pass

    @classmethod
    def console_download_callback(cls, ftc, status, resp):
        path = os.path.join('.', 'Downloads')
        if os.path.isdir(path) is False:
            os.mkdir(path)
        dest = os.path.join(path, ftc.filename)
        if status is True:
            print("\nThe file", dest, " completed downloading! ->", ftc)
        else:
            with open(dest, 'ab+') as f:
                f.write(resp.data)

    @classmethod
    def console_on_message(cls, verified, feedback, msg):
        if verified is False:
            if USER_NOT_FOUND in feedback:
                print("User not found, failed to send the message")
            else:
                print("Failed to send the message: ", msg)

    @staticmethod
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

    def input_login(self):
        logged_out = True
        while logged_out:
            try:
                super().login(input("Please enter your username: "))
                logged_out = False
            except ClientExceptions.UsernameInUse:
                print("Username is in use, please use another one.")
            except KeyboardInterrupt:
                print("\nGood bye!")
                return False
            except (ConnectionError, ConnectionResetError, ConnectionRefusedError):
                print("Couldn't communicate with the server, make sure it's online and try again.")
                return False
        return True

    def eval_input(self):
        inp = input('>')
        if inp == 'exit':
            self.logout()
            exit(0)
        if inp.startswith('msg '):
            inp = inp[len('msg '):]
            if ' ' not in inp:
                print("Invalid syntax, to message use: <msg> <dest> <msg_txt>")
                return True
            dest, msg = inp.split(' ', maxsplit=1)
            if dest not in self.online_users:
                print("User not online, check online list and try again")
            else:
                self.message(dest, msg)
        elif inp.startswith('broadcast '):
            self.broadcast(None, inp[len('broadcast '):])
        elif inp.startswith('list users'):
            print(self.online_users)
        elif inp.startswith('list files'):
            print(self.list_files)
        elif inp.startswith('download '):
            filename = inp[len('download '):]
            print("The file ", filename, ' will be download shortly in Downloads folder.\n'
                                         'Warning, the download will override existing file if exists')
            try:
                dest = os.path.join(self.downloads_path, filename)
                if os.path.isfile(dest):
                    os.remove(dest)
                self.download_file(filename)
            except FileNotFoundError:

                print(filename, " was not found!")
        elif inp != '':
            self.help_()
        return True

    def start(self, downloads_path=''):
        self.downloads_path = downloads_path
        if self.input_login() is False:
            exit(0)
        try:
            while True:
                self.eval_input()
        except KeyboardInterrupt:
            print("Logging out.. Good bye!")
            self.logout()
            exit(0)


def main():
    c = ConsoleClient("127.0.0.1", 12000)
    c.start(downloads_path='')


if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        pass
