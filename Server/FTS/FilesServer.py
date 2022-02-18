from Server.FTS.Responder import Responder
from Server.FTS.UDPServer import UDPServer

# UDP Based File Transferring Server.


class FilesServer:
    def __init__(self, ip, port, database):
        self.database = database
        self.server = UDPServer(ip, port, self.handler, Responder.req_header_len)

    def handler(self, data, addr):
        Responder(self.server.sock, self.database, addr, data).respond()

    def start(self):
        self.server.start()

    def stop(self):
        self.server.stop()

