from pathlib import Path

from .. import model, view
from ..puid import inferPUID
from ..rc import config

parser = view.Parser(
    prog="fixnames",
    description="Fixes all the filenames to match PUID and rebuilds the index.",
)


def main(argv: list[str]):
    parser.parse_args(argv)
    base_path = Path(config().base_path)
    for p in model.getAllProblems():
        puid = inferPUID(p.source)
        src = base_path / p.path
        target = base_path / src.parent / f"{puid}.tex"
        if not target.exists():
            src.rename(target)
    model.rebuildIndex()
