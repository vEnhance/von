import model, view
import os

parser = view.Parser(prog='po',\
		description='Prepares a LaTeX file to send to Po-Shen!')
parser.add_argument('keys', nargs = '+',
		help="The keys of the problem to propose.")
parser.add_argument('-t', '--title', default = 'Problems',
		help="Title of the LaTeX document.")
parser.add_argument('-s', '--subtitle', default = None,
		help="Subtitle of the LaTeX document.")
parser.add_argument('--author', default = 'Evan Chen',
		help="Author of the LaTeX document.")
parser.add_argument('--date', default = r'\today',
		help="Date of the LaTeX document.")
parser.add_argument('-k', '--sourced', action = 'store_const',
		const = True, default = False,
		help="Include the source.")
parser.add_argument('--tex', action='store_const',
		const = True, default = False,
		help="Supply only the TeX source, rather than compiling to PDF.")

LATEX_PREAMBLE = r"""
\usepackage{amsmath,amssymb,amsthm}
\usepackage{hyperref}

\newtheorem{theorem}{Theorem}
\newtheorem{lemma}[theorem]{Lemma}
\newtheorem{proposition}[theorem]{Proposition}
\newtheorem{corollary}[theorem]{Corollary}
\newtheorem*{theorem*}{Theorem}
\newtheorem*{lemma*}{Lemma}
\newtheorem*{proposition*}{Proposition}
\newtheorem*{corollary*}{Corollary}

\theoremstyle{definition}
\newtheorem{problem}{Problem}

\newtheorem{claim}[theorem]{Claim}
\newtheorem{conjecture}[theorem]{Conjecture}
\newtheorem{definition}[theorem]{Definition}
\newtheorem{fact}[theorem]{Fact}
\newtheorem{answer}[theorem]{Answer}
\newtheorem{case}[theorem]{Case}
\newtheorem{ques}[theorem]{Question}
\newtheorem{exercise}[theorem]{Exercise}
\newtheorem*{answer*}{Answer}
\newtheorem*{case*}{Case}
\newtheorem*{claim*}{Claim}
\newtheorem*{conjecture*}{Conjecture}
\newtheorem*{definition*}{Definition}
\newtheorem*{fact*}{Fact}
\newtheorem*{joke*}{Joke}
\newtheorem*{ques*}{Question}
\newtheorem*{exercise*}{Exercise}
\newtheorem*{problem*}{Problem}

\usepackage{asymptote}
\begin{asydef}
import olympiad;
import cse5;
pointpen = black;
pathpen = black;
pathfontpen = black;
anglepen = black;
anglefontpen = black;
pointfontsize = 10;
defaultpen(fontsize(10pt));
size(8cm); // set a reasonable default
usepackage("amsmath");
usepackage("amssymb");
settings.tex="latex";
settings.outformat="pdf";
\end{asydef}

% The below really should be scrlayer-scrpage
% but a lot of old distros don't have this yet

\usepackage[headsepline]{scrpage2}
\addtolength{\textheight}{3.14cm}
\setlength{\footskip}{0.5in}
\setlength{\headsep}{10pt}
\lehead{\normalfont\footnotesize\textbf{AUTHOR}}
\lohead{\normalfont\footnotesize\textbf{AUTHOR}}
\rehead{\normalfont\footnotesize\textbf{TITLE}}
\rohead{\normalfont\footnotesize\textbf{TITLE}}
\pagestyle{scrheadings}

"""

def main(self, argv):
	opts = parser.process(argv)
	s = r"\documentclass[11pt]{scrartcl}" + "\n"
	s += LATEX_PREAMBLE.replace("AUTHOR", opts.author).replace("TITLE", opts.title)
	s += r"\begin{document}" + "\n"
	s += r"\title{" + opts.title + "}" + "\n"
	if opts.subtitle is not None:
		s += r"\subtitle{" + opts.subtitle + "}" + "\n"
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
			if opts.sourced:
				s += r"\begin{problem}[" + key + "]\n"
			else:
				s += r"\begin{problem}" + "\n"
			s += model.demacro(problem.bodies[0]) + "\n"
			s += r"\end{problem}" + "\n"
			s += r"\vspace{2em}" + "\n\n"
			s += r"\begin{proof}[Solution]" + "\n"
			s += model.demacro(problem.bodies[1]) + "\n"
			s += r"\end{proof}" + "\n"
			s += r"\pagebreak" + "\n\n"
	s += r"\end{document}"
	if opts.tex:
		view.out(s)
	else:
		with open("/tmp/po.tex", "w") as f:
			print >>f, s
		os.chdir('/tmp')
		os.system("latexmk -pv /tmp/po.tex;")
