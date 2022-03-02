from Lib.SecurePipe import SecurePipe

from Server.ChatServer.TCPServer import Server
from Server.ChatServer.ClientHandler import ClientHandler


class CServer:
    # TCP Server over SecurePipe, Handle client with ClientHandler (Chat Server)
    # Adapter server
    def __init__(self, ip, port, db, debug=False):
        self.ip = ip
        self.port = port
        self.debug = debug
        self.server = Server(self.ip, self.port)
        self.db = db

    def client_handler(self, conn, addr):
        # User handler
        if self.debug is True:
            print("<{ip}, {port}> Server: Connection from <{client}>".format(ip=self.ip, port=self.port, client=addr))
            print("Securing connection")
        connection = SecurePipe(conn, server_side=True)
        if self.debug is True:
            print("Connection secured" if connection.secured else "Connection is not secured")
        ClientHandler(self, connection, self.debug).handle()
        conn.close()

    def start(self):
        print("Starting Chat client, debug is: ", self.debug)
        self.server.start(user_handler=self.client_handler)

    def stop(self):
        self.server.stop()

