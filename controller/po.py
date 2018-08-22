from .. import model, view
import os

parser = view.Parser(prog='po',\
		description='Prepares a LaTeX file to send to Po-Shen!')
parser.add_argument('keys', nargs = '+',
		help="The keys of the problem to propose.")
parser.add_argument('-t', '--title', default = None,
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
parser.add_argument('-f', '--filename', default = None,
		help="Filename for the file to produce (defaults to po.tex).")

LATEX_PREAMBLE = r"""
\usepackage{amsmath,amssymb,amsthm}
\usepackage{mathtools}
\usepackage{hyperref}
\usepackage[shortlabels]{enumitem}

\newtheorem{theorem}{Theorem}
\newtheorem{lemma}[theorem]{Lemma}
\newtheorem{proposition}[theorem]{Proposition}
\newtheorem{corollary}[theorem]{Corollary}
\newtheorem*{theorem*}{Theorem}
\newtheorem*{lemma*}{Lemma}
\newtheorem*{proposition*}{Proposition}
\newtheorem*{corollary*}{Corollary}

\theoremstyle{definition}

\newtheorem{claim}[theorem]{Claim}
\newtheorem{conjecture}[theorem]{Conjecture}
\newtheorem{definition}[theorem]{Definition}
\newtheorem{fact}[theorem]{Fact}
\newtheorem{answer}[theorem]{Answer}
\newtheorem{case}[theorem]{Case}
\newtheorem{ques}[theorem]{Question}
\newtheorem{exercise}[theorem]{Exercise}
\newtheorem{problem}{Problem}
\newtheorem{remark}{Remark}
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
\newtheorem*{remark*}{Remark}

\usepackage{epic} % diagrams
\usepackage{tikz-cd} % diagrams
\usepackage{asymptote} % more diagrams
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

\newcommand{\hrulebar}{
  \par\hspace{\fill}\rule{0.95\linewidth}{.7pt}\hspace{\fill}
  \par\nointerlineskip \vspace{\baselineskip}
}

"""

def main(self, argv):
	opts = parser.process(argv)

	# Better default title:
	if opts.title is not None:
		title = opts.title
	elif len(opts.keys) == 1:
		entry = model.getEntryByKey(opts.keys[0])
		if entry is not None:
			title = entry.source
		else:
			title = "Solution"
	else:
		title = "Solutions"

	s = r"\documentclass[11pt]{scrartcl}" + "\n"
	s += LATEX_PREAMBLE.replace("AUTHOR", opts.author).replace("TITLE", title)
	s += r"\begin{document}" + "\n"
	s += r"\title{" + title + "}" + "\n"
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
		elif entry.secret and not opts.brave:
			view.error("Problem `%s` not shown without --brave" %entry.source)
			return
		else:
			problem = entry.full
			s += r"\begin{problem}" if len(opts.keys) > 1 \
					else r"\begin{problem*}"
			if opts.sourced:
				s += "[" + entry.source + "]"
			s += "\n"
			s += model.demacro(problem.bodies[0]) + "\n"
			s += r"\end{problem}" if len(opts.keys) > 1 \
					else r"\end{problem*}"
			s += "\n" + r"\hrulebar" + "\n\n"
			s += model.demacro(problem.bodies[1]) + "\n"
			s += r"\pagebreak" + "\n\n"
	s += r"\end{document}"
	if opts.tex:
		view.out(s)
	else:
		if opts.filename is not None:
			fname = opts.filename
		elif len(opts.keys) == 1:
			fname = view.file_escape(title)
		else:
			fname = 'po'
		if not os.path.exists("/tmp/po/"):
			os.mkdir("/tmp/po")
		with open("/tmp/po/%s.tex" %fname, "w") as f:
			print(s, file=f)
		os.chdir('/tmp/po')
		os.system("latexmk -pv /tmp/po/%s.tex;" %fname)
