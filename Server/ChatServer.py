from TCPServer import Server as Server
from Lib.SecurePipe import SecurePipe
import ClientHandler
from Server.DatabaseConnection import DatabaseConnection as Database


class ChatServer:
    def __init__(self, ip, port, **args):
        self.ip = ip
        self.port = port
        self.server = Server(self.ip, self.port)
        self.db = Database(**args)
        self.db.users["admin"] = {"conn_alive": True}

    def client_handler(self, conn, addr):
        # User handler
        print("<{ip}, {port}> Server: Connection from <{client}>".format(ip=self.ip, port=self.port, client=addr))
        print("Securing connection")
        connection = SecurePipe(conn, server_side=True)
        print("Connection secured" if connection.secured else "Connection is not secured")
        ClientHandler.ClientHandler(self, connection).handle()
        conn.close()

    def list_files(self):
        return ["h.txt", "hello.txt"]

    def get_file(self, filename):
        return b'THIS IS THE REQUESTED FILE' + filename

    def start(self):
        self.server.start(user_handler=self.client_handler)

    def stop(self):
        self.server.stop()

