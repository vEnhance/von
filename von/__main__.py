import sys

from . import term
from .__about__ import __version__ as VERSION


def main():
    cmd = term.VonTerminal()
    if len(sys.argv) == 1:
        cmd.run()
    elif len(sys.argv) == 2 and sys.argv[1] in ("-h", "--help"):
        cmd.direct(["help"])
    elif len(sys.argv) == 2 and sys.argv[1] in ("-v", "--version"):
        print(VERSION)
    elif len(sys.argv) >= 2 and sys.argv[1].startswith("-"):
        print(
            f"ERROR: You need to start with a command name (rather than {sys.argv[1]})"
        )
        cmd.direct(["help"])
        sys.exit(1)
    else:
        cmd.direct(sys.argv[1:])  # to preserve command line quotes etc


if __name__ == "__main__":
    main()
