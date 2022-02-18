from hashlib import md5


def unpad(data):
    while data and data[0] == 0:
        data = data[1:]
    return data


class Response:
    header_length = 72
    hash_len = 32
    int_len = 4
    known_errors = [b"UNKNOWN_FORMAT", b"FILE_NOT_FOUND", b"OFFSET_OVERFLOW"]

    def __init__(self, response):
        self.response = response
        self.filename = b""
        self.expected_hash = b""
        self.data = b""
        self.actual_hash = b""
        self.length = 0
        self.error = b"NOT_PROCESSED_YET"

    def valid(self, request):
        return self.filename == request.filename and \
               (self.error is None or self.error == b"OFFSET_OVERFLOW")

    def eval(self):
        self.response = unpad(self.response)
        if self.response in self.known_errors:
            self.error = self.response
            return

        if len(self.response) < self.header_length:
            self.error = b"UNKNOWN_RESPONSE"
            return
        self.filename = self.response[:self.hash_len]
        self.length = int.from_bytes(
            bytes=self.response[self.hash_len: self.hash_len + self.int_len],
            byteorder="big",
            signed=False)
        if self.length < 0:
            self.error = b"LENGTH_IS_NEGATIVE"
            return
        pos = self.hash_len + self.int_len
        self.expected_hash = self.response[pos: pos + self.hash_len]
        pos += self.hash_len
        if self.length > len(self.response) - pos:
            self.error = b"INVALID_DATA_LENGTH"
            return
        if self.length == 0:
            self.data = b''
        else:
            self.data = self.response[-self.length:]
        self.actual_hash = md5(self.data).hexdigest().encode()
        if self.expected_hash != self.actual_hash:
            self.error = b"CORRUPTED_FILE"
            return
        self.error = None

    def final(self, request):
        return self.length < request.length - self.header_length
