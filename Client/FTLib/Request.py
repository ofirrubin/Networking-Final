from hashlib import md5
from time import time_ns


class Request:
    int_len = 4

    def __init__(self, filename, offset, length):
        self.filename = md5(filename.encode()).hexdigest().encode()
        self.offset = offset
        self.length = length
        self.request_ts = None

    def build_request(self):
        return self.filename + \
               int.to_bytes(self.length, length=self.int_len, byteorder="big", signed=False) + \
               int.to_bytes(self.offset, length=self.int_len, byteorder="big", signed=False)

    def send_request(self, socket, address):
        socket.sendto(self.build_request(), address)
        self.request_ts = time_ns()
