# File Transfer Client - Reliable UDP client for file transferring

import socket

from Client.Request import Request
from Client.Response import Response


class FTC:
    FILE_NOT_FOUND = b"FILE_NOT_FOUND"
    SYNTAX_ERROR = b"UNKNOWN_FORMAT"
    MAX_LENGTH = 4096
    BASE_LENGTH = 1024

    # although udp supports up to 65535 (such as on Windows),
    # I found that my PC (macOS) supports up to 9216 bytes, I settled on 4096.

    def __init__(self, address, filename, offset=0):
        self.filename = filename
        self.address = address
        self.s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.offset = 0
        self.length = self.BASE_LENGTH

    def __str__(self):
        return str(self.offset) + " bytes of the file '" + self.filename + "' downloaded from " + str(self.address)

    def request(self, callback):
        while self.length > 0:
            req = Request(self.filename, self.offset, self.length)
            resp, r_address, delta_time = self.timed_request(req)
            self.length = 0
            if resp.valid(req) is True:
                self.offset += resp.length
                callback(self, False, resp)
                if resp.final(req) is True:
                    self.length = 0  # There is no need for further requests
                else:
                    self.length = min(2 * self.length, self.MAX_LENGTH)
            else:
                if resp.error == self.FILE_NOT_FOUND:
                    raise FileNotFoundError("File not found")
                elif resp.error == self.SYNTAX_ERROR:
                    raise SyntaxError("Request syntax error")
                self.length = max(resp.header_length + 1, int(self.length / 2) + 1)
        callback(self, True, None)

    def request_updater(self, resp, dt):
        if resp.valid():
            yield resp.data
            self.offset += resp.length
            if resp.final():
                # Do not validate length as it's final.
                self.length = 0
                return True
            else:
                self.length = self.length_calc(True, dt)
        else:
            self.length = self.length_calc(False, dt)
        # Make sure length is valid.
        self.length = min(max(self.length, resp.header_length + 1), self.MAX_LENGTH)

    def length_calc(self, valid, dt):
        if valid:
            return self.length * 2
        else:
            return int(self.length / 2) + 1

    def timed_request(self, request):
        dt = 0
        request.send_request(self.s, self.address)
        response, r_address = self.s.recvfrom(request.length)
        response = Response(response)
        response.eval()

        return response, r_address, dt
