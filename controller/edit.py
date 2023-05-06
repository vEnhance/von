import logging
import subprocess

from .. import model, view
from ..fzf import fzf_choose
from ..rc import EDITOR
from . import preview

parser = view.Parser(prog="edit", description="Opens problem(s) by source name.")
parser.add_argument(
    "-a",
    "--all",
    action="store_true",
    dest="all",
    help="Edit all problems in cache",
)
parser.add_argument(
    "keys",
    nargs="*",
    help="The key of the problem to open (either source or cache index).",
)


def main(self: object, argv: list[str]):
    opts = parser.process(argv)
    opts.verbose = True

    if opts.all is True:
        entries = model.readCache()
    elif len(opts.keys) == 0:
        entries = [model.getEntryByKey(fzf_choose())]
    else:
        entries = [model.getEntryByKey(key) for key in opts.keys]
    for entry in entries:
        if entry is None:
            logging.error("Not found")
        else:
            full_path = model.completePath(entry.path)
            preview.make_preview(full_path)
            subprocess.call([EDITOR, full_path])  # do editing

            problem = model.makeProblemFromPath(entry.path)
            new_entry = model.updateEntryByProblem(old_entry=entry, new_problem=problem)
            # update cache after editing problem
            view.printEntry(new_entry)
