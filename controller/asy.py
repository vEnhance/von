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


def main(self: object, argv: list[str]):
    opts = parser.process(argv)
    entry = model.getEntryByKey(opts.key)
    if entry is None:
        logging.error(opts.key + " not found")
    else:
        problem = entry.full
        soln = problem.bodies[opts.body]
        asys = re.findall(r"\\begin\{asy\}(.+?)\\end\{asy\}", soln, flags=re.DOTALL)
        assert opts.number >= 1
        diagram = asys[opts.number - 1]

        if not opts.comments:
            diagram = re.sub(r"/\*.*?\*/", "", diagram, flags=re.DOTALL)
        print("\n".join(line.strip() for line in diagram.strip().split("\n")))
