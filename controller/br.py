from .. import model, view
import sys
import webbrowser

parser = view.Parser(prog='br', description='Browse a problem on AoPS')
parser.add_argument('key', help="The key of the problem to open")


def main(self, argv):
	opts = parser.process(argv)
	entry = model.getEntryByKey(opts.key)
	if entry is None:
		view.error(opts.key + " not found")
	else:
		aops = entry.aops
		if aops is None:
			print("No AoPS link provided for this problem")
			sys.exit(1)
		print(f"Opening {aops}...")
		webbrowser.open(aops)
