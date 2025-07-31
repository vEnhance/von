# VON: vEnhance's Olympiad Navigator

## A problem database written in Python

![Language: Python](https://img.shields.io/github/languages/top/vEnhance/von)
![License](https://img.shields.io/github/license/vEnhance/von)
![Last commit](https://img.shields.io/github/last-commit/vEnhance/von)
[<img src="https://github.com/vEnhance/von/actions/workflows/ci.yml/badge.svg" alt="von status">](https://github.com/vEnhance/von/actions)
[<img src="https://github.com/vEnhance/von/actions/workflows/codeql-analysis.yml/badge.svg" alt="von status">](https://github.com/vEnhance/von/actions)

[<img src="https://img.shields.io/badge/python%20style-black-000000.svg" alt="style: black">](https://github.com/psf/black)
[<img src="https://img.shields.io/badge/types-pyright-00cca7.svg" alt="types: pyright">](https://github.com/Microsoft/pyright)
[<img src="https://img.shields.io/endpoint?url=https://raw.githubusercontent.com/astral-sh/ruff/main/assets/badge/v2.json" alt="lint: ruff">](https://github.com/astral-sh/ruff)
![Forks](https://img.shields.io/github/forks/vEnhance/von)
![Stars](https://img.shields.io/github/stars/vEnhance/von)

VON is a Python script I wrote in order to help me manage
my centralized database of solutions to olympiad problems.

There is no graphical user interface; it is based on standard command line.
Therefore, it will work best on Linux systems.
Windows users may experience some grief,
and Windows users unfamiliar with command line are
[going to have a bad time](https://undertale.wiki/w/Sans).

I haven't gotten around to properly documenting this,
but posting it by popular request.
Here are a few hints. Pull requests to improve this documentation are welcome.

## Installation

1. Run `pip install vondb` (note the package name on PyPI is `vondb` and not `von`;
   but the command and module are named `von`).
   (Here is the [PyPI listing](https://pypi.org/project/vondb/).)
   Or if you're on Arch Linux, install from [python-vondb in AUR](https://aur.archlinux.org/packages/python-vondb).
2. When first run, the program will (try to) create a configuration file
   `~/.config/von/config` or similar if it does not exist.
   You should then edit that file and choose some values.
   The program will be unlikely to work correctly
   until after you have chosen e.g. the `base_path` parameter.
3. Optional LaTeX integration uses [von.sty][vonsty] and PythonTeX.
   The optional previewer requires [evan.sty][evansty]. (See below for details.)
   This assumes a working LaTeX compiler with `latexmk` installed.
   (I recommend [TeX Live][texlive]).
4. If fuzzy searching is desired (optional),
   install [fzf](https://github.com/junegunn/fzf).

## Help

Use `von help` to display full help.
The following information is mostly a subset of it.

To exit VON, type an EOF character (usually Ctrl-D).

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
tags:  [favorite, construct, medium]
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

Alternatively, the `f` command opens an interface which
allows you to fuzzily search for a problem across problems with a preview.
It is an alias for `show` without arguments.

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
To fix this run `von nuke` to recompile the entire index.
`von nuke` is also useful in the cases of deleting a file
and thus problem from the index.

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
