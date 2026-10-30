import getpass
import os
import sys
import tempfile
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Literal

import yaml

SEPARATOR = "\n---\n"
NSEPARATOR = "\n" + SEPARATOR + "\n"

# These used to be editable but I don't think it's worth it
VON_INDEX_NAME = "index"

OSName = Literal["windows", "mac", "linux"]


class ConfigError(Exception):
    pass


def default_config_path() -> Path:
    return (
        Path(
            os.environ.get("APPconfig")
            or os.environ.get("XDG_CONFIG_HOME")
            or os.path.join(os.environ["HOME"], ".config")
        )
        / "von"
        / "config"
    )


def detect_os() -> OSName:
    if sys.platform.startswith("win32"):
        return "windows"
    elif sys.platform.startswith("darwin"):
        return "mac"
    else:
        return "linux"  # including cygwin


EXAMPLE_CONFIG_STRING = """# vim: ft=yaml
# This is an example of a VON config file
# Please edit it to suit your needs

# REQUIRED: Choose the default author for generated TeX files.
# (You should probably put your name here)
name: "YOUR NAME HERE"

# REQUIRED: Path to folder where you want to store your VON database
# You can include "~" which gets expanded to your home directory
# Make sure this folder exists!
base_path: "~/Documents/vondb/"

# REQUIRED: A list of sort tags
# These particular tags are used for sorting and are highlighted differently.
# Specify them however you want. Should be in increasing order.
tags: ["trivial", "easy", "medium", "hard", "brutal"]

# If your terminal sucks and doesn't have color sequences (e.g. you are using Windows)
# then you should uncomment this option and change it to false
# color: true

# The following text is placed as you do editing
# in order to help you remember which tags you have.
# tag_hint_text: ""

# By default your OS is autodetected
# If this fails for some reason, you can set it to `windows`, `mac`, or `linux` below
# os: linux

# path to store temporary files (von cache, TeX previewer, posted output files)
# Defaults to the output of Python's tempfile.gettempdir()
# von_tmp_path: "/tmp"

# Name of text editor to invoke
# By default, it detects from $EDITOR automatically
# editor: vim

# If you would like to define a custom contest name (to be used in the PUID script),
# then you should define it here.
# This will also override any "standard" lookups in `puid.py`.
# abbreviations:
#   Inter Galaxy Math Olympiad: IGMO
#   Inter Universe Math Olympiad: IUMO
"""


@dataclass(frozen=True)
class Config:
    # Mandatory fields
    name: str
    base_path: str
    tags: list[str]
    # Optional fields
    evil_path: Path | None = None
    editor: str = field(default_factory=lambda: os.environ.get("EDITOR", "vim"))
    tag_hint_text: str = ""
    color: bool = True
    os: OSName = field(default_factory=detect_os)
    abbreviations: dict[str, str] = field(default_factory=dict)
    tmp_path: str = field(default_factory=tempfile.gettempdir)

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "Config":
        missing = [k for k in ("name", "base_path", "tags") if k not in data]
        if missing:
            raise ConfigError(
                f"Config is missing required fields: {', '.join(missing)}"
            )
        kwargs: dict[str, Any] = {
            "name": data["name"],
            "base_path": str(Path(data["base_path"]).expanduser()),
            "tags": data["tags"],
        }
        if evil_path := data.get("evil_path"):
            kwargs["evil_path"] = Path(evil_path).expanduser()
        if editor := data.get("editor"):
            kwargs["editor"] = editor
        if "tag_hint_text" in data:
            kwargs["tag_hint_text"] = data["tag_hint_text"]
        if "color" in data:
            kwargs["color"] = data["color"]
        if data.get("os") is not None:
            kwargs["os"] = data["os"]
        if data.get("abbreviations"):
            kwargs["abbreviations"] = data["abbreviations"]
        if tmp_path := data.get("von_tmp_path"):
            kwargs["tmp_path"] = str(Path(tmp_path).expanduser())
        return cls(**kwargs)

    @property
    def index_path(self) -> str:
        return os.path.join(self.base_path, VON_INDEX_NAME)

    @property
    def cache_path(self) -> str:
        return os.path.join(self.tmp_path, "von_cache_" + getpass.getuser())

    @property
    def preview_path(self) -> str:
        return os.path.join(
            self.tmp_path, "preview_" + getpass.getuser(), "von_preview.tex"
        )

    @property
    def post_output_dir(self) -> str:
        return os.path.join(self.tmp_path, "po_" + getpass.getuser())


def load_config(path: Path | None = None) -> Config:
    """Reads the config file, writing an example one if it doesn't exist."""
    if path is None:
        path = default_config_path()
    if not path.exists():
        try:
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text(EXAMPLE_CONFIG_STRING + "\n")
        except OSError as e:
            raise ConfigError(
                f"{path} does not exist and could not be written ({e})."
            ) from e
        raise ConfigError(
            f"{path} does not exist, so we wrote a default file for you.\n"
            "You should probably open this file and change its contents."
        )
    with open(path) as f:
        data = yaml.safe_load(f)
    if not isinstance(data, dict):
        raise ConfigError(f"{path} does not contain a valid config.")
    return Config.from_dict(data)


_config: Config | None = None


def config() -> Config:
    """Returns the active config, loading it from disk on first use."""
    global _config
    if _config is None:
        _config = load_config()
    return _config


def set_config(cfg: Config | None) -> None:
    """Replaces the active config (None means reload from disk on next use)."""
    global _config
    _config = cfg
