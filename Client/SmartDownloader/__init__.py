import math
from enum import Enum
from os import unlink
from tempfile import NamedTemporaryFile
from threading import Thread
from time import time_ns

from Client.FTLib.FTC import FTC


# Multi agent download manager.
class Match(Enum):
    Below = 1
    Above = 2
    Equal = 3


class DownloadAgent:
    def __init__(self, server_address, filename, on_complete, range_):
        self.server_address = server_address
        self.filename = filename
        self.callback = on_complete
        self.start_range, self.end_range = range_
        self.request = None
        self.data = b''
        self.complete = False
        self.tmp_file = NamedTemporaryFile(delete=False)

    def __str__(self):
        return "<Download agent: (addr:{address}, file: {fname})> Offset: {offset}," \
               " Length: {offset_end}, Complete? {status}".format(address=self.server_address,
                                                                  fname=self.filename,
                                                                  offset=self.start_range,
                                                                  offset_end=self.end_range,
                                                                  status=self.complete)

    def __repr__(self):
        return "{" + str(self) + "}"

    def start(self):
        self.request = FTC(self.server_address, self.filename, self.start_range, self.end_range, self.download_callback)
        self.request.request()

    def download_callback(self, filename, valid, offset, length, resp):
        if valid is True and length == 0:
            self.complete = True
            self.tmp_file.seek(0)
            self.callback(self, True)
        elif valid is True:
            self.tmp_file.write(resp.data)
            self.data += resp.data
        else:
            print("Error, ", resp.response)


class DownloadManager:
    def __init__(self, server_address, filename, path, agents=2):
        self.addr = server_address
        self.filename = filename
        self.path = path
        self.filesize = b''

        self.agents_n = agents if agents > 0 else 1
        self.agents = {}
        self.agents_threads = []
        self.started = False
        self.complete = False
        self.download_units = {}

    def download(self):
        if self.started is True or self.complete is True:
            return
        file_size = FTC.request_file_size(self.addr, self.filename)
        if file_size == -1:
            raise FileNotFoundError("File not found")
        self.filesize = file_size
        j = math.ceil(file_size / self.agents_n)
        for x in range(0, file_size, j):
            range_ = (x, min(x + j, file_size))
            self.agents[range_] = DownloadAgent(self.addr, self.filename, self.__agent_complete, range_)
        for agent_r in self.agents:
            self.agents_threads.append(Thread(target=self.agents[agent_r].start, daemon=True))
            self.agents_threads[-1].start()
        self.started = True
        return self  # allows us to chain commands

    def __agent_complete(self, agent, status=False):
        if status is True:
            # Save this part...
            self.download_units[agent.start_range] = DownloadUnit(agent)

            if all(self.agents[x].complete for x in self.agents):
                # Unit all data
                total_unit = self.download_units[0]  # starter download unit
                while total_unit.e_range != self.filesize:
                    total_unit += self.download_units[total_unit.e_range]
                # Save all units to a file
                self.complete = True
                self.started = False
                with open(self.filename, "wb+") as f:
                    for tmp in total_unit.chained_files():
                        f.write(tmp.read())
                        tmp.close()
                        unlink(tmp.name)
        else:
            pass

    def wait(self):
        if self.started is False or self.complete is True:
            return
        for agent in self.agents_threads:
            agent.join()


class DownloadUnit:
    def __init__(self, *agents: DownloadAgent):
        self.s_range = min(agent.start_range for agent in agents)
        self.e_range = max(agent.end_range for agent in agents)
        self.agents = {agent.start_range: agent for agent in agents}

    def dup(self):
        new_agent = DownloadUnit(DownloadAgent("", "", print, (0, 0)))
        new_agent.start_range = self.s_range
        new_agent.end_range = self.e_range
        new_agent.agents = self.agents
        return new_agent

    def __str__(self):
        return "Start: " + str(self.s_range) + " End: " + str(self.e_range) + " Agents: " + str(self.agents)

    def __add__(self, other):
        if type(other) != type(self):
            raise TypeError("Invalid type!")
        if type(self.is_linked(other)) is not Match:
            raise ValueError("Units not matching!")
        unit = self.dup()
        unit.s_range = min(unit.s_range, other.s_range)
        unit.e_range = max(unit.e_range, other.e_range)
        unit.agents.update(other.agents)
        return unit

    def is_linked(self, other):  # Is this part right above/below/equal to other part.
        if type(other) != type(self):
            raise TypeError("Invalid type!")
        if self.s_range == other.s_range and self.e_range == other.e_range:
            return Match.Equal
        elif other.s_range == self.e_range:
            return Match.Below
        elif other.e_range == self.s_range:
            return Match.Above

    def yield_data(self):
        pos = self.s_range
        while pos != self.e_range:
            yield self.agents[pos].data
            pos = self.agents[pos].end_range

    def chained_files(self):
        # yields NamedTempFile of each data part while maintaining order to unite them into one peace.
        pos = self.s_range
        while pos != self.e_range:
            yield self.agents[pos].tmp_file
            pos = self.agents[pos].end_range


start = time_ns()
DownloadManager(('127.0.0.1', 12001), '20MB.png', '.').download().wait()
end = time_ns()
diff = end - start
diff /= 1000000
print("Total time in ms", diff)
