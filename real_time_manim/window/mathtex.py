"""Native MathTex support: tokenising TeX into glyphs without LaTeX.

Also owns the two MathTex monkey patches (substring splitting and the
`__init__` dispatch that can bypass LaTeX entirely)."""

from manim import (
    Text, VGroup, ORIGIN, WHITE
)


from manim.mobject.text.tex_mobject import MathTex as _OrigMathTex
from manim.mobject.text.tex_mobject import MathTexPart

def _patched_break_up_by_substrings(self):
    """Reorganize submobjects into MathTexPart instances.

    The SVG's named groups carry the exact glyph -> tex_string mapping, so that
    path is always preferred.  Only when the SVG has no named groups (a file
    compiled without the \\special tags) does this fall back to splitting the
    glyph list by position, weighting each string by its character count --
    which is a *guess*: characters and glyphs do not correspond one to one
    (spaces and `\\\\` draw nothing, `fi` is one ligature glyph), so a guess can
    hand a string's last glyph to the next part.
    """
    new_submobjects = []
    try:
        for tex_string, tex_string_id in self._main_matches:
            mtp = MathTexPart()
            mtp.tex_string = tex_string
            mtp.add(*self.id_to_vgroup_dict[tex_string_id].submobjects)
            new_submobjects.append(mtp)
    except KeyError:
        # ── positional fallback ──
        # Collect leaf mobjects (SVG glyphs) from the root group.
        # They appear in the same order as the tex_strings.
        leaf_mobs = []
        def _collect_leaves(vg):
            for sub in (vg.submobjects if hasattr(vg, 'submobjects') else []):
                has_subs = hasattr(sub, 'submobjects') and sub.submobjects
                if has_subs:
                    _collect_leaves(sub)
                elif hasattr(sub, 'points') and len(sub.points) > 0:
                    leaf_mobs.append(sub)
        root = self.id_to_vgroup_dict.get("root")
        if root is not None:
            _collect_leaves(root)
        if not leaf_mobs:
            self.submobjects = new_submobjects
            return self

        main_matches = self._main_matches
        total_chars = sum(max(1, len(ts)) for ts, _ in main_matches)
        total_leaves = len(leaf_mobs)
        leaf_idx = 0

        for tex_string, tex_string_id in main_matches:
            weight = max(1, len(tex_string))
            alloc = max(1, round(total_leaves * weight / total_chars))
            alloc = min(alloc, total_leaves - leaf_idx)
            if alloc < 1:
                alloc = 1
            mtp = MathTexPart()
            mtp.tex_string = tex_string
            end = min(leaf_idx + alloc, total_leaves)
            for i in range(leaf_idx, end):
                mtp.add(leaf_mobs[i])
            leaf_idx = end
            new_submobjects.append(mtp)
            # Populate id_to_vgroup_dict so get_part_by_tex etc. still work
            self.id_to_vgroup_dict[tex_string_id] = mtp
        # Give any stragglers to the last part
        while leaf_idx < total_leaves and new_submobjects:
            new_submobjects[-1].add(leaf_mobs[leaf_idx])
            leaf_idx += 1

    self.submobjects = new_submobjects
    return self

_OrigMathTex._break_up_by_substrings = _patched_break_up_by_substrings

# ── Replace MathTex rendering with native Text layout (zero LaTeX) ──
# MathTex.__init__ normally compiles TeX → DVI → SVG via tex_to_svg_file().
# We monkey-patch __init__ on the original class so even previously-imported
# references (e.g. `from manim import *` in the scene) avoid LaTeX.

_SUPER_TRANS = str.maketrans('0123456789+-=()', '⁰¹²³⁴⁵⁶⁷⁸⁹⁺⁻⁼⁽⁾')
_SUB_TRANS = str.maketrans('0123456789+-=()', '₀₁₂₃₄₅₆₇₈₉₊₋₌₍₎')
_SCRIPT_SCALE = 0.62
_SCRIPT_X_TIGHTEN = 0.08
_NORMAL_PART_BUFF = 0.15

