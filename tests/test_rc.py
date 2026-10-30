from dataclasses import replace
from pathlib import Path

import pytest

from von import model, view
from von.puid import inferPUID
from von.rc import Config, ConfigError, load_config, set_config


class TestLoadConfig:
    def test_writes_example_when_missing(self, tmp_path: Path):
        path = tmp_path / "von" / "config"
        with pytest.raises(ConfigError, match="wrote a default file"):
            load_config(path)
        assert "YOUR NAME HERE" in path.read_text()
        # the example file is itself a loadable config
        assert load_config(path).name == "YOUR NAME HERE"

    def test_unwritable(self, tmp_path: Path):
        blocker = tmp_path / "file"
        blocker.write_text("")
        with pytest.raises(ConfigError, match="could not be written"):
            load_config(blocker / "von" / "config")

    def test_missing_required_fields(self, tmp_path: Path):
        path = tmp_path / "custom_config"
        path.write_text('name: "A"\n')
        with pytest.raises(ConfigError, match="base_path, tags"):
            load_config(path)

    def test_not_a_mapping(self, tmp_path: Path):
        path = tmp_path / "custom_config"
        path.write_text("just a string\n")
        with pytest.raises(ConfigError):
            load_config(path)


class TestFromDict:
    def test_defaults(self):
        cfg = Config.from_dict({"name": "A", "base_path": "/db", "tags": ["easy"]})
        assert cfg.color is True
        assert cfg.evil_path is None
        assert cfg.abbreviations == {}
        assert cfg.index_path == "/db/index"

    def test_expands_user(self):
        cfg = Config.from_dict(
            {
                "name": "A",
                "base_path": "~/db",
                "tags": [],
                "von_tmp_path": "~/tmp",
                "evil_path": "~/evil.json",
            }
        )
        assert not cfg.base_path.startswith("~")
        assert not cfg.tmp_path.startswith("~")
        assert cfg.evil_path is not None and "~" not in str(cfg.evil_path)

    def test_optional_fields(self):
        cfg = Config.from_dict(
            {
                "name": "A",
                "base_path": "/db",
                "tags": [],
                "editor": "nano",
                "color": False,
                "os": "windows",
                "abbreviations": {"Inter Galaxy Math Olympiad": "IGMO"},
            }
        )
        assert cfg.editor == "nano"
        assert cfg.color is False
        assert cfg.os == "windows"


class TestConfigIsLive:
    """Modules read the active config at call time, not import time."""

    def test_color(self, von_config: Config):
        assert view.APPLY_COLOR("RED", "x") != "x"
        set_config(replace(von_config, color=False))
        assert view.APPLY_COLOR("RED", "x") == "x"

    def test_base_path(self, von_config: Config, tmp_path: Path):
        assert model.completePath("a.tex") == f"{von_config.base_path}/a.tex"
        set_config(replace(von_config, base_path=str(tmp_path)))
        assert model.completePath("a.tex") == f"{tmp_path}/a.tex"

    def test_puid_abbreviations(self, von_config: Config):
        assert inferPUID("USAMO 2000/6") == "00AMO6"
        assert inferPUID("Inter Galaxy Math Olympiad 2020/1") != "20IGMO1"
        set_config(
            replace(von_config, abbreviations={"Inter Galaxy Math Olympiad": "IGMO"})
        )
        assert inferPUID("Inter Galaxy Math Olympiad 2020/1") == "20IGMO1"

    def test_otis_used_sources(self, von_config: Config, tmp_path: Path):
        assert model.getOtisUsedSources() is None
        evil = tmp_path / "evil.json"
        evil.write_text('{"a": "USAMO 2000/6"}')
        set_config(replace(von_config, evil_path=evil))
        assert model.getOtisUsedSources() == ["USAMO 2000/6"]
