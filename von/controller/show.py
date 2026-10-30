import logging
from argparse import Namespace

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


def render(
    entry: model.PickleMappingEntry, opts: Namespace, display: view.Display
) -> str | None:
    """Returns the text to show for entry, or None (after logging) on error"""
    if entry.secret and not opts.brave:
        logging.error("Problem can't be shown without --brave option")
        return None
    b = opts.body
    problem = entry.full
    if b is None and opts.twitch:
        b = 1
    elif b is None and opts.aops:
        b = 0
    elif b is None:
        return view.getProblemString(problem, display, i=entry.i)
    try:
        body = problem.bodies[b]
    except IndexError:
        logging.error(f"Couldn't access {b}-th body of {problem}")
        return None
    if opts.twitch:
        return "Solution from [i]Twitch Solves ISL[/i]:\n\n" + strparse.toAOPS(body)
    elif opts.aops:
        return strparse.toAOPS(body)
    elif opts.preserve:
        return body
    else:
        return strparse.demacro(body)


def main(argv: list[str]):
    opts = parser.parse_args(argv)
    display = view.Display.from_opts(opts)
    key = opts.key if opts.key is not None else fzf_choose(display)
    entry = model.getEntryByKey(key)
    if entry is None:
        logging.error(key + " not found")
    elif (text := render(entry, opts, display)) is not None:
        view.out(text)