# ── LaTeX command → Unicode mapping (comprehensive) ──
_LATEX_UNICODE = {
    # Greek lowercase
    r"\alpha": 'α', r"\beta": 'β', r"\gamma": 'γ', r"\delta": 'δ',
    r"\epsilon": 'ε', r"\zeta": 'ζ', r"\eta": 'η', r"\theta": 'θ',
    r"\iota": 'ι', r"\kappa": 'κ', r"\lambda": 'λ', r"\mu": 'μ',
    r"\nu": 'ν', r"\xi": 'ξ', r"\omicron": 'o', r"\pi": 'π',
    r"\rho": 'ρ', r"\sigma": 'σ', r"\tau": 'τ', r"\upsilon": 'υ',
    r"\phi": 'φ', r"\chi": 'χ', r"\psi": 'ψ', r"\omega": 'ω',
    # Greek variant
    r"\varepsilon": 'ε', r"\vartheta": 'ϑ', r"\varkappa": 'ϰ',
    r"\varpi": 'ϖ', r"\varrho": 'ϱ', r"\varsigma": 'ς',
    r"\varphi": 'ϕ', r"\digamma": 'ϝ',
    # Greek uppercase
    r"\Gamma": 'Γ', r"\Delta": 'Δ', r"\Theta": 'Θ', r"\Lambda": 'Λ',
    r"\Xi": 'Ξ', r"\Pi": 'Π', r"\Sigma": 'Σ', r"\Upsilon": 'Υ',
    r"\Phi": 'Φ', r"\Psi": 'Ψ', r"\Omega": 'Ω',
    # Hebrew
    r"\aleph": 'ℵ', r"\beth": 'ℶ', r"\daleth": 'ℸ', r"\gimel": 'ℷ',
    # Binary ops
    r"\pm": '±', r"\mp": '∓', r"\div": '÷',
    r"\ast": '∗', r"\star": '⋆', r"\cdot": '·',
    r"\circ": '∘', r"\bullet": '•', r"\diamond": '◇',
    r"\oplus": '⊕', r"\ominus": '⊖', r"\otimes": '⊗', r"\odot": '⊙',
    r"\oslash": '⊘', r"\bigcirc": '○', r"\circledcirc": '⊚',
    r"\circledast": '⊛', r"\circleddash": '⊝', r"\circledS": 'Ⓢ',
    r"\centerdot": '·', r"\dotplus": '∔',
    r"\Box": '□', r"\square": '□', r"\blacksquare": '■',
    # Set ops
    r"\cap": '∩', r"\cup": '∪', r"\sqcap": '⊓', r"\sqcup": '⊔',
    r"\wedge": '∧', r"\vee": '∨', r"\setminus": '∖',
    r"\wr": '≀', r"\amalg": '⨿', r"\dagger": '†', r"\ddagger": '‡',
    r"\veebar": '⊻', r"\barwedge": '⊼',
    r"\boxminus": '⊟', r"\boxtimes": '⊠', r"\boxdot": '⊡',
    r"\Cap": '⋒', r"\Cup": '⋓',
    r"\leftthreetimes": '⋋', r"\rightthreetimes": '⋌',
    r"\ltimes": '⋉', r"\rtimes": '⋊', r"\divideontimes": '⋇',
    r"\intercal": '⊺',
    # Relations
    r"\leq": '≤', r"\geq": '≥', r"\ll": '≪', r"\gg": '≫',
    r"\equiv": '≡', r"\sim": '∼', r"\simeq": '≃', r"\approx": '≈',
    r"\cong": '≅', r"\neq": '≠', r"\doteq": '≐', r"\propto": '∝',
    r"\asymp": '≍', r"\bowtie": '⋈', r"\Join": '⋈',
    r"\subset": '⊂', r"\supset": '⊃', r"\subseteq": '⊆', r"\supseteq": '⊇',
    r"\sqsubset": '⊏', r"\sqsupset": '⊐',
    r"\sqsubseteq": '⊑', r"\sqsupseteq": '⊒',
    r"\in": '∈', r"\ni": '∋', r"\notin": '∉',
    r"\mid": '∣', r"\parallel": '∥', r"\nmid": '∤', r"\nparallel": '∦',
    r"\perp": '⊥',
    r"\prec": '≺', r"\succ": '≻', r"\preceq": '≼', r"\succeq": '≽',
    r"\lll": '⋘', r"\ggg": '⋙',
    r"\vdash": '⊢', r"\dashv": '⊣', r"\models": '⊨',
    r"\Vdash": '⊩', r"\vDash": '⊨', r"\Vvdash": '⊪',
    r"\neg": '¬', r"\lnot": '¬',
    r"\smile": '⌣', r"\frown": '⌢',
    # Extended relations
    r"\leqq": '≦', r"\geqq": '≧', r"\leqslant": '⩽', r"\geqslant": '⩾',
    r"\lessgtr": '≶', r"\gtrless": '≷', r"\lesseqgtr": '⋚', r"\gtreqqless": '⋛',
    r"\lessapprox": '⪅', r"\gtrapprox": '⪆', r"\lesssim": '≲', r"\gtrsim": '≳',
    r"\lessdot": '⋖', r"\gtrdot": '⋗',
    r"\triangleq": '≜', r"\circeq": '≗', r"\thicksim": '∼', r"\thickapprox": '≈',
    r"\backsim": '∽', r"\backsimeq": '⋍', r"\approxeq": '≊',
    r"\bumpeq": '≏', r"\Bumpeq": '≎', r"\between": '≬',
    r"\precsim": '≾', r"\succsim": '≿',
    r"\precapprox": '⪷', r"\succapprox": '⪸',
    r"\curlyeqprec": '⋞', r"\curlyeqsucc": '⋟',
    r"\preccurlyeq": '≼', r"\succcurlyeq": '≽',
    r"\subseteqq": '⫅', r"\supseteqq": '⫆',
    r"\Subset": '⋐', r"\Supset": '⋑',
    r"\fallingdotseq": '≒', r"\risingdotseq": '≓',
    r"\varpropto": '∝', r"\pitchfork": '⋔',
    r"\shortmid": '∣', r"\shortparallel": '∥',
    r"\nshortmid": '∤', r"\nshortparallel": '∦',
    r"\therefore": '∴', r"\because": '∵',
    r"\vartriangleleft": '⊲', r"\vartriangleright": '⊳',
    r"\trianglelefteq": '⊴', r"\trianglerighteq": '⊵',
    r"\blacktriangleleft": '◂', r"\blacktriangleright": '▸',
    r"\lhd": '◁', r"\rhd": '▷', r"\unlhd": '⊴', r"\unrhd": '⊵',
    r"\triangleleft": '◃', r"\triangleright": '▹',
    # Negated relations
    r"\ncong": '≇', r"\nsim": '≁',
    r"\nleq": '≰', r"\ngeq": '≱', r"\nleqslant": '≰', r"\ngeqslant": '≱',
    r"\nleqq": '≰', r"\ngeqq": '≱',
    r"\nprec": '⊀', r"\nsucc": '⊁', r"\npreceq": '⋠', r"\nsucceq": '⋡',
    r"\nsubseteq": '⊈', r"\nsupseteq": '⊉', r"\nsubseteqq": '⊈', r"\nsupseteqq": '⊉',
    r"\subsetneq": '⊊', r"\supsetneq": '⊋',
    r"\varsubsetneq": '⊊', r"\varsupsetneq": '⊋',
    r"\varsubsetneqq": '⫋', r"\varsupsetneqq": '⫌',
    r"\lnapprox": '⪉', r"\gnapprox": '⪊', r"\lneqq": '≨', r"\gneqq": '≩',
    r"\lnsim": '⋦', r"\gnsim": '⋧', r"\lvertneqq": '≨', r"\gvertneqq": '≩',
    r"\ntriangleleft": '⋪', r"\ntriangleright": '⋫',
    r"\ntrianglelefteq": '⋬', r"\ntrianglerighteq": '⋭',
    r"\nVDash": '⊯', r"\nvDash": '⊭', r"\nvdash": '⊬',
    r"\precnapprox": '⪹', r"\precnsim": '⋨', r"\succnapprox": '⪺', r"\succnsim": '⋩',
    r"\nless": '≮', r"\ngtr": '≯',
    # Arrows
    r"\to": '→',
    r"\leftarrow": '←', r"\rightarrow": '→', r"\leftrightarrow": '↔',
    r"\Leftarrow": '⇐', r"\Rightarrow": '⇒', r"\Leftrightarrow": '⇔',
    r"\longleftarrow": '←', r"\longrightarrow": '→',
    r"\longleftrightarrow": '↔',
    r"\mapsto": '↦', r"\longmapsto": '↦',
    r"\hookrightarrow": '↪', r"\hookleftarrow": '↩',
    r"\uparrow": '↑', r"\downarrow": '↓', r"\updownarrow": '↕',
    r"\Uparrow": '⇑', r"\Downarrow": '⇓', r"\Updownarrow": '⇕',
    r"\rightleftharpoons": '⇋',
    r"\nLeftarrow": '⇍', r"\nRightarrow": '⇏', r"\nLeftrightarrow": '⇎',
    r"\rightharpoonup": '⇀', r"\rightharpoondown": '⇁',
    r"\leftharpoonup": '↼', r"\leftharpoondown": '↽',
    # Misc symbols
    r"\infty": '∞', r"\forall": '∀', r"\exists": '∃', r"\nexists": '∄',
    r"\emptyset": '∅', r"\varnothing": '∅',
    r"\nabla": '∇', r"\partial": '∂', r"\eth": 'ð',
    r"\angle": '∠', r"\measuredangle": '∡',
    r"\triangle": '△', r"\triangledown": '▽', r"\vartriangle": '△',
    r"\blacktriangle": '▲', r"\blacktriangledown": '▼',
    r"\bigtriangleup": '△', r"\bigtriangledown": '▽',
    r"\lozenge": '◊', r"\blacklozenge": '⧫',
    r"\cdots": '⋯', r"\vdots": '⋮', r"\ddots": '⋱', r"\ldots": '…',
    r"\prime": '′', r"\backprime": '‵',
    r"\sharp": '♯', r"\flat": '♭', r"\natural": '♮',
    r"\surd": '√', r"\hbar": 'ℏ', r"\ell": 'ℓ', r"\wp": '℘',
    r"\imath": 'ı', r"\jmath": 'ȷ', r"\hslash": 'ℏ',
    r"\clubsuit": '♣', r"\diamondsuit": '♢', r"\heartsuit": '♡',
    r"\spadesuit": '♠',
    r"\bigstar": '★', r"\Game": '⅁', r"\Finv": 'Ⅎ', r"\Bbbk": '𝕜',
    r"\complement": '∁', r"\mho": '℧',
    r"\Re": 'ℜ', r"\Im": 'ℑ',
    r"\diagup": '╱', r"\diagdown": '╲',
    # Delimiters (keep structural commands, these are handled specially)
    r"\backslash": '\\',
    # Math fonts (these become prefix modifiers — handle in processing)
    # Standard function names — keep as text
}

