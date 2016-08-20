import model, view
from rc import EDITOR

import subprocess

parser = view.Parser(prog='edit', description='Opens problem(s) by source name.')
parser.add_argument('keys', nargs='+', help="The key of the problem to open (either source or cache index).")

def main(self, argv):
	opts = parser.process(argv)
	opts.verbose = True
	for key in opts.keys:
		entry = model.getEntryByKey(key)
		if entry is None:
			view.error(key + " not found")
		else:
			subprocess.call([EDITOR, entry.path])
			problem = model.makeProblemFromPath(entry.path)
			new_entry = model.updateEntryByProblem(
					old_entry = entry, new_problem = problem) # update cache after editing problem
			view.printEntry(new_entry)
