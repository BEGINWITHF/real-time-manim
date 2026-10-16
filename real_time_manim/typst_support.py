"""Typst support for RTM.

Two jobs live here (see RTM-Wiki 04-图形与文本/10-Typst.md):

1. **Typst / TypstMath mobjects** -- re-export ManimCE's Typst classes
   (``manim.mobject.text.typst_mobject``) so RTM scenes can use Typst
   markup directly.  They are plain ``SVGMobject`` subclasses, which RTM's
   paint path already renders; no native work is needed.

2. **LaTeX -> Typst auto-routing for MathTex** -- when a ``MathTex`` string
   lies inside the Typst-convertible subset (fractions, sqrt, scripts,
   matrices, greek/symbol commands, ...), compile it with the in-process
   Typst compiler instead of spawning a LaTeX toolchain.  The conversion is
   *conservative*: anything the converter does not recognise returns
   ``None`` and the string goes through real LaTeX untouched.

   Compilation itself runs on a small background thread pool
   (``warmup_typst_math``): every part of one formula is submitted first and
   only then awaited, so a multi-part formula compiles in parallel.  The
   SVG files are content-hashed and cached by Manim's
   ``typst_to_svg_file`` under ``config.get_dir("tex_dir")`` (media/Tex),
   which also means ``run.py``'s tex_cache restore keeps them warm.

Toggles
-------
``RTM_TYPST=0`` disables the whole Typst layer (auto-routing and the
exports stay importable but MathTex goes straight to LaTeX).
``RTM_TYPST_DEBUG=1`` prints each conversion fallback to stderr.
"""

from __future__ import annotations

import os
import re
from concurrent.futures import ThreadPoolExecutor

__all__ = [
    "Typst",
    "MathTypst",
    "TypstMath",
    "ENABLED",
    "latex_to_typst_math",
    "typst_mathtex_init",
    "warmup_typst_math",
]

# ---------------------------------------------------------------------------
# availability
# ---------------------------------------------------------------------------

try:  # manim >= 0.21 ships the Typst mobjects; they need the typst wheel.
    from manim import Typst, MathTypst  # noqa: F401
except Exception:  # pragma: no cover - older manim or missing typst wheel
    Typst = MathTypst = None  # type: ignore[assignment]

#: Legacy/CE-0.19 name documented in the RTM wiki.
TypstMath = MathTypst

try:
    import typst as _typst_pkg  # noqa: F401

    _HAS_TYPST = True
except ImportError:  # pragma: no cover
    _HAS_TYPST = False

#: Master switch (see module docstring).
ENABLED = _HAS_TYPST and Typst is not None and os.environ.get("RTM_TYPST", "1") != "0"


def _debug(msg: str) -> None:
    if os.environ.get("RTM_TYPST_DEBUG"):
        print(f"[rtm-typst] {msg}")


# ---------------------------------------------------------------------------
# LaTeX -> Typst math conversion
# ---------------------------------------------------------------------------

#: Functions Typst predefines upright (same names as LaTeX).
# NB: Typst predefines no arctg/arcctg, so those LaTeX commands are left out
# of the table on purpose -- their strings fail conversion and fall back.
_FUNCTIONS = (
    "sin", "cos", "tan", "cot", "sec", "csc",
    "arcsin", "arccos", "arctan",
    "sinh", "cosh", "tanh",
    "exp", "log", "ln", "lg",
    "lim", "liminf", "limsup", "max", "min", "sup", "inf",
    "det", "dim", "gcd", "arg", "ker", "deg", "Pr",
)

#: Plain Greek letters: Typst identifiers with the same names.
_GREEK = (
    "alpha", "beta", "gamma", "delta", "epsilon", "zeta", "eta", "theta",
    "iota", "kappa", "lambda", "mu", "nu", "xi", "pi", "rho", "sigma",
    "tau", "upsilon", "phi", "chi", "psi", "omega",
    "Gamma", "Delta", "Theta", "Lambda", "Xi", "Pi", "Sigma",
    "Upsilon", "Phi", "Psi", "Omega", "digamma",
)

