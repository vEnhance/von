from .. import model, view
import re

parser = view.Parser(prog = 'asy',
		description = 'Prints the diagram from the solution to a problem')
parser.add_argument('key',
		help = "The key of the problem to open")
parser.add_argument('-n', '--number', default = 1, type = int,
		help = "Takes the n-th diagram, one-indexed. Defaults to 1.")
parser.add_argument('-b', '--body', default = 1, type = int,
		help = "Takes the diagram from the b'th body. Defaults to 1.")
parser.add_argument('-c', '--comments', action='store_const',
		const = True, default = False,
		help = "Decides whether or not commented lines should be displayed")

def main(self, argv):
	opts = parser.process(argv)
	entry = model.getEntryByKey(opts.key)
	if entry is None:
		view.error(opts.key + " not found")
	else:
		problem = entry.full
		soln = problem.bodies[opts.body]
		asys = re.findall(r"\\begin\{asy\}(.+?)\\end\{asy\}", soln, flags=re.DOTALL)
		diagram = asys[opts.number-1]

		if not opts.comments:
			diagram = re.sub('/\*.*?\*/', '', diagram, flags=re.DOTALL)
		print('\n'.join(line.strip() for line in diagram.strip().split('\n')))
