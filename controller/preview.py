import os

from ..rc import USER_OS, VON_DEFAULT_AUTHOR, VON_PREVIEW_PATH


def make_preview(full_path: str):
    if not os.path.exists(os.path.dirname(VON_PREVIEW_PATH)):
        os.mkdir(os.path.dirname(VON_PREVIEW_PATH))
    if USER_OS == "windows":
        full_path = full_path.replace("\\", "/")  # lmao

    with open(VON_PREVIEW_PATH, "w") as f:
        print(r"\documentclass[11pt]{scrartcl}", file=f)
        print(r"\usepackage[sexy,diagrams]{evan}", file=f)
        print(r"\author{" + VON_DEFAULT_AUTHOR + "}", file=f)

        print(r"\title{VON Preview}", file=f)
        print(r"\begin{document}", file=f)
        print(r"\input{" + full_path + "}", file=f)
        print(r"\end{document}", file=f)
