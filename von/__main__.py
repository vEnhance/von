import sys

from . import controller, term
from .__about__ import __version__ as VERSION
from .rc import ConfigError, config


def main():
    try:
        config()
    except ConfigError as e:
        print(e, file=sys.stderr)
        sys.exit(1)
    if len(sys.argv) == 1:
        term.VonTerminal().run()
    elif len(sys.argv) == 2 and sys.argv[1] in ("-h", "--help"):
        controller.dispatch(["help"])
    elif len(sys.argv) == 2 and sys.argv[1] in ("-v", "--version"):
        print(VERSION)
    elif len(sys.argv) >= 2 and sys.argv[1].startswith("-"):
        print(
            f"ERROR: You need to start with a command name (rather than {sys.argv[1]})"
        )
        controller.dispatch(["help"])
        sys.exit(1)
    else:
        controller.dispatch(sys.argv[1:])  # to preserve command line quotes etc


if __name__ == "__main__":
    main()
