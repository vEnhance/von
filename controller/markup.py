import logging

from .. import model, strparse, view
from ..fzf import fzf_choose

parser = view.Parser(
    prog="markup",
    description="Gives a Markdown version of problem statement for copy-pasting in email etc.",
)
parser.add_argument(
    "keys",
    nargs="*",
    help="The key(S) of the problem to open.",
)
parser.add_argument(
    "-p",
    "--preserve",
    action="store_true",
    help="Suppress macro expansion from body.",
)
parser_display_modes = parser.add_mutually_exclusive_group()

parser_display_modes.add_argument(
    "-a",
    "--aops",
    action="store_true",
    help="Returns in AoPS mode.",
)
parser_display_modes.add_argument(
    "-d",
    "--discord",
    action="store_true",
    help="Returns in Discord mode.",
)


def main(self: object, argv: list[str]):
    opts = parser.process(argv)
    keys = opts.keys
    if len(keys) == 0:
        keys = [fzf_choose()]

    for i, key in enumerate(keys):
        entry = model.getEntryByKey(key)

        if entry is None:
            logging.error(opts.key + " not found")
            return
        elif entry.secret and not opts.brave:
            logging.error("Problem can't be shown without --brave option")
            return

        problem = entry.full
        statement = problem.bodies[0]

        if opts.aops is True:
            header = "[b]"
            if problem.url is not None:
                header += f"[url={problem.url}]{entry.source}[/url]"
            else:
                header += entry.source
            if problem.author is not None:
                header += f", proposed by {problem.author}.[/b]"
            else:
                header += ".[/b]"
            view.out(header)
            view.out(strparse.toAOPS(statement))
            if i != len(keys) - 1:
                view.out("\n--------\n")
        else:
            header = "## "
            if problem.url is not None:
                header += f"[{problem.source}]({problem.url})"
            else:
                header += entry.source
            if problem.author is not None:
                header += f", proposed by {problem.author}."
            else:
                header += "."
            view.out(header)
            if opts.discord is True:
                view.out(r"```latex")
            else:
                view.out("")
            view.out(
                statement if opts.preserve is True else strparse.demacro(statement)
            )
            if opts.discord is True:
                view.out(r"```")
            elif i != len(keys) - 1:
                view.out("\n")
