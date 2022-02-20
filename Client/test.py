from Client.FTLib.FTC import FTC


def download_handler(ftc, status, resp):
    if status is True:
        print("\nThis file completed downloading! ->", ftc)
    else:
        print("Recieved data from file >", ftc, "\nactual data: ", str(resp.data))


req = FTC(('127.0.0.1', 12334), 'test.txt')
req.request(download_handler)
