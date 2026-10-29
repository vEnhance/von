from .. import model, view

parser = view.Parser(
    prog="index", description="Rebuilds the problem index. No arguments."
)


def main(self: object, argv: list[str]):
    parser.parse_args(argv)
    model.rebuildIndex()
