from von.strparse import demacro, oper_demacro


class TestOperDemacro:
    def test_multiple_macros(self):
        assert (
            oper_demacro(r"\abs{x} + \floor{y}")
            == r" \left\lvert x \right\lvert  +  \left\lfloor y \right\rfloor "
        )

    def test_no_macros(self):
        text = r"x + y = z"
        assert oper_demacro(text) == text


class TestDemacro:
    def test_item(self):
        assert demacro(r"\ii Item") == r"\item Item"
        assert demacro(r"\ii[Header] Item") == r"\item[Header] Item"

    def test_arcsin(self):
        assert demacro(r"\arcsin") == r"\arcsin"
        assert demacro(r"\arcsin{x}") == r"\arcsin{x}"

    def test_blackboard(self):
        assert demacro(r"\FF") == r"\mathbb{F}"
        assert demacro(r"\FF_p") == r"\mathbb{F}_p"

    def test_vdotswithin(self):
        assert demacro(r"\vdotswithin=") == r"\vdots"

    def test_multiple_replacements(self):
        assert (
            demacro(r"Let $f \colon \RR \to \CC$ with $f\inv$ and $\half$")
            == r"Let $f \colon \mathbb{R} \to \mathbb{C}$ with $f^{-1}$ and $\frac{1}{2}$"
        )

    def test_degree(self):
        assert demacro(r"$\dang A = 90\dg$") == r"$\measuredangle A = 90^{\circ}$"

    def test_commands_with_braces(self):
        assert demacro(r"\wh{x} + \ol{y}") == r"\widehat{x} + \overline{y}"
