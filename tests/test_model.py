from dataclasses import replace
from pathlib import Path

import pytest

from von import model
from von.rc import Config, set_config

from .conftest import write_problem


def sources(entries: list[model.PickleMappingEntry]) -> list[str]:
    return [e.source for e in entries]


class TestParsing:
    def test_make_problem_from_path(self, db: Path):
        p = model.makeProblemFromPath("usamo/00AMO6.tex")
        assert p.source == "USAMO 2000/6"
        assert p.desc == "Fiendish inequality"
        assert p.tags == ["hard", "alg"]
        assert p.author == "Titu Andreescu"
        assert p.hardness == 40
        assert p.bodies == ["Prove it.", "Solution here."]
        assert p.state == "Prove it."

    def test_absolute_path(self, db: Path):
        p = model.makeProblemFromPath(str(db / "imo" / "05IMO3.tex"))
        assert p.source == "IMO 2005/3"

    def test_requires_source(self, von_config: Config):
        write_problem(Path(von_config.base_path), "bad.tex", "''")
        with pytest.raises(AssertionError, match="No source"):
            model.makeProblemFromPath("bad.tex")

    def test_entry_roundtrip(self, db: Path):
        p = model.makeProblemFromPath("usamo/00AMO6.tex")
        e = p.entry
        assert isinstance(e, model.PickleMappingEntry)
        assert (e.source, e.path, e.author) == (p.source, p.path, p.author)
        assert e.full.bodies == p.bodies


class TestIndex:
    def test_rebuild(self, db: Path):
        index = model.VonIndex().store
        assert sorted(index) == [
            "IMO 2005/2",
            "IMO 2005/3",
            "USAMO 2000/6",
            "USAMO 2001/1",
        ]
        assert index["IMO 2005/3"].path == "imo/05IMO3.tex"

    def test_duplicate_sources(self, db: Path):
        write_problem(db, "dupe/x.tex", "IMO 2005/3")
        model.rebuildIndex()
        index = model.VonIndex().store
        assert "IMO 2005/3" in index
        assert sum(k.startswith("DUPLICATE ") for k in index) == 1

    def test_add_problem_by_file_contents(self, db: Path):
        text = "source: ISL 2010 A1\ndesc: New one\ntags: [easy]\n---\nBody."
        p = model.addProblemByFileContents(str(db / "isl" / "10SLA1.tex"), text)
        assert p.source == "ISL 2010 A1"
        assert p.path == "isl/10SLA1.tex"
        assert model.VonIndex()["ISL 2010 A1"].desc == "New one"

    def test_update_entry_renames(self, db: Path):
        old = model.getEntryByKey("IMO 2005/3")
        assert old is not None
        model.setCache([old])
        new = model.makeProblemFromPath(old.path)
        new.source = "IMO 2005/3 renamed"
        model.updateEntryByProblem(old, new)
        index = model.VonIndex().store
        assert "IMO 2005/3" not in index
        assert "IMO 2005/3 renamed" in index
        assert sources(list(model.readCache())) == ["IMO 2005/3 renamed"]


class TestSearch:
    def test_term_matches_desc_source_author_tag_puid(self, db: Path):
        assert sources(model.runSearch(terms=["fiendish"])) == ["USAMO 2000/6"]
        assert sources(model.runSearch(terms=["2001"])) == ["USAMO 2001/1"]
        assert sources(model.runSearch(terms=["titu"])) == ["USAMO 2000/6"]
        assert sources(model.runSearch(terms=["nt"])) == ["IMO 2005/2"]
        assert sources(model.runSearch(terms=["05imo3"])) == ["IMO 2005/3"]

    def test_terms_are_anded(self, db: Path):
        assert sources(model.runSearch(terms=["inequality", "imo"])) == ["IMO 2005/3"]

    def test_tags_case_insensitive(self, db: Path):
        assert sources(model.runSearch(tags=["ALG"])) == [
            "IMO 2005/3",
            "USAMO 2000/6",
        ]

    def test_sources_and_authors(self, db: Path):
        assert sources(model.runSearch(sources=["usamo"])) == [
            "USAMO 2001/1",
            "USAMO 2000/6",
        ]
        assert sources(model.runSearch(authors=["andreescu"])) == ["USAMO 2000/6"]
        assert model.runSearch(authors=["titu andreescu"]) == []

    def test_path_restriction(self, db: Path):
        assert sources(model.runSearch(tags=["alg"], path="imo")) == ["IMO 2005/3"]

    def test_has_url(self, db: Path):
        assert sources(model.runSearch(has_url=True)) == ["USAMO 2001/1"]
        assert "USAMO 2001/1" not in sources(model.runSearch(has_url=False))

    def test_in_otis(self, db: Path, von_config: Config, tmp_path: Path):
        evil = tmp_path / "evil.json"
        evil.write_text('{"x": "IMO 2005/2"}')
        set_config(replace(von_config, evil_path=evil))
        assert sources(model.runSearch(in_otis=True)) == ["IMO 2005/2"]
        assert "IMO 2005/2" not in sources(model.runSearch(in_otis=False))

    def test_sort_by_config_tags_then_hardness(self, db: Path):
        # tags in config are [easy, medium, hard]
        assert sources(model.runSearch()) == [
            "USAMO 2001/1",
            "IMO 2005/2",
            "IMO 2005/3",
            "USAMO 2000/6",
        ]

    def test_alphabetical(self, db: Path):
        assert sources(model.runSearch(alph_sort=True)) == [
            "IMO 2005/2",
            "IMO 2005/3",
            "USAMO 2000/6",
            "USAMO 2001/1",
        ]

    def test_sets_cache_and_refine(self, db: Path):
        model.runSearch(tags=["alg"])
        assert sources(list(model.readCache())) == ["IMO 2005/3", "USAMO 2000/6"]
        assert [e.i for e in model.readCache()] == [0, 1]
        assert sources(model.runSearch(terms=["usamo"], refine=True)) == [
            "USAMO 2000/6"
        ]

    def test_no_results_keeps_cache(self, db: Path):
        model.runSearch(tags=["alg"])
        assert model.runSearch(terms=["nonexistent"]) == []
        assert len(model.readCache()) == 2


