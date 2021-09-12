from pathlib import Path

from .. import model, view
from ..puid import inferPUID

parser = view.Parser(prog='nuke', description='Fixes all the filenames to match PUID')


def main(self, argv):
	for p in model.getAllProblems():
		puid = inferPUID(p.source)
		src = Path(p.path)
		src.rename(src.parent / f'{puid}.tex')
	model.rebuildIndex()
