from sys import argv
from os import mkdir, remove, rename, getcwd
from os.path import isdir, isfile, join, abspath
from argparse import ArgumentParser, ArgumentTypeError, ArgumentError

from Client.QClient import ClientExceptions
from Client.Chatter import Chatter


import eel

client = None
program_args = []
last_updated_files = []
path = '.'


@eel.expose
def login(ip, port, username):
    global client
    check_connection(False)
    if client is not None:
        return
    try:
        if any([int(x) > 255 for x in ip.split(".")]):
            raise ValueError("Invalid Value for IP")
    except ValueError:  # Catches int convert error, split error and unwanted value error(raised by me)
        return eel.setInvalidIP()
    try:
        port = int(port)
        if port > 65535 or port < 1200:
            raise ValueError("Invalid value for port")
    except ValueError:
        return eel.setInvalidPort()

    try:
        global program_args
        client = Chatter(ip, port, *program_args)
        client.login(username)
    except ValueError:  # either IP or port is incorrect
        eel.setInvalidIP()
        return eel.setInvalidPort()
    except ClientExceptions.UsernameInUse:
        return eel.setUserNameInUse()
    eel.setChatView()


@eel.expose
def logout():
    global client
    if client is not None:
        client.logout()
        # It might take a moment for the client to shutdown at the background. Setting it to None allows us to continue
        client = None
    eel.clearDrop("FilesList")
    eel.setLoginView()
    eel.sleep(1)


@eel.expose
def request_download(filename):
    global client
    if client is None or client.logged_in is False:
        return eel.setLoginView()
    if filename not in client.list_files:
        return eel.alertUser("The files list has updated. Please check again")
    fname = join(get_filepath(), filename)
    if isfile(fname):
        remove(fname)
    client.download_file(filename)


@eel.expose
def send_msg(send_to, msg):
    global client
    if client is None or client.logged_in is False:
        eel.setLoginView()
        return False
    if "\n" in send_to:
        return False
    if send_to == '':
        client.broadcast(msg)
    else:
        client.message(send_to, msg)
    return True


def on_login():
    eel.setChatView()
    update_users()
    global last_updated_files
    last_updated_files = []
    update_downloads()


@eel.expose
def check_connection(display_msg=True):
    global client
    if client is not None:
        if client.logged_in:
            on_login()
            if display_msg is True:
                eel.alertUser("You're already logged in as " + client.username.decode())
        else:
            client = None


@eel.expose
def update_users():
    global client
    if client is None or client.logged_in is False:
        return
    for user in client.online_users:
        eel.addToDrop("usersList", user)


def on_update(updates, failed):
    for update in updates:
        try:
            src, msg = update.decode().split("\n", maxsplit=2)
            if src.startswith("-"):
                eel.onBroadcastRcv(src.replace('-', '', 1), msg)
            else:
                eel.onMsgRcv(src.replace('+', '', 1), msg)
        except UnicodeDecodeError:  # failed to decode message
            pass


def on_msg(verified, feedback, msg):
    if verified:
        username, msg = msg.split("\n", maxsplit=1)
        eel.onMsgSent(username, msg)
    else:
        eel.alertUser("Error sending your message: " + msg)
        # Since using the UI I can just use the stdout for debugging
        print("Error sending message, ", msg, " feedback: ", feedback)


def on_broadcast(verified, feedback, msg):
    if verified:
        eel.onBroadcastSent(msg.replace("\n", "", 1))
    else:
        eel.alertUser("Error sending your message: " + msg)
        print("Error sending message, ", msg, " feedback: ", feedback)


def on_users_changed(logged_in, logged_out):
    for user in logged_in:
        if eel.containsInDrop("usersList", user)() is False:
            eel.addToDrop("usersList", user)  # Add the user to the users list
            eel.systemMessage('Say hi to ' + user)  # Show message to user
    for user in logged_out:
        eel.removeFromDrop("usersList", user)  # Remove user from users list
        eel.systemMessage('Good bye ' + user)  # Show message to user


@eel.expose
def update_downloads():
    global last_updated_files
    if client is None or client.logged_in is False:  # Check valid call state
        eel.setLoginView()
    elif last_updated_files == client.list_files:  # No update available
        return
    else:
        # For every file not in the drop, add it.
        # To prevent duplicates if any bug, checking them by the actual value in the UI,
        # not based on the script knowledge.
        for f in client.list_files:
            if eel.containsInDrop("FilesList", f)() is False:
                eel.addToDrop("FilesList", f)
        # Remove files no longer available
        to_remove = [f for f in last_updated_files if f not in client.list_files]
        for f in to_remove:
            eel.removeFromDrop("FilesList", f)  # This will remove the username only if it finds it.
        last_updated_files = client.list_files


def get_filepath():
    global path
    return join(path, "Downloads")


def on_download(filename, valid, offset, length, resp):  # Same as console client
    path = get_filepath()
    if isdir(path) is False:
        mkdir(path)
    dest = join(path, filename)
    tmp = dest + '.download'
    if valid is True and length == 0:
        rename(tmp, dest)
        eel.alertUser("File downloaded sucessfully!")
    else:
        with open(tmp, 'ab+') as f:
            f.write(resp.data)


def close_window():
    eel.closeWindow()


def main(settings):
    web_ops = ['chrome', 'default', 'chrome-app', 'electron']
    try:
        parser = ArgumentParser('Graphical Client Chat Application')
        parser.add_argument('-mode', metavar='w', default='default',
                            help='Choose which "engine" to run the program on: available options: ' + " ,".join(web_ops))
        parser.add_argument('-dir', metavar='d', default=".",
                            help='Choose a path in which Downloads folder will be created &'
                                 ' Files will be saved.')
        settings = parser.parse_args(settings)
    except (ArgumentError, ArgumentTypeError):
        print("Unable to parse your arguments. try again or use help to see syntax")
        return
    if settings.mode not in web_ops:
        settings.mode = 'default'
    if isdir(settings.dir) is False:
        settings.dir = '.'
    global program_args
    global path
    program_args = [on_update, on_users_changed, on_msg, on_broadcast, on_download, update_downloads]
    path = settings.dir
    p = join(abspath(getcwd()), "ClientGUI", "Web")
    eel.init(p)
    eel.start("main.html", block=False, mode=settings.mode, port=0)
    while True:
        eel.sleep(0.01)
        

if __name__ == '__main__':
    try:
        main(argv[1:])
    except (KeyboardInterrupt, KeyboardInterrupt):
        close_window()
