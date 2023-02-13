# VON: vEnhance's Olympiad Navigator

## A problem database written in Python

![Language: Python](https://img.shields.io/github/languages/top/vEnhance/von)
![License](https://img.shields.io/github/license/vEnhance/von)
![Last commit](https://img.shields.io/github/last-commit/vEnhance/von)
[<img src="https://github.com/vEnhance/von/actions/workflows/ci.yml/badge.svg" alt="von status">](https://github.com/vEnhance/von/actions)
[<img src="https://github.com/vEnhance/von/actions/workflows/codeql-analysis.yml/badge.svg" alt="von status">](https://github.com/vEnhance/von/actions)

[<img src="https://img.shields.io/badge/python%20style-black-000000.svg" alt="Python style: black">](https://github.com/psf/black)
[<img src="https://img.shields.io/badge/types-pyright-00cca7.svg" alt="types: pyright">](https://github.com/PyCQA/pyflakes)
[<img src="https://img.shields.io/badge/types-mypy-00cca7.svg" alt="types: mypy">](http://mypy-lang.org/)
[<img src="https://img.shields.io/badge/lint-pyflakes-ff69b4.svg" alt="lint: pyflakes">](https://github.com/PyCQA/pyflakes)
![Forks](https://img.shields.io/github/forks/vEnhance/von)
![Stars](https://img.shields.io/github/stars/vEnhance/von)

VON is a Python script I wrote in order to help me manage
the problems and solutions to olympiad databases.
There is no graphical user interface, and it is based on the command line.
It is designed to run on Linux systems.

I haven't gotten around to properly documenting this,
but posting it by popular request.
Here are a few hints:

## Setup

This program assumes you have:

- Python 3 installed, and
- A working LaTeX compiler with `latexmk` installed.
  (I recommend [TeX Live][texlive]).

1. You **must** create a copy of `rc.py` based on `rc.py.EXAMPLE`.
   This is the "settings" file for the script.
2. This directory should be included under PYTHONPATH,
   and invoked by `python -m von` (to get an interactive terminal).
   If you only want to issue one command, you can also type it directly,
   e.g. `python -m von help` will list the help and exit.
3. You may need to `pip install -r requirements.txt`.
   On Windows, you want to `pip install -r requirements-windows.txt`.
4. LaTeX integration uses [von.sty][vonsty].
   The previewer requires [evan.sty][evansty].
   (See below for details.)

## Help

Use `von help` to display full help.
The following information is mostly a subset of it.

To exit VON, type an EOF character.

## Storing problems and solutions

- `add "Shortlist 2016 G2"`: add problem to database

1. Problems are stored in TeX files in `VON_BASE_PATH`. You can
   keep subdirectories in here, as well, to organize those files.
2. Problems and solutions are separated using `SEPARATOR` in `rc.py`,
   which by default is three dashes padded by newlines.
   So when entering new problems, write the statement, the separator,
   and then the solution.
3. Actually more generally, each problem and solution is separated into
   several "bodies", delimited by the separator.
   It's basically assumed that 0'th body is the problem statement
   and the 1'st body is the solution,
   but you can have further bodies for other purposes too.

## Meta-data

- `edit "Shortlist 2016 G2"` or `edit "16SLG2"`: edit entry for problem in database

1. Meta-data is stored at the top of each file after being added.
2. Problems must have a _source_ like "Shortlist 2016 G2".
3. Problems should also have a description, and a set of tags.
   If a tag is specified as a sorting tag in `rc.py`,
   it will be displayed differently,
   but otherwise functionally equivalently.
4. Problems can also have an "author" attribute, which is displayed.
5. Problems can also have a "hardness" attribute, an integer,
   which is displayed differently by the user interface.
   You can pick any scale you want; [here is mine][mohs].
6. Problems can be marked as _SECRET_.
   Problems marked as SECRET will appear in searches,
   but will be replaced by placeholders (unless `--brave` is passed).

   There are two ways to mark a problem as SECRET:

   - Include `SECRET` as a substring of the problem's source.
   - Include `secret` as one of the problem's tags.

An example of an entry:

```
desc:  $5^n$ has six consecutive zeros
author: Evan Chen
source:  JMO 2016/2
tags:  [wishful, favorite, mods, construct, mine, 2016-04, free, brave]
hardness: 25

---

Prove that there exists a positive integer $n < 10^6$
such that $5^n$ has six consecutive zeros in its decimal representation.

---

We will prove that $\boxed{n = 20 + 2^{19} = 524308}$ fits the bill.

... (rest of solution) ...

```

## Searching

The `search` command searches everything.
Use `search --help` for a lot of options.

- `search "Shortlist 2016"`: search for problems with "Shortlist 2016"
- `search -t anglechase`: searches for problems tagged `anglechase`

The `s` command is a shorthand for `search`.

You can use `search --everything` to list all problems.

## Displaying problems

When using various commands,
every problem can be identified in two ways.
One is by the source, such as "Shortlist 2016 G2".
Alternatively, when one uses the search command,
the results are indexed by positive integers,
and those indices can be used instead of the source.
For example, `show 3` will display the 3rd problem in search results.

- `show 3`: Print the 3rd problem
- `po 3`: Produces a TeX/PDF of the problem and solution.

Use `show --help` and `po --help` for more details.

## Recompiling the index

Sometimes the list of problems and file paths might become
messed up in some way (for example, if you move a file).
To fix this run `von index` to recompile the entire index.

## Preview

When running `von add` or `von edit` on Linux,
the program creates the file `/tmp/preview/von_preview.tex`
which is a wrapper file that inputs the currently edited problem.
If you use [latexmk][latexmk] (which I recommend!),
you can run `latexmk -pvc` on this in order to render what you are typing.
This makes it possible to work simultaneously with the input
and output that you are adding in to `von`.

## LaTeX integration

If you have [von.sty][vonsty] and [latexmk][latexmk],
then by using a similar mechanic to Asymptote,
you can also directly query the database for problems.
You should add a `pythontex` routine to your `.latexmkrc` for this to auto-work;
an example might be:

```perl
sub pythontex {
    system("pythontex --runall true \"$_[0]\"");
    system("touch \$(basename \"$_[0]\").pytxmcr");
    return;
}
add_cus_dep("pytxcode", "pytxmcr", 0, "pythontex");
```

The basic syntax is that `\voninclude{source}` will
include the problem statement (0th body),
while `\voninclude[1]{source}` will include the 1st body (the solution), etc.

Of course, this would most commonly be used with theorem environments,
so you can use some shortcuts to this effect.
The three possible shortcuts are:

- `\von{X}` is shorthand for `\begin{problem}[X] \voninclude{X} \end{problem}`
- `\von[text]{X}` is shorthand for `\begin{problem}[text] \voninclude{X} \end{problem}`
- `\von*{X}` is shorthand for `\begin{problem} \voninclude{X} \end{problem}`

Of course, the string `problem` might want to be changed,
if you are using a differently named theorem environment.
You can change this by running `\renewcommand{\vonenvname}{name}`.

[vonsty]: https://github.com/vEnhance/dotfiles/blob/master/texmf/tex/latex/von/von.sty
[evansty]: https://github.com/vEnhance/dotfiles/blob/master/texmf/tex/latex/evan/evan.sty
[latexmk]: http://personal.psu.edu/~jcc8/software/latexmk/
[mohs]: https://web.evanchen.cc/upload/MOHS-hardness.pdf
[texlive]: https://www.tug.org/texlive/
