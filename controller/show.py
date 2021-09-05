from .. import model, view
from .. import strparse

parser = view.Parser(prog='show', description='Displays a problem by source name.')
parser.add_argument('key', help="The key of the problem to open.")
parser.add_argument(
	'-b', '--body', nargs='?', type=int, const=0, default=None, help="Prints only the b-th body."
)
parser.add_argument(
	'-a',
	'--aops',
	action='store_const',
	const=True,
	default=False,
	help="Returns string in `AoPS mode'. Automatically causes -b."
)
parser.add_argument(
	'-p',
	'--preserve',
	action='store_const',
	const=True,
	default=False,
	help="With -b, suppress macro expansion from body."
)


def main(self, argv):
	opts = parser.process(argv)
	entry = model.getEntryByKey(opts.key)
	if entry is None:
		view.error(opts.key + " not found")
	elif entry.secret and not opts.brave:
		view.error("Problem can't be shown without --brave option")
		return
	else:
		problem = entry.full
		b = opts.body
		if b is None and opts.aops:
			b = 0
		if b is None:
			view.printProblem(problem)
		else:
			try:
				if opts.aops:
					view.out(strparse.toAOPS(problem.bodies[b]))
				elif opts.preserve:
					view.out(problem.bodies[b])
				else:
					view.out(strparse.demacro(problem.bodies[b]))
			except IndexError:
				view.error("Couldn't access {}-th body of {}".format(b, problem.source))