class TestCache:
    def test_set_augment_clear(self, db: Path):
        a, b = model.getEntryByKey("IMO 2005/2"), model.getEntryByKey("IMO 2005/3")
        assert a is not None and b is not None
        model.setCache([a])
        model.augmentCache(b)
        assert sources(list(model.readCache())) == ["IMO 2005/2", "IMO 2005/3"]
        model.clearCache()
        assert len(model.readCache()) == 0

    def test_get_entry_by_key(self, db: Path):
        model.runSearch(tags=["alg"])
        by_num = model.getEntryByKey("2")
        assert by_num is not None and by_num.source == "USAMO 2000/6"
        by_puid = model.getEntryByKey("05imo2")
        assert by_puid is not None and by_puid.source == "IMO 2005/2"
        # prefers the cached copy, which knows its cache position
        cached = model.getEntryByKey("USAMO 2000/6")
        assert cached is not None and cached.i == 1
        assert model.getEntryByKey("nope") is None


class TestViewDirectory:
    def test_lists_problems_and_dirs(self, db: Path):
        entries, dirs = model.viewDirectory(str(db))
        assert entries == [] and dirs == ["imo", "usamo"]
        entries, dirs = model.viewDirectory(str(db / "imo"))
        assert sources(entries) == ["IMO 2005/2", "IMO 2005/3"]
        assert dirs == []
        assert sources(list(model.readCache())) == ["IMO 2005/2", "IMO 2005/3"]


class TestCwd:
    def test_getcwd_relative_to_base(self, db: Path, monkeypatch: pytest.MonkeyPatch):
        monkeypatch.chdir(db / "imo")
        assert model.getcwd() == "imo"
        assert model.getCompleteCwd() == str(db / "imo")
        monkeypatch.chdir(db)
        assert model.getcwd() == ""


def entry(source: str, **kwargs: object) -> model.PickleMappingEntry:
    kwargs.setdefault("desc", "")
    kwargs.setdefault("tags", [])
    kwargs.setdefault("path", f"{source}.tex")
    return model.PickleMappingEntry(source=source, **kwargs)


class TestPureFunctions:
    """The building blocks above, without touching disk."""

    def test_parse_problem(self):
        p = model.parseProblem(
            "x.tex", "source: A 2000/1\ndesc: D\ntags: [easy]\n---\nS\n---\nSol\n"
        )
        assert (p.source, p.desc, p.tags, p.bodies) == (
            "A 2000/1",
            "D",
            ["easy"],
            ["S", "Sol"],
        )

    def test_parse_problem_requires_desc(self):
        with pytest.raises(AssertionError, match="No description"):
            model.parseProblem("x.tex", "source: A\ndesc: ''\n---\nS")

    def test_search_query(self):
        q = model.SearchQuery(tags=("alg",), has_url=False, path="imo/")
        assert q.matches(entry("IMO 2005/3", tags=["ALG"], path="imo/a.tex"))
        assert not q.matches(entry("IMO 2005/3", tags=["alg"], path="usamo/a.tex"))
        assert not q.matches(
            entry("IMO 2005/3", tags=["alg"], path="imo/a.tex", url="http://x")
        )
        assert model.SearchQuery().matches(entry("anything"))

    def test_sort_entries(self):
        es = [
            entry("C", tags=["hard"]),
            entry("B", tags=["easy"], hardness=10),
            entry("A", tags=["easy"], hardness=20),
            entry("D"),
        ]
        assert sources(model.sortEntries(es)) == ["D", "B", "A", "C"]
        assert sources(model.sortEntries(es, alph_sort=True)) == ["A", "B", "C", "D"]

    def test_find_entry_by_term(self):
        index = {e.source: e for e in (entry("USAMO 2000/6"), entry("IMO 2005/3"))}
        assert model.findEntryByTerm(index, "IMO 2005/3") is index["IMO 2005/3"]
        assert model.findEntryByTerm(index, "00amo6") is index["USAMO 2000/6"]
        assert model.findEntryByTerm(index, "nope") is None

    def test_build_index(self):
        problems = [
            model.Problem("a.tex", source="X", desc="", tags=[]),
            model.Problem("b.tex", source="Y", desc="", tags=[]),
            model.Problem("c.tex", source="X", desc="", tags=[]),
        ]
        index = model.buildIndex(problems)
        assert index["X"].path == "a.tex"
        assert index["Y"].path == "b.tex"
        (dupe,) = [k for k in index if k.startswith("DUPLICATE ")]
        assert index[dupe].path == "c.tex"
