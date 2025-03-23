import getpass
import os
import sys
import tempfile
from pathlib import Path
from typing import Literal

import yaml

CONFIG_DIR = (
    Path(
        os.environ.get("APPconfig")
        or os.environ.get("XDG_CONFIG_HOME")
        or os.path.join(os.environ["HOME"], ".config")
    )
    / "von"
)
CONFIG_FILE = CONFIG_DIR / "config"

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

if not CONFIG_DIR.exists():
    try:
        CONFIG_DIR.mkdir()
    except PermissionError:
        print(
            f"{CONFIG_DIR} does not exist! Could not load configuration.",
            file=sys.stderr,
        )
        sys.exit(1)

if not CONFIG_FILE.exists():
    try:
        with open(CONFIG_FILE, "w") as f:
            print(EXAMPLE_CONFIG_STRING, file=f)
    except PermissionError:
        print(
            f"{CONFIG_FILE} does not exist and could not be written!", file=sys.stderr
        )
        sys.exit(1)
    else:
        print(
            f"{CONFIG_FILE} does not exist, so we wrote a default file for you.",
            file=sys.stderr,
        )
        print(
            "You should probably open this file and change its contents.",
            file=sys.stderr,
        )
        sys.exit(1)


with open(CONFIG_FILE) as f:
    config = yaml.load(f, Loader=yaml.SafeLoader)

# Mandatory fields in config
VON_DEFAULT_AUTHOR = config["name"]
SORT_TAGS = config["tags"]
VON_BASE_PATH = str(Path(config["base_path"]).expanduser())

# Optional fields
if evil_path := config.get("evil_path", None):
    OTIS_EVIL_JSON_PATH = Path(evil_path).expanduser()
else:
    OTIS_EVIL_JSON_PATH = None

EDITOR = config.get("editor", None) or os.environ.get("EDITOR", "vim")
TAG_HINT_TEXT = config.get("tag_hint_text", "")
USE_COLOR = config.get("color", True)

# OS detector (can be overridden)
USER_OS: Literal["windows"] | Literal["mac"] | Literal["linux"]

if (user_os := config.get("os")) is not None:
    USER_OS = user_os
elif sys.platform.startswith("win32"):
    USER_OS = "windows"
elif sys.platform.startswith("darwin"):
    USER_OS = "mac"
else:
    USER_OS = "linux"  # including cygwin

VON_CUSTOM_LOOKUP = config.get("abbreviations", {})

VON_TMP_PATH = str(Path(config.get("von_tmp_path", tempfile.gettempdir())).expanduser())

# These used to be editable but I don't think it's worth it
VON_INDEX_NAME = "index"
VON_INDEX_PATH = os.path.join(VON_BASE_PATH, VON_INDEX_NAME)
VON_CACHE_NAME = "von_cache_" + getpass.getuser()
VON_CACHE_PATH = os.path.join(VON_TMP_PATH, VON_CACHE_NAME)
VON_PREVIEW_PATH = os.path.join(
    VON_TMP_PATH, "preview_" + getpass.getuser(), "von_preview.tex"
)
VON_POST_OUTPUT_DIR = os.path.join(VON_TMP_PATH, "po_" + getpass.getuser())

SEPARATOR = "\n---\n"
NSEPARATOR = "\n" + SEPARATOR + "\n"
