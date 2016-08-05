from rc import APPLY_COLOR
import argparse
import model

parser = argparse.ArgumentParser(prog='ss',\
		description='Prints the Cache.')
parser.add_argument('-t', '--tags', action = "store_const",\
		default = False, const = True,\
		help = "Also print problem tags.")

def main(argv):
	opts = parser.parse_args(argv)
	for entry in model.readCache():
		print entry
		if opts.tags:
			print "\t" + APPLY_COLOR("MAGENTA", ' '.join(entry.tags))
