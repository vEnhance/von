"""End-to-end output of each command on a small fixture database."""

from pathlib import Path

import pytest

from von import model
from von.term import VonTerminal

from .conftest import write_problem


def dispatch(argv: list[str]) -> None:
    VonTerminal().direct(argv)


ESC = "\033["


@pytest.fixture
def run(db: Path, capsys: pytest.CaptureFixture[str]):
    def _run(*argv: str) -> str:
        capsys.readouterr()
        dispatch(list(argv))
        return capsys.readouterr().out

    return _run


@pytest.fixture
def asy_db(db: Path) -> Path:
    write_problem(
        db,
        "geo/G1.tex",
        "ISL 2010 G1",
        desc="Diagram",
        tags=["easy"],
        bodies=(
            "State.",
            "Sol.\n\\begin{asy}\n    pair A = (0,0); /* origin */\n"
            "    dot(A);\n\\end{asy}\nMore.\n\\begin{asy}\n  draw(B);\n\\end{asy}",
        ),
    )
    model.rebuildIndex()
    return db


class TestSearch:
    def test_results(self, run):
        out = run("search", "--nocolor", "-t", "alg")
        assert out.splitlines() == [
            "  1 IMO 2005/3       25M Inequality again #medium",
            "  2 USAMO 2000/6     40M [TA] Fiendish inequality #hard",
        ]

    def test_tabs(self, run):
        out = run("search", "--tabs", "-t", "alg")
        assert out.splitlines() == [
            "IMO 2005/3\tInequality again\tmedium",
            "USAMO 2000/6\tFiendish inequality\thard",
        ]

    def test_color(self, run):
        assert ESC in run("search", "-t", "alg")
        assert ESC not in run("search", "--nocolor", "-t", "alg")

    def test_requires_query(self, run, caplog: pytest.LogCaptureFixture):
        assert run("search") == ""
        assert "--everything" in caplog.text

    def test_refine(self, run):
        run("search", "-t", "alg")
        assert "USAMO 2000/6" in run("search", "--nocolor", "-r", "usamo")


class TestCacheCommands:
    def test_status_and_paths(self, run):
        run("search", "-t", "alg")
        assert run("status", "--nocolor").splitlines() == [
            "  1 IMO 2005/3       25M Inequality again #medium",
            "  2 USAMO 2000/6     40M [TA] Fiendish inequality #hard",
        ]
        assert run("paths").splitlines() == ["imo/05IMO3.tex", "usamo/00AMO6.tex"]
        run("clear")
        assert run("status") == ""

    def test_ls(self, run, db: Path, monkeypatch: pytest.MonkeyPatch):
        monkeypatch.chdir(db)
        assert run("ls", "--nocolor").splitlines() == [
            "Directory imo",
            "Directory usamo",
        ]
        monkeypatch.chdir(db / "imo")
        assert run("ls", "--nocolor").splitlines() == [
            "  1 IMO 2005/2       20M Sequence #medium",
            "  2 IMO 2005/3       25M Inequality again #medium",
        ]

    def test_cd(self, run, db: Path, monkeypatch: pytest.MonkeyPatch):
        monkeypatch.chdir(db)
        assert "IMO 2005/2" in run("cd", "--nocolor", "imo")
        assert Path.cwd() == db / "imo"
        assert run("cd", "-q", "..") == ""


class TestShow:
    def test_full(self, run):
        assert run("show", "--nocolor", "USAMO 2000/6").splitlines() == [
            "USAMO 2000/6     40M [TA] Fiendish inequality #hard",
            "    PUID:00AMO6 | Titu Andreescu",
            "    hard alg",
            "Prove it.",
        ]

    def test_body(self, run):
        assert run("show", "-b", "1", "00amo6") == "Solution here.\n"
        assert run("show", "--aops", "00amo6") == "Prove it.\n"
        assert run("show", "--twitch", "00amo6") == (
            "Solution from [i]Twitch Solves ISL[/i]:\n\nSolution here.\n"
        )

    def test_missing_body(self, run, caplog: pytest.LogCaptureFixture):
        assert run("show", "-b", "5", "00amo6") == ""
        assert "5-th body" in caplog.text

    def test_not_found(self, run, caplog: pytest.LogCaptureFixture):
        assert run("show", "nope") == ""
        assert "nope not found" in caplog.text


class TestMarkup:
    def test_markdown(self, run):
        assert run("markup", "USAMO 2001/1") == (
            "## [USAMO 2001/1](https://example.com).\n\nStatement.\n"
        )

    def test_multiple_aops(self, run):
        assert run("markup", "--aops", "USAMO 2001/1", "USAMO 2000/6") == (
            "[b][url=https://example.com]USAMO 2001/1[/url].[/b]\nStatement.\n"
            "\n--------\n\n"
            "[b]USAMO 2000/6, proposed by Titu Andreescu.[/b]\nProve it.\n"
        )

    def test_discord(self, run):
        assert run("markup", "-d", "IMO 2005/3") == (
            "## IMO 2005/3.\n```latex\nStatement.\n```\n"
        )

    def test_not_found(self, run, caplog: pytest.LogCaptureFixture):
        assert run("markup", "nope") == ""
        assert "nope not found" in caplog.text


class TestPo:
    def test_tex(self, run):
        out = run("po", "--tex", "--author", "Me", "USAMO 2000/6")
        assert out.startswith(r"\documentclass[11pt]{scrartcl}")
        assert r"\title{USAMO 2000/6}" in out
        assert r"\author{Me}" in out
        assert "\\begin{problem*}\nProve it.\n\\end{problem*}" in out
        assert "\\hrulebar\n\nSolution here.\n" in out
        assert out.endswith("\\end{document}\n")

    def test_default_author(self, run):
        assert r"\author{Test Author}" in run("po", "--tex", "IMO 2005/3")


class TestSolve:
    def test_expands_von(self, run, tmp_path: Path):
        tex = tmp_path / "in.tex"
        tex.write_text("Intro\n\\von{USAMO 2000/6}\n\\von*{IMO 2005/3}\nOutro\n")
        assert run("solve", str(tex)) == (
            "Intro\n"
            "\\begin{problem}[USAMO 2000/6]\nProve it.\n\\end{problem}\n"
            "\\subsection*{\\ul{Solution}}\nSolution here.\n\\hrulebar\n"
            "\\begin{problem}\nStatement.\n\\end{problem}\n"
            "Outro\n\n"
        )


class TestAsy:
    def test_first_diagram(self, run, asy_db: Path):
        assert run("asy", "ISL 2010 G1") == "pair A = (0,0);\ndot(A);\n"

    def test_options(self, run, asy_db: Path):
        assert run("asy", "-c", "ISL 2010 G1") == (
            "pair A = (0,0); /* origin */\ndot(A);\n"
        )
        assert run("asy", "-n", "2", "ISL 2010 G1") == "draw(B);\n"


class TestOptionsDoNotLeak:
    """Display options apply to one command only."""

    def test_nocolor(self, run, monkeypatch: pytest.MonkeyPatch):
        monkeypatch.setattr("sys.stdin.isatty", lambda: False)
        run("search", "--nocolor", "-t", "alg")
        assert ESC in VonTerminal().prompt
        assert ESC in run("status")

    def test_brave(self, run, db: Path):
        write_problem(db, "s.tex", "SECRET 1", desc="Hidden", tags=["easy"])
        model.rebuildIndex()
        assert "Hidden" in run("search", "--brave", "--nocolor", "hidden")
        assert "Hidden" not in run("status", "--nocolor")
        assert "Problem not shown" in run("status", "--nocolor")
