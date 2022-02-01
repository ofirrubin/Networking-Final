import re
from datetime import datetime, timedelta
from random import random
from time import sleep
from hashlib import md5


class ClientHandler:
    delta = timedelta(minutes=1)
    commands = {"login": [b"LOGIN", b"TICK"], "online_list": b"GET_USERS"}

    def __init__(self, server, connection):
        self.server = server  # Contains the database, notifies others on change.
        self.connection = connection
        self.username = None
        self.logged_in = datetime.fromisocalendar(1990, 1, 1)  # Put some old date as last login

    def handle(self):
        self.login()  # Login also handles online updates & registering user.
        try:
            while datetime.now() - self.logged_in < ClientHandler.delta:  # Half of second of inactivity = offline
                # Get next wanted command if any (client adds command as queue and backend sends them)
                command = self.connection.recv()
                if any(command.startswith(c) for c in self.commands["login"]):
                    self.login(command)
                if command.startswith(self.commands["online_list"]):
                    self.get_online_list()
                sleep(0.1)
        except (ConnectionResetError, BrokenPipeError):
            pass
        # Close connection
        self.connection.close()
        print("Closed connection to client")

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
        credentials = credentials.split(b"\n")
        if not(len(credentials) == 3 and credentials[0] == b'LOGIN' or
               len(credentials) == 4 and credentials[0] == b"TICK"):
            # Invalid input.
            return
        status = credentials[0]
        if status == b'LOGIN':
            username, h_password = credentials[1:]  # password is hashed
            if username in self.server.db.users:
                # Already taken
                if datetime.now() - self.server.db.users[username]["last_seen"] > ClientHandler.delta:
                    del self.server.db.users[username]
                else:
                    self.connection.send(b"USERNAME_IN_USE")
                    return
            if re.match(b"^[a-zA-Z0-9]*$", h_password) is False:
                # Invalid password
                self.connection.send(b"INVALID_CREDENTIAL")
                return
            # Register user
            self.username = username
            self.logged_in = datetime.now()
            self.server.db.users[username] = {"cred": h_password, "last_seen": self.logged_in}
            self.connection.send(b"USER_REGISTERED")
        elif status == b'TICK':  # Tick last seen
            self.tick(credentials[1:])

    def tick(self, credentials):
        # Updates login time
        username, password, rand = credentials
        # Check if user exists
        if username not in self.server.db.users:
            return
        # Check for password correctness
        if self.server.db.users[username]["cred"] != password:
            return
        # If valid, update the login registry.
        self.logged_in = datetime.now()
        self.server.db.users[username]["last_seen"] = self.logged_in
        stat = b"TRUE" if username in self.server.db.chats and len(self.server.db.chats[username]) > 0 else b"FALSE"
        self.connection.send(stat + str(random()).encode())
        return

    def list_online_users(self):
        now = datetime.now()
        online = []
        for user in list(self.server.db.users):
            if user not in self.server.db.users:
                continue
            if now - self.server.db.users[user]['last_seen'] > self.delta and user != self.username:
                del self.server.db.users[user]
            else:
                online.append(user)
        return online

    def get_online_list(self):
        online = str(self.list_online_users())[1:-1].encode()
        h = md5(online).hexdigest().encode()
        self.connection.send(online + b"\n" + h)

    def dm(self, metadata):
        # Client wants to send message to a specific user.
        # metadata contains the rest of the last message (i.e dest. user)
        pass

    def broadcast(self, msg):
        # Client wants to broadcast all users online in the server.
        pass

    def logout(self):
        # Close is essentially removing the user

        # Remove pending messages, remove online status (Delete user? depends on what ill choose with db)
        self.logged_in = False
        self.connection.close()

    def upload_file(self, filename):
        pass

    def download_file(self, filename):
        pass
