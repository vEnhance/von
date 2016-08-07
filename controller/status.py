import model
import view
import argparse

parser = argparse.ArgumentParser(prog='ss',\
		description='Prints the Cache.')
parser.add_argument('-t', '--tags', action = "store_const",\
		default = False, const = True,\
		help = "Also print problem tags.")

def main(self, argv):
	opts = parser.parse_args(argv)
	for entry in model.readCache():
		view.printEntry(entry, tags = opts.tags)
