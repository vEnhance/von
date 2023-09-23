import datetime
import logging
import os
import re
import subprocess
import tempfile
import traceback
from argparse import Namespace
from typing import Any, Callable

import yaml
from yaml.scanner import ScannerError

from .. import model, view
from ..clipboard import get_clipboard
from ..puid import inferPUID
from ..rc import EDITOR, NSEPARATOR, SEPARATOR, TAG_HINT_TEXT
from . import preview

# https://urlregex.com/
RE_URL = re.compile(
    r"http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\(\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+"
)


def user_file_input(
    initial="",
    extension=".tmp",
    pre_hook: Callable[[str], None] = None,
    delete: bool = False,
):
    """Opens in $EDITOR a file with content 'initial'
    and 'extension', and returns edited file.
    If pre_hook is not None, runs pre_hook(tf.name) before opening EDITOR.
    If delete is True, delete the file afterwards.
    """

    with tempfile.NamedTemporaryFile(suffix=extension, delete=False) as tf:
        tf.write(initial.encode())
        filename = tf.name
    if pre_hook is not None:
        pre_hook(filename)
    subprocess.run([EDITOR, filename])

    with open(filename, "r") as tf:
        edited_message = "".join(_ for _ in tf.readlines())
    if delete:
        os.unlink(filename)
    return edited_message


def alert_error_tryagain(message=""):
    """Prints an error message and waits for user to confirm."""
    logging.error(message)
    return input("** Press enter to continue: ")


PS_INSTRUCT = r"""% Input your problem and solution below.
% Three dashes on a newline indicate the breaking points.
% URL detected: {url}
% TEX root = {preview_path}
"""


def solicit_user_for_content(raw_text: str, url: str, opts: Namespace):
    del opts
    initial = (
        PS_INSTRUCT.format(
            url=url if url != "<++>" else "None",
            preview_path=preview.VON_PREVIEW_PATH,
        )
        + NSEPARATOR
        + raw_text
    )

    def pre_hook(tempfile_name: str):
        preview.make_preview(tempfile_name)

    while True:
        # TODO maybe give user instructions
        raw_ps = user_file_input(
            initial=initial, extension="von.tex", pre_hook=pre_hook
        )

        if raw_ps.count(SEPARATOR) >= 1:
            bodies = [_.strip() for _ in raw_ps.split(SEPARATOR)[1:]]
            if bodies[0] == "":
                return None
            return bodies
        elif raw_ps.strip() == "":
            return None
        else:
            alert_error_tryagain("Bad format: can't find separator. Try again.")
            initial = raw_ps


DEFAULT_PATH = model.getcwd()
YAML_DATA_FILE = """# Input your problem metadata here

source: {source}     # e.g. USAMO 2000/6. This must be unique
desc:   <++>     # e.g. Fiendish inequality
path:   {path}<++>
tags:   [{now.year}-{now.month:02d}, <++>]
url: {url}

{hint}"""


def solicit_user_for_yaml(opts: Namespace, url: str) -> None | tuple[str, Any]:
    if clipboard_text := get_clipboard():
        if RE_URL.fullmatch(clipboard_text) is not None:
            url = clipboard_text

    initial = YAML_DATA_FILE.format(
        path=model.completePath(DEFAULT_PATH),
        now=datetime.datetime.now(),
        source="<++>" if opts.source is None else opts.source,
        hint=TAG_HINT_TEXT,
        url=url,
    )
    while True:
        raw_yaml = user_file_input(initial=initial, extension="von.yaml", delete=True)
        try:
            d = yaml.safe_load(raw_yaml)
            if d is None:
                return None
            assert "path" in d, "Path is mandatory"
            assert "source" in d, "Source is mandatory"
            if d["path"][-1] != "/":
                d["path"] += "/"
            assert os.path.isdir(d["path"]), d["path"] + " directory non-existent"
            target = d["path"] + inferPUID(d["source"]) + ".tex"
            assert not os.path.isfile(target), target + " already taken"
            assert model.getEntryByKey(d["source"]) is None, (
                d["source"] + " is already an existing problem source"
            )
        except AssertionError:
            traceback.print_exc()
            alert_error_tryagain("Assertions failed, please try again.")
            initial = raw_yaml
        except ScannerError:
            traceback.print_exc()
            alert_error_tryagain("Could not parse YAML, please try again.")
            initial = raw_yaml
        else:
            del d["path"]
            # darn PyYAML used to do this fine -_-
            tags = d.pop("tags")
            output = (
                yaml.dump(d, default_flow_style=False).strip()
                + "\n"
                + "tags: ["
                + ", ".join(tags)
                + "]"
            )
            return (target, output)


def do_add_problem(raw_text: str, url: str, opts: Namespace):
    """Core procedure. Opens two instances of editors to solicit user input
    on problem and produce a problem instance."""

    # Get problem and solution
    bodies = solicit_user_for_content(raw_text, url, opts)
    if bodies is None:
        logging.warning("Aborting due to empty input...")
        return

    yaml_info = solicit_user_for_yaml(opts, url)
    if yaml_info is None:
        logging.warning("Aborting due to empty input...")
        return

    target, out_yaml = yaml_info
    out_text = NSEPARATOR.join([out_yaml] + bodies)
    p = model.addProblemByFileContents(target, out_text)
    assert p is not None
    model.augmentCache(p.entry)
    view.printEntry(p.entry)


parser = view.Parser(prog="add", description="Adds a problem to VON.")
parser.add_argument(
    "source",
    default=None,
    nargs="?",
    help="If specified, sets the source for the new problem.",
)
parser.add_argument(
    "-f",
    "--file",
    dest="filename",
    default=None,
    help="If specified, uses contents of file as body",
)
parser.add_argument(
    "-u",
    "--url",
    default=None,
    help="Specify a URL on the command line",
)


def main(self: object, argv: list[str]):
    del self
    opts = parser.process(argv)
    opts.verbose = True
    url = opts.url if opts.url is not None else "<++>"
    if opts.filename is not None:
        if not os.path.isfile(opts.filename):
            logging.error("The file " + opts.filename + " doesn't exist")
            return
        with open(opts.filename) as f:
            initial_text = "".join(f.readlines())
    else:
        if clipboard_text := get_clipboard():
            if RE_URL.fullmatch(clipboard_text) is not None and opts.url is not None:
                initial_text = "<++>"
                url = clipboard_text
            else:
                initial_text = clipboard_text
        else:
            initial_text = "<++>"
    do_add_problem(initial_text, url, opts)
