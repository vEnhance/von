from . import term
import sys

if __name__ == "__main__":
    cmd = term.VonTerminal()
    if len(sys.argv) == 1:
        cmd.run()
    else:
        cmd.direct(sys.argv[1:])  # to preserve command line quotes etc
