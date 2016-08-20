import model, view

parser = view.Parser(prog='po',\
		description='Prepares a LaTeX file to send to Po-Shen!')
parser.add_argument('keys', nargs = '+',
		help="The keys of the problem to propose.")
parser.add_argument('-t', '--title', default = 'Problem Proposals',
		help="Title of the LaTeX document.")
parser.add_argument('-s', '--subtitle', default = None,
		help="Subtitle of the LaTeX document.")
parser.add_argument('--author', default = 'Evan Chen',
		help="Author of the LaTeX document.")
parser.add_argument('--date', default = r'\today',
		help="Date of the LaTeX document.")

def main(self, argv):
	opts = parser.process(argv)
	s = r"\documentclass[11pt]{scrartcl}" + "\n"
	s += r"\usepackage{evan}" + "\n\n"
	s += r"\begin{document}" + "\n"
	s += r"\title{" + opts.title + "}" + "\n"
	if opts.subtitle is not None:
		s += r"\subtitle{" + opts.title + "}" + "\n"
	s += r"\author{" + opts.author + "}" + "\n"
	s += r"\date{" + opts.date + "}" + "\n"
	s += r"\maketitle" + "\n"
	s += "\n"
	for key in opts.keys:
		entry = model.getEntryByKey(key)
		if entry is None:
			view.error(key + " not found")
		else:
			problem = entry.full
			s += r"\begin{problem}" + "\n"
			s += model.demacro(problem.bodies[0]) + "\n"
			s += r"\end{problem}" + "\n"
			s += r"\vspace{2em}" + "\n\n"
			s += r"\begin{proof}[Solution]" + "\n"
			s += model.demacro(problem.bodies[1]) + "\n"
			s += r"\end{proof}" + "\n"
			s += r"\pagebreak" + "\n\n"
	s += r"\end{document}"
	view.out(s)
