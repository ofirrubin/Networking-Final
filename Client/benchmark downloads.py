import datetime

from Client.FTLib.FTC import FTC


def download_handler(ftc, status, resp):
    if status is True:
        end = datetime.datetime.now()
        print(end - start)
        print("\nThis file completed downloading! ->", ftc)
    else:
        print("Recieved data from file >", ftc, "\nactual data: ", str(resp.data))


req = FTC(('127.0.0.1', 12001), '1MB.txt')
start = datetime.datetime.now()
req.request(download_handler)
