import argparse
import string
from typing import Any

from .model import PickleMappingEntry, Problem
from .puid import inferPUID
from .rc import USER_OS
from .termcolors import TERM_COLOR

if USER_OS == "windows":
    from colorama import init  # type: ignore

    init()


def APPLY_COLOR(color_name: str, s: str):
    if OPTS.color is False:
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


# Arguments hacking whee
# We have _OPTS here which will pick up any parse_args()
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

OPTS = _view_parser.parse_args([])


class Parser(argparse.ArgumentParser):
    def __init__(self, *args: Any, **kwargs: Any):
        super(Parser, self).__init__(parents=[_view_parser], *args, **kwargs)  # type: ignore

    def process(self, *args: Any, **kwargs: Any) -> argparse.Namespace:
        global OPTS
        OPTS = self.parse_args(*args, **kwargs)
        return OPTS


def getProblemString(problem: Problem, i: int | None = None):
    s = getEntryString(problem.entry, verbose=True, i=i)
    s += "\n"
    s += APPLY_COLOR("CYAN", problem.state.strip())
    return s


def getEntryString(entry: PickleMappingEntry, verbose=False, i: int | None = None):
    # SPECIAL hide brave
    if OPTS.verbose is True:
        verbose = True
    if entry.secret and not OPTS.brave:
        return APPLY_COLOR("BOLD_YELLOW", "Problem not shown")

    if OPTS.tabs is True:
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
            s += APPLY_COLOR("YELLOW", index_string)
        elif "waltz" in entry.tags:
            s += APPLY_COLOR("GREEN", index_string)
        elif entry.url is not None and entry.used_by_otis is False:
            s += APPLY_COLOR("BOLD_RED", index_string)
        elif entry.url is not None and entry.used_by_otis is True:
            s += APPLY_COLOR("RED", index_string)
        elif entry.used_by_otis is False:  # url missing
            s += APPLY_COLOR("BG_BLUE", index_string)
        else:  # url missing, used by OTIS
            s += APPLY_COLOR("BG_MAGENTA", index_string)
        s += " "

    # source (glows for favorite or nice)
    if verbose or len(entry.source) <= 16:
        source_string: str = entry.source
    else:
        words_in_source: list[str] = entry.source.split(" ")
        source_string = ""
        for word in words_in_source:
            if word == "Shortlist":
                source_string += "Shrt. "
            elif any(_ in string.ascii_lowercase for _ in word):
                source_string += word[:1] + "."
            else:
                source_string += word + " "
        source_string = source_string.strip()
    if "favorite" in entry.tags:
        s += APPLY_COLOR("BOLD_YELLOW", source_string)
    elif "nice" in entry.tags:
        s += APPLY_COLOR("BOLD_CYAN", source_string)
    elif "good" in entry.tags:
        s += APPLY_COLOR("BOLD_MAGENTA", source_string)
    else:
        s += APPLY_COLOR("BOLD_BLUE", source_string)
    s += " " * max(1, 17 - len(source_string))

    # hardness
    if isinstance(entry.hardness, int):
        s += APPLY_COLOR("BOLD_RED", f"{entry.hardness:2}M")
        s += " "

    # author
    if entry.author is not None:
        s += APPLY_COLOR("GREEN", "[" + get_author_initials(entry.author) + "]")
        s += " "

    # the description
    s += entry.desc if verbose else entry.desc[:40]

    # sorting hashtag
    s += " " + APPLY_COLOR("RED", "#" + entry.sortstring)

    # PUID, author credits
    if verbose:
        s += "\n" + " " * 4
        s += "PUID:" + APPLY_COLOR("CYAN", inferPUID(entry.source))
        if entry.author is not None:
            s += APPLY_COLOR("RESET", " | ")
            s += APPLY_COLOR("GREEN", entry.author)
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
            s += APPLY_COLOR("BG_BLUE", url)

    # tags
    if verbose:
        s += "\n" + " " * 4
        s += APPLY_COLOR("MAGENTA", " ".join(entry.tags))
    return s


def formatPath(path: str):
    return "VON/" + path


def getDirString(path: str):
    return "Directory " + APPLY_COLOR("BOLD_BLUE", path)


def printProblem(*args: Any, **kwargs: Any):
    print(getProblemString(*args, **kwargs))


def printEntry(*args: Any, **kwargs: Any):
    print(getEntryString(*args, **kwargs))


def printDir(*args: Any, **kwargs: Any):
    print(getDirString(*args, **kwargs))


def out(msg: str):
    print(msg)
