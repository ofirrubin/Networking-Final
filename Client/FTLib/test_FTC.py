from unittest import TestCase

from Client.FTLib.FTC import FTC
from Server.Data.DatabaseConnection import DatabaseConnection
from Server.FTS.FilesServer import FilesServer
import tempfile
from os.path import dirname, basename
from os import unlink


class TestFTC(TestCase):
    ip, port = ("127.0.0.1", 22345)
    server = None
    path = 'temp'
    data = 10000000 * b'a'
    tmp = None
    rcv = b''

    def setUp(self) -> None:
        self.tmp = tempfile.NamedTemporaryFile(delete=False)
        self.tmp.write(self.data)
        self.tmp.close()
        self.server = FilesServer(self.ip, self.port, DatabaseConnection(dirname(self.tmp.name)))
        self.server.database.filter = self.tmp.name
        self.server.start()

    def test_request(self):
        f = FTC((self.ip, self.port), basename(self.tmp.name))
        self.rcv = b''

        def download_callback(filename, valid, resp, offset, length):
            if valid and length != 0:
                self.rcv += resp.data
            else:
                self.assertEqual(self.rcv, self.data)
                unlink(self.tmp.name)
                self.server.stop()
        f.request(download_callback)
