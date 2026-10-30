import logging
from argparse import Namespace

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


def render(entries: list[model.PickleMappingEntry], opts: Namespace) -> str:
    """Returns the markup for the given problems, one after another"""
    lines: list[str] = []
    for i, entry in enumerate(entries):
        is_last = i == len(entries) - 1
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
            lines += [header, strparse.toAOPS(statement)]
            if not is_last:
                lines.append("\n--------\n")
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
            lines.append(header)
            lines.append(r"```latex" if opts.discord is True else "")
            lines.append(
                statement if opts.preserve is True else strparse.demacro(statement)
            )
            if opts.discord is True:
                lines.append(r"```")
            elif not is_last:
                lines.append("\n")
    return "\n".join(lines)


def main(self: object, argv: list[str]):
    opts = parser.parse_args(argv)
    keys = opts.keys
    if len(keys) == 0:
        keys = [fzf_choose(view.Display.from_opts(opts))]

    entries: list[model.PickleMappingEntry] = []
    for key in keys:
        entry = model.getEntryByKey(key)
        if entry is None:
            logging.error(key + " not found")
            return
        elif entry.secret and not opts.brave:
            logging.error("Problem can't be shown without --brave option")
            return
        entries.append(entry)
    view.out(render(entries, opts))
