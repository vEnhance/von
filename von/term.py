import cmd
import glob
import logging
import os
import shlex
import traceback

from . import controller, model
from .rc import USER_OS, VON_BASE_PATH
from .view import APPLY_COLOR

if USER_OS != "windows":
    import readline

    readline.set_completer_delims(" \t\n")
else:
    from pyreadline3 import Readline  # type: ignore

    readline = Readline()
    from colorama import init  # type: ignore

    init()

WELCOME_STRING = APPLY_COLOR("BOLD_YELLOW", "Welcome to VON!")
GOODBYE_STRING = APPLY_COLOR("BOLD_YELLOW", "OK, goodbye! :D")


def _complete_path(path: str):
    if os.path.isdir(path):
        return glob.glob(os.path.join(path, "*"))
    else:
        return glob.glob(path + "*")


class VonTerminal(cmd.Cmd, controller.VonController):
    def getcwd(self):
        return model.getcwd().replace(VON_BASE_PATH.rstrip("/"), "")

    @property
    def prompt(self):
        return (
            APPLY_COLOR("BOLD_CYAN", "VON/")
            + APPLY_COLOR("YELLOW", self.getcwd())
            + "\n"
            + APPLY_COLOR("BOLD_GREEN", ":)")
            + " "
        )

    def emptyline(self):
        pass

    def completedefault(self, text: str, line: str, start_idx: int, end_idx: int):
        del line, start_idx, end_idx
        return _complete_path(text)

    def run(self):
        print(WELCOME_STRING)
        os.chdir(model.getCompleteCwd())
        while 1:
            try:
                self.cmdloop()
                break
            except KeyboardInterrupt:
                print("^C")
            except SystemExit:
                pass
            except Exception:
                traceback.print_exc()
        print("\n" + GOODBYE_STRING)

    def onecmd(self, line):
        """Interpret the argument as though it had been typed in response
        to the prompt."""
        if line.strip() == "":
            return self.emptyline()
        _ = shlex.split(line)
        cmd = _[0]
        argv = _[1:]
        self.lastcmd = line
        if line == "EOF":
            self.lastcmd = ""
            return 1
        else:
            try:
                func = getattr(self, "do_" + cmd)
            except AttributeError:
                return self.default(line)
            return func(argv)

    def direct(self, cargs: list[str]):
        # cargs = sys.argv ostensibly
        if len(cargs) == 0:
            logging.error("No command given")
        cmd = cargs[0]
        if hasattr(self, "do_" + cmd):
            func = getattr(self, "do_" + cmd)
            func(cargs[1:])
        else:
            logging.error(f"Command {cmd} not recognized")

    def do_help(self, argv: list[str]):
        arg = "".join(argv)
        if arg:
            try:
                func = getattr(self, "do_" + arg)
            except AttributeError:
                logging.error(f"Command {arg} not found")
            else:
                print(APPLY_COLOR("MAGENTA", f"Getting `{arg} --help`..."))
                func(["--help"])
        else:
            print("Here is a list of available commands:")
            for name in sorted(self.get_names()):
                if name[:3] == "do_" and name != "do_help" and name != "do_EOF":
                    print("*", name[3:])
            print("Running with no arguments starts an interactive terminal.")
            print("You can get more help on a command by typing its name then --help.")
            print("To exit VON, type an EOF character (usually possible via Ctrl+D).")
