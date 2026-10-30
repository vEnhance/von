import logging
import re

from .. import model, view

parser = view.Parser(
    prog="asy", description="Prints the diagram from the solution to a problem"
)
parser.add_argument("key", help="The key of the problem to open")
parser.add_argument(
    "-n",
    "--number",
    default=1,
    type=int,
    help="Takes the n-th diagram, one-indexed. Defaults to 1.",
)
parser.add_argument(
    "-b",
    "--body",
    default=1,
    type=int,
    help="Takes the diagram from the b'th body. Defaults to 1.",
)
parser.add_argument(
    "-c",
    "--comments",
    action="store_true",
    help="Decides whether or not commented lines should be displayed",
)


def extract(solution: str, number: int = 1, comments: bool = False) -> str:
    """Returns the number-th (one-indexed) Asymptote diagram in solution,
    dedented and optionally with /* comments */ removed"""
    asys = re.findall(r"\\begin\{asy\}(.+?)\\end\{asy\}", solution, flags=re.DOTALL)
    assert number >= 1
    diagram = asys[number - 1]

    if not comments:
        diagram = re.sub(r"/\*.*?\*/", "", diagram, flags=re.DOTALL)
    lines = [line.rstrip() for line in diagram.lstrip("\n").rstrip().split("\n")]
    min_indent = min(len(line) - len(line.lstrip()) for line in lines if line.strip())
    return "\n".join(line[min_indent:] for line in lines)


def main(self: object, argv: list[str]):
    opts = parser.parse_args(argv)
    entry = model.getEntryByKey(opts.key)
    if entry is None:
        logging.error(opts.key + " not found")
    else:
        solution = entry.full.bodies[opts.body]
        view.out(extract(solution, opts.number, opts.comments))
