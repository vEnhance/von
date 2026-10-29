from .. import model, view

parser = view.Parser(prog="clear", description="Clears the Cache.")


def main(self: object, argv: list[str]):
    parser.parse_args(argv)
    model.clearCache()
