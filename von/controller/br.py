import logging
import sys
import webbrowser

from .. import model, view

parser = view.Parser(prog="br", description="Browse a problem on AoPS")
parser.add_argument("key", help="The key of the problem to open")


def main(self: object, argv: list[str]):
    opts = parser.process(argv)
    entry = model.getEntryByKey(opts.key)
    if entry is None:
        logging.error(opts.key + " not found")
    else:
        url = entry.url
        if url is None:
            print("No URL is provided for this problem")
            sys.exit(1)
        print(url)
        webbrowser.open(url)
