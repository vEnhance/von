import sys

from . import term


def main():
    cmd = term.VonTerminal()
    if len(sys.argv) == 1:
        cmd.run()
    else:
        cmd.direct(sys.argv[1:])  # to preserve command line quotes etc


if __name__ == "__main__":
    main()
