import re


# Demacro
def demacro(text: str) -> str:
    # TODO this doesn't quite work, but oh well
    replacements: list[tuple[str, str]] = [
        (r"\ii ", r"\item "),
        (r"\ii[", r"\item["),
        (r"\wh", r"\widehat"),
        (r"\wt", r"\widetilde"),
        (r"\ol", r"\overline"),
        (r"\epsilon", r"\eps"),
        (r"\eps", r"\varepsilon"),
        (r"\dang", r"\measuredangle"),
        (r"\dg", r"^{\circ}"),
        (r"\inv", r"^{-1}"),
        (r"\half", r"\frac{1}{2}"),
        (r"\GL", r"\operatorname{GL}"),
        (r"\SL", r"\operatorname{SL}"),
        (r"\NN", r"{\mathbb N}"),
        (r"\ZZ", r"{\mathbb Z}"),
        (r"\CC", r"{\mathbb C}"),
        (r"\RR", r"{\mathbb R}"),
        (r"\QQ", r"{\mathbb Q}"),
        (r"\FF", r"{\mathbb F}"),
        (r"\ts", r"\textsuperscript"),
        (r"\opname", r"\operatorname"),
        (r"\defeq", r"\overset{\text{def}}{=}"),
        (r"\id", r"\operatorname{id}"),
        (r"\ord", r"\operatorname{ord}"),
        (r"\sign", r"\operatorname{sign}"),
        (r"\injto", r"\hookrightarrow"),
        (r"\vdotswithin=", r"\vdots"),
    ]
    s = text
    for short, full in replacements:
        s = s.replace(short, full)
    return s


def remove_soft_newlines(text: str) -> str:
    return re.sub(r"[a-zA-Z]\n[a-zA-Z]", lambda m: m.group(0).replace("\n", " "), text)


def toAOPS(text: str) -> str:
    DIVIDER = "\n" + r"-------------------" + "\n\n"
    text = demacro(text)
    text = text.replace(r"\qedhere", "")
    text = text.replace(r"\begin{asy}", "\n" + "[asy]" + "\n")
    text = text.replace(r"\end{asy}", "\n" + "[/asy]")
    text = text.replace(r"\begin{center}", "")
    text = text.replace(r"\end{center}", "")
    text = text.replace(r"\par ", "\n")
    text = text.replace(r"\item ", "[*]")
    text = text.replace(r"\begin{enumerate}", "[list=1]")
    text = text.replace(r"\end{enumerate}", "[/list]")
    text = text.replace(r"\begin{itemize}", "[list]")
    text = text.replace(r"\end{itemize}", "[/list]")
    text = text.replace(r"\begin{description}", "[list]")
    text = text.replace(r"\end{description}", "[/list]")
    for env in [
        "theorem",
        "claim",
        "lemma",
        "proposition",
        "corollary",
        "definition",
        "remark",
    ]:
        text = text.replace(
            r"\begin{" + env + "*}",
            "\n\n" + "[b][color=red]" + env.title() + ":[/color][/b] ",
        )
        text = text.replace(r"\end{" + env + "*}", "")
        text = text.replace(
            r"\begin{" + env + "}",
            "\n\n" + "[b][color=red]" + env.title() + ":[/color][/b] ",
        )
        text = text.replace(r"\end{" + env + "}", "")
    text = text.replace(r"\begin{proof}", "[i]Proof.[/i] ")
    text = text.replace(r"\end{proof}", r"$\blacksquare$" + "\n")
    text = text.replace(r"\bigskip", DIVIDER)
    text = text.replace(r"\medskip", DIVIDER)
    text = text.replace(r"\#", "#")
    text = text.replace("%\n", "\n")  # strip trailing percent signs
    # Remove Asy opacities, doesn't work on AoPS
    text = re.sub(r"opacity\(0.[0-9]+\)+([^,]+), ", "invisible, ", text)
    # Replace \emph, \textit, et al
    text = re.sub(r"\\emph{([^}]*)}", r"[i]\1[/i]", text)
    text = re.sub(r"\\textit{([^}]*)}", r"[i]\1[/i]", text)
    text = re.sub(r"\\textbf{([^}]*)}", r"[b]\1[/b]", text)
    text = re.sub(
        r"\\paragraph{([^}]*)}", DIVIDER + r"[color=blue][b]\1[/b][/color]", text
    )
    text = re.sub(r"\\subparagraph{([^}]*)}", DIVIDER + r"[b]\1[/b]", text)
    text = re.sub(r"\\url{([^}]*)}", r"[url]\1[/url]", text)
    text = re.sub(r"\\href{([^}]*)}{([^}]*)}", r"[url=\1]\2[/url]", text)
    text = re.sub(
        r"\\item\[([^\]]*)\]", r"[*] [b]\1[/b]", text
    )  # for description items
    text = text.replace(r"\arc", r"\widehat")

    # Join together newlines
    paragraphs = [
        " ".join([line.strip() for line in paragraph.splitlines()]).strip()
        for paragraph in text.split("\n\n")
    ]
    return "\n".join(paragraphs)
