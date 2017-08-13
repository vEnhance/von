import os

def make_preview(full_path):
	if not os.path.exists("/tmp/preview/"):
		os.mkdir("/tmp/preview")
	with open("/tmp/preview/von_preview.tex", "w") as f:
		print(r"\documentclass[11pt]{scrartcl}", file=f)
		print(r"\usepackage{evan}", file=f)
		print(r"\title{VON Preview}", file=f)
		print(r"\begin{document}", file=f)
		print(r"\input{%s}" % full_path, file=f)
		print(r"\end{document}", file=f)
