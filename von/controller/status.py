from .. import model, view

parser = view.Parser(prog="ss", description="Prints the Cache.")


def main(self: object, argv: list[str]):
    parser.process(argv)
    for entry in model.readCache():
        view.printEntry(entry)