#: Command -> Typst math source.  Every entry has been compile- and
#: render-tested against Typst 0.15 (tools/typst probes, see tests).
_CMD_TO_TYPST = {
    **{f"\\{name}": name for name in _FUNCTIONS},
    # big operators
    r"\sum": "sum", r"\prod": "product", r"\int": "integral",
    r"\oint": "integral.cont",
    r"\bigcup": "union.big", r"\bigcap": "inter.big",
    # binary ops / relations verified in Typst
    r"\pm": "plus.minus", r"\times": "times", r"\div": "div",
    r"\cdot": "dot.c", r"\ast": "ast", r"\star": "star",
    r"\bullet": "bullet", r"\circ": "circle.small",
    r"\leq": "<=", r"\le": "<=", r"\geq": ">=", r"\ge": ">=",
    r"\neq": "!=", r"\ne": "!=",
    r"\approx": "approx", r"\equiv": "equiv",
    r"\subseteq": "subset.eq", r"\supseteq": "supset.eq",
    r"\subset": "subset", r"\supset": "supset",
    r"\cup": "union", r"\cap": "inter",
    r"\in": "in", r"\notin": "in.not",
    r"\emptyset": "emptyset", r"\varnothing": "emptyset",
    r"\land": "and", r"\lor": "or", r"\neg": "not", r"\lnot": "not",
    r"\forall": "forall", r"\exists": "exists", r"\nexists": "∄",
    r"\mid": "mid", r"\parallel": "parallel", r"\nparallel": "∦",
    r"\perp": "perp", r"\therefore": "therefore", r"\because": "because",
    # arrows (ASCII shorthands / verified names)
    r"\to": "->", r"\rightarrow": "->", r"\leftarrow": "<-",
    r"\longrightarrow": "->", r"\longleftarrow": "<-",
    r"\Rightarrow": "=>", r"\Leftarrow": "arrow.l.double",
    r"\leftrightarrow": "<->", r"\Leftrightarrow": "<=>",
    r"\mapsto": "|->", r"\longmapsto": "|->",
    # misc symbols
    r"\infty": "infinity", r"\partial": "partial", r"\nabla": "nabla",
    r"\ell": "ell", r"\aleph": "aleph", r"\Re": "Re", r"\Im": "Im",
    r"\angle": "angle", r"\triangle": "triangle", r"\square": "square",
    r"\prime": "prime",
    r"\ldots": "dots", r"\cdots": "dots.c",
    r"\vdots": "dots.v", r"\ddots": "dots.down",
    # Greek: plain names are Typst identifiers; variants fall back to the
    # unicode table (Typst passes unicode math letters straight through).
    **{f"\\{name}": name for name in _GREEK},
    r"\varepsilon": "ε", r"\varkappa": "ϰ", r"\vartheta": "ϑ",
    r"\varpi": "ϖ", r"\varrho": "ϱ", r"\varsigma": "ς", r"\varphi": "ϕ",
    r"\omicron": "ο",
}

#: Structural commands handled by the parser itself (name -> arg count).
_STRUCT = {
    "frac": 2, "dfrac": 2, "tfrac": 2, "cfrac": 2, "binom": 2, "dbinom": 2,
    "sqrt": -1,                       # optional [n]
    "text": 1, "textbf": 1, "textit": 1, "textrm": 1,
    "mathrm": 1, "mathbf": 1, "mathbb": 1, "mathcal": 1, "mathfrak": 1,
    "mathsf": 1, "mathit": 1, "boldsymbol": 1, "operatorname": 1,
    "hat": 1, "widehat": 1, "bar": 1, "overline": 1, "underline": 1,
    "tilde": 1, "widetilde": 1, "dot": 1, "ddot": 1, "vec": 1,
    "breve": 1, "check": 1, "acute": 1, "grave": 1, "mathring": 1,
}

#: Commands that only change style/size and can be dropped.
_SKIP = (
    "displaystyle", "textstyle", "scriptstyle", "limits", "nolimits",
    "big", "Big", "bigg", "Bigg", "bigl", "bigr", "bigm",
    "Bigl", "Bigr", "Bigm", "biggl", "biggr", "biggm",
    "Biggl", "Biggr", "Biggm", "hline", "not", "left.", "right.",
)

#: \\begin{env} -> (typst open text, typst close text).  Delimiter-less
#: ``matrix`` and text-ish environments (cases/align/array/...) are absent
#: on purpose: they fail conversion and fall back to LaTeX.
_ENVS = {
    "pmatrix": ("mat(", ")"),
    "bmatrix": ("mat(delim: \"[\", ", ")"),
    "Bmatrix": ("mat(delim: \"{\", ", ")"),
    "vmatrix": ("mat(delim: \"|\", ", ")"),
}

