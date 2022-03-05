import math
from threading import Thread

from Client.FTLib.FTC import FTC


# Multi agent download manager.


class DownloadAgent:
    def __init__(self, server_address, filename, on_complete, range_):
        self.server_address = server_address
        self.filename = filename
        self.callback = on_complete
        self.start_range, self.end_range = range_
        self.data = b''
        self.complete = False

    def __str__(self):
        print("<Download agent: (addr:{address}, file: {fname})> Offset: {offset},"
              " Length: {offset_end}, Complete? {status}".format(address=self.server_address,
                                                                 fname=self.filename,
                                                                 offset=self.start_range,
                                                                 offset_end=self.end_range,
                                                                 status=self.complete))

    def start(self):
        FTC(self.server_address, self.filename, self.start_range, self.end_range - self.start_range,
            self.download_callback).request()

    def on_fail(self):
        pass

    def on_pass(self):
        pass

    def download_callback(self, filename, valid, offset, length, resp):
        if valid is True and length == 0:
            if self.start_range != 0:
                return
            print("I requested from: ", self.start_range, " to: ", self.end_range, "len of(",
                  self.end_range - self.start_range, ")")
            print(len(self.data))
            self.complete = True
        elif valid is True:
            if self.start_range == 0:
                print(offset, ", ", length)
            self.data += resp.data
        else:
            print("Error, ", resp)


class DownloadManager:
    def __init__(self, server_address, filename, path, agents=4):
        self.addr = server_address
        self.filename = filename
        self.path = path
        self.agents_n = agents if agents > 0 else 1
        self.filesize = b''
        self.agents = {}

    def download(self):
        file_size = FTC.request_file_size(self.addr, self.filename)
        if file_size == -1:
            raise FileNotFoundError("File not found")
        j = math.ceil(file_size / self.agents_n)
        for x in range(0, file_size, j):
            range_ = (x, min(x + j, file_size))
            self.agents[range_] = DownloadAgent(self.addr, self.filename, self.__agent_complete, range_)
        for agent_r in self.agents:
            Thread(target=self.agents[agent_r].start, daemon=True).run()

    def __agent_complete(self, s, e, status=False, ls_fails=None):
        if status is True:
            if all(self.agents[x].complete for x in self.agents):
                # Unit all data
                pass
            else:
                # Save this part only.
                pass
        else:
            pass

    def pause(self):
        pass

    def resume(self):
        pass

    @classmethod
    def load(cls, filename, path):
        # Load download configuration: Missing frames, Which frames downloaded etc.
        pass


DownloadManager(('127.0.0.1', 12001), 'Image.png', '.').download()
