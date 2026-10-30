import os

from ..rc import config


def make_preview(full_path: str):
    preview_path = config().preview_path
    if not os.path.exists(os.path.dirname(preview_path)):
        os.mkdir(os.path.dirname(preview_path))
    if config().os == "windows":
        full_path = full_path.replace("\\", "/")  # lmao

    with open(preview_path, "w") as f:
        print(r"\documentclass[11pt]{scrartcl}", file=f)
        print(r"\usepackage[sexy]{evan}", file=f)
        print(r"\author{" + config().name + "}", file=f)

        print(r"\title{VON Preview}", file=f)
        print(r"\begin{document}", file=f)
        print(r"\input{" + full_path + "}", file=f)
        print(r"\end{document}", file=f)
