from .. import model, view
import re

parser = view.Parser(prog='solve',\
		description=r'Taking as input a TeX file, expands \von instances.')

parser.add_argument('filename', help="The filename to translate.")
parser.add_argument('-p', '--pagebreaks', action='store_const',
		const = True, default = False,
		help="Include page break after every solution (default is a bar).")
parser.add_argument('-l', '--lazy', action='store_const',
		const = True, default = False,
		help="Don't include solutions to the problems.")
parser.add_argument('-k', '--sourced', action='store_const',
		const = True, default = False,
		help="Always include the keyed source anyways.")


r = re.compile(r'\\von(\*)?(\[([^\]]+)\])?\{([A-Za-z0-9 /\-?,.!]+)\}')
def main(self, argv):
	opts = parser.process(argv)
	s = ''

	with open(opts.filename) as f:
		for line in f:
			result = r.match(line)
			if result is None:
				s += line
			else:
				has_star = result.group(1) is not None
				source = result.group(2)
				key = result.group(4)
				if has_star and not opts.sourced:
					s += r'\begin{problem}' + '\n'
				elif source is not None:
					s += r'\begin{problem}' + source + '\n'
				else:
					s += r'\begin{problem}[' + key + ']' + '\n'
				entry = model.getEntryByKey(key)
				assert entry is not None, key
				problem = entry.full
				s += model.demacro(problem.bodies[0]) + '\n'
				s += r'\end{problem}' + '\n'
				if not opts.lazy:
					if len(problem.bodies) > 1:
						s += r'\subsubsection*{\ul{Solution}}' + '\n'
						s += model.demacro(problem.bodies[1]) + '\n'
						if opts.pagebreaks:
							s += r'\newpage' + '\n'
						else:
							s += r'\hrulebar' + '\n'
					else:
						view.warn("No solution to " + key)
		view.out(s)
