from .. import model, view

parser = view.Parser(prog='paths', description='Prints the paths of all files in cache.')


def main(self, argv):
	for entry in model.readCache():
		print(entry.path)
