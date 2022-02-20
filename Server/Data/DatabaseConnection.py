import os
from hashlib import md5


class DatabaseConnection:
    def __init__(self, root, **kwargs):
        self.chats = {}  # messages of each client
        self.users = {}  # username hash: is_logged_in, might include other info..
        self.root = root
        self.filter_ = None
        self.files = {}
        self.update_list_files()

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

    def update_list_files(self):
        self.files = {}
        for file in self.__list_files():
            self.files[md5(file.encode()).hexdigest().encode()] = file

    def __list_files(self):
        return self.__filtered_walk(self.filter_) if type(self.filter_) is str else self.__walk()

    def __filtered_walk(self, filter):
        files = []
        for root_, dir_, files_ in os.walk(self.root):
            files += filter(lambda x: x.endswith(filter), files_)
        return files

    def __walk(self):
        return [f for f in os.listdir(self.root) if os.path.isfile(os.path.join(self.root, f))]

    def list_files(self):
        return self.files.values()

    def get_file(self, filename):
        if filename not in self.files:
            return None
        with open(os.path.join(self.root, self.files[filename]), 'rb') as f:
            return f.read()
