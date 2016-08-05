from rc import APPLY_COLOR, KEY_CHAR, TAG_CHARS
import argparse
import model

parser = argparse.ArgumentParser(prog='search',\
		description='Searches for problems by tags or text.')
parser.add_argument('words', nargs='+',\
		help="Terms you want to search for. To find tags, use #tag.")
parser.add_argument('-r', '--refine', action = "store_const",\
		default = False, const = True,\
		help = "Prune through the Cache rather than the whole database.")
# TODO eventually maybe don't put numbers on everything

def main(argv):
	opts = parser.parse_args(argv)
	tags = [t[1:] for t in opts.words if t[0] in TAG_CHARS]
	terms = [t for t in opts.words if t[0] not in TAG_CHARS]

	result = model.runSearch(tags, terms, refine = opts.refine)

	for i, entry in enumerate(result):
		print entry
