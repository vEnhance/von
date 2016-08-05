from rc import EDITOR
import model
import view

import argparse
import subprocess

parser = argparse.ArgumentParser(prog='show', description='Displays a problem by source name.')
parser.add_argument('key', help="The key of the problem to open (either source or cache index).")

def main(self, argv):
	opts = parser.parse_args(argv)
	entry = model.getEntryByKey(opts.key)
	if entry is None:
		view.error(opts.key + " not found")
	else:
		problem = entry.full
		views.printProblem(problem)
