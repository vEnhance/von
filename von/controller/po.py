import logging
import os
import subprocess

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
\usepackage{listings}

\usepackage{keytheorems}
\usepackage{tcolorbox}
\tcbuselibrary{skins,breakable,hooks}
% text right after \end{theorem} continues the same paragraph, i.e. no indent
\makeatletter
\AddToHook{env/tcolorbox/after}{\@doendpe}
\makeatother

\tcbset{
  bluebox/.style={
    enhanced,
    arc=9pt, outer arc=10pt,
    colframe=blue, colback=TealBlue!5, boxrule=1pt,
    before skip=12pt, after skip=2pt,
    left=10pt, right=10pt, top=6pt, bottom=9pt,
  },
  redbox/.style={
    enhanced, sharp corners,
    colframe=RawSienna, colback=Salmon!5, boxrule=0.5pt,
    before skip=12pt, after skip=2pt,
    left=10pt, right=10pt, top=4pt, bottom=8pt,
  },
  greenbox/.style={
    enhanced, breakable, sharp corners,
    boxrule=0pt, frame hidden,
    borderline west={2pt}{0pt}{ForestGreen},
    colback=ForestGreen!5,
    before skip=8pt, after skip=0pt,
    left=10pt, right=10pt,
  },
  blackbox/.style={
    enhanced, breakable, sharp corners,
    boxrule=0pt, frame hidden,
    borderline west={3pt}{0pt}{black},
    colback=RedViolet!5!gray!5,
    before skip=8pt,
    left=10pt, right=10pt,
  },
}
\declarekeytheoremstyle{thmbluebox}{
  headfont=\sffamily\bfseries\color{MidnightBlue},
  bodyfont=\normalfont,
  tcolorbox-no-titlebar={bluebox},
  headpunct={\\[3pt]},
  postheadspace={0pt},
}
\declarekeytheoremstyle{thmredbox}{
  headfont=\bfseries\color{RawSienna},
  bodyfont=\normalfont,
  tcolorbox-no-titlebar={redbox},
  headpunct={\\[3pt]},
  postheadspace={0pt},
}
\declarekeytheoremstyle{thmgreenbox}{
  headfont=\bfseries\sffamily\color{ForestGreen!70!black},
  bodyfont=\normalfont,
  tcolorbox-no-titlebar={greenbox},
  headpunct={ --- },
}
\declarekeytheoremstyle{thmblackbox}{
  headfont=\bfseries,
  bodyfont=\normalfont\small,
  tcolorbox-no-titlebar={blackbox},
}

\newkeytheorem{theorem}[style=thmbluebox,name=Theorem,parent=section]
\newkeytheorem{theorem*}[style=thmbluebox,name=Theorem,numbered=no]
\newkeytheorem{algorithm*}[style=thmgreenbox,name=Algorithm,numbered=no]
\newkeytheorem{algorithm}[style=thmgreenbox,name=Algorithm,sibling=theorem]
\newkeytheorem{claim*}[style=thmgreenbox,name=Claim,numbered=no]
\newkeytheorem{claim}[style=thmgreenbox,name=Claim,sibling=theorem]
\newkeytheorem{corollary*}[style=thmbluebox,name=Corollary,numbered=no]
\newkeytheorem{corollary}[style=thmbluebox,name=Corollary,sibling=theorem]
\newkeytheorem{example*}[style=thmredbox,name=Example,numbered=no]
\newkeytheorem{example}[style=thmredbox,name=Example,sibling=theorem]
\newkeytheorem{lemma*}[style=thmbluebox,name=Lemma,numbered=no]
\newkeytheorem{lemma}[style=thmbluebox,name=Lemma,sibling=theorem]
\newkeytheorem{proposition*}[style=thmbluebox,name=Proposition,numbered=no]
\newkeytheorem{proposition}[style=thmbluebox,name=Proposition,sibling=theorem]
\newkeytheorem{remark*}[style=thmblackbox,name=Remark,numbered=no]
\newkeytheorem{remark}[style=thmblackbox,name=Remark,sibling=theorem]
\theoremstyle{definition}
\newtheorem*{answer*}{Answer}
\newtheorem*{conjecture*}{Conjecture}
\newtheorem*{definition*}{Definition}
\newtheorem*{exercise*}{Exercise}
\newtheorem*{fact*}{Fact}
\newtheorem*{problem*}{Problem}
\newtheorem*{ques*}{Question}
\newtheorem{answer}[theorem]{Answer}
\newtheorem{conjecture}[theorem]{Conjecture}
\newtheorem{definition}[theorem]{Definition}
\newtheorem{exercise}[theorem]{Exercise}
\newtheorem{fact}[theorem]{Fact}
\newtheorem{problem}[theorem]{Problem}
\newtheorem{ques}[theorem]{Question}

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
        subprocess.run(["latexmk", "-pv", filepath])