def _convert_visible_math_text(text, translate_table=None):
    s = str(text)

    # 1. Apply LaTeX → Unicode mapping FIRST (longer patterns first to avoid
    #    \left eating \leftarrow, etc.)
    for cmd, uni in sorted(_LATEX_UNICODE.items(), key=lambda x: -len(x[0])):
        s = s.replace(cmd, uni)

    # 2. Strip remaining structural commands
    s = s.replace(r'\left', '').replace(r'\right', '')
    s = s.replace(r'\quad', '  ').replace(r'\qquad', '    ')
    s = s.replace('{', '').replace('}', '')
    s = s.replace('\\\\', '\n')  # array row separator → newline

    if translate_table is not None:
        s = s.translate(translate_table)
    return s

def _consume_script_content(tex_string, start_index):
    if start_index >= len(tex_string):
        return '', start_index
    if tex_string[start_index] != '{':
        return tex_string[start_index], start_index + 1

    depth = 1
    idx = start_index + 1
    while idx < len(tex_string) and depth > 0:
        ch = tex_string[idx]
        if ch == '{':
            depth += 1
        elif ch == '}':
            depth -= 1
        idx += 1
    return tex_string[start_index + 1:idx - 1], idx

def _tokenize_math_text(tex_string):
    tokens = []
    idx = 0
    while idx < len(tex_string):
        ch = tex_string[idx]
        if ch in '^_':
            content, idx = _consume_script_content(tex_string, idx + 1)
            if content:
                tokens.append(('sup' if ch == '^' else 'sub', content))
            continue

        start = idx
        while idx < len(tex_string) and tex_string[idx] not in '^_':
            idx += 1
        if idx > start:
            tokens.append(('base', tex_string[start:idx]))
    return tokens or [('base', tex_string)]

