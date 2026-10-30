import logging
import re
from argparse import Namespace
from collections.abc import Iterable

from .. import model, strparse, view

parser = view.Parser(
    prog="solve", description=r"Taking as input a TeX file, expands \von instances."
)

parser.add_argument("filename", help="The filename to translate.")
parser.add_argument(
    "-p",
    "--pagebreaks",
    action="store_true",
    help="Include page break after every solution (default is a bar).",
)
parser.add_argument(
    "-l",
    "--lazy",
    action="store_true",
    help="Don't include solutions to the problems.",
)
parser.add_argument(
    "-k",
    "--sourced",
    action="store_true",
    help="Always include the keyed source anyways.",
)

r = re.compile(r"\\von(\*)?(\[([^\]]+)\])?\{([A-Za-z0-9 /\-?,.!]+)\}")


def render(lines: Iterable[str], opts: Namespace) -> str:
    """Expands every \von line in the TeX source into problem and solution"""
    s = ""
    for line in lines:
        result = r.match(line)
        if result is None:
            s += line
        else:
            has_star = result.group(1) is not None
            source = result.group(2)
            key = result.group(4)
            entry = model.getEntryByKey(key)
            assert entry is not None, key
            problem = entry.full

            if has_star and not opts.sourced:
                s += r"\begin{problem}" + "\n"
            elif source is not None:
                if entry.url is not None and r"\href" not in source:
                    s += r"\begin{problem}["
                    s += r"\href{" + entry.url + "}{" + source[1:-1] + "}"
                    s += "]\n"
                else:
                    s += r"\begin{problem}" + source + "\n"
            else:
                if entry.url is not None:
                    s += r"\begin{problem}[\href{" + entry.url + "}{" + key + "}]\n"
                else:
                    s += r"\begin{problem}[" + key + "]" + "\n"
            s += strparse.demacro(problem.bodies[0]) + "\n"
            s += r"\end{problem}" + "\n"
            if not opts.lazy:
                if len(problem.bodies) > 1:
                    s += r"\subsection*{\ul{Solution}}" + "\n"
                    s += strparse.demacro(problem.bodies[1]) + "\n"
                    if opts.pagebreaks:
                        s += r"\newpage" + "\n"
                    else:
                        s += r"\hrulebar" + "\n"
                else:
                    logging.error("No solution to " + key)
    return s


def main(self: object, argv: list[str]):
    opts = parser.parse_args(argv)
    with open(opts.filename) as f:
        view.out(render(f, opts))
