import logging

from .. import model, strparse, view
from ..fzf import fzf_choose

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
    action="store_true",
    help="Returns string in `AoPS mode'. Automatically causes -b.",
)
parser.add_argument(
    "-p",
    "--preserve",
    action="store_true",
    help="With -b, suppress macro expansion from body.",
)
parser.add_argument(
    "-t",
    "--twitch",
    action="store_true",
    help="Implies --aops --body=1 and includes an ad for Twitch Solves ISL.",
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
        if b is None and opts.twitch:
            b = 1
        elif b is None and opts.aops:
            b = 0
        elif b is None:
            view.printProblem(problem, i=entry.i)
            return
        try:
            if opts.twitch:
                view.out("Solution from [i]Twitch Solves ISL[/i]:\n")
                view.out(strparse.toAOPS(problem.bodies[b]))
            elif opts.aops:
                view.out(strparse.toAOPS(problem.bodies[b]))
            elif opts.preserve:
                view.out(problem.bodies[b])
            else:
                view.out(strparse.demacro(problem.bodies[b]))
        except IndexError:
            logging.error(f"Couldn't access {b}-th body of {problem}")
