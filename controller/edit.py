from rc import EDITOR
import argparse
import subprocess
import model

parser = argparse.ArgumentParser(prog='open', description='Opens a problem by source name.')
parser.add_argument('source', help="The source ID of the problem to open")

def main(argv):
	opts = parser.parse_args(argv)
	p = model.getProblemBySource(opts.source)
	subprocess.call([EDITOR, p.path])
	model.addToCache(p) # update cache after editing problem
