try:
    import pyperclip
except ModuleNotFoundError:
    PYPERCLIP_AVAILABLE = False
    pyperclip = None
else:
    PYPERCLIP_AVAILABLE = True


def get_clipboard() -> str:
    if PYPERCLIP_AVAILABLE:
        assert pyperclip is not None
        return pyperclip.paste().strip()
    else:
        return ""


def set_clipboard(s: str):
    if PYPERCLIP_AVAILABLE:
        assert pyperclip is not None
        pyperclip.copy(s)
