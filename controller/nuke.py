from pathlib import Path

from .. import model, view
from ..puid import inferPUID

parser = view.Parser(prog='nuke', description='Fixes all the filenames to match PUID')


def main(self, argv):
	for p in model.getAllProblems():
		puid = inferPUID(p.source)
		src = Path(p.path)
		target = src.parent / f'{puid}.tex'
		if not target.exists():
			src.rename(target)
	model.rebuildIndex()
