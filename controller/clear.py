from .. import model, view

parser = view.Parser(prog='clear',\
		description='Clears the Cache.')

def main(self, argv):
	opts = parser.process(argv)
	model.clearCache()
