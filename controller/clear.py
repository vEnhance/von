from .. import model, view

parser = view.Parser(prog='clear', description='Clears the Cache.')


def main(self, argv):
	model.clearCache()
