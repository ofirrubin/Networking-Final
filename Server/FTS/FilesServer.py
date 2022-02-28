from Server.FTS.Responder import Responder
from Server.FTS.UDPServer import UDPServer

# UDP Based File Transferring Server.


class FilesServer:
    def __init__(self, ip, port, database, debug=False):
        self.database = database
        self.debug = debug
        self.server = UDPServer(ip, port, self.handler, Responder.req_header_len)

    def handler(self, data, address):
        Responder(self.server.sock, self.database, address, data, self.debug).respond()

    def start(self):
        self.server.start()

    def stop(self):
        self.server.stop()
