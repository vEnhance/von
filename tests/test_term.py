import re
import subprocess
import sys

import pytest

from von import controller
from von.controller import COMMANDS, dispatch
from von.term import VonTerminal


def run_von(*args: str) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        [sys.executable, "-m", "von", *args],
        capture_output=True,
        text=True,
        stdin=subprocess.DEVNULL,
        timeout=30,
    )


class TestEntryPoint:
    @pytest.mark.parametrize(
        "args", [["help"], ["--help"], ["-h"], ["help", "add"], ["-v"]]
    )
    def test_runs_cleanly(self, args: list[str]):
        result = run_von(*args)
        assert result.returncode == 0, result.stderr
        assert "Traceback" not in result.stderr

    def test_help_lists_commands(self):
        out = run_von("help").stdout
        assert "Here is a list of available commands" in out
        assert "* add" in out

    def test_flag_without_command(self):
        result = run_von("--nocolor")
        assert result.returncode == 1
        assert "need to start with a command name" in result.stdout


class TestDispatch:
    def test_help(self, capsys: pytest.CaptureFixture[str]):
        dispatch(["help"])
        out = capsys.readouterr().out
        for name in COMMANDS:
            assert f"* {name}\n" in out

    def test_help_for_command(self, capsys: pytest.CaptureFixture[str]):
        with pytest.raises(SystemExit) as e:
            dispatch(["help", "add"])
        assert e.value.code == 0
        assert "usage: add" in capsys.readouterr().out

    def test_help_unknown(self, caplog: pytest.LogCaptureFixture):
        dispatch(["help", "nope"])
        assert "Command nope not found" in caplog.text

    def test_unknown_command(self, caplog: pytest.LogCaptureFixture):
        dispatch(["nope"])
        assert "Command nope not recognized" in caplog.text

    def test_no_command(self, caplog: pytest.LogCaptureFixture):
        dispatch([])
        assert "No command given" in caplog.text

    def test_aliases(self):
        assert COMMANDS["s"] is COMMANDS["search"]
        assert COMMANDS["e"] is COMMANDS["edit"]
        assert COMMANDS["ss"] is COMMANDS["status"]


@pytest.mark.parametrize("command", sorted(COMMANDS))
class TestCommandHelp:
    def test_dispatch(self, command: str, capsys: pytest.CaptureFixture[str]):
        with pytest.raises(SystemExit) as e:
            dispatch([command, "--help"])
        assert e.value.code == 0
        assert "usage:" in capsys.readouterr().out

    def test_interactive(self, command: str, capsys: pytest.CaptureFixture[str]):
        with pytest.raises(SystemExit) as e:
            VonTerminal().onecmd(f"{command} --help")
        assert e.value.code == 0
        assert "usage:" in capsys.readouterr().out


class TestTerminal:
    def test_onecmd_dispatches(self, monkeypatch: pytest.MonkeyPatch):
        calls: list[list[str]] = []
        monkeypatch.setattr(controller, "dispatch", calls.append)
        assert VonTerminal().onecmd('search -t "two words"') is False
        assert calls == [["search", "-t", "two words"]]

    def test_help_interactive(self, capsys: pytest.CaptureFixture[str]):
        VonTerminal().onecmd("help")
        assert "* search" in capsys.readouterr().out

    def test_eof_and_empty_line(self):
        assert VonTerminal().onecmd("EOF") is True
        assert VonTerminal().onecmd("   ") is False

    def test_completes_command_names(self):
        assert VonTerminal().completenames("se") == ["search"]
        assert "help" in VonTerminal().completenames("he")

    def test_prompt_refreshed_after_command(self, monkeypatch: pytest.MonkeyPatch):
        term = VonTerminal()
        term.preloop()
        monkeypatch.setattr(term, "getcwd", lambda: "elsewhere")
        assert "elsewhere" not in term.prompt
        term.postcmd(False, "cd elsewhere")
        assert "elsewhere" in term.prompt


class TestPrompt:
    def test_readline_markers(self, monkeypatch: pytest.MonkeyPatch):
        monkeypatch.setattr(sys.stdin, "isatty", lambda: True, raising=False)
        prompt = VonTerminal().make_prompt()
        # every escape sequence must be wrapped in \001...\002
        # so readline does not count it towards the prompt width
        assert re.search(r"(?<!\001)\033\[", prompt) is None
        assert prompt.count("\001") == prompt.count("\002")
        visible = re.sub(r"\001[^\002]*\002", "", prompt)
        assert visible.startswith("VON/")
        assert visible.endswith("\n:) ")

    def test_no_markers_without_tty(self, monkeypatch: pytest.MonkeyPatch):
        monkeypatch.setattr(sys.stdin, "isatty", lambda: False, raising=False)
        prompt = VonTerminal().make_prompt()
        assert "\001" not in prompt and "\002" not in prompt
