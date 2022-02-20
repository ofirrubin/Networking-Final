import socket
from time import sleep
from hashlib import md5
from Lib.SecurePipe import salt


class ClientHandler:
    # Allowed commands and their byte format
    commands = {"login": [b"LOGIN", b"REGISTER"],
                "online_list": b"GET_USERS",
                "has_update": b"USER_QUESTS",
                "get_updates": b"GET_UPDATES",
                "message": b"SEND_MSG\n",
                "files_list": b"LIST_FILES"}

    # consts
    TIMEOUT = 60  # Seconds
    USERNAME_IN_USE = b'USERNAME_IN_USE'
    USERNAME_REGISTERED = b'USER_REGISTERED'
    USERNAME_NOT_FOUND = b'USER_NOT_FOUND'
    MSG_ADDED = b'MSG_ADDED'
    INVALID_FORMAT = b'INVALID_FORMAT'
    TRUE = b'TRUE'
    FALSE = b'FALSE'
    DIVIDER = b'\n'
    DIVIDER_DEC = DIVIDER.decode()

    def __init__(self, server,  connection, debug=False):
        self.server = server  # Contains the database, notifies others on change.
        self.connection = connection
        self.username = None
        self.logged_in = False
        self.debug = debug

    def handle(self):
        self.login()  # Login also handles registering user,
        try:
            while self.logged_in is True:
                # Get next wanted command if any (client adds command as queue and backend sends them)
                command = self.connection.recv(ftimeout=self.TIMEOUT)
                if any(command.startswith(c) for c in self.commands["login"]):
                    self.login(command)
                elif command.startswith(self.commands["online_list"]):
                    self.get_online_list()
                elif command.startswith(self.commands["has_update"]):
                    self.has_update()
                elif command.startswith(self.commands["get_updates"]):
                    self.get_updates()
                elif command.startswith(self.commands["message"]):
                    self.message(command[len(self.commands["message"]):])
                elif command.startswith(self.commands["files_list"]):
                    self.list_files()
                else:
                    self.logged_in = False
                sleep(0.2)
        except (ConnectionResetError, BrokenPipeError) as e:
            self.logout()
        # Close connection
        self.logout()
        if self.debug:
            print(self.username, " Logged out, connection closed")

    def login(self, credentials=None):
        # Login, Then chose what is the required action.
        if credentials is None:
            try:
                credentials = self.connection.recv()
            except ConnectionResetError:
                return
        if credentials is None or credentials == b'':
            # Do not update log in status, close the connection.
            return
        try:
            req, username, salt_ = credentials.split(b"\n", maxsplit=3)
        except ValueError:
            return
        if req not in self.commands["login"]:
            return
        if username in self.server.db.users:
            # Already taken
            self.connection.send(self.USERNAME_IN_USE)
            return
        # Register user
        self.username = username
        self.logged_in = True
        self.server.db.users[username] = {"conn_alive": self.logged_in}
        self.connection.send(self.USERNAME_REGISTERED)

    def list_online_users(self):
        return list(self.server.db.users)

    def __has_update(self):
        return True if self.username in self.server.db.chats and len(self.server.db.chats[self.username]) > 0 else False

    def has_update(self):
        self.connection.send(str(self.__has_update()).upper().encode() + salt())

    def get_updates(self):
        if self.__has_update() is False:
            updates = []
        else:
            updates = self.server.db.chats[self.username]
        size = int.to_bytes(len(updates), length=8, byteorder="big")
        self.connection.send(size)
        if self.connection.recv() != size:
            return
        for update in updates:
            sender, msg = update
            m = sender + self.DIVIDER + msg
            self.connection.send(m)
            h = md5(m).hexdigest().encode()
            rh = self.connection.recv()
            self.connection.send(h)
            if rh == h:
                self.server.db.remove_msg(self.username, update)

    def get_online_list(self):
        online = str(self.list_online_users())[1:-1].encode()
        h = md5(online).hexdigest().encode()
        self.connection.send(online + b"\n" + h)

    def message(self, metadata):
        # Client wants to send message to a specific user.
        # metadata contains the rest of the last message (i.e dest. user)
        try:
            salt_, dest, msg = metadata.split(b"\n", maxsplit=3)
            if dest == b"":
                if self.debug:
                    print("Broadcast from: ", self.username, "-> ", msg)
                self.broadcast(msg)
            else:
                if msg == b'':
                    raise ValueError("Can't send empty message")
                if self.username == dest:
                    raise ValueError("You can't send message to your self!")
                if self.server.db.add_message(self.username, dest, msg) is True:
                    if self.debug:
                        print("Message from: ", self.username, " to: ", dest, " -> ", msg)
                    status = [self.TRUE, self.MSG_ADDED]
                else:
                    status = [self.FALSE + self.USERNAME_NOT_FOUND]
                status.append(salt())
                self.connection.send(self.DIVIDER.join(status))
        except ValueError:
            self.connection.send(self.DIVIDER.join([self.FALSE, self.INVALID_FORMAT, salt()]))

    def broadcast(self, msg):
        # Client wants to broadcast all users online in the server.
        for user in self.server.db.users:
            if self.username != user:
                self.server.db.add_message(self.username, user, msg)
        self.connection.send(self.TRUE + self.DIVIDER)

    def logout(self):
        # Close is essentially removing the user
        if self.username in self.server.db.users:
            self.server.db.remove_user(self.username)
        # Remove pending messages, remove online status (Delete user? depends on what ill choose with db)
        self.logged_in = False
        try:
            self.connection.close()
        except socket.error:
            pass

    def list_files(self):
        files = self.DIVIDER_DEC.join(self.server.db.list_files()).encode()
        self.connection.send(files)
