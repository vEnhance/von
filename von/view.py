import argparse
import string
import sys
from dataclasses import dataclass
from typing import Any

from .model import PickleMappingEntry, Problem
from .puid import inferPUID
from .rc import config
from .termcolors import TERM_COLOR

if sys.platform == "win32":
    from colorama import init  # type: ignore

    init()


def APPLY_COLOR(color_name: str, s: str, enabled: bool = True):
    if enabled is False or config().color is False:
        return s
    num_leading_spaces = len(s) - len(s.lstrip())
    return (
        " " * num_leading_spaces
        + TERM_COLOR[color_name]
        + s.lstrip()
        + TERM_COLOR["RESET"]
    )


def file_escape(s: str):
    s = s.replace("/", "-")
    s = s.replace(" ", "")
    s = "".join([_ for _ in s if _ in string.ascii_letters + string.digits + "-"])
    if s == "":
        s += "emptyname"
    return s


def get_author_initials(author: str) -> str:
    author_words = author.replace(",", " ,").split(" ")
    if len(author_words) == 0:
        return "?"
    elif len(author_words) == 1:
        a = author_words[0]
        if capitals := "".join(_ for _ in a if _ in string.ascii_uppercase):
            return capitals
        return a
    else:  # len(author_words) > 1

        def passes(a: str):
            return a and (
                a[0] in string.ascii_uppercase
                or a == ","
                or all(_ in string.ascii_letters + string.digits for _ in a)
            )

        return "".join(a[0] for a in author_words if passes(a))


# Display options shared by every command
_view_parser = argparse.ArgumentParser(add_help=False)
_view_parser.add_argument(
    "-q",
    "--quiet",
    action="store_const",
    default=False,
    const=True,
    help="Suppress some output (only with ls now).",
)  # TODO generalize
_view_parser.add_argument(
    "--nocolor",
    action="store_const",
    dest="color",
    default=True,
    const=False,
    help="Suppress color output.",
)
_view_parser.add_argument(
    "--tabs",
    action="store_const",
    dest="tabs",
    default=False,
    const=True,
    help="Uses tabs as separator for data in list-type commands.",
)
_view_parser.add_argument(
    "--brave",
    action="store_const",
    dest="brave",
    default=False,
    const=True,
    help="Show problems marked as SECRET.",
)
_view_parser.add_argument(
    "-v",
    "--verbose",
    action="store_const",
    default=False,
    const=True,
    help="More verbose displays (e.g. include problem tags).",
)


class Parser(argparse.ArgumentParser):
    def __init__(self, *args: Any, **kwargs: Any):
        super(Parser, self).__init__(parents=[_view_parser], *args, **kwargs)


@dataclass(frozen=True)
class Display:
    """How to render output, from the options shared by every command"""

    color: bool = True
    verbose: bool = False
    tabs: bool = False
    brave: bool = False

    @classmethod
    def from_opts(cls, opts: argparse.Namespace, **overrides: bool) -> "Display":
        kwargs = {
            "color": opts.color,
            "verbose": opts.verbose,
            "tabs": opts.tabs,
            "brave": opts.brave,
        }
        kwargs.update(overrides)
        return cls(**kwargs)

    def paint(self, color_name: str, s: str) -> str:
        return APPLY_COLOR(color_name, s, enabled=self.color)


def getProblemString(problem: Problem, display: Display, i: int | None = None):
    s = getEntryString(problem.entry, display, verbose=True, i=i)
    s += "\n"
    s += display.paint("CYAN", problem.state.strip())
    return s


def getSourceColor(entry: PickleMappingEntry) -> str:
    if "favorite" in entry.tags:
        return "BOLD_YELLOW"
    elif "nice" in entry.tags:
        return "BOLD_CYAN"
    elif "good" in entry.tags:
        return "BOLD_MAGENTA"
    else:
        return "BOLD_BLUE"


def getEntryString(
    entry: PickleMappingEntry,
    display: Display,
    verbose=False,
    i: int | None = None,
):
    paint = display.paint
    # SPECIAL hide brave
    if display.verbose is True:
        verbose = True
    if entry.secret and not display.brave:
        return paint("BOLD_YELLOW", "Problem not shown")

    if display.tabs is True:
        s = "\t".join([entry.source, entry.desc, entry.sortstring])
        if verbose:
            s += "\t" + " ".join(entry.tags)
        return s
    s = ""

    # SPECIAL GLOW for index number
    if i is None:
        i = entry.i
    if i is not None:
        index_string = f"{i + 1:3}"
        if "final" in entry.tags:
            s += paint("YELLOW", index_string)
        elif "waltz" in entry.tags:
            s += paint("GREEN", index_string)
        elif entry.url is not None and entry.used_by_otis is False:
            s += paint("BOLD_RED", index_string)
        elif entry.url is not None and entry.used_by_otis is True:
            s += paint("RED", index_string)
        elif entry.used_by_otis is False:  # url missing
            s += paint("BG_BLUE", index_string)
        else:  # url missing, used by OTIS
            s += paint("BG_MAGENTA", index_string)
        s += " "

    # source (glows for favorite or nice)
    if verbose or len(entry.source) <= 16:
        source_string: str = entry.source
    else:
        words_in_source = entry.source.split(" ")
        source_string = ""
        for word in words_in_source:
            if word == "Shortlist":
                source_string += "Shrt. "
            elif any(_ in string.ascii_lowercase for _ in word):
                source_string += word[:1] + "."
            else:
                source_string += word + " "
        source_string = source_string.strip()
    s += paint(getSourceColor(entry), source_string)
    s += " " * max(1, 17 - len(source_string))

    # hardness
    if isinstance(entry.hardness, int):
        s += paint("BOLD_RED", f"{entry.hardness:2}M")
        s += " "

    # author
    if entry.author is not None:
        s += paint("GREEN", "[" + get_author_initials(entry.author) + "]")
        s += " "

    # the description
    s += entry.desc if verbose else entry.desc[:40]

    # sorting hashtag
    s += " " + paint("RED", "#" + entry.sortstring)

    # PUID, author credits
    if verbose:
        s += "\n" + " " * 4
        s += "PUID:" + paint("CYAN", inferPUID(entry.source))
        if entry.author is not None:
            s += paint("RESET", " | ")
            s += paint("GREEN", entry.author)
        if entry.url is not None:
            url = entry.url
            if url.startswith("http://"):
                url = url[7:]
            if url.startswith("https://"):
                url = url[8:]
            if url.startswith("www."):
                url = url[4:]
            if len(url) > 32:
                url = url[:29] + "..."
            s += " | "
            s += paint("BG_BLUE", url)

    # tags
    if verbose:
        s += "\n" + " " * 4
        s += paint("MAGENTA", " ".join(entry.tags))
    return s


def formatPath(path: str):
    return "VON/" + path


def getDirString(path: str, display: Display):
    return "Directory " + display.paint("BOLD_BLUE", path)


def printProblem(problem: Problem, display: Display, i: int | None = None):
    print(getProblemString(problem, display, i=i))


def printEntry(
    entry: PickleMappingEntry,
    display: Display,
    verbose=False,
    i: int | None = None,
):
    print(getEntryString(entry, display, verbose=verbose, i=i))


def printDir(path: str, display: Display):
    print(getDirString(path, display))


def out(msg: str):
    print(msg)
