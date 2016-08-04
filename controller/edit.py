from rc import EDITOR, ERROR_PRE
import argparse
import subprocess
import model

parser = argparse.ArgumentParser(prog='open', description='Opens a problem by source name.')
parser.add_argument('source', help="The source ID of the problem to open")

def main(argv):
	opts = parser.parse_args(argv)
	p = model.getProblemBySource(opts.source)
	if p is None:
		print ERROR_PRE, "Not found"
	else:
		subprocess.call([EDITOR, p.path])
		model.addToIndex(p) # update cache after editing problem
