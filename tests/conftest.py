from collections.abc import Iterator
from pathlib import Path

import pytest

from von import model
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


def write_problem(
    base: Path,
    relpath: str,
    source: str,
    desc: str = "Some problem",
    tags: list[str] | None = None,
    bodies: tuple[str, ...] = ("Statement.",),
    **extra: object,
) -> Path:
    path = base / relpath
    path.parent.mkdir(parents=True, exist_ok=True)
    header = f"source: {source}\ndesc: {desc}\ntags: [{', '.join(tags or [])}]\n"
    for key, value in extra.items():
        header += f"{key}: {value}\n"
    path.write_text(header + "".join(f"\n---\n{b}" for b in bodies) + "\n")
    return path


@pytest.fixture
def db(von_config: Config) -> Path:
    """A small VON database, already indexed."""
    base = Path(von_config.base_path)
    write_problem(
        base,
        "usamo/00AMO6.tex",
        "USAMO 2000/6",
        desc="Fiendish inequality",
        tags=["hard", "alg"],
        author="Titu Andreescu",
        hardness=40,
        bodies=("Prove it.", "Solution here."),
    )
    write_problem(
        base,
        "usamo/01AMO1.tex",
        "USAMO 2001/1",
        desc="Coloring boxes",
        tags=["easy", "comb"],
        url="https://example.com",
    )
    write_problem(
        base,
        "imo/05IMO3.tex",
        "IMO 2005/3",
        desc="Inequality again",
        tags=["medium", "alg"],
        hardness=25,
    )
    write_problem(
        base,
        "imo/05IMO2.tex",
        "IMO 2005/2",
        desc="Sequence",
        tags=["medium", "nt"],
        hardness=20,
    )
    (base / "imo" / "notes.txt").write_text("not a problem")
    model.rebuildIndex()
    return base
