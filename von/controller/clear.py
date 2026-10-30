from .. import model, view

parser = view.Parser(prog="clear", description="Clears the Cache.")


def main(argv: list[str]):
    parser.parse_args(argv)
    model.clearCache()