_LR_DELIMS = {"(": "(", ")": ")", "[": "[", "]": "]", "{": "{", "}": "}",
              "|": "|"}
_LR_CLOSE = {"(": ")", "[": "]", "{": "}", "|": "|", "||": "||"}
_UNICODE_DELIMS = {  # no lr scaling for these, plain literals
    r"\langle": ("⟨", "⟩"), r"\rangle": ("⟨", "⟩"),
    r"\lfloor": ("⌊", "⌋"), r"\rfloor": ("⌊", "⌋"),
    r"\lceil": ("⌈", "⌉"), r"\rceil": ("⌈", "⌉"),
}

_SPECIAL_CHARS = {  # \<c> after a backslash
    "{": "{", "}": "}", "%": "%", "#": "#", "&": "&", "$": "$",
    ",": ",", ";": ";", "!": "!", "|": "|", "/": "/", "-": "-", "'": "'",
    "~": "space", " ": "space", "<": "<", ">": ">", "(": "(", ")": ")",
    "[": "[", "]": "]", '"': '"',
}

_ACCENTS = {"hat": "hat", "widehat": "hat", "bar": "bar",
            "overline": "overline", "underline": "underline",
            "tilde": "tilde", "widetilde": "tilde", "dot": "dot",
            "ddot": "dot.double", "vec": "vec", "breve": "breve",
            "check": "caron", "acute": "acute", "grave": "grave",
            "mathring": "circle.small"}

_TEXT_FONTS = {"mathrm": "upright", "text": "upright", "textrm": "upright",
               "textbf": "bold", "mathbf": "bold", "boldsymbol": "bold",
               "mathbb": "bb", "mathcal": "cal", "mathfrak": "frak",
               "mathsf": "sans", "textit": None, "mathit": None}

_WORD_RE = re.compile(r"[A-Za-z0-9 ]+")
_PLAIN_CMD_RE = re.compile(r"\\[A-Za-z]+")


class _Unsupported(Exception):
    """The string is outside the Typst-convertible subset."""


def _convert_str(s: str, in_matrix: bool = False) -> str:
    """Convert one LaTeX math fragment; raises _Unsupported when impossible."""
    return _Conv(s, in_matrix).parse()


