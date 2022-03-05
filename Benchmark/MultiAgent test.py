from time import time_ns

from Client.SmartDownloader import DownloadManager

start = time_ns()
DownloadManager(('10.0.0.37', 12001), 'Image.png', '.', agents=2).download().wait()
end = time_ns()
diff = end - start
diff /= 1000000
print("Total time in ms", diff)
