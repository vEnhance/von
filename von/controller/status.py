from .. import model, view

parser = view.Parser(prog="ss", description="Prints the Cache.")


def main(argv: list[str]):
    display = view.Display.from_opts(parser.parse_args(argv))
    for entry in model.readCache():
        view.printEntry(entry, display)
