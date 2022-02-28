from hashlib import md5


class Responder:
    req_header_len = 40
    resp_header_len = 72
    default_block_size = 1024
    maximum_block_size = 4096

    int_len = 4
    hash_len = 32

    def __init__(self, server_sock, database, add, metabytes, debug):
        self.debug = debug
        if self.debug:
            print(metabytes)
        self.add = add
        self.handle = False
        self.block_size = self.default_block_size
        self.s = server_sock
        self.header = self.req_header_len * b"\0"
        if len(metabytes) < self.req_header_len:
            self.send(b"")
            return
        self.requested_file = metabytes[:self.hash_len]
        try:
            self.block_size = int.from_bytes(metabytes[self.hash_len: self.hash_len + self.int_len],
                                             "big", signed=False)
            self.offset = int.from_bytes(metabytes[self.hash_len + self.int_len:self.hash_len + 2 * self.int_len],
                                         "big", signed=False)
        except ValueError:
            self.send(b"UNKNOWN_PARAMETERS")
            return
        if self.block_size <= self.resp_header_len:
            self.send(b"")
            return
        self.database = database
        self.file = None
        self.handle = True

    def build_response(self):
        resp = self.requested_file
        try:
            size_sent = min(self.block_size, self.maximum_block_size) - self.resp_header_len
            self.file = self.database.get_file(self.requested_file, size_sent, self.offset)
        except OverflowError:
            return self.padding(b"OFFSET_OVERFLOW", self.resp_header_len)
        size_sent = len(self.file) if len(self.file) < size_sent else size_sent
        # : PAYLOAD_SENT_SIZE | PAYLOAD_MD5 | PAYLOAD padded
        resp += int.to_bytes(size_sent, self.int_len, "big", signed=False)
        resp += md5(self.file).hexdigest().encode()
        resp += self.padding(self.file)
        if self.debug:
            print(self)
        return resp

    def respond(self):
        if self.handle is False:
            if self.debug:
                print("UNKNOWN FORMAT")
            self.send(b"UNKNOWN_FORMAT", True)
            return
        if self.requested_file not in self.database.files:
            if self.debug:
                print(self.file, " <-> FILE NOT FOUND")
            self.send(b"FILE_NOT_FOUND", True)
        else:
            self.send(self.build_response())

    def send(self, bytes_, header_only=False):
        self.s.sendto(self.padding(bytes_,
                                   None if header_only is False else self.resp_header_len), self.add)

    def padding(self, bytes_, length=None):
        times = (self.block_size - len(bytes_) - self.resp_header_len) if length is None else length
        return b"\0" * times + bytes_

    def __str__(self):
        return """Requested file: {requested_file}
        Offset: {offset}
        Block Size: {block_size}
        Actual Block Size Sent: {actual_size}
               """.format(requested_file=self.requested_file,
                          offset=self.offset,
                          block_size=self.block_size,
                          actual_size=len(self.file) if self.file is not None else 'File Not Found')