def _make_text_token(text, font_size, **kwargs):
    return Text(_convert_visible_math_text(text), font_size=font_size, fill_color=WHITE, **kwargs)

def _make_script_token(text, font_size, role, **kwargs):
    translate = _SUPER_TRANS if role == 'sup' else _SUB_TRANS
    visible = _convert_visible_math_text(text, translate_table=translate)
    return Text(visible, font_size=font_size * _SCRIPT_SCALE, fill_color=WHITE, **kwargs)

def _position_script_token(mob, anchor, role):
    x = anchor.get_right()[0] + mob.width * 0.20 - _SCRIPT_X_TIGHTEN
    if role == 'sup':
        y = anchor.get_top()[1] - mob.height * 0.05
    else:
        y = anchor.get_bottom()[1] + mob.height * 0.05
    mob.move_to([x + mob.width / 2, y, 0])

def _build_math_part(tex_string, font_size, **kwargs):
    tokens = _tokenize_math_text(str(tex_string))
    part = MathTexPart()
    part.tex_string = str(tex_string)
    part.fill_opacity = 1.0

    cursor_x = 0.0
    baseline_anchor = None
    part_role = 'normal'

    for idx, (role, content) in enumerate(tokens):
        mob = _make_text_token(content, font_size, **kwargs) if role == 'base' else _make_script_token(content, font_size, role, **kwargs)

        if role == 'base':
            mob.move_to([cursor_x + mob.width / 2, 0, 0])
            cursor_x = mob.get_right()[0] + 0.02
            baseline_anchor = mob
            part_role = 'normal'
        else:
            if baseline_anchor is None and idx == 0 and len(tokens) == 1:
                mob.move_to([mob.width / 2, 0, 0])
                part_role = role
            else:
                anchor = baseline_anchor if baseline_anchor is not None else mob
                _position_script_token(mob, anchor, role)
                cursor_x = max(cursor_x, mob.get_right()[0] + 0.02)

        part.add(mob)

    part._math_role = part_role
    return part

