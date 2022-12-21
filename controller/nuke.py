from pathlib import Path

from .. import model, view
from ..puid import inferPUID
from ..rc import VON_BASE_PATH

parser = view.Parser(prog="nuke", description="Fixes all the filenames to match PUID")


def main(self: object, argv: list[str]):
    parser.process(argv)
    for p in model.getAllProblems():
        puid = inferPUID(p.source)
        src = VON_BASE_PATH / Path(p.path)
        target = VON_BASE_PATH / src.parent / f"{puid}.tex"
        if not target.exists():
            src.rename(target)
    model.rebuildIndex()
