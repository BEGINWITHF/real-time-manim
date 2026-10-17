"""Tests for the Typst layer (real_time_manim.typst_support).

Two deliverables per RTM-Wiki 04-图形与文本/10-Typst.md:

1. the Typst/TypstMath mobjects (re-exported from ManimCE) must stay usable
   under RTM's patched MathTex dispatch;
2. the LaTeX -> Typst auto-routing: convertible MathTex strings compile
   through the in-process Typst backend (zero LaTeX invocations), anything
   outside the subset still goes to real LaTeX, and a Typst compile error
   falls back to LaTeX instead of breaking the scene.

Pure Python, no GPU/DLL required.
"""
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

import manim.mobject.text.tex_mobject as tm
import real_time_manim.typst_support as ts
from manim import MathTex
from real_time_manim.window import mathtex as mh  # noqa: F401  (installs dispatch)

pytestmark = pytest.mark.skipif(
    not ts.ENABLED, reason="typst layer disabled (RTM_TYPST=0 or typst missing)"
)


# ---------------------------------------------------------------------------
# converter: supported subset
# ---------------------------------------------------------------------------

@pytest.mark.parametrize("latex,expected", [
    (r"\frac{a}{b}", "(a)/(b)"),
    (r"\sqrt{2} + \sqrt[3]{x}", "sqrt(2) + root(3, x)"),
    (r"\alpha + \beta", "alpha + beta"),
    (r"x \leq y \neq z", "x <= y != z"),
    (r"\lim_{x \to 0} f(x)", "lim_(x -> 0) f(x)"),
    (r"\operatorname{sgn}", 'op("sgn")'),
    (r"\hat{x} + \ddot{q}", "hat(x) + dot.double(q)"),
    (r"\vec{v}", "accent(v, →)"),
    (r"\vec{AB}", "accent(A B, →)"),
    (r"\bar{x}", "overline(x)"),
    (r"\mathring{x}", "accent(x, ○)"),
    (r"x \mid y", "x ∣ y"),
    (r"\mathsf{A}", "upright(sans(A))"),
    (r"\mathbf{v}", "upright(bold(v))"),
    (r"\boldsymbol{v}", "bold(v)"),
    (r"\textbf{hi}", 'upright(bold("hi"))'),
    (r"\lfloor x \rfloor", "⌊ x ⌋"),
    (r"\left\lceil x \right\rfloor", "⌈ x ⌋"),
    (r"a\,b", "a#h(0.1667em)b"),
    (r"\mathbb{R}^n", "bb(R)^n"),
    (r"\left( \frac{a}{b} \right)", "lr(( (a)/(b) ))"),
    (r"\left\{ x \right\}", "lr({ x })"),
    (r"\begin{pmatrix} 1 & 2 \\ 3 & 4 \end{pmatrix}",
     "mat(1, 2; 3, 4)"),
    (r"\text{speed}", 'upright("speed")'),
    (r"\mathrm{d}x", "upright(d)x"),
    (r"e^{i\pi}", "e^(i pi)"),
    (r"\int_0^1 f(x)\,dx", "integral_0^1 f(x)#h(0.1667em)d x"),
])
def test_converter_supported(latex, expected):
    got = ts.latex_to_typst_math(latex)
    assert got is not None
    # Typst ignores math-mode whitespace, and how many spaces the converter
    # emits around & / \\ separators is an implementation detail.
    assert got.replace(" ", "") == expected.replace(" ", "")


@pytest.mark.parametrize("latex", [
    r"\begin{cases} 1 & x > 0 \\ 0 & x \leq 0 \end{cases}",
    r"\begin{align*} a &= b \\ c &= d \end{align*}",
    r"\usepackage{tikz}",
    r"\mymacro{x}",
    r"a & b",                      # & outside a matrix
    r"a \\ b",                     # \\ outside a matrix
    r"\left[ 0, 1 \right)",        # mismatched delimiters
    r"\frac{\usepackage{x}}{2}",   # unsupported nested inside a supported cmd
    r"\not\in",                    # no generic negation bar in Typst
    r"\text{say \"hi\"}",          # unbalanced quotes would break the string
])
def test_converter_unsupported_returns_none(latex):
    assert ts.latex_to_typst_math(latex) is None


def test_every_mapped_token_compiles_in_typst():
    """Each command table entry must be a valid Typst math token."""
    import typst
    import tempfile

    tokens = sorted(set(ts._CMD_TO_TYPST.values()))
    # accent templates (filled with a base) and the spacing snippets that
    # the converter splices into the middle of a formula must compile too
    tokens += sorted({tmpl.format(x="x") for tmpl in ts._ACCENTS.values()})
    tokens += sorted(set(ts._TEX_SPACES.values()))
    with tempfile.TemporaryDirectory() as td:
        for i, tok in enumerate(tokens):
            p = Path(td) / f"t{i}.typ"
            p.write_text(
                "#set page(width: auto, height: auto, margin: 0pt)\n"
                f"$ {tok} $\n", encoding="utf-8",
            )
            try:
                typst.compile(str(p), format="svg")
            except Exception as exc:
                pytest.fail(f"token {tok!r} does not compile: {exc}")


# ---------------------------------------------------------------------------
# Typst path vs LaTeX path: structural parity
# ---------------------------------------------------------------------------

