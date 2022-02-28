import os.path

from ChatServer.CServer import CServer
from FTS.FilesServer import FilesServer
from Data.DatabaseConnection import DatabaseConnection


class Chat:
    def __init__(self, ip, port, files_root, debug):
        self.ip = ip
        self.port = port
        self.db = DatabaseConnection(root=files_root)
        self.chat_server = CServer(ip, port, self.db)
        self.files_server = FilesServer(ip, port + 1, self.db, debug)

    def start(self):
        self.chat_server.start()
        print("Chat server started at ...", (self.ip, self.port))
        self.files_server.start()
        print("Files Server started...", (self.ip, self.port + 1))

    def stop(self):
        self.chat_server.stop()
        self.files_server.stop()


if __name__ == "__main__":
    try:
        chat = Chat(ip="127.0.0.1", port=12000, files_root=os.path.join(os.path.curdir, 'Data', 'Files'), debug=True)
        chat.start()
        while input() != 'exit':
            continue
        chat.stop()
    except KeyboardInterrupt:
        pass
