import re
import subprocess
import sys

import pytest

from von.term import VonTerminal

COMMANDS = sorted(
    name[3:]
    for name in dir(VonTerminal)
    if name.startswith("do_") and name not in ("do_help", "do_EOF")
)


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


class TestHelp:
    def test_direct(self, capsys: pytest.CaptureFixture[str]):
        VonTerminal().direct(["help"])
        assert "* search" in capsys.readouterr().out

    def test_interactive(self, capsys: pytest.CaptureFixture[str]):
        VonTerminal().onecmd("help")
        assert "* search" in capsys.readouterr().out

    def test_help_for_command(self, capsys: pytest.CaptureFixture[str]):
        with pytest.raises(SystemExit) as e:
            VonTerminal().onecmd("help add")
        assert e.value.code == 0
        assert "usage: add" in capsys.readouterr().out


@pytest.mark.parametrize("command", COMMANDS)
class TestCommandHelp:
    def test_direct(self, command: str, capsys: pytest.CaptureFixture[str]):
        with pytest.raises(SystemExit) as e:
            VonTerminal().direct([command, "--help"])
        assert e.value.code == 0
        assert "usage:" in capsys.readouterr().out

    def test_interactive(self, command: str, capsys: pytest.CaptureFixture[str]):
        with pytest.raises(SystemExit) as e:
            VonTerminal().onecmd(f"{command} --help")
        assert e.value.code == 0
        assert "usage:" in capsys.readouterr().out


class TestPrompt:
    def test_readline_markers(self, monkeypatch: pytest.MonkeyPatch):
        monkeypatch.setattr(sys.stdin, "isatty", lambda: True, raising=False)
        prompt = VonTerminal().prompt
        # every escape sequence must be wrapped in \001...\002
        # so readline does not count it towards the prompt width
        assert re.search(r"(?<!\001)\033\[", prompt) is None
        assert prompt.count("\001") == prompt.count("\002")
        visible = re.sub(r"\001[^\002]*\002", "", prompt)
        assert visible.startswith("VON/")
        assert visible.endswith("\n:) ")

    def test_no_markers_without_tty(self, monkeypatch: pytest.MonkeyPatch):
        monkeypatch.setattr(sys.stdin, "isatty", lambda: False, raising=False)
        prompt = VonTerminal().prompt
        assert "\001" not in prompt and "\002" not in prompt
