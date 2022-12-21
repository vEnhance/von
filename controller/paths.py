from .. import model, view

parser = view.Parser(
    prog="paths", description="Prints the paths of all files in cache."
)


def main(self: object, argv: list[str]):
    for entry in model.readCache():
        print(entry.path)
