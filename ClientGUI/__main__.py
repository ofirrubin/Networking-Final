from sys import argv

from ChatApp import main, close_window

program_args = []
path = '.'


if __name__ == '__main__':
    try:
        main(argv[1:])
    except (KeyboardInterrupt, KeyboardInterrupt):
        close_window()