class _Conv:
    def __init__(self, s: str, in_matrix: bool = False):
        self.s = s
        self.i = 0
        self.in_matrix = in_matrix
        self.lr_stack: list = []

    # -- low-level readers ---------------------------------------------------

    def _fail(self):
        raise _Unsupported(self.s)

    def _skip_spaces(self):
        while self.i < len(self.s) and self.s[self.i] in " \t\n\r":
            self.i += 1

    def _read_group_raw(self) -> str:
        """Consume a balanced {...} group and return its raw content."""
        assert self.s[self.i] == "{"
        self.i += 1
        depth = 1
        start = self.i
        while self.i < len(self.s):
            ch = self.s[self.i]
            if ch == "\\":
                self.i += 2
                continue
            if ch == "{":
                depth += 1
            elif ch == "}":
                depth -= 1
                if depth == 0:
                    raw = self.s[start:self.i]
                    self.i += 1
                    return raw
            self.i += 1
        self._fail()

    def _read_env_raw(self) -> str:
        self._skip_spaces()
        if self.i >= len(self.s) or self.s[self.i] != "{":
            self._fail()
        return self._read_group_raw()

    # -- argument readers ----------------------------------------------------

    def _arg_raw(self) -> str:
        """Read the raw argument of a structural command (TeX arg rules)."""
        self._skip_spaces()
        if self.i >= len(self.s):
            self._fail()
        if self.s[self.i] == "{":
            return self._read_group_raw()
        if self.s[self.i] == "\\":
            self._fail()          # single-token args like ^\alpha only
        raw = self.s[self.i]
        self.i += 1
        return raw

    def _arg_conv(self) -> str:
        return _convert_str(self._arg_raw(), self.in_matrix)

    # -- scripts -------------------------------------------------------------

    def _script_arg(self) -> str:
        """Read ^/_ argument and return *wrapped* Typst script source."""
        self._skip_spaces()
        if self.i >= len(self.s):
            self._fail()
        ch = self.s[self.i]
        if ch == "{":
            raw = self._read_group_raw()
        elif ch == "\\":
            # x^\alpha -- a single command; parse_cmd returns converted text.
            self.i += 1
            piece = self.parse_cmd()
            if piece is None:
                self._fail()
            return f"({piece})"
        else:
            raw = ch
            self.i += 1
            if raw in "^_{}":
                self._fail()
            return raw
        stripped = raw.strip()
        if not stripped:
            return "(space)"
        if len(stripped) == 1:
            conv = _convert_str(stripped, self.in_matrix)
            return conv if len(conv) == 1 else f"({conv})"
        if re.fullmatch(r"[A-Za-z]+", stripped):
            # A word: LaTeX renders letters separately; Typst identifiers of
            # length > 1 are unknown variables, so join letters with spaces.
            return "(" + " ".join(stripped) + ")"
        conv = _convert_str(stripped, self.in_matrix)
        return f"({conv})"

    # -- main loop -----------------------------------------------------------

    def _emit(self, out, text: str):
        """Append a unit, keeping adjacent letter identifiers separated.

        ``i\\pi`` must become ``i pi`` in Typst source: glued together they
        would parse as one unknown identifier ``ipi``.
        """
        if out and text and out[-1][-1].isalpha() and text[0].isalpha():
            out.append(" ")
        out.append(text)

    def parse(self, depth: int = 0) -> str:
        out = []
        while self.i < len(self.s):
            ch = self.s[self.i]
            if ch == "}":
                if depth == 0:
                    self._fail()
                self.i += 1
                return "".join(out)
            if ch == "{":
                self.i += 1
                out.append(self.parse(depth + 1))
                continue
            if ch in "^_":
                self.i += 1
                out.append(ch + self._script_arg())
                continue
            if ch == "&":
                if not self.in_matrix:
                    self._fail()
                out.append(", ")
                self.i += 1
                continue
            if ch == "~":
                out.append("space")
                self.i += 1
                continue
            if ch == "\\":
                self.i += 1
                piece = self.parse_cmd()
                if piece is not None:
                    self._emit(out, piece)
                continue
            if "a" <= ch <= "z" or "A" <= ch <= "Z":
                # Plain letters are *separate* italic variables in LaTeX, but
                # Typst would glue a run into one identifier ("pit" -> pi*t,
                # "i\pi" -> unknown "ipi"), so emit them space-separated.
                start = self.i
                while self.i < len(self.s) and (
                        "a" <= self.s[self.i] <= "z"
                        or "A" <= self.s[self.i] <= "Z"):
                    self.i += 1
                run = self.s[start:self.i]
                self._emit(out, " ".join(run))
                continue
            out.append(ch)
            self.i += 1
        if depth != 0 or self.lr_stack:
            self._fail()
        return "".join(out)

    # -- commands ------------------------------------------------------------

    def parse_cmd(self) -> str | None:
        if self.i < len(self.s) and self.s[self.i] == "\\":
            # escaped backslash: row separator inside a matrix, else nope
            self.i += 1
            if self.in_matrix:
                return "; "
            self._fail()
        if self.i >= len(self.s):
            self._fail()
        if self.s[self.i].isalpha():
            start = self.i
            while self.i < len(self.s) and self.s[self.i].isalpha():
                self.i += 1
            name = self.s[start:self.i]
            return self._cmd_word(name)
        ch = self.s[self.i]
        self.i += 1
        if ch in ",;:!":
            # \, \; \: \! are TeX spacing modifiers, not punctuation.
            return None
        if ch in _SPECIAL_CHARS:
            return _SPECIAL_CHARS[ch]
        self._fail()

    def _cmd_word(self, name: str) -> str:
        if name == "left":
            return self._left()
        if name == "right":
            return self._right()
        if name == "begin":
            return self._env_begin()
        if name == "end":
            return self._env_end()
        if name in _SKIP:
            return None
        if name == "frac" or name == "dfrac" or name == "tfrac" or name == "cfrac":
            a = self._arg_conv()
            b = self._arg_conv()
            return f"({a})/({b})"
        if name == "binom" or name == "dbinom":
            a = self._arg_conv()
            b = self._arg_conv()
            return f"binom({a}, {b})"
        if name == "sqrt":
            self._skip_spaces()
            n = None
            if self.i < len(self.s) and self.s[self.i] == "[":
                self.i += 1
                start = self.i
                while self.i < len(self.s) and self.s[self.i] != "]":
                    self.i += 1
                if self.i >= len(self.s):
                    self._fail()
                n = _convert_str(self.s[start:self.i], self.in_matrix)
                self.i += 1
            x = self._arg_conv()
            return f"root({n}, {x})" if n else f"sqrt({x})"
        if name in _ACCENTS:
            x = self._arg_conv()
            return f"{_ACCENTS[name]}({x})"
        if name in _TEXT_FONTS:
            fn = _TEXT_FONTS[name]
            raw = self._arg_raw().strip()
            if "\\" in raw:
                # \text with commands inside: let LaTeX do the whole string.
                if fn is None:
                    return _convert_str(raw, self.in_matrix)
                self._fail()
            if fn is None:                      # \mathit / \textit
                return _convert_str(raw, self.in_matrix)
            if fn == "upright":                 # \text / \mathrm / \textrm
                if len(raw) == 1 and raw.isalnum():
                    return f"upright({raw})"
                return f'upright("{raw}")'
            # font families: \mathbb \mathcal \mathfrak \mathsf \mathbf
            if not raw.isalnum():
                self._fail()
            if len(raw) == 1:
                return f"{fn}({raw})"
            return f'{fn}("{raw}")'
        if name == "operatorname":
            raw = self._arg_raw().strip()
            if not raw or not _WORD_RE.fullmatch(raw):
                self._fail()
            return f'op("{raw}")'
        if name in _CMD_TO_TYPST:
            return _CMD_TO_TYPST[name]
        if "\\" + name in _CMD_TO_TYPST:
            return _CMD_TO_TYPST["\\" + name]
        self._fail()

    # -- left / right --------------------------------------------------------

    def _read_lr_delim(self):
        """Return ('sym', ch) | ('dbl', '||') | ('plain', (l, r)) | None(dot)."""
        self._skip_spaces()
        if self.i >= len(self.s):
            self._fail()
        if self.s[self.i] == "\\":
            self.i += 1
            if self.i >= len(self.s):
                self._fail()
            if self.s[self.i] == "|":
                self.i += 1
                return ("dbl", "||")
            if self.s[self.i] in _LR_DELIMS:
                ch = self.s[self.i]
                self.i += 1
                return ("sym", ch)
            start = self.i
            while self.i < len(self.s) and self.s[self.i].isalpha():
                self.i += 1
            word = self.s[start:self.i]
            key = "\\" + word
            if key in _UNICODE_DELIMS:
                return ("plain", _UNICODE_DELIMS[key])
            self._fail()
        ch = self.s[self.i]
        if ch == ".":
            self.i += 1
            return ("dot", ".")
        if ch in _LR_DELIMS:
            self.i += 1
            return ("sym", ch)
        self._fail()

    def _left(self) -> str:
        kind = self._read_lr_delim()
        if kind[0] == "dot":
            self.lr_stack.append(("dot", None, None))
            return ""
        if kind[0] == "plain":
            l, r = kind[1]
            self.lr_stack.append(("plain", l, r))
            return l
        ch = kind[1]
        self.lr_stack.append(("sym", ch, ch))
        return f"lr({ch}"

    def _right(self) -> str:
        kind = self._read_lr_delim()
        if kind[0] == "dbl":
            kind = ("sym", "||")
        if not self.lr_stack or self.lr_stack[-1][0] == "env":
            self._fail()          # stray \right without \left
        entry = self.lr_stack.pop()
        if entry[0] == "dot":
            # \left. x \right) -- only the right delimiter is drawn.
            if kind[0] == "dot":
                return ""
            if kind[0] == "sym":
                return kind[1]
            self._fail()
        if entry[0] == "plain":
            if kind[0] == "plain":
                return entry[2]
            self._fail()
        # entry == ("sym", open_ch, open_ch)
        ch = entry[1]
        if kind[0] == "dot":
            return _LR_CLOSE[ch] + ")"   # \left( x \right.
        if kind[0] == "sym" and kind[1] == _LR_CLOSE[ch]:
            return _LR_CLOSE[ch] + ")"
        self._fail()                 # mismatched pair: let LaTeX handle it

    def _env_begin(self) -> str:
        env = self._read_env_raw().strip()
        if env not in _ENVS:
            self._fail()
        opener, _ = _ENVS[env]
        self.lr_stack.append(("env", env, None))
        self.in_matrix = True
        return opener

    def _env_end(self) -> str:
        env = self._read_env_raw().strip()
        if not self.lr_stack or self.lr_stack[-1][0] != "env" \
                or self.lr_stack[-1][1] != env:
            self._fail()
        self.lr_stack.pop()
        self.in_matrix = any(e[0] == "env" for e in self.lr_stack)
        _, close = _ENVS[env]
        return close


