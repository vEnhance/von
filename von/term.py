import cmd
import glob
import os
import re
import shlex
import sys
import traceback
from typing import Any

from . import controller, model
from .rc import config
from .view import APPLY_COLOR

if sys.platform != "win32":
    import readline

    readline.set_completer_delims(" \t\n")
else:
    from pyreadline3 import Readline  # type: ignore

    readline = Readline()
    from colorama import init  # type: ignore

    init()


def _complete_path(path: str):
    if os.path.isdir(path):
        return glob.glob(os.path.join(path, "*"))
    else:
        return glob.glob(path + "*")


class VonTerminal(cmd.Cmd):
    def getcwd(self):
        return model.getcwd().replace(config().base_path.rstrip("/"), "")

    def make_prompt(self) -> str:
        s = (
            APPLY_COLOR("BOLD_CYAN", "VON/")
            + APPLY_COLOR("YELLOW", self.getcwd())
            + "\n"
            + APPLY_COLOR("BOLD_GREEN", ":)")
            + " "
        )
        if config().os != "windows" and sys.stdin.isatty():
            # mark escape sequences as zero-width so readline computes
            # the prompt length (and hence cursor position) correctly
            s = re.sub(r"(\033\[[0-9;]*m)", "\001\\1\002", s)
        return s

    def preloop(self):
        self.prompt = self.make_prompt()

    def postcmd(self, stop: bool, line: str) -> bool:
        self.prompt = self.make_prompt()  # cwd may have changed
        return stop

    def emptyline(self) -> bool:
        return False

    def completenames(self, text: str, *ignored: Any) -> list[str]:
        return [
            name for name in [*controller.COMMANDS, "help"] if name.startswith(text)
        ]

    def completedefault(self, *ignored: Any) -> list[str]:
        text = ignored[0] if ignored else ""
        return _complete_path(text)

    def run(self):
        print(APPLY_COLOR("BOLD_YELLOW", "Welcome to VON!"))
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
        print("\n" + APPLY_COLOR("BOLD_YELLOW", "OK, goodbye! :D"))

    def onecmd(self, line: str) -> bool:
        """Runs a line typed at the prompt; returns True to exit"""
        if line.strip() == "":
            return self.emptyline()
        self.lastcmd = line
        if line == "EOF":
            self.lastcmd = ""
            return True
        controller.dispatch(shlex.split(line))
        return False
