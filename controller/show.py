from rc import EDITOR
import model
import view

import subprocess

parser = view.Parser(prog='show', description='Displays a problem by source name.')
parser.add_argument('key', help="The key of the problem to open (either source or cache index).")
parser.add_argument('-b', '--body', nargs = '?', type = int, const = 0, default = None,
		help = "Prints only the b-th body")

def main(self, argv):
	opts = parser.process(argv)
	entry = model.getEntryByKey(opts.key)
	if entry is None:
		view.error(opts.key + " not found")
	else:
		problem = entry.full
		b = opts.body
		if b is None:
			view.printProblem(problem)
		else:
			view.out(problem.bodies[b])
