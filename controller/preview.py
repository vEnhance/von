import os

def make_preview(target):
	if not os.path.exists("/tmp/preview/"):
		os.mkdir("/tmp/preview")
	with open("/tmp/preview/von_preview.tex", "w") as f:
		print >>f, r"\documentclass[11pt]{scrartcl}"
		print >>f, r"\usepackage{evan}"
		print >>f, r"\title{VON Preview}"
		print >>f, r"\begin{document}"
		print >>f, r"\input{%s}" % target
		print >>f, r"\end{document}"
