from von import model, view

ESC = "\033["


def entry(**kwargs: object) -> model.PickleMappingEntry:
    kwargs.setdefault("source", "USAMO 2000/6")
    kwargs.setdefault("desc", "Fiendish inequality")
    kwargs.setdefault("tags", ["hard"])
    kwargs.setdefault("path", "x.tex")
    return model.PickleMappingEntry(**kwargs)


class TestDisplay:
    def test_from_opts(self):
        opts = view.Parser(prog="x").parse_args(["--nocolor", "--brave"])
        assert view.Display.from_opts(opts) == view.Display(color=False, brave=True)
        assert view.Display.from_opts(opts, verbose=True).verbose is True

    def test_color(self):
        assert ESC in view.getEntryString(entry(), view.Display())
        assert ESC not in view.getEntryString(entry(), view.Display(color=False))

    def test_secret_needs_brave(self):
        secret = entry(tags=["secret"])
        plain = view.Display(color=False)
        assert view.getEntryString(secret, plain) == "Problem not shown"
        brave = view.Display(color=False, brave=True)
        assert "Fiendish" in view.getEntryString(secret, brave)

    def test_tabs(self):
        assert view.getEntryString(entry(), view.Display(tabs=True)) == (
            "USAMO 2000/6\tFiendish inequality\thard"
        )
        assert view.getEntryString(
            entry(), view.Display(tabs=True, verbose=True)
        ).endswith("\thard")

    def test_verbose(self):
        s = view.getEntryString(entry(), view.Display(color=False, verbose=True))
        assert "PUID:00AMO6" in s
