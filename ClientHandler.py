class ClientHandler:
    def __init__(self, server, connection):
        self.server = server  # Contains the database, notifies others on change.
        self.connection = connection
        self.logged_in = False
        self.login()
        while self.logged_in is True:
            # Get next wanted command if any ( client adds command as queue and backend sends them)
            pass
            # Sleep for 100ms

    def login(self):
        # Login, Then chose what is the required action.
        u_p = self.connection.recv()
        pass

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
