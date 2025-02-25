import subprocess

from .model import PickleMappingEntry, VonIndex, setCache
from .puid import inferPUID


def _fzf_line(entry: PickleMappingEntry) -> str:
    puid = inferPUID(entry.source)
    return f"{puid}\t{entry.source:<13}\t{entry.desc}"


def fzf_choose() -> str:
    with VonIndex() as index:
        choices = "\n".join(_fzf_line(entry) for entry in index.values())
    chosen = subprocess.check_output(
        args=[
            "fzf",
            "-e",
            "--tabstop",
            "12",
            "-d",
            r"\t",
            "--preview",
            "python -m von show {2}",
            "--preview-window",
            "down",
        ],
        input=choices,
        text=True,
    )
    source = chosen.split("\t")[1].strip()
    setCache([index[source]])
    return source
