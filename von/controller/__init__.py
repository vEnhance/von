import logging
from collections.abc import Callable

from ..view import APPLY_COLOR
from . import (
    add,
    asy,
    br,
    cd,
    clear,
    edit,
    fixnames,
    index,
    link,
    markup,
    paths,
    po,
    search,
    show,
    solve,
    status,
)

Command = Callable[[list[str]], None]


def ls(argv: list[str]):
    cd.main(["."] + argv)


COMMANDS: dict[str, Command] = {
    "add": add.main,
    "asy": asy.main,
    "br": br.main,
    "build": fixnames.main,
    "cd": cd.main,
    "clear": clear.main,
    "cs": cd.main,
    "e": edit.main,
    "edit": edit.main,
    "f": show.main,  # alias find
    "fix": fixnames.main,
    "fixnames": fixnames.main,
    "index": index.main,
    "link": link.main,
    "ls": ls,
    "m": markup.main,
    "markup": markup.main,
    "nuke": fixnames.main,
    "paths": paths.main,
    "po": po.main,
    "s": search.main,
    "search": search.main,
    "show": show.main,
    "solve": solve.main,
    "ss": status.main,
    "status": status.main,
}


def show_help(argv: list[str]):
    if argv:
        name = argv[0]
        if name not in COMMANDS:
            logging.error(f"Command {name} not found")
        else:
            print(APPLY_COLOR("MAGENTA", f"Getting `{name} --help`..."))
            COMMANDS[name](["--help"])
    else:
        print("Here is a list of available commands:")
        for name in sorted(COMMANDS):
            print("*", name)
        print("Running with no arguments starts an interactive terminal.")
        print("You can get more help on a command by typing its name then --help.")
        print("To exit VON, type an EOF character (usually possible via Ctrl+D).")


def dispatch(argv: list[str]):
    """Runs a command given as a list of arguments, e.g. ["show", "-b", "1", "X"]"""
    if len(argv) == 0:
        logging.error("No command given")
        return
    name, args = argv[0], argv[1:]
    if name == "help":
        show_help(args)
    elif name in COMMANDS:
        COMMANDS[name](args)
    else:
        logging.error(f"Command {name} not recognized")
