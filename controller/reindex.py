import view
import model

parser = view.Parser(prog='reindex',\
		description='Rebuilds the problem index. No arguments.')

def main(self, argv):
	opts = parser.process(argv)
	model.rebuildIndex()
