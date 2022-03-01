from threading import Thread

from Client.QClient.QClient import QClient
from time import sleep


class Chatter:
    # User friendly Chat & Files Client to allow connection to both servers,
    # Automatically retrieve updates => messages, online list, files list
    INTERVALS = 1.5  # SLEEP INTERVALS

    def __init__(self, ip, port, on_update, on_users_changed, on_msg, on_broadcast, on_download, on_ls_files_changed=None):
        self.ip = ip
        self.port = port
        self.client = QClient(self.ip, self.port)
        self.online_users = []
        self.list_files = []
        self.chats = {}
        self.client.on_update = on_update
        self.on_users_changed = on_users_changed
        self.on_message = on_msg
        self.on_broadcast = on_broadcast
        self.on_download = on_download
        self.on_list_files_changed = on_ls_files_changed

    def login(self, username):
        self.online_users = []
        self.list_files = []
        self.chats = {}
        self.client.login(username.encode())
        Thread(target=self.update_online_list, daemon=False).start()

    def update_online_list(self):
        while self.client.logged_in:
            self.client.get_online_list(self.__set_online_list)
            sleep(self.INTERVALS)
            self.client.list_files(self._set_list_files)
            sleep(self.INTERVALS)

    def _set_list_files(self, files_):
        if '' in files_:
            files_.remove(files_)
        self.list_files = files_
        if callable(self.on_list_files_changed):
            self.on_list_files_changed()

    def __set_online_list(self, status_feedback):
        status, users = status_feedback
        if status is True:
            users = self.__get_strings(users)
            new_users = [u for u in users if u not in self.online_users]
            logged_out = [u for u in self.online_users if u not in users]
            self.online_users = users
            self.on_users_changed(new_users, logged_out)

    @classmethod
    def __get_strings(cls, strings):
        st = []
        for string in strings:
            try:
                st.append(string.decode())
            except UnicodeDecodeError:
                pass
        return st

    def message(self, dest, message):
        return self.client.send_msg(self.on_message, dest, message)

    def download_file(self, filename):
        self.client.download_file(filename, self.on_download)

    def pause_download(self, filename):
        return self.client.pause_download(filename)

    def resume_download(self, filename):
        return self.client.resume_download(filename)

    def load_resume_file(self, filename, filepath):
        return self.client.resume_download(filename, filepath, self.on_download)

    def broadcast(self, msg):
        return self.client.broadcast(self.on_broadcast, msg)

    def logout(self):
        return self.client.logout()

    @property
    def logged_in(self):
        return self.client.list_files

    @property
    def username(self):
        return self.client.username

    @property
    def now_downloading(self):
        return self.client.downloads

    def shutdown(self):
        return self.client.shutdown()
