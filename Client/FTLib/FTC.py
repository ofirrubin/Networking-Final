# File Transfer Client - Reliable UDP client for file transferring

import socket
from time import time_ns
from Client.FTLib.Request import Request
from Client.FTLib.Response import Response


class FTC:
    FILE_NOT_FOUND = b"FILE_NOT_FOUND"
    SYNTAX_ERROR = b"UNKNOWN_FORMAT"
    MAX_LENGTH = 4096
    BASE_LENGTH = 2048
    MIN_LENGTH = 128

    # although udp supports up to 65535 (such as on Windows),
    # I found that my PC (macOS) supports up to 9216 bytes, I settled on 4096.

    def __init__(self, address, filename, offset=0):
        self.filename = filename
        self.address = address
        self.s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.offset = 0
        self.length = self.BASE_LENGTH
        self.last_bpns = 0.9  # Last bytes per nano sec, defaulted to 0.9 because anything * (1 > n > 0) will be bigger

    def __str__(self):
        return str(self.offset) + " bytes of the file '" + self.filename + "' downloaded from " + str(self.address)

    def request(self, callback):
        while self.length > 0:
            req = Request(self.filename, self.offset, self.length)
            resp, r_address, delta_time = self.timed_request(req)
            if resp.error == self.FILE_NOT_FOUND:
                raise FileNotFoundError("File not found")
            elif resp.error == self.SYNTAX_ERROR:
                raise SyntaxError("Request syntax error")
            valid = resp.valid(req)

            if valid is True:
                self.offset += resp.length
                callback(self, False, resp)
            self.length = self.length_calc(resp, req, valid, delta_time)
        callback(self, True, None)

    def length_calc(self, resp, req, valid, delta):
        margin_above = 1.05
        margin_below = 0.98
        bpns = self.length / delta
        ratio = bpns / (margin_below * self.last_bpns)  # Making margin_below margin so it's increased
        self.last_bpns = bpns
        if valid and resp.final(req):
            return 0
        if valid and ratio >= margin_above:  # another margin_above improvement we just going to double the bandwidth
            length = self.length * 2
        else:
            length = ratio * self.length if ratio != 0 else self.MIN_LENGTH
        return max(self.MIN_LENGTH, min(self.MAX_LENGTH, int(length)))

    def timed_request(self, request):
        st = time_ns()
        request.send_request(self.s, self.address)
        response, r_address = self.s.recvfrom(request.length)
        et = time_ns()
        response = Response(response)
        response.eval()
        return response, r_address, et - st
