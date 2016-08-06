import view

import model
import os
import argparse

parser = argparse.ArgumentParser(prog='cd',\
		description='Changes the working directory.')
parser.add_argument('path', help='The path to change to')
parser.add_argument('-q', '--quiet', action = "store_const",\
		default = False, const = True,\
		help = "Don't print the directory on CD-ing.")
parser.add_argument('-t', '--tags', action = "store_const",\
		default = False, const = True,\
		help = "Print tags for entries.")

def main(self, argv):
	opts = parser.parse_args(argv)
	os.chdir(opts.path)

	if not opts.quiet:
		entries, dirs = model.viewDirectory(model.getcwd())
		for d in dirs:
			view.printDir(d)
		for e in entries:
			view.printEntry(e, tags = opts.tags)
