import os
import tempfile
from pathlib import Path

# von.rc reads (and may create) the user's config at import time,
# so point it at a throwaway config before any test imports von.
_TEST_ROOT = Path(tempfile.mkdtemp(prefix="von-test-"))
_CONFIG_DIR = _TEST_ROOT / "config" / "von"
_BASE_PATH = _TEST_ROOT / "vondb"
_TMP_PATH = _TEST_ROOT / "tmp"
for d in (_CONFIG_DIR, _BASE_PATH, _TMP_PATH):
    d.mkdir(parents=True)
(_CONFIG_DIR / "config").write_text(
    f"""name: "Test Author"
base_path: "{_BASE_PATH}"
von_tmp_path: "{_TMP_PATH}"
tags: ["easy", "medium", "hard"]
"""
)

os.environ.pop("APPconfig", None)
os.environ["XDG_CONFIG_HOME"] = str(_CONFIG_DIR.parent)
