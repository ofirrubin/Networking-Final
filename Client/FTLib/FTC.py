# File Transfer Client - Reliable UDP client for file transferring

import socket
from Client.FTLib.Request import Request
from Client.FTLib.Response import Response


class FTC:
    FILE_NOT_FOUND = b"FILE_NOT_FOUND"
    SYNTAX_ERROR = b"UNKNOWN_FORMAT"
    Errors = [FILE_NOT_FOUND, SYNTAX_ERROR]
    MAX_LENGTH = 4096
    BASE_LENGTH = 2048
    MIN_LENGTH = 128

    # although udp supports up to 65535 (such as on Windows),
    # I found that my PC (macOS) supports up to 9216 bytes, I settled on 4096.

    def __init__(self, address, filename, offset=0, length=0):
        self.filename = filename
        self.address = address
        self.s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.offset = offset
        self.max_length = length
        self.length = self.BASE_LENGTH if length == 0 else min(self.BASE_LENGTH, length)
        self.last_bpn = 0.9  # Last bytes per nano sec, defaulted to 0.9 because anything * (1 > n > 0) will be bigger
        self.pause_ = False

    def __str__(self):
        return str(self.offset) + " bytes of the file '" + self.filename + "' downloaded from " + str(self.address)

    def request(self, callback):
        while self.length > 0 and self.pause_ is False:
            req = Request(self.filename, self.offset, self.length)
            resp, delta_time = self.timed_request(req)
            is_error = resp.error in FTC.Errors
            if is_error:
                return callback(filename=self.filename, valid=False, resp=resp,
                                offset=self.offset, length=self.length)
            valid = resp.valid(req)
            callback(filename=self.filename, valid=valid, resp=resp,
                     offset=self.offset, length=self.length)

            self.length = self.length_calc(resp, req, valid, delta_time)
            self.offset += resp.length
            print("New offset, ", self.offset)
        callback(filename=self.filename, valid=True, resp=self,
                 offset=self.offset, length=self.length)

    def length_calc(self, resp, req, valid, delta):
        margin_above = 1.05
        margin_below = 0.98
        bpn = self.length / delta
        ratio = bpn / (margin_below * self.last_bpn)  # Making margin_below margin so it's increased
        self.last_bpn = bpn
        if valid and resp.final(req):
            return 0
        if valid and ratio >= margin_above:  # another margin_above improvement we just going to double the bandwidth
            length = self.length * 2
        else:
            length = ratio * self.length if ratio != 0 else self.MIN_LENGTH
        if self.max_length != 0 and self.offset + length > self.max_length:
            length = self.max_length - self.max_length
        return max(self.MIN_LENGTH, min(self.MAX_LENGTH, int(length)))

    def timed_request(self, request):
        request.send_request(self.s, self.address)
        response = Response(*self.s.recvfrom(request.length))
        response.eval()
        return response, response.resp_ts - request.request_ts

    def pause(self):
        self.pause_ = True

    def resume(self):
        self.pause_ = False
