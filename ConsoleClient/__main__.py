from ConsoleClient.ConsoleClient import ConsoleClient


def main():
    c = ConsoleClient("127.0.0.1", 12000)
    c.start(downloads_path='')


if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        pass
