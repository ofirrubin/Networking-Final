class DatabaseConnection:
    def __init__(self, **kwargs):
        self.chats = {}
        self.users = {}

    def remove_user(self, username):
        if username in self.users.keys():
            del self.users[username]
        if username in self.chats.keys():
            del self.chats[username]

    def add_message(self, src, dest, msg):
        if src in self.users and dest in self.users:
            if dest not in self.chats:
                self.chats[dest] = [(src, msg)]
            else:
                self.chats[dest].append((src, msg))
            return True
        return False

    def remove_msg(self, user, src_msg: tuple):
        try:
            if user in self.chats:
                self.chats[user].remove(src_msg)
        except ValueError:
            pass

    def get_file(self, filename):
        return b""

    def remove_file(self, filename):
        return b""

    def add_file(self, filename):
        return b""