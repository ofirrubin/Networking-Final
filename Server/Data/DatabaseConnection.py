import os
from hashlib import md5


class DatabaseConnection:
    def __init__(self, root, debug=False, **kwargs):
        # Simple temp database
        self.chats = {}  # messages of each client
        self.users = {}  # username hash: is_logged_in, might include other info..
        self.root = root
        self.filter_ = None
        self.files = {}
        self.debug = debug
        self.update_list_files()  # retrieve files from file-system

    def remove_user(self, username):
        # delete users and chats
        if username in self.users.keys():
            del self.users[username]
        if username in self.chats.keys():
            del self.chats[username]

    def add_message(self, src, dest, msg, broadcast=False):
        # add message if users exists
        if src in self.users and dest in self.users:
            src = (b'-' if broadcast else b'+') + src
            if dest not in self.chats:
                self.chats[dest] = [(src, msg)]
            else:
                self.chats[dest].append((src, msg))
            return True
        return False

    def remove_msg(self, user, src_msg: tuple):
        # remove message if exists
        try:
            if user in self.chats:
                self.chats[user].remove(src_msg)
        except ValueError:
            pass

    def update_list_files(self):
        # update files hash map 'list'
        self.files = {}
        for file in self.__list_files():
            self.files[md5(file.encode()).hexdigest().encode()] = file
        if self.debug is True:
            print("List files updated <cwd , ", os.path.abspath(os.getcwd()), " | src ", self.root, ">: ", self.files)

    def __list_files(self):
        # update list files, with file filter (ends with) if required
        return self.__filtered_walk(self.filter_) if type(self.filter_) is str else self.__walk()

    def __filtered_walk(self, filter_: list):
        # update files hash map with the given filter -> files must end with any of the filters.
        files = []
        if os.path.isdir(self.root) is False:
            return files
        for root_, dir_, files_ in os.walk(self.root):
            files += filter(lambda x: any(x.endswith(f) for f in filter_) and not x.startwith('.'), files_)
        return files

    def __walk(self):
        # Get all files from file system
        return [] if os.path.isdir(self.root) is False else [f for f in os.listdir(self.root)
                                                             if os.path.isfile(os.path.join(self.root, f)) is True and f.startswith('.') is False]

    def list_files(self):
        # Returns the files available for the client
        return self.files.values()

    def get_file_size(self, filename):
        path = os.path.join(self.root, self.files[filename])
        return os.path.getsize(path) if os.path.isfile(path) else -1

    def get_file(self, filename, length: int, offset=None):
        # Returns the file data from offset up to <length> len (if possible).
        path = os.path.join(self.root, self.files[filename])
        actual_size = os.path.getsize(path)
        ofs = offset if type(offset) is int else 0
        if ofs < 0 or ofs > actual_size:
            raise OverflowError("Offset is out of bounds")
        if ofs + length > actual_size:
            read_size = actual_size - ofs
        else:
            read_size = length
        with open(path, 'rb') as f:
            f.seek(ofs)  # set offset
            return f.read(read_size)  # read up to length if possible
