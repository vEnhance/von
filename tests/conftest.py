from collections.abc import Iterator
from pathlib import Path

import pytest

from von.rc import Config, load_config, set_config


@pytest.fixture(autouse=True)
def von_config(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> Iterator[Config]:
    """Gives every test its own config file and empty VON database."""
    base_path = tmp_path / "vondb"
    tmp_dir = tmp_path / "tmp"
    config_dir = tmp_path / "config" / "von"
    for d in (base_path, tmp_dir, config_dir):
        d.mkdir(parents=True)
    (config_dir / "config").write_text(
        f"""name: "Test Author"
base_path: "{base_path}"
von_tmp_path: "{tmp_dir}"
tags: ["easy", "medium", "hard"]
"""
    )
    # also picked up by `python -m von` subprocesses
    monkeypatch.delenv("APPconfig", raising=False)
    monkeypatch.setenv("XDG_CONFIG_HOME", str(config_dir.parent))

    cfg = load_config()
    set_config(cfg)
    yield cfg
    set_config(None)
