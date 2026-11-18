from .. import model, view

parser = view.Parser(
    prog="index",
    description="Rebuilds the problem index and clears the cache. No arguments.",
)


def main(argv: list[str]):
    parser.parse_args(argv)
    model.rebuildIndex()