def _layout_math_parts(parts):
    cursor_x = 0.0
    anchor_part = None

    for part in parts:
        role = getattr(part, '_math_role', 'normal')
        if role in ('sup', 'sub') and anchor_part is not None:
            _position_script_token(part, anchor_part, role)
            cursor_x = max(cursor_x, part.get_right()[0] + _NORMAL_PART_BUFF)
            continue

        part.move_to([cursor_x + part.width / 2, 0, 0])
        cursor_x = part.get_right()[0] + _NORMAL_PART_BUFF
        anchor_part = part

    result = VGroup(*parts)
    result.move_to(ORIGIN)
    return result

def _native_mathtex_init(self, *tex_strings, arg_separator=' ',
                          substrings_to_isolate=None, tex_to_color_map=None,
                          tex_environment='align*', **kwargs):
    """Monkey-patched MathTex.__init__ — renders simple math via Text, no LaTeX.

    It preserves Manim's top-level brace splitting so TransformMatchingTex can
    still match equation parts, but lays out superscripts/subscripts manually
    instead of relying on TeX compilation."""

    font_size = kwargs.pop('font_size', 48)

    self.arg_separator = arg_separator
    self.substrings_to_isolate = [] if substrings_to_isolate is None else list(substrings_to_isolate)
    self.tex_to_color_map = dict(tex_to_color_map or {})
    self.substrings_to_isolate.extend(self.tex_to_color_map.keys())
    self.tex_environment = tex_environment
    self.brace_notation_split_occurred = False
    self.tex_strings = self._prepare_tex_strings(tex_strings)

    math_parts = [_build_math_part(ts, font_size, **kwargs) for ts in self.tex_strings]
    result = _layout_math_parts(math_parts)

    result.tex_string = self.arg_separator.join(self.tex_strings)
    result.tex_strings = list(self.tex_strings)
    result.arg_separator = arg_separator
    result.tex_environment = tex_environment
    result.substrings_to_isolate = list(self.substrings_to_isolate)
    result.tex_to_color_map = dict(self.tex_to_color_map)

    for tex, color in result.tex_to_color_map.items():
        for part in result.submobjects:
            if getattr(part, 'tex_string', None) == tex:
                part.set_color(color)

    self.__dict__.update(result.__dict__)
    self.__class__ = type(result)

# NOTE: Keep real Manim MathTex enabled by default.
# The old native-text fallback rendered many commands literally (e.g. \\frac,
# \\sqrt, \\mathbb, matrices, accents) instead of as math glyphs/layout.
# Set _USE_NATIVE_MATHTEX = True to bypass LaTeX entirely (fast, Unicode-only).
_OrigMathTexInit = _OrigMathTex.__init__
_USE_NATIVE_MATHTEX = False


def _mathtex_init_dispatch(self, *args, **kwargs):
    if _USE_NATIVE_MATHTEX:
        _native_mathtex_init(self, *args, **kwargs)
    else:
        _OrigMathTexInit(self, *args, **kwargs)


_OrigMathTex.__init__ = _mathtex_init_dispatch
