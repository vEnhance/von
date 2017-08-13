from .. import model, view
import os

parser = view.Parser(prog='cd',\
		description='Changes the working directory.')
parser.add_argument('path', help='The path to change to')

def main(self, argv):
	opts = parser.process(argv)
	os.chdir(opts.path)

	if not opts.quiet:
		entries, dirs = model.viewDirectory(model.getcwd())
		for d in dirs:
			view.printDir(d)
		for e in entries:
			view.printEntry(e)
