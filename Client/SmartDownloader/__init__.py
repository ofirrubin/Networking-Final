import os

from Client.FTLib.FTC import FTC


class SmartDownloader:

    def __init__(self, filename, address, base_path):
        self.filename = filename
        self.address = address
        self.download_path = os.path.join(base_path, filename)
        self.tmp_path = os.path.join(base_path, filename + '.download')
        self.config_path = os.path.join(base_path, filename + '.config')
        self.self_download = False
        self.incomplete = True
        self.failed = 0

    def clear_filename(self):
        [os.remove(p) for p in [self.download_path, self.tmp_path, self.config_path] if os.path.isfile(p)]

    def vfe(self):  # verify file existence
        for f in [self.config_path, self.tmp_path]:
            with open(f, 'ab+'):  # using append so If the file exists it won't be overwritten.
                pass

    def tmp_to_final(self):
        if os.path.isfile(self.download_path):
            os.remove(self.download_path)
        if os.path.isfile(self.tmp_path):
            os.rename(self.tmp_path, self.download_path)

    def get_config(self):
        pass

    def rm_config(self, offset, length):
        # Checks if the request inside the config, if so remove it.
        with open(self.config_path, 'rb+') as f:
            b = f.read()
        others = []
        for pos in range(0, len(b), 8):
            of, ln = b[pos: pos + 4], b[pos + 4: pos + 8]
            if (of, ln) != (offset, length):
                others.append((of, ln))

    def append_config(self, offset: int, length: int):
        if offset < 0 or length < 0:
            raise ValueError("File offset and length must be positive int")
        with open(self.config_path, 'ab+') as f:
            f.write(int.to_bytes(offset, 4, 'big', signed=False))
            f.write(int.to_bytes(length, 4, 'big', signed=False))

    def download_callback(self, filename, offset, length, valid, resp):
        self.vfe()
        if valid is False:
            # Add it to the failed list
            # Fill with white space
            pass
        else:
            if length == 0:  # We downloaded the last part of the file.
                # If there are errors try re-download them.
                # Otherwise, rename the tmp file to the actual filename

                pass
            else:
                # We download something of the middle, we need to use the offset and length to add it in the right place
                pass

    def download(self):
        self.self_download = True
        self.clear_filename()
        requester = FTC(self.address, self.filename)
        requester.request(self.download_callback)

    def resume(self):
        if self.incomplete is False:
            return
        if self.self_download is True:
            # This instance started downloading the file, there is no skipping:
            if os.path.isfile(self.config_path) is False:
                # There is no tmp file, the file didn't start downloading.
                if os.path.isfile(self.tmp_path) is False:
                    self.download()
                # There is a tmp file, we started downloading and we've no skipped parts. so we append the file.
                else:
                    requester = FTC(self.address, self.filename)
                    requester.offset = os.path.getsize(self.tmp_path)
                    requester.length = requester.MIN_LENGTH
                    requester.request(self.download_callback)
            else:
                # Read all skips
                skips = []
                for skip in skips:  # Request each skip and save it in the required place
                    offset, length = skip  # length 0 means we paused / stopped downloading here, download
                    # everything left from the file too.
                    # We create new requester and set
                    requester = FTC(self.address, self.filename, offset, length)
                    requester.request(self.download_callback)
