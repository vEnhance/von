import shlex
import subprocess
import sys

from . import view
from .model import PickleMappingEntry, VonIndex, setCache
from .puid import inferPUID


def _fzf_line(entry: PickleMappingEntry, tags: bool) -> str:
    puid = view.APPLY_COLOR("CYAN", inferPUID(entry.source))
    source = view.APPLY_COLOR(view.getSourceColor(entry), f"{entry.source:<13}")
    line = f"{puid}\t{source}\t"
    if not tags:
        return line + entry.desc
    hashtags = view.APPLY_COLOR("RED", " ".join(f"#{tag}" for tag in entry.tags))
    return line + f"{entry.desc:<50}\t{hashtags}"


def fzf_choose(tags=True) -> str:
    brave = view.OPTS.brave
    color = view.OPTS.color
    with VonIndex() as index:
        choices = "\n".join(
            _fzf_line(entry, tags)
            for entry in index.values()
            if brave or not entry.secret
        )
    try:
        chosen = subprocess.check_output(
            args=[
                "fzf",
                "-e",
                *(["--ansi"] if color else []),
                "--tabstop",
                "12",
                "-d",
                r"\t",
                "--preview",
                f"{shlex.quote(sys.executable)} -m von show"
                + (" --brave" if brave else "")
                + " {2}",
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
