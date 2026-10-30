import os

from .. import model, view

parser = view.Parser(prog="cd", description="Changes the working directory.")
parser.add_argument("path", help="The path to change to")


def main(argv: list[str]):
    opts = parser.parse_args(argv)
    os.chdir(opts.path)

    if not opts.quiet:
        display = view.Display.from_opts(opts)
        entries, dirs = model.viewDirectory(model.getCompleteCwd())
        for d in dirs:
            view.printDir(d, display)
        for e in entries:
            view.printEntry(e, display)