def latex_to_typst_math(tex: str) -> str | None:
    """Convert a LaTeX math fragment to Typst math source.

    Returns ``None`` when the string uses anything outside the supported
    subset -- callers must then keep the LaTeX path.
    """
    if not ENABLED:
        return None
    try:
        return _convert_str(tex)
    except _Unsupported:
        return None
    except Exception as exc:                       # pragma: no cover
        _debug(f"converter error on {tex!r}: {exc}")
        return None


# ---------------------------------------------------------------------------
# background compilation
# ---------------------------------------------------------------------------

_POOL = ThreadPoolExecutor(max_workers=4, thread_name_prefix="rtm-typst")


def warmup_typst_math(bodies):
    """Compile Typst bodies on the background pool; await all results.

    ``bodies`` are Typst *math* fragments (no ``$`` delimiters).  Each one
    is submitted as the same ``$ ... $`` document MathTypst would build, so
    the content-hash SVG cache is shared and MathTypst hits it afterwards.
    """
    from manim.utils.typst_file_writing import typst_to_svg_file

    futs = []
    for body in bodies:
        if not body:
            continue
        code = f"$ {body} $"
        futs.append(_POOL.submit(typst_to_svg_file, code, ""))
    return [f.result() for f in futs]


# ---------------------------------------------------------------------------
# MathTex integration
# ---------------------------------------------------------------------------

