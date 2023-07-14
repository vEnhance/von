import logging
import os

from .. import model, strparse, view
from ..fzf import fzf_choose
from ..rc import VON_DEFAULT_AUTHOR, VON_POST_OUTPUT_DIR

parser = view.Parser(prog="po", description="Prepares a LaTeX file to send to Po-Shen!")
parser.add_argument("keys", nargs="*", help="The keys of the problem to propose.")
parser.add_argument("-t", "--title", default=None, help="Title of the LaTeX document.")
parser.add_argument(
    "-s", "--subtitle", default=None, help="Subtitle of the LaTeX document."
)
parser.add_argument(
    "--author", default=VON_DEFAULT_AUTHOR, help="Author of the LaTeX document."
)
parser.add_argument("--date", default=r"\today", help="Date of the LaTeX document.")
parser.add_argument(
    "-k",
    "--sourced",
    action="store_true",
    help="Include the source.",
)
parser.add_argument(
    "--tex",
    action="store_true",
    help="Supply only the TeX source, rather than compiling to PDF.",
)
parser.add_argument(
    "-f",
    "--filename",
    default=None,
    help="Filename for the file to produce (defaults to po.tex).",
)

LATEX_PREAMBLE = r"""\usepackage{amsmath,amssymb,amsthm}
\usepackage[minimal]{yhmath}
\usepackage{derivative}

\PassOptionsToPackage{usenames,svgnames,dvipsnames}{xcolor}
\usepackage{thmtools}
\usepackage[framemethod=TikZ]{mdframed}
\usepackage{listings}

\mdfdefinestyle{mdbluebox}{%
    roundcorner = 10pt,
    linewidth=1pt,
    skipabove=12pt,
    innerbottommargin=9pt,
    skipbelow=2pt,
    linecolor=blue,
    nobreak=true,
    backgroundcolor=TealBlue!5,
}
\declaretheoremstyle[
    headfont=\sffamily\bfseries\color{MidnightBlue},
    mdframed={style=mdbluebox},
    headpunct={\\[3pt]},
    postheadspace={0pt}
]{thmbluebox}

\mdfdefinestyle{mdredbox}{%
    linewidth=0.5pt,
    skipabove=12pt,
    frametitleaboveskip=5pt,
    frametitlebelowskip=0pt,
    skipbelow=2pt,
    frametitlefont=\bfseries,
    innertopmargin=4pt,
    innerbottommargin=8pt,
    nobreak=true,
    backgroundcolor=Salmon!5,
    linecolor=RawSienna,
}
\declaretheoremstyle[
    headfont=\bfseries\color{RawSienna},
    mdframed={style=mdredbox},
    headpunct={\\[3pt]},
    postheadspace={0pt},
]{thmredbox}

\mdfdefinestyle{mdgreenbox}{%
    skipabove=8pt,
    linewidth=2pt,
    rightline=false,
    leftline=true,
    topline=false,
    bottomline=false,
    linecolor=ForestGreen,
    backgroundcolor=ForestGreen!5,
}
\declaretheoremstyle[
    headfont=\bfseries\sffamily\color{ForestGreen!70!black},
    bodyfont=\normalfont,
    spaceabove=2pt,
    spacebelow=1pt,
    mdframed={style=mdgreenbox},
    headpunct={ --- },
]{thmgreenbox}

\mdfdefinestyle{mdblackbox}{%
    skipabove=8pt,
    linewidth=3pt,
    rightline=false,
    leftline=true,
    topline=false,
    bottomline=false,
    linecolor=black,
    backgroundcolor=RedViolet!5!gray!5,
}
\declaretheoremstyle[
    headfont=\bfseries,
    bodyfont=\normalfont\small,
    spaceabove=0pt,
    spacebelow=0pt,
    mdframed={style=mdblackbox}
]{thmblackbox}

\declaretheorem[style=thmbluebox,name=Theorem]{theorem}
\declaretheorem[style=thmbluebox,name=Lemma,sibling=theorem]{lemma}
\declaretheorem[style=thmbluebox,name=Proposition,sibling=theorem]{proposition}
\declaretheorem[style=thmbluebox,name=Corollary,sibling=theorem]{corollary}
\declaretheorem[style=thmbluebox,name=Theorem,numbered=no]{theorem*}
\declaretheorem[style=thmbluebox,name=Lemma,numbered=no]{lemma*}
\declaretheorem[style=thmbluebox,name=Proposition,numbered=no]{proposition*}
\declaretheorem[style=thmbluebox,name=Corollary,numbered=no]{corollary*}

\declaretheorem[style=thmgreenbox,name=Claim,sibling=theorem]{claim}
\declaretheorem[style=thmgreenbox,name=Claim,numbered=no]{claim*}
\declaretheorem[style=thmredbox,name=Example,sibling=theorem]{example}
\declaretheorem[style=thmredbox,name=Example,numbered=no]{example*}
\declaretheorem[style=thmblackbox,name=Remark,sibling=theorem]{remark}
\declaretheorem[style=thmblackbox,name=Remark,numbered=no]{remark*}

\theoremstyle{definition}
\newtheorem{conjecture}[theorem]{Conjecture}
\newtheorem{definition}[theorem]{Definition}
\newtheorem{fact}[theorem]{Fact}
\newtheorem{ques}[theorem]{Question}
\newtheorem{exercise}[theorem]{Exercise}
\newtheorem{problem}[theorem]{Problem}

\newtheorem*{conjecture*}{Conjecture}
\newtheorem*{definition*}{Definition}
\newtheorem*{fact*}{Fact}
\newtheorem*{ques*}{Question}
\newtheorem*{exercise*}{Exercise}
\newtheorem*{problem*}{Problem}

\usepackage{mathtools}
\usepackage{hyperref}
\usepackage[shortlabels]{enumitem}
\usepackage{multirow}
\usepackage{ellipsis}

\usepackage{epic} % diagrams
\usepackage{tikz-cd} % diagrams
\usepackage{asymptote} % more diagrams
\begin{asydef}
defaultpen(fontsize(10pt));
size(8cm); // set a reasonable default
usepackage("amsmath");
usepackage("amssymb");
settings.tex="pdflatex";
settings.outformat="pdf";
// Replacement for olympiad+cse5 which is not standard
import geometry;
// recalibrate fill and filldraw for conics
void filldraw(picture pic = currentpicture, conic g, pen fillpen=defaultpen, pen drawpen=defaultpen)
    { filldraw(pic, (path) g, fillpen, drawpen); }
void fill(picture pic = currentpicture, conic g, pen p=defaultpen)
    { filldraw(pic, (path) g, p); }
// some geometry
pair foot(pair P, pair A, pair B) { return foot(triangle(A,B,P).VC); }
pair orthocenter(pair A, pair B, pair C) { return orthocentercenter(A,B,C); }
pair centroid(pair A, pair B, pair C) { return (A+B+C)/3; }
// cse5 abbreviations
path CP(pair P, pair A) { return circle(P, abs(A-P)); }
path CR(pair P, real r) { return circle(P, r); }
pair IP(path p, path q) { return intersectionpoints(p,q)[0]; }
pair OP(path p, path q) { return intersectionpoints(p,q)[1]; }
path Line(pair A, pair B, real a=0.6, real b=a) { return (a*(A-B)+A)--(b*(B-A)+B); }
// cse5 more useful functions
picture CC() {
    picture p=rotate(0)*currentpicture;
    currentpicture.erase();
    return p;
}
pair MP(Label s, pair A, pair B = plain.S, pen p = defaultpen) {
    Label L = s;
    L.s = "$"+s.s+"$";
    label(s, A, B, p);
    return A;
}
pair Drawing(Label s = "", pair A, pair B = plain.S, pen p = defaultpen) {
    dot(MP(s, A, B, p), p);
    return A;
}
path Drawing(path g, pen p = defaultpen, arrowbar ar = None) {
    draw(g, p, ar);
    return g;
}
\end{asydef}

\usepackage[headsepline]{scrlayer-scrpage}
\addtolength{\textheight}{3.14cm}
\setlength{\footskip}{0.5in}
\setlength{\headsep}{10pt}
\lehead{\normalfont\footnotesize\textbf{AUTHOR}}
\lohead{\normalfont\footnotesize\textbf{AUTHOR}}
\rehead{\normalfont\footnotesize\textbf{TITLE}}
\rohead{\normalfont\footnotesize\textbf{TITLE}}
\pagestyle{scrheadings}

\providecommand{\arc}[1]{\wideparen{#1}}
\newcommand{\hrulebar}{
\par\hspace{\fill}\rule{0.95\linewidth}{.7pt}\hspace{\fill}
\par\nointerlineskip \vspace{\baselineskip}}

\addtokomafont{paragraph}{\color{orange!35!black}\P\ }"""


