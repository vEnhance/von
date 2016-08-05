import argparse
import model

parser = argparse.ArgumentParser(prog='reindex',\
		description='Rebuilds the problem index. No arguments.')

def main(self, argv):
	opts = parser.parse_args(argv)
	model.rebuildIndex()
