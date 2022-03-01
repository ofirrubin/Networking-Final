import os

from Client.FTLib.FTC import FTC

# Multi agent download manager.


class DownloadManager:
    def __init__(self, filename, path):
        self.filename = filename
        self.path = path

    def download(self):
        pass

    def pause(self):
        pass

    def resume(self):
        pass

    @classmethod
    def load(cls, filename, path):
        # Load download configuration: Missing frames, Which frames downloaded etc.
        pass