def main(self: object, argv: list[str]):
    opts = parser.process(argv)

    keys = opts.keys
    if len(keys) == 0:
        keys = [fzf_choose()]

    # Better default title:
    if opts.title is not None:
        title = opts.title
    elif len(keys) == 1:
        entry = model.getEntryByKey(keys[0])
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
    for key in keys:
        entry = model.getEntryByKey(key)
        if entry is None:
            logging.error(key + " not found")
        elif entry.secret and not opts.brave:
            logging.error(f"Problem `{entry.source}` not shown without --brave")
            return
        else:
            problem = entry.full
            s += r"\begin{problem}" if len(keys) > 1 else r"\begin{problem*}"
            if opts.sourced:
                s += "[" + entry.source + "]"
            s += "\n"
            s += strparse.demacro(problem.bodies[0]) + "\n"
            s += r"\end{problem}" if len(keys) > 1 else r"\end{problem*}"
            if entry.url:
                s += r"\noindent\emph{Link}: \url{" + entry.url + "}" + "\n"
            if len(problem.bodies) > 1:
                s += "\n" + r"\hrulebar" + "\n\n"
                s += strparse.demacro(problem.bodies[1]) + "\n"
            s += r"\pagebreak" + "\n\n"
    s += r"\end{document}"
    if opts.tex:
        view.out(s)
    else:
        if opts.filename is not None:
            fname = opts.filename
        elif len(keys) == 1:
            fname = view.file_escape(title)
        else:
            fname = "po"
        if not os.path.exists(VON_POST_OUTPUT_DIR):
            os.mkdir(VON_POST_OUTPUT_DIR)
        filepath = os.path.join(VON_POST_OUTPUT_DIR, f"{fname}.tex")
        with open(filepath, "w") as f:
            print(s, file=f)
        os.chdir(VON_POST_OUTPUT_DIR)
        os.system("latexmk -pv %s" % filepath)
