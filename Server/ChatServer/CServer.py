from Lib.SecurePipe import SecurePipe

from Server.ChatServer.TCPServer import Server
from Server.ChatServer.ClientHandler import ClientHandler


class CServer:
    def __init__(self, ip, port, db):
        self.ip = ip
        self.port = port
        self.server = Server(self.ip, self.port)
        self.db = db
        self.db.users["admin"] = {"conn_alive": True}

    def client_handler(self, conn, addr):
        # User handler
        print("<{ip}, {port}> Server: Connection from <{client}>".format(ip=self.ip, port=self.port, client=addr))
        print("Securing connection")
        connection = SecurePipe(conn, server_side=True)
        print("Connection secured" if connection.secured else "Connection is not secured")
        ClientHandler(self, connection).handle()
        conn.close()

    def start(self):
        self.server.start(user_handler=self.client_handler)

    def stop(self):
        self.server.stop()

