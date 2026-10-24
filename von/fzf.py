import shlex
import subprocess
import sys

from .model import PickleMappingEntry, VonIndex, setCache
from .puid import inferPUID


def _fzf_line(entry: PickleMappingEntry, tags: bool) -> str:
    puid = inferPUID(entry.source)
    line = f"{puid}\t{entry.source:<13}\t"
    if not tags:
        return line + entry.desc
    hashtags = " ".join(f"#{tag}" for tag in entry.tags)
    return line + f"{entry.desc:<50}\t{hashtags}"


def fzf_choose(tags=True) -> str:
    with VonIndex() as index:
        choices = "\n".join(_fzf_line(entry, tags) for entry in index.values())
    try:
        chosen = subprocess.check_output(
            args=[
                "fzf",
                "-e",
                # Force left-align results if searching tags.
                *(["--no-hscroll"] if tags else []),
                "--tabstop",
                "12",
                "-d",
                r"\t",
                "--preview",
                f"{shlex.quote(sys.executable)} -m von show {{2}}",
                "--preview-window",
                "down",
            ],
            input=choices,
            text=True,
        )
    except subprocess.CalledProcessError as e:
        sys.exit(e.returncode)
    source = chosen.split("\t")[1].strip()
    setCache([index[source]])
    return source
