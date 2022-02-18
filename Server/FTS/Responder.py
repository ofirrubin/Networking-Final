from hashlib import md5


class Responder:
    req_header_len = 40
    resp_header_len = 72
    default_block_size = 1024
    maximum_block_size = 4096

    int_len = 4
    hash_len = 32

    def __init__(self, server_sock, database, add, metabytes):
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
        self.file = database.get_file(self.requested_file)
        self.handle = True

    def request_len(self):
        # If we passed the end of the file, or we have 'less file' then required we send left,
        # otherwise we send in the maximum possible size.
        size_sent = min(self.block_size, self.maximum_block_size - self.resp_header_len) - self.resp_header_len
        left = len(self.file) - self.offset
        return left if left < 0 or left < size_sent else size_sent

    def build_response(self):
        resp = self.requested_file
        # size_sent = self.block_size
        # if self.block_size + self.resp_header_len > self.maximum_block_size:
        #     size_sent = self.maximum_block_size
        # left = len(self.file) - self.offset
        # if left < 0:
        #     return self.padding(b"OFFSET_OVERFLOW", self.resp_header_len)
        #
        # size_sent -= self.resp_header_len
        # if left < size_sent:
        #     size_sent = left
        size_sent = self.request_len()
        if size_sent < 0:
            return self.padding(b"OFFSET_OVERFLOW", self.resp_header_len)
        file_data = self.file[self.offset: self.offset + size_sent]
        # : PAYLOAD_SENT_SIZE | PAYLOAD_MD5 | PAYLOAD padded
        resp += int.to_bytes(size_sent, self.int_len, "big", signed=False)
        resp += md5(file_data).hexdigest().encode()
        resp += self.padding(file_data)
        return resp

    def respond(self):
        if self.handle is False:
            self.send(b"UNKNOWN_FORMAT", True)
            return

        if self.file is None:
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
                          actual_size=self.request_len())
