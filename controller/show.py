from .. import model, strparse, view
from ..fzf import fzf_choose
import logging

parser = view.Parser(prog="show", description="Displays a problem by source name.")
parser.add_argument(
    "key", nargs="?", help="The key of the problem to open.", default=None
)
parser.add_argument(
    "-b",
    "--body",
    nargs="?",
    type=int,
    const=0,
    default=None,
    help="Prints only the b-th body.",
)
parser.add_argument(
    "-a",
    "--aops",
    action="store_const",
    const=True,
    default=False,
    help="Returns string in `AoPS mode'. Automatically causes -b.",
)
parser.add_argument(
    "-p",
    "--preserve",
    action="store_const",
    const=True,
    default=False,
    help="With -b, suppress macro expansion from body.",
)


def main(self: object, argv: list[str]):
    opts = parser.process(argv)
    if opts.key is not None:
        entry = model.getEntryByKey(opts.key)
    else:
        entry = model.getEntryByKey(fzf_choose())
    if entry is None:
        logging.error(opts.key + " not found")
    elif entry.secret and not opts.brave:
        logging.error("Problem can't be shown without --brave option")
        return
    else:
        b = opts.body
        problem = entry.full
        if b is None and opts.aops:
            b = 0
        if b is None:
            view.printProblem(problem, i=entry.i)
        else:
            try:
                if opts.aops:
                    view.out(strparse.toAOPS(problem.bodies[b]))
                elif opts.preserve:
                    view.out(problem.bodies[b])
                else:
                    view.out(strparse.demacro(problem.bodies[b]))
            except IndexError:
                logging.error(
                    "Couldn't access {}-th body of {}".format(b, problem.source)
                )