def _leaf_count(mob):
    if not mob.submobjects:
        return 1 if mob.get_num_points() else 0
    return sum(_leaf_count(sub) for sub in mob.submobjects)


@pytest.mark.parametrize("latex", [
    r"\vec{v}",
    r"\bar{x}",
    r"\mathring{x}",
    r"\mathsf{A}",
    r"\mathbf{v}",
    r"\lfloor x \rfloor",
    r"\mid",
    r"\hat{x}",
])
def test_typst_glyph_count_matches_latex(latex, monkeypatch):
    """The Typst route must draw the same number of glyphs as LaTeX.

    This is the guard that catches "the accent silently vanished" bugs:
    ``\vec{v}`` is v + arrow in both renderers (2 leaves), while the old
    ``vec(v)`` mapping drew a stray ``(v)`` instead (3 leaves).
    """
    m_typst = MathTex(latex)
    monkeypatch.setattr(ts, "ENABLED", False)
    m_latex = MathTex(latex)
    got, want = _leaf_count(m_typst), _leaf_count(m_latex)
    assert got == want, f"{latex}: typst drew {got} glyphs, latex drew {want}"


# ---------------------------------------------------------------------------
# MathTex auto-routing
# ---------------------------------------------------------------------------

@pytest.fixture()
def latex_calls(monkeypatch):
    """Count real LaTeX compilations triggered through manim."""
    calls = []
    orig = tm.tex_to_svg_file

    def counted(*args, **kwargs):
        calls.append(args[0] if args else kwargs.get("tex_string"))
        return orig(*args, **kwargs)

    monkeypatch.setattr(tm, "tex_to_svg_file", counted)
    return calls


def test_convertible_mathtex_skips_latex(latex_calls):
    m = MathTex(r"\sum_{k=0}^n k = \frac{n(n+1)}{2}")
    assert latex_calls == []
    assert len(m.submobjects) >= 1
    assert m.tex_string == r"\sum_{k=0}^n k = \frac{n(n+1)}{2}"
    # the mobject is actually built from glyphs
    leaves = [g for p in m.submobjects for g in p.submobjects]
    assert leaves and all(g.get_num_points() > 0 for g in leaves)


def test_unconvertible_mathtex_uses_latex(latex_calls):
    MathTex(r"\begin{cases} 1 & x > 0 \\ 0 & x \leq 0 \end{cases}")
    assert len(latex_calls) == 1


def test_brace_split_parts_keep_tex_strings(latex_calls):
    m = MathTex("{{a}} + {{b}} = {{c}}")
    parts = [p.tex_string for p in m.submobjects]
    assert parts == ["a", " + ", "b", " = ", "c"]
    assert latex_calls == []
    assert m.tex_string == " ".join(parts)


def test_cross_boundary_scripts_use_typst(latex_calls):
    # {{x}}^2 splits off a "^2" part; it is compiled with a zero-width
    # base (#h(0pt)^2) so the whole equation stays on the Typst path.
    m = MathTex("{{x}}^2 + {{y}}^2")
    assert latex_calls == []
    assert len(m.submobjects) == 4
    assert [p.tex_string for p in m.submobjects] == ["x", "^2 + ", "y", "^2"]


def test_substring_isolation_groups_substrings(latex_calls):
    from manim import RED

    # "+" is not its own tex_string; manim isolates it inside the string,
    # which must still yield a group set_color_by_tex can recolour.
    m = MathTex("a+b", tex_to_color_map={"+": RED})
    assert latex_calls == []
    plus = m.get_part_by_tex("+")
    assert plus is not None
    assert plus[0].get_color() == RED


def test_color_map_applied(latex_calls):
    from manim import RED

    m = MathTex("a", "+", "b", tex_to_color_map={"+": RED})
    plus = m.get_part_by_tex("+")
    assert plus is not None
    assert plus[0].get_color() == RED
    assert m.get_part_by_tex("a")[0].get_color() != RED


def test_typst_compile_error_falls_back(monkeypatch, latex_calls):
    def boom(*args, **kwargs):
        raise RuntimeError("injected typst failure")

    monkeypatch.setattr(ts, "warmup_typst_math", boom)
    m = MathTex(r"\frac{a}{b}")
    assert len(latex_calls) == 1
    assert m.submobjects


def test_disabled_flag_uses_latex(monkeypatch, latex_calls):
    monkeypatch.setattr(ts, "ENABLED", False)
    MathTex(r"\frac{a}{b}")
    assert len(latex_calls) == 1


def test_font_size_and_write_animation(latex_calls):
    from real_time_manim.animations.write import Write

    m = MathTex(r"\frac{a}{b}", font_size=32)
    w = Write(m)
    w.begin(0)
    m._vulkan_progress = 0.0
    w.interpolate(0.6)
    w.finish()


# ---------------------------------------------------------------------------
# Typst / TypstMath mobjects
# ---------------------------------------------------------------------------

def test_typst_mobjects_exported():
    assert ts.Typst is not None and ts.MathTypst is not None
    assert ts.TypstMath is ts.MathTypst


def test_mathtypst_basic_build():
    m = ts.MathTypst("sum_(k=0)^n k = frac(n(n+1), 2)")
    assert len(m.submobjects) > 0
    t = ts.Typst("*bold* text")
    assert len(t.submobjects) > 0
