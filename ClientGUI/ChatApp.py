import os
import eel

from Client import ClientExceptions
from Client import Chatter
from Client.QClient import USER_NOT_FOUND

client = None
known_users = []
last_updated_files = []


class ChatApp(Chatter.Chatter):
    def __init__(self, ip, port, file_chooser_func, on_update_, on_users_changed_,
                 on_msg_, on_broadcast_, list_files_changed, debug=False):
        self.debug = debug
        self.file_chooser = file_chooser_func
        super().__init__(ip, port,
                         on_update=on_update_,
                         on_users_changed=on_users_changed_,
                         on_msg=on_msg_,
                         on_broadcast=on_broadcast_,
                         on_download=self.download_callback)
        self.list_files_changed = list_files_changed

    @classmethod
    def download_callback(cls, filename, valid, offset, length, resp):
        pass


@eel.expose
def login(ip, port, username):
    global client
    if client is not None:
        if client.logged_in:
            eel.setChatView()
        return
    try:
        if any([int(x) > 255 for x in ip.split(".")]):
            raise ValueError("Invalid Value for IP")
    except ValueError:
        eel.setInvalidIP()
        return
    try:
        port = int(port)
        if port > 65000 or port < 1000:
            raise ValueError("Invalid value for port")
    except ValueError:
        eel.setInvalidPort()
        return

    client = ChatApp(ip, port, choose_save_dist, on_update,
                     lists_update, on_msg, on_msg, list_files_changed=set_downloads, debug= True)
    try:
        client.login(username)
    except ValueError:  # either IP or port is incorrect
        eel.setInvalidIP()
        eel.setInvalidPort()
        return
    except ClientExceptions.UsernameInUse:
        eel.setUserNameInUse()
        return
    eel.setChatView()


@eel.expose
def logout():
    global client
    global last_updated_files
    if client is not None:
        client.logout()
        client.shutdown()
    client = None
    eel.setLoginView()
    eel.sleep(1)


def choose_save_dist():
    pass


def on_update(updates, failed):
    pass


def on_msg(verified, feedback, msg):
    pass


def lists_update(logged_in, logged_out):
    global known_users
    for user in logged_in:
        if user not in known_users:
            eel.addUserName(user)
            known_users.append(user)
    for user in logged_out:
        eel.removeUserName(user)
        if user in known_users:
            known_users.remove(user)


def set_downloads():
    global last_updated_files
    if client is None or client.logged_in is False:
        eel.setLoginView()
    else:
        print("Current: ", last_updated_files)
        print("Up to date: ", client.list_files)
        if client.list_files == last_updated_files:
            return
        new_files = [f for f in client.list_files if f not in last_updated_files]
        to_remove = [f for f in last_updated_files if f not in client.list_files]
        print("New files ", new_files)
        print("Old files ", to_remove)
        for f in new_files:
            eel.addFile(f)
        for f in to_remove:
            eel.removeFile(f)
        last_updated_files = client.list_files


def request_download():
    pass


@eel.expose
def send_msg(send_to, msg):
    global client
    print("Sending message to: ", send_to, " saying: ", msg)
    if client is None or client.logged_in is False:
        eel.setLoginView()
        return
    if "\n" in send_to:
        return False
    if send_to == '':
        client.broadcast(msg)
    else:
        client.message(send_to, msg)
    return True


def send_broadcast():
    pass


def main():
    eel.init("Web")
    eel.start("simple.html", block=False)
    client = None
    while True:
        eel.sleep(0.01)


if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        pass
