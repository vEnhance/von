from rc import EDITOR
import view

import subprocess
import model

parser = view.Parser(prog='edit', description='Opens a problem by source name.')
parser.add_argument('key', help="The key of the problem to open (either source or cache index).")

def main(self, argv):
	opts = parser.process(argv)
	entry = model.getEntryByKey(opts.key)
	if entry is None:
		view.error(opts.key + " not found")
	else:
		subprocess.call([EDITOR, entry.path])
		problem = model.makeProblemFromPath(entry.path)
		new_entry = model.updateEntryByProblem(
				old_entry = entry, new_problem = problem) # update cache after editing problem
		view.printEntry(new_entry)
