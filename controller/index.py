from .. import model, view

parser = view.Parser(prog='index',\
		description='Rebuilds the problem index. No arguments.')

def main(self, argv):
	opts = parser.process(argv)
	model.rebuildIndex()
