from .. import model, view
from ..rc import VON_BASE_PATH

parser = view.Parser(prog='search', description='Searches for problems by tags or text.')
parser.add_argument('s_terms', nargs='*', metavar='term', help="Terms you want to search for.")
parser.add_argument(
	'-t',
	'--tag',
	nargs='+',
	metavar='tag',
	dest='s_tags',
	default=[],
	help="Tags you want to search for."
)
parser.add_argument(
	'-k',
	'--source',
	nargs='+',
	metavar='source',
	dest='s_sources',
	default=[],
	help="Sources you want to search for."
)
parser.add_argument(
	'-w',
	'--authors',
	nargs='+',
	metavar='authors',
	dest='s_authors',
	default=[],
	help="Authors you want to search for."
)
parser.add_argument(
	'-r',
	'--refine',
	action="store_const",
	default=False,
	const=True,
	help="Prune through the Cache rather than the whole database."
)
parser.add_argument(
	'-a',
	'--alph',
	action="store_const",
	default=False,
	const=True,
	help="Sort the results alphabetically, not by sort tag."
)
parser.add_argument(
	'-e',
	'--everything',
	action="store_const",
	default=False,
	const=True,
	help="Allow searching everything."
)
otis_group = parser.add_mutually_exclusive_group()
otis_group.add_argument('-n', '--notused', action='store_true', help="Problem not used in OTIS")
otis_group.add_argument('-o', '--occupied', action='store_true', help="Problem used in OTIS")


def main(self, argv):
	opts = parser.process(argv)

	query_is_empty = len(opts.s_terms + opts.s_tags + opts.s_sources + opts.s_authors) == 0

	if opts.everything is False and query_is_empty is True:
		view.warn("Must supply at least one search keyword or pass --everything option.")
		return
	if opts.everything is True and query_is_empty is False:
		view.warn("Passing --everything with parameters makes no sense.")
		return
	if opts.notused is True:
		in_otis = False
	elif opts.used is True:
		in_otis = True
	else:
		in_otis = None

	search_path = model.getcwd()
	if search_path != '':
		view.warn(
			"Search restricted to " + view.APPLY_COLOR("BOLD_GREEN", view.formatPath(search_path))
		)
	result = model.runSearch(
		terms=opts.s_terms,
		tags=opts.s_tags,
		sources=opts.s_sources,
		authors=opts.s_authors,
		refine=opts.refine,
		path=search_path,
		alph_sort=opts.alph,
		in_otis=in_otis
	)

	for i, entry in enumerate(result):
		view.printEntry(entry)
	if len(result) == 0:
		view.warn("No matches found.")
