from rc import EDITOR, ERROR_PRE
import argparse
import subprocess
import model

parser = argparse.ArgumentParser(prog='show', description='Displays a problem by source name.')
parser.add_argument('key', help="The key of the problem to open (either source or cache index).")

def main(argv):
	opts = parser.parse_args(argv)
	entry = model.getEntryByKey(opts.key)
	if entry is None:
		print ERROR_PRE, "Not found"
	else:
		problem = entry.full
		print problem