def _locate_first_match(substrings, unprocessed_string):
    """Leftmost-longest substring match, mirroring manim's rule.

    Same algorithm as ``MathTex._locate_first_match`` (the one that decides
    where dvisvgm group tags get injected in the LaTeX path): earliest
    start wins, ties broken by the longest matched substring.
    """
    first_match_start = len(unprocessed_string)
    first_match_length = 0
    first_match = None
    for substring in substrings:
        match = re.match(
            f"(.*?)({re.escape(substring)})(.*)",
            unprocessed_string,
            flags=re.DOTALL,
        )
        if match and len(match.group(1)) < first_match_start:
            first_match = match
            first_match_start = len(match.group(1))
            first_match_length = len(match.group(2))
        elif match and len(match.group(1)) == first_match_start:
            if first_match_length < len(match.group(2)):
                first_match = match
                first_match_start = len(match.group(1))
                first_match_length = len(match.group(2))
    return first_match


def _split_by_substrings(substrings, tex_string):
    """Split *tex_string* into ``("plain" | "sub", text)`` segments.

    Isolated substrings become their own segments so they can be compiled
    and grouped independently (mirrors how the LaTeX path nests a ``<g>``
    per substring inside the string's main group).
    """
    if not substrings:
        return [("plain", tex_string)]
    segments = []
    unprocessed = str(tex_string)
    while unprocessed:
        match = _locate_first_match(substrings, unprocessed)
        if not match:
            segments.append(("plain", unprocessed))
            break
        pre, matched, post = match.group(1), match.group(2), match.group(3)
        if pre:
            segments.append(("plain", pre))
        segments.append(("sub", matched))
        unprocessed = post
    return segments


_SCRIPT_OFFSETS_48: tuple[float, float] | None = None


def _script_offsets_at(font_size: float) -> tuple[float, float]:
    """Vertical (sup-raise, sub-drop) offsets for split-off script parts.

    When ``{{x}}^2`` splits off a ``^2`` part, that part is compiled as its
    own Typst page, which trims to ink and loses the baseline the joint
    ``x^2`` render would give it.  Calibrate the offsets once against
    Typst's own joint rendering (glyph ink positions relative to the shared
    baseline) at the default font size and scale linearly, since Typst's
    script placement is proportional to the font size.
    """
    global _SCRIPT_OFFSETS_48
    if _SCRIPT_OFFSETS_48 is None:
        from manim.constants import DEFAULT_FONT_SIZE

        sup = MathTypst("x^2", font_size=DEFAULT_FONT_SIZE)
        sub = MathTypst("x_n", font_size=DEFAULT_FONT_SIZE)
        sup_raise = sub_drop = 0.0
        if len(sup.submobjects) >= 2:
            sup_raise = float(
                sup.submobjects[1].get_bottom()[1]
                - sup.submobjects[0].get_bottom()[1]
            )
        if len(sub.submobjects) >= 2:
            sub_drop = float(
                sub.submobjects[0].get_bottom()[1]
                - sub.submobjects[1].get_top()[1]
            )
        _SCRIPT_OFFSETS_48 = (sup_raise, sub_drop)
    scale = font_size / 48.0
    return _SCRIPT_OFFSETS_48[0] * scale, _SCRIPT_OFFSETS_48[1] * scale


