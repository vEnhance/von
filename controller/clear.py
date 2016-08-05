import model
import argparse
parser = argparse.ArgumentParser(prog='clear',\
		description='Clears the Cache.')

def main(self, argv):
	opts = parser.parse_args(argv)
	model.clearCache()
