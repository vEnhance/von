import re

# Demacro
def demacro(text):
	# TODO this doesn't quite work, e.g. \epsilon -> \epsilonilon
	replacements = [
		(r"\ii",			 r"\item") ,
		(r"\wh",			 r"\widehat") ,
		(r"\ol",			 r"\overline"),
		(r"\eps",			r"\varepsilon"),
		(r"\dang",		 r"\measuredangle"),
		(r"\dg",			 r"^{\circ}"),
		(r"\inv",			r"^{-1}"),
		(r"\half",		 r"\frac{1}{2}"),
		(r"\NN",			 r"{\mathbb N}"),
		(r"\ZZ",			 r"{\mathbb Z}"),
		(r"\CC",			 r"{\mathbb C}"),
		(r"\RR",			 r"{\mathbb R}"),
		(r"\QQ",			 r"{\mathbb Q}"),
		(r"\FF",			 r"{\mathbb F}"),
		(r"\opname",	 r"\operatorname"),
		(r"\defeq",		r"\overset{\text{def}}{=}"),
		(r"\id",			 r"\operatorname{id}"),
		(r"\injto",		r"\hookrightarrow"),
		(r"\vdotswithin=", r"\vdots"),
	]
	s = text
	for short, full in replacements:
		s = s.replace(short, full)
	return s

def toAOPS(text):
	text = demacro(text)
	text = text.replace(r"\begin{asy}", "[asy]")
	text = text.replace(r"\end{asy}", "[/asy]")
	text = text.replace(r"\begin{center}", "\n")
	text = text.replace(r"\end{center}", "\n")
	text = text.replace(r"\par ", "\n\n")
	text = text.replace(r"\item ", "[*]")
	text = text.replace(r"\begin{enumerate}", "[list=1]")
	text = text.replace(r"\end{enumerate}", "[/list]")
	text = text.replace(r"\begin{itemize}", "[list]")
	text = text.replace(r"\end{itemize}", "[/list]")
	for env in ['theorem', 'claim', 'lemma', 'proposition', 'corollary', 'definition', 'remark']:
		text = text.replace(r"\begin{" + env + "*}", "\n[b]" + env.title() + "[/b]: ")
		text = text.replace(r"\end{" + env + "*}", "")
		text = text.replace(r"\begin{" + env + "}", "\n[b]" + env.title() + "[/b]: ")
		text = text.replace(r"\end{" + env + "}", "")
	text = text.replace(r"\begin{proof}", "\n[i]Proof.[/i] ")
	text = text.replace(r"\end{proof}", r"$\blacksquare$" + "\n")
	text = text.replace(r"\#", "#")
	text = re.sub(r"\\emph{([^}]*)}", r"[i]\1[/i]", text)
	text = re.sub(r"\\textit{([^}]*)}", r"[i]\1[/i]", text)
	text = re.sub(r"\\textbf{([^}]*)}", r"[b]\1[/b]", text)
	text = re.sub(r"\\url{([^}]*)}", r"[url]\1[/url]", text)
	text = re.sub(r"\\href{([^}]*)}{([^}]*)}", r"[url=\1]\2[/url]", text)

	# Join together newlines
	paragraphs = [_.strip().replace("\n", " ") for _ in text.split('\n\n')]
	return '\n\n'.join(paragraphs)
