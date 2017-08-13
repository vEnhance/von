from .. import model, view

parser = view.Parser(prog='ss',\
		description='Prints the Cache.')

def main(self, argv):
	opts = parser.process(argv)
	for entry in model.readCache():
		view.printEntry(entry)
