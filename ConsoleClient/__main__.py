from ConsoleClient.ConsoleClient import ConsoleClient
from argparse import ArgumentError, ArgumentTypeError, ArgumentParser
from sys import argv


def main():
    if not argv:  # No idea when will happen, but safety...
        return
    args = argv[1:]
    parser = ArgumentParser("Chat Client - Console Edition")
    try:

        parser.add_argument("-ip", metavar="i", type=str, default="127.0.0.1", help="Enter Server IPv4")
        parser.add_argument("-port", metavar="p", type=int, default=12000, help="Enter Server Port (Chat Port)")
        parser.add_argument("-download", metavar="d", type=str, default='',
                            help="Enter a directory path in which files will be downloaded")
    except (ArgumentError, ArgumentTypeError):
        print("Couldn't parse the input, try using -help to see how to run")
        exit(0)
    args = parser.parse_args(args)
    c = ConsoleClient(args.ip, args.port)
    c.start(downloads_path=args.download)


if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        pass
