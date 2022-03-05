# File Transfer Client - Reliable UDP client for file transferring

import socket
from hashlib import md5

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

    def __init__(self, address, filename, offset=0, offset_end=0, callback=None):
        self.filename = filename
        self.address = address
        self.s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)  # IPv4, UserDatagramProtocol <=> DGRAM
        self.s_offset = offset
        self.offset = offset
        self.max_offset = offset_end
        self.__last_length = self.BASE_LENGTH
        self.length = self.BASE_LENGTH if offset_end <= 0 else min(self.BASE_LENGTH, offset_end)
        self.last_bpn = 0.9  # Last bytes per nano sec, defaulted to 0.9 because anything * (1 > n > 0) will be bigger
        self.pause_ = False
        self.callback = callback

    def __str__(self):
        return str(self.offset) + " bytes of the file '" + self.filename + "' downloaded from " + str(self.address)

    @classmethod
    def request_file_size(cls, address, filename):
        req = Request(filename, 0, 0)
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        req.send_request(s, address)
        request_len = 8 + Response.hash_len
        data, _ = s.recvfrom(request_len)
        if data == b'FILE_NOT_FOUND' or len(data) < request_len:
            return -1
        s, h = data[:8], data[8:]
        return -1 if md5(str(s).encode()).hexdigest().encode() != h else int.from_bytes(s, 'big', signed=False)

    def request(self, callback=None):
        if callable(callback) is False and callable(self.callback) is False:
            return  # if we don't have to do anything with the data, don't even download it
        if callable(callback):  # if replace callback
            self.callback = callback
        self.s.settimeout(1)  # 1 sec timeout
        while self.length > 0 and self.pause_ is False:  # while not finished and pause not requested
            req = Request(self.filename, self.offset, self.length)  # create the next part request
            resp, delta_time = self.timed_request(req)  # request with timelapse
            if resp is None:
                self.length = self.length_calc(resp, req, False, delta_time)
                continue  # Skip callback and don't update offset.
            if resp.error in FTC.Errors:  # If error occurred, return the error.
                return self.callback(filename=self.filename, valid=False, resp=resp,
                                     offset=self.offset, length=self.length)
            valid = resp.valid(req)  # Throw this peace of information to the callback
            self.callback(filename=self.filename, valid=valid, resp=resp,
                          offset=self.offset, length=resp.length)

            self.length = self.length_calc(resp, req, valid, delta_time)  # calculate next window size if any
            self.offset += resp.length  # update the current offset
        if self.pause_ is True:  # Save the current window size for resuming
            self.__last_length = self.length
        self.callback(filename=self.filename, valid=True, resp=self,
                      offset=self.offset, length=self.length)  # callback on complete

    def length_calc(self, resp, req, valid, delta):
        if resp is None:  # On fail to receive, set half the window size.
            return min(self.MAX_LENGTH, max(self.MIN_LENGTH, int(self.length/2)))
        if valid and resp.final(req):  # if completed downloading, change window size to 0.
            return 0

        margin_above = 1.05  # margins are essential for calibrating the RTT, each data is sent in different size
        margin_below = 0.98  # by using margins we adapt the ratios to our needs.
        bpn = self.length / delta  # calculate current ratio
        ratio = bpn / (margin_below * self.last_bpn)  # Making margin_below margin so it's increased
        self.last_bpn = bpn  # update as last bpn

        if valid and ratio >= margin_above:  # another margin_above improvement we just going to double the bandwidth
            length = self.length * 2  # if ratio is higher than margin, we will double the window size for fast recovery
        else:  # otherwise, we'll decrease fast the window size.
            length = ratio * self.length if ratio != 0 else self.MIN_LENGTH
        if self.max_offset != 0 and self.offset + resp.length + length > self.max_offset:  # If we want to download partial file,
            length = self.max_offset - self.offset - resp.length  # we must make sure we don't pass it
            if length < 0:
                return 0
        return max(self.MIN_LENGTH, min(self.MAX_LENGTH, int(length)))

    def timed_request(self, request):  # get the request while timing send+receive+processing time
        request.send_request(self.s, self.address)
        try:
            response = Response(*self.s.recvfrom(request.length))
        except socket.timeout:
            return None, -1
        response.eval()
        return response, response.resp_ts - request.request_ts

    def pause(self):
        self.pause_ = True

    def resume(self):
        self.pause_ = False
        self.length = self.__last_length  # on resume we update the window size to the last used one,
        if self.length == 0:  # unless we finished downloading
            return False
        self.request()  # Then we sending the requests.
        return True
