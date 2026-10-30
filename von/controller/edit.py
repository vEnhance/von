import logging
import shlex
import subprocess

from .. import model, view
from ..fzf import fzf_choose
from ..rc import config
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


def main(argv: list[str]):
    opts = parser.parse_args(argv)
    display = view.Display.from_opts(opts, verbose=True)

    if opts.all is True:
        entries = model.readCache()
    elif len(opts.keys) == 0:
        entries = [model.getEntryByKey(fzf_choose(display))]
    else:
        entries = [model.getEntryByKey(key) for key in opts.keys]
    for entry in entries:
        if entry is None:
            logging.error("Not found")
        else:
            full_path = model.completePath(entry.path)
            preview.make_preview(full_path)
            subprocess.call([*shlex.split(config().editor), full_path])  # do editing

            problem = model.makeProblemFromPath(entry.path)
            new_entry = model.updateEntryByProblem(old_entry=entry, new_problem=problem)
            # update cache after editing problem
            view.printEntry(new_entry, display)