def typst_mathtex_init(self, *tex_strings, arg_separator=" ",
                       substrings_to_isolate=None, tex_to_color_map=None,
                       tex_environment="align*", **kwargs) -> bool:
    """Build ``self`` (a MathTex) from Typst-compiled parts.

    Mirrors ``MathTex.__init__``'s observable state (``tex_strings``,
    ``tex_string``, MathTexPart submobjects with ``tex_string`` for
    TransformMatchingTex, ``tex_to_color_map`` colouring) but renders each
    prepared string through MathTypst instead of the LaTeX toolchain.

    Returns False when any string is not convertible; raises when Typst
    itself fails to compile (the dispatch then falls back to LaTeX).
    """
    from manim import ORIGIN, Square
    from manim.constants import DEFAULT_FONT_SIZE, SCALE_FACTOR_PER_FONT_POINT
    from manim.mobject.text.tex_mobject import MATHTEX_SUBSTRING, MathTexPart
    from manim.mobject.types.vectorized_mobject import VGroup, VMobject

    from real_time_manim.window.mathtex import _NORMAL_PART_BUFF

    # MathTex.__init__ was intercepted before any base __init__ ran, so give
    # the mobject its base state (points, style defaults) like the LaTeX path
    # would get from SVGMobject.__init__.
    VMobject.__init__(self)
    # Mobject.__init__ dispatches init_colors() to SingleStringMathTex's
    # override, which only recolors submobjects; the rgba arrays on self
    # (fill/stroke/background_stroke rgbas) that align_data/align_rgbas
    # rely on are left unset. The SVG path gets them via set_style; set
    # them explicitly here.
    VMobject.init_colors(self)

    font_size = kwargs.pop("font_size", DEFAULT_FONT_SIZE)
    color = kwargs.pop("color", None)
    kwargs.pop("stroke_width", None)
    kwargs.pop("organize_left_to_right", None)
    kwargs.pop("tex_template", None)

    self.arg_separator = arg_separator
    self.substrings_to_isolate = (
        [] if substrings_to_isolate is None else list(substrings_to_isolate)
    )
    self.tex_to_color_map = dict(tex_to_color_map or {})
    self.substrings_to_isolate.extend(self.tex_to_color_map.keys())
    self.tex_environment = tex_environment
    self.brace_notation_split_occurred = False
    self.organize_left_to_right = False
    self.tex_strings = self._prepare_tex_strings(tex_strings)

    # ---- plan the compile jobs ------------------------------------------
    # Each tex_string is split into segments by substrings_to_isolate (the
    # same leftmost-longest rule the LaTeX path uses when it injects
    # dvisvgm group tags), and every segment becomes its own Typst compile.
    plan = []        # per main string: [(kind, body, ss_id), ...]
    valigns = []     # per main string: None | "sup" | "sub"
    matched = []     # (tex_string, id) entries for get_part_by_tex & co
    all_bodies = []  # every non-empty Typst body, compiled in parallel
    ss_idx = 0
    for idx, ts in enumerate(self.tex_strings):
        matched.append((ts, f"unique{idx:03d}"))
        entries = []
        valign = None
        for kind, text in _split_by_substrings(self.substrings_to_isolate, ts):
            if not text:
                continue
            body = latex_to_typst_math(text)
            if body is None:
                return False
            if body[:1] in ("^", "_"):
                # A fragment starting with a script (from "{{x}}^2", which
                # splits off "^2") has no base to attach to when compiled
                # alone; give it a zero-width one so it renders as a bare
                # superscript/subscript instead of failing to compile.
                if valign is None:
                    valign = "sup" if body[0] == "^" else "sub"
                body = "#h(0pt)" + body
            if kind == "sub":
                ss_id = f"unique{ss_idx:03d}{MATHTEX_SUBSTRING}"
                ss_idx += 1
                matched.append((text, ss_id))
            else:
                ss_id = None
            entries.append((kind, body, ss_id))
            all_bodies.append(body)
        plan.append(entries)
        valigns.append(valign)

    if any(v is not None for v in valigns):
        # Calibration formulas for the script offsets -- submitted to the
        # pool with everything else so measuring costs no extra latency.
        all_bodies.extend(("x^2", "x_n"))

    # Submit every segment to the background pool first, then await: a
    # multi-part formula compiles in parallel instead of serially.
    warmup_typst_math(all_bodies)

    # ---- build the parts --------------------------------------------------
    parts = []
    id_to_vgroup = {}
    typst_kwargs = {"font_size": font_size}
    if color is not None:
        typst_kwargs["color"] = color
    for idx, entries in enumerate(plan):
        part = MathTexPart()
        part.tex_string = self.tex_strings[idx]
        part.fill_opacity = 1.0
        cursor = 0.0
        for kind, body, ss_id in entries:
            if body == "":
                seg = VGroup(Square(0.01, fill_opacity=0, stroke_width=0))
            else:
                seg = VGroup(*MathTypst(body, **typst_kwargs).submobjects)
            # Lay the segments of one string out sequentially; they are
            # pieces of a single formula, so no buff between them.
            seg.move_to([cursor + seg.width / 2, 0, 0])
            cursor = seg.get_right()[0]
            if kind == "sub":
                # Wrap substring glyphs in a nested group, like the SVG
                # nesting in the LaTeX path, so set_color_by_tex can
                # recolour just that substring.
                grp = VMobject()
                grp.add(*seg.submobjects)
                id_to_vgroup[ss_id] = grp
                part.add(grp)
            else:
                part.add(*seg.submobjects)
        parts.append(part)
        id_to_vgroup[f"unique{idx:03d}"] = part

    # ---- lay the parts out ------------------------------------------------
    # Same horizontal scheme as _layout_math_parts (sequential run with the
    # normal buff) but split-off script parts are placed by their calibrated
    # baseline offsets instead of being vertically centred, which would drag
    # a raised "2" back down to mid-height.
    sup_raise, sub_drop = (
        _script_offsets_at(font_size)
        if any(v is not None for v in valigns)
        else (0.0, 0.0)
    )
    cursor_x = 0.0
    prev_height = None
    for part, valign in zip(parts, valigns):
        h = part.height
        if valign == "sup" and prev_height is not None and part.submobjects:
            # Anchor on the part's first glyph (the raised script): put its
            # ink bottom at the previous part's baseline + the joint-render
            # raise.  The rest of the part keeps Typst's own relative layout.
            anchor_bottom = float(part.submobjects[0].get_bottom()[1])
            dy = -prev_height / 2 + sup_raise - anchor_bottom
        elif valign == "sub" and prev_height is not None and part.submobjects:
            anchor_top = float(part.submobjects[0].get_top()[1])
            dy = -prev_height / 2 - sub_drop - anchor_top
        else:
            dy = 0.0
        part.move_to([cursor_x + part.width / 2, dy, 0])
        cursor_x = part.get_right()[0] + _NORMAL_PART_BUFF
        prev_height = h
    result = VGroup(*parts)
    result.move_to(ORIGIN)

    self.tex_string = self.arg_separator.join(self.tex_strings)
    # Populate the lookup tables that get_part_by_tex /
    # set_color_by_tex_to_color_map read (the LaTeX path fills these in
    # _join_tex_strings_with_unique_deliminters + _break_up_by_substrings).
    self.matched_strings_and_ids = matched
    self.id_to_vgroup_dict = id_to_vgroup
    self.submobjects = list(result.submobjects)
    self.init_colors()
    # font_size property semantics: getter == height / initial_height /
    # SCALE_FACTOR_PER_FONT_POINT, where initial_height is the *unscaled*
    # natural height (the LaTeX path records the raw SVG import height).
    # Our parts were already built at font_size, so back it out.
    if self.height > 0:
        self.initial_height = self.height / font_size / SCALE_FACTOR_PER_FONT_POINT
    else:  # pragma: no cover - fully empty content
        self.initial_height = 1.0
    self._font_size = font_size
    self.set_color_by_tex_to_color_map(self.tex_to_color_map)
    return True
