from hashlib import md5


def unpad(data):
    while data and data[0] == 0:
        data = data[1:]
    return data


class Response:
    NOT_PROCESSED = b"NOT_PROCESSED_YET"
    SYNTAX_ERR = b"UNKNOWN_FORMAT"
    FILE_NOT_FOUND = b"FILE_NOT_FOUND"
    OVERFLOW_ERR = b"OFFSET_OVERFLOW"

    RESP_UKN = b"UNKNOWN_RESPONSE"
    NEGATIVE_LEN = b"LENGTH_IS_NEGATIVE"
    INV_DATA_LEN = b"INVALID_DATA_LENGTH"
    COR_FILE = b"CORRUPTED_FILE"

    header_length = 72
    hash_len = 32
    int_len = 4
    known_errors = [SYNTAX_ERR, FILE_NOT_FOUND, OVERFLOW_ERR]

    def __init__(self, response):
        self.response = response
        self.filename = b""
        self.expected_hash = b""
        self.data = b""
        self.actual_hash = b""
        self.length = 0
        self.error = self.NOT_PROCESSED

    def valid(self, request):
        return self.filename == request.filename and \
               (self.error is None or self.error == self.OVERFLOW_ERR)

    def eval(self):
        self.response = unpad(self.response)
        if self.response in self.known_errors:
            self.error = self.response
            return

        if len(self.response) < self.header_length:
            self.error = self.RESP_UKN
            return
        self.filename = self.response[:self.hash_len]
        self.length = int.from_bytes(
            bytes=self.response[self.hash_len: self.hash_len + self.int_len],
            byteorder="big",
            signed=False)
        if self.length < 0:
            self.error = self.NEGATIVE_LEN
            return
        pos = self.hash_len + self.int_len
        self.expected_hash = self.response[pos: pos + self.hash_len]
        pos += self.hash_len
        if self.length > len(self.response) - pos:
            self.error = self.INV_DATA_LEN
            return
        if self.length == 0:
            self.data = b''
        else:
            self.data = self.response[-self.length:]
        self.actual_hash = md5(self.data).hexdigest().encode()
        if self.expected_hash != self.actual_hash:
            self.error = self.COR_FILE
            return
        self.error = None

    def final(self, request):
        return self.length < request.length - self.header_length

    @classmethod
    def get_overflow(cls, filename):
        r = Response(b'')
        r.filename = filename
        r.error = cls.OVERFLOW_ERR
        return r
