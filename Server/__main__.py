import os.path
from sys import argv
from argparse import ArgumentParser, ArgumentTypeError, ArgumentError
from Server.ChatServer.ChatServer import CServer
from Server.FTS.FilesServer import FilesServer
from Server.Data.DatabaseConnection import DatabaseConnection


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
        parser = ArgumentParser(description="Chat Server | Message over TCP & Download file over UDP")
        parser.add_argument("--debug", metavar="d", default=False, help="Use True for debug, default is False")
        parser.add_argument("-ip", metavar='-i', type=str, default="127.0.0.1",
                            help="Select IPv4 you want the server to run at.")
        parser.add_argument("-port", metavar='-p', type=int, default="12000",
                            help="Select port in which you want the server to operate. "
                                 "<port> will be used as TCP server PORT "
                                 "while <port> + 1 will be used for the UDP server")
        parser.add_argument('-files', metavar='-f', type=str, default='',
                            help="Select the directory which includes the files available for the user to download.")
        args = parser.parse_args(argv[1:])
        chat = Chat(ip=args.ip, port=args.port, files_root=args.files, debug=args.debug)
        chat.start()
        while input() != 'exit':
            continue
        chat.stop()
    except KeyboardInterrupt:
        pass
    except (ArgumentTypeError, ArgumentError):
        print("Couldn't parse your input, please try again..")

