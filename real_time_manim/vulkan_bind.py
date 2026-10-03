import ctypes
import hashlib
import inspect
import os
import re
import sys
import math
import time
import shutil
import subprocess
import tempfile
import numpy as np
from manim import (
    Square, Circle, Line, Rectangle, Polygon, Polygram,
    Arrow, Dot, DashedLine,
    Arc, Ellipse, Point, Text, VGroup, Group, OUT, ORIGIN, WHITE
)
from manim.animation.transform import Transform as _ManimTransform
from manim.mobject.types.image_mobject import AbstractImageMobject
from manim.mobject.types.point_cloud_mobject import PMobject
from manim.animation.transform import FadeTransform as _ManimFadeTransform

from real_time_manim.rate_functions import (
    _smooth, _linear, _rush_into, _rush_from,
    _there_and_back, _slow_into, _double_smooth,
    _wiggle, _lingering, _exponential_decay,
    _squish_rate_func, _sigmoid,
)
from real_time_manim.animations import (
    Animation, Create, Uncreate, DrawBorderThenFill, Write, Unwrite,
    ShowIncreasingSubsets, SpiralIn,
    Blink, TypeWithCursor, UntypeWithCursor,
    Succession, Wait, Add, AnimationGroup, MoveToTarget, Indicate,
    FadeIn, FadeOut, FadeTransform, FadeTransformPieces,
    Rotating, Rotate,
    Transform, ReplacementTransform,
    TransformMatchingAbstractBase, TransformMatchingShapes, TransformMatchingTex,
    GrowFromCenter, GrowArrow, GrowFromEdge, GrowFromPoint, SpinInFromNothing,
    ApplyWave, Circumscribe, ShowPassingFlash, Homotopy, MoveAlongPath,
    set_anim_opacity, get_anim_opacity,
    set_anim_rotation, get_anim_rotation,
    set_anim_rotation_delta, get_anim_rotation_delta, clear_anim_rotation_delta,
    TARGET_FPS, FRAME_DURATION,
    TextDecimalNumber,
)
from real_time_manim.vulkan_util import manim_to_screen, rotate_point, get_fill_rgb, get_stroke_rgb, get_stroke_w
from real_time_manim.vulkan_shapes import ShapeMixin
from real_time_manim.vulkan_text import TextMixin

from manim import ChangingDecimal as _OrigChangingDecimal
from manim import ChangeDecimalToValue as _OrigChangeDecimalToValue
_OrigChangingDecimal.check_validity_of_input = lambda self, dm: None
_OrigChangeDecimalToValue.check_validity_of_input = lambda self, dm: None

from manim.animation.animation import prepare_animation as _orig_prepare_animation
from real_time_manim.animations.base import Animation as _OurAnimation
def _patched_prepare_animation(anim):
    if isinstance(anim, _OurAnimation):
        return anim
    return _orig_prepare_animation(anim)
import manim.animation.speedmodifier as _sm
_sm.prepare_animation = _patched_prepare_animation
import manim.animation.animation as _aa
_aa.prepare_animation = _patched_prepare_animation

# Broadcast should emanate from the broadcast mobject's own position by
# default (focal_point = mobject.get_center()), so the glow follows the
# object instead of staying at manim's default ORIGIN.
import manim.animation.specialized as _spec
_orig_broadcast_init = _spec.Broadcast.__init__
def _patched_broadcast_init(self, mobject, focal_point=None, **kwargs):
    if focal_point is None:
        focal_point = mobject.get_center()
    _orig_broadcast_init(self, mobject, focal_point=focal_point, **kwargs)
_spec.Broadcast.__init__ = _patched_broadcast_init

# ── Monkey-patch MathTex to avoid \special{dvisvgm:raw} tags in TeX files ──
# Standard manim wraps each tex_string in \special{dvisvgm:raw <g id='uniqueNNN'>}
# so that dvisvgm produces named SVG groups.  We remove this wrapping and instead
# assign SVG glyphs to tex_strings via positional matching (SVG elements appear in
# the same order as the tex_strings they originate from).
from manim.mobject.text.tex_mobject import MathTex as _OrigMathTex
from manim.mobject.text.tex_mobject import MathTexPart, MATHTEX_SUBSTRING

def _patched_join_tex_strings(self, tex_strings, substrings_to_isolate):
    """Join tex_strings without \\special{dvisvgm:raw} wrapping.
    Still populates matched_strings_and_ids so get_part_by_tex etc. can work."""
    joined_string = ""
    ssIdx = 0
    for idx, tex_string in enumerate(tex_strings):
        self.matched_strings_and_ids.append((tex_string, f"unique{idx:03d}"))
        unprocessed_string = str(tex_string)
        processed_string = ""
        while len(unprocessed_string) > 0:
            first_match = self._locate_first_match(
                substrings_to_isolate, unprocessed_string
            )
            if first_match:
                processed, unprocessed_string = self._patched_handle_match(
                    ssIdx, first_match
                )
                processed_string = processed_string + processed
                ssIdx += 1
            else:
                processed_string = processed_string + unprocessed_string
                unprocessed_string = ""
        string_part = processed_string
        if idx < len(tex_strings) - 1:
            string_part += self.arg_separator
        joined_string = joined_string + string_part
    return joined_string

def _patched_handle_match(self, ssIdx, first_match):
    """Handle substring isolation match without \\special wrapping."""
    pre_match = first_match.group(1)
    matched_string = first_match.group(2)
    post_match = first_match.group(3)
    self.matched_strings_and_ids.append(
        (matched_string, f"unique{ssIdx:03d}{MATHTEX_SUBSTRING}")
    )
    processed_string = pre_match + matched_string
    unprocessed_string = post_match
    return processed_string, unprocessed_string

def _patched_break_up_by_substrings(self):
    """Reorganize submobjects into MathTexPart instances.
    Falls back to positional matching when the SVG lacks named groups
    (i.e. when \\special{dvisvgm:raw} was not used)."""
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

_OrigMathTex._join_tex_strings_with_unique_deliminters = _patched_join_tex_strings
_OrigMathTex._handle_match = _patched_handle_match
_OrigMathTex._patched_handle_match = _patched_handle_match  # used in patched_join above
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


class BITMAPINFOHEADER(ctypes.Structure):
    _pack_ = 1
    _fields_ = [
        ("biSize", ctypes.c_uint32),
        ("biWidth", ctypes.c_long),
        ("biHeight", ctypes.c_long),
        ("biPlanes", ctypes.c_uint16),
        ("biBitCount", ctypes.c_uint16),
        ("biCompression", ctypes.c_uint32),
        ("biSizeImage", ctypes.c_uint32),
        ("biXPelsPerMeter", ctypes.c_long),
        ("biYPelsPerMeter", ctypes.c_long),
        ("biClrUsed", ctypes.c_uint32),
        ("biClrImportant", ctypes.c_uint32),
    ]

class BITMAPFILEHEADER(ctypes.Structure):
    _pack_ = 1
    _fields_ = [
        ("bfType", ctypes.c_uint16),
        ("bfSize", ctypes.c_uint32),
        ("bfReserved1", ctypes.c_uint16),
        ("bfReserved2", ctypes.c_uint16),
        ("bfOffBits", ctypes.c_uint32),
    ]


def _setup_anim_scene(anim, scene):
    """Give a manim animation its scene, the way manim's ``Scene.play`` does.

    manim calls ``Animation._setup_scene(scene)`` before ``begin()``: it stores
    ``anim.scene`` (``AddTextWordByWord`` reads it, and so do other manim
    classes) and, for introducers, adds the animation's mobject to the scene.
    RTM drives manim's animation classes directly, so it has to do the same --
    otherwise such an animation dies with "has no attribute 'scene'".

    Returns True when the animation learned about the scene.
    """
    setup = getattr(anim, "_setup_scene", None)
    if callable(setup):
        try:
            setup(scene)
        except Exception:
            pass
    # manim 0.21's hook stores anim.scene itself; 0.20's only registers
    # introducers' mobjects, so make sure the attribute is there either way.
    if getattr(anim, "scene", None) is None:
        try:
            anim.scene = scene
        except Exception:
            return False
    return getattr(anim, "scene", None) is scene


def _drive_mobject_updaters(scene, dt, patch_group=None, unpatch_group=None):
    """Run every mobject updater on ``scene``, as manim does once per frame.

    Updaters are *stateful* -- they accumulate over frames -- so this is only
    meaningful while playing forward.  A seek should pass ``dt=0`` to re-anchor
    instead of replaying history, which is what ``Timeline`` does.

    ``patch_group``/``unpatch_group`` are optional hooks for the VGroup rotate
    machinery, which lives in ``play()`` as closures over its per-frame state
    (``_anim_alpha``, ``_prev_vg_rotation``); the play loop passes them, the
    timeline path does not need them.
    """
    if patch_group is not None:
        for mob in scene.mobjects:
            if isinstance(mob, (VGroup, Group)) and getattr(mob, 'updaters', None):
                patch_group(mob)

    for mob in reversed(scene.mobjects):
        if getattr(mob, 'updaters', None) and not getattr(mob, 'updating_suspended', False):
            for updater in mob.updaters:
                nparams = len(inspect.signature(updater).parameters)
                if nparams == 0:
                    updater()
                elif nparams == 1:
                    updater(mob)
                else:
                    updater(mob, dt)

    if unpatch_group is not None:
        for mob in scene.mobjects:
            if isinstance(mob, (VGroup, Group)):
                unpatch_group(mob)


# Stable texture slot for the phase-5.4 camera fallback: the rasterised frame
# is re-uploaded whenever its content digest changes, but always through
# this one token (image tokens from vulkan_image start at 1, so no clash).
_RASTER_TOKEN = 0xCA11E4A5


def _raster_debug(message):
    """Append a line to $RTM_RASTER_DEBUG when that is set (phase-5.4 tracing)."""
    import os
    path = os.environ.get("RTM_RASTER_DEBUG")
    if not path:
        return
    try:
        with open(path, "a", encoding="utf-8") as fh:
            fh.write(message + "\n")
    except Exception:
        pass

def container_subs(mob):
    """The children of a container mobject.

    manim's ``Mobject.__iter__`` yields *self first* when the mobject has points
    (``it.chain([self] if self.has_points() else [], self.submobjects)``), so
    ``enumerate(mob)`` / ``len(list(mob))`` on a point-bearing VGroup hands the
    container back to itself -- a 978-frame recursion in HeatDiagramPlot, and an
    off-by-one in the progress segmentation.  Iterate ``submobjects`` instead.
    """
    return getattr(mob, "submobjects", None) or ()


class MLWindow(ShapeMixin, TextMixin):
    # When True, play() records a timeline instead of rendering (see play()).
    _schedule_mode = False
    # Windows created while this is True are built hidden (never shown), so
    # offline work -- frame export, fast record, batch rendering -- does not pop
    # windows onto the desktop.  Set it around a scene run, then restore.
    _hidden_default = False
    # Every constructed window is registered here (used by frames.FrameServer
    # to grab the window a scene created for itself).
    _registry = []

    def __init__(self, w=1920, h=1080, hidden=None):
        if hidden is None:
            hidden = bool(getattr(type(self), '_hidden_default', False))
        self.hidden = bool(hidden)
        self.win_w = w
        self.win_h = h
        self.frame_count = 0
        self.scene = None
        self._active_anims = []
        # Schedule mode (2.0.0): when the class flag _schedule_mode is True,
        # play() records animations on a global timeline instead of rendering,
        # so any frame can later be produced on demand via build_timeline().
        self._sched = []          # list of (start_seconds, animation)
        self._cursor = 0.0        # current end of the recorded timeline
        self._defer_close = bool(getattr(type(self), '_schedule_mode', False))
        type(self)._registry.append(self)
        self._recording = False
        self._record_dir = None
        self._record_frame_idx = 0
        self._record_path = None
        self._record_fps = 60

        # Fast offline record — renders at full speed via simulated time
        self._fast_record = False
        self._fast_record_path = None
        self._fast_record_fps = 60
        self._fast_record_sim_time = 0.0
        self._fast_record_frame_idx = 0
        self._fast_record_segment = None  # (start_frame, end_frame) or None for all

        base_dir = os.path.dirname(os.path.abspath(__file__))
        # Search order: bundled lib (pip-installed package) → dev repo release → dev repo debug
        if sys.platform == "darwin":
            candidates = [
                os.path.join(base_dir, "vulkan_core.dylib"),
                os.path.normpath(os.path.join(base_dir, "..", "dist", "release", "vulkan_core.dylib")),
                os.path.normpath(os.path.join(base_dir, "..", "dist", "debug", "vulkan_core.dylib")),
            ]
            lib_kind = "vulkan_core.dylib"
            build_hint = "native/build_mac.sh (requires Vulkan SDK + MoltenVK)"
        else:
            candidates = [
                os.path.join(base_dir, "vulkan_core.dll"),
                os.path.normpath(os.path.join(base_dir, "..", "dist", "release", "vulkan_core.dll")),
                os.path.normpath(os.path.join(base_dir, "..", "dist", "debug", "vulkan_core.dll")),
            ]
            lib_kind = "vulkan_core.dll"
            build_hint = "native/build.ps1 (requires Vulkan SDK + MinGW-w64)"
        dll_path = next((p for p in candidates if os.path.exists(p)), None)
        if dll_path is None:
            raise FileNotFoundError(
                f"{lib_kind} not found. If running from source, build it with {build_hint}."
            )

        self.dll = ctypes.CDLL(dll_path)

        self.dll.Vulkan_Init.restype = ctypes.c_int
        self.dll.Vulkan_Init.argtypes = [ctypes.c_int, ctypes.c_int]
        self.dll.Vulkan_Tick.restype = ctypes.c_int
        self.dll.Vulkan_Tick.argtypes = []
        self.dll.Vulkan_Shutdown.restype = None
        self.dll.Vulkan_Shutdown.argtypes = []
        self.dll.ClearShapes.restype = None
        self.dll.ClearShapes.argtypes = []

        self.dll.AddRect.restype = None
        self.dll.AddRect.argtypes = [
            ctypes.c_float, ctypes.c_float, ctypes.c_float,
            ctypes.c_float, ctypes.c_float,
            ctypes.c_int, ctypes.c_int, ctypes.c_int,
            ctypes.c_int, ctypes.c_int, ctypes.c_int,
            ctypes.c_float, ctypes.c_float,
            ctypes.c_float,
        ]
        self.dll.AddCircle.restype = None
        self.dll.AddCircle.argtypes = [
            ctypes.c_float, ctypes.c_float, ctypes.c_float,
            ctypes.c_int, ctypes.c_int, ctypes.c_int,
            ctypes.c_int, ctypes.c_int, ctypes.c_int,
            ctypes.c_float, ctypes.c_float,
            ctypes.c_float,
        ]
        self.dll.AddLine.restype = None
        self.dll.AddLine.argtypes = [
            ctypes.c_float, ctypes.c_float,
            ctypes.c_float, ctypes.c_float,
            ctypes.c_int, ctypes.c_int,
            ctypes.c_int, ctypes.c_int,
            ctypes.c_float,
        ]
        self.dll.AddLineStrip.restype = None
        self.dll.AddLineStrip.argtypes = [
            ctypes.POINTER(ctypes.c_float),
            ctypes.POINTER(ctypes.c_float),
            ctypes.c_int,
            ctypes.c_int, ctypes.c_int,
            ctypes.c_int, ctypes.c_int,
            ctypes.c_float,
        ]
        self.dll.AddEllipse.restype = None
        self.dll.AddEllipse.argtypes = [
            ctypes.c_float, ctypes.c_float,
            ctypes.c_float, ctypes.c_float,
            ctypes.c_int, ctypes.c_int, ctypes.c_int,
            ctypes.c_int, ctypes.c_int, ctypes.c_int,
            ctypes.c_float, ctypes.c_float,
            ctypes.c_float,
        ]
        self.dll.AddPolygon.restype = None
        self.dll.AddPolygon.argtypes = [
            ctypes.c_float, ctypes.c_float,
            ctypes.c_int, ctypes.c_int, ctypes.c_int,
            ctypes.c_int, ctypes.c_int, ctypes.c_int,
            ctypes.c_float, ctypes.c_int,
            ctypes.POINTER(ctypes.c_float),
            ctypes.c_float, ctypes.c_float,
            ctypes.c_int,
        ]
        self.dll.AddDashedLine.restype = None
        self.dll.AddDashedLine.argtypes = [
            ctypes.c_float, ctypes.c_float,
            ctypes.c_float, ctypes.c_float,
            ctypes.c_int, ctypes.c_int,
            ctypes.c_int, ctypes.c_int,
            ctypes.c_float, ctypes.c_float,
            ctypes.c_float,
        ]
        self.dll.AddArc.restype = None
        self.dll.AddArc.argtypes = [
            ctypes.c_float, ctypes.c_float, ctypes.c_float,
            ctypes.c_float, ctypes.c_float,
            ctypes.c_int, ctypes.c_int, ctypes.c_int,
            ctypes.c_float,
            ctypes.c_float,
        ]
        self.dll.AddPoint.restype = None
        self.dll.AddPoint.argtypes = [
            ctypes.c_float, ctypes.c_float,
            ctypes.c_int, ctypes.c_int, ctypes.c_int,
            ctypes.c_float,
            ctypes.c_float,
        ]
        self.dll.AddText.restype = None
        self.dll.AddText.argtypes = [
            ctypes.c_float, ctypes.c_float,
            ctypes.c_int, ctypes.c_int, ctypes.c_int,
            ctypes.c_float, ctypes.c_float,
            ctypes.c_char_p, ctypes.c_float,
        ]
        self.dll.Text_LoadFont.restype = ctypes.c_int
        self.dll.Text_LoadFont.argtypes = [ctypes.POINTER(ctypes.c_ubyte), ctypes.c_int]
        self.dll.AddBezierPath.restype = None
        self.dll.AddBezierPath.argtypes = [
            ctypes.POINTER(ctypes.c_float), ctypes.c_int,
            ctypes.c_int, ctypes.c_int, ctypes.c_int, ctypes.c_float,
            ctypes.c_int, ctypes.c_int, ctypes.c_int, ctypes.c_float,
            ctypes.c_float, ctypes.c_int, ctypes.c_int,
            ctypes.c_float,
        ]

        self.dll.SaveScreenshot.restype = ctypes.c_int
        self.dll.SaveScreenshot.argtypes = [ctypes.c_char_p]

        # Textured quads (plan 4.4B): one stable token per mobject owning a GPU
        # texture slot, refreshed only when the pixel digest changes.
        self.dll.AddImageQuad.restype = None
        self.dll.AddImageQuad.argtypes = [
            ctypes.c_ulonglong, ctypes.c_ulonglong,
            ctypes.POINTER(ctypes.c_ubyte), ctypes.c_int, ctypes.c_int,
            ctypes.POINTER(ctypes.c_float), ctypes.c_float,
        ]

        # Frame clear colour (manim's `camera.background_color`).  Optional: a DLL
        # built before this existed simply keeps clearing to black.
        _set_background = getattr(self.dll, 'SetBackgroundColor', None)
        if _set_background is not None:
            _set_background.restype = None
            _set_background.argtypes = [ctypes.c_float, ctypes.c_float, ctypes.c_float]
        self._set_background = _set_background

        self.dll.Vulkan_SetWindowVisible.restype = None
        self.dll.Vulkan_SetWindowVisible.argtypes = [ctypes.c_int]
        self.dll.Vulkan_InitEx.restype = ctypes.c_int
        self.dll.Vulkan_InitEx.argtypes = [ctypes.c_int, ctypes.c_int, ctypes.c_int]

        init_ex = getattr(self.dll, 'Vulkan_InitEx', None)
        if self.hidden and init_ex is not None:
            # Create the window without ever showing it: offline work (frame
            # export, fast record) must not pop a window onto the desktop.
            if not init_ex(w, h, 1):
                raise RuntimeError("Vulkan_InitEx failed")
        else:
            if self.dll.Vulkan_Init(w, h) != 1:
                raise RuntimeError("Vulkan_Init failed")
            if self.hidden:
                # Older DLL without hidden creation: hide right after building.
                self.set_visible(False)

        if sys.platform == "darwin":
            font_paths = [
                "/System/Library/Fonts/Supplemental/Times New Roman.ttf",
                "/System/Library/Fonts/Supplemental/Arial.ttf",
                "/System/Library/Fonts/Supplemental/Helvetica.ttc",
            ]
        else:
            font_paths = [r"C:\Windows\Fonts\times.ttf", r"C:\Windows\Fonts\arial.ttf"]
        font_loaded = False
        for fp in font_paths:
            try:
                with open(fp, "rb") as f:
                    data = f.read()
                arr = (ctypes.c_ubyte * len(data))(*data)
                if self.dll.Text_LoadFont(arr, len(data)):
                    font_loaded = True
                    break
            except Exception:
                pass
        if not font_loaded:
            raise RuntimeError("Failed to load any font")

    def _publish_background_color(self, scene):
        """Hand native the frame's clear colour.

        manim lets a scene override it (`self.camera.background_color`, falling back
        to `config.background_color`); the native side used to hard-code black, so a
        scene with a light background rendered on black (measured on the gallery logo
        scene: CE luma 220 vs RTM 9.5, the largest mismatch in the suite).
        """
        setter = getattr(self, "_set_background", None)
        if setter is None:
            return
        camera = getattr(scene, "camera", None)
        colour = getattr(camera, "background_color", None)
        if colour is None:
            try:
                from manim import config as _config
                colour = _config["background_color"]
            except Exception:
                return
        try:
            if isinstance(colour, str):
                from manim.utils.color.core import ManimColor
                colour = ManimColor(colour)
            rgb = colour.to_rgb() if hasattr(colour, "to_rgb") else colour
            values = [float(v) for v in list(rgb)[:3]]
        except Exception:
            return
        if len(values) == 3:
            setter(*values)

    @staticmethod
    def _camera_needs_raster(scene, cam):
        """True for a Camera subclass that redefines how a frame is captured.

        Only *unhandled* subclasses qualify (plan 5.4): a Camera that overrides
        ``capture_mobjects``/``get_frame`` can apply arbitrary per-pixel effects that
        no vector pipeline can express, but the ones RTM already models properly --
        MovingCamera (5.1), ThreeDCamera (5.2) -- must keep the vector path, or every
        camera scene would silently become a slow full-screen rasterisation.
        """
        try:
            from manim.camera.camera import Camera as _BaseCamera
        except Exception:                              # pragma: no cover
            return False
        if type(cam) is _BaseCamera:
            return False
        handled = set()
        for module, names in (
                ("manim.camera.moving_camera", ("MovingCamera",)),
                ("manim.camera.three_d_camera", ("ThreeDCamera", "SpecialThreeDCamera")),
                ("manim.camera.mapping_camera", ("MappingCamera", "OldMultiCamera")),
        ):
            for name in names:
                try:
                    mod = __import__(module, fromlist=[name])
                    handled.add(getattr(mod, name))
                except Exception:
                    pass
        if isinstance(cam, tuple(handled)) or getattr(cam, "zoomed_display", None) is not None:
            return False
        for klass in type(cam).__mro__:
            if klass is _BaseCamera:
                break
            if "capture_mobjects" in klass.__dict__ or "get_frame" in klass.__dict__:
                return True
        return False

    def _rasterise_custom_camera(self, scene):
        """Draw a custom camera's frame as one textured quad (plan 5.4).

        The scene's *own* camera does the rasterising, so whatever the subclass does
        to the pixels is included by construction.  Correct but slow: one
        rasterisation per frame, which is the accepted price of a fallback.
        Returns True when it drew the frame.
        """
        cam = getattr(scene, "camera", None)
        needs = cam is not None and self._camera_needs_raster(scene, cam)
        _raster_debug(f"camera={type(cam).__name__ if cam is not None else None} "
                      f"needs_raster={needs}")
        if not needs:
            return False
        try:
            reset = getattr(cam, "reset", None)
            if callable(reset):
                reset()                                # clear the previous frame
            cam.capture_mobjects(list(scene.mobjects))
            pixels = np.asarray(cam.pixel_array, dtype=np.float32)
        except Exception as exc:
            _raster_debug(f"  capture failed: {type(exc).__name__}: {exc}")
            return False                               # fall back to the vector path
        if pixels.ndim != 3 or pixels.shape[2] < 3:
            _raster_debug(f"  unusable pixel_array: {getattr(pixels, 'shape', None)}")
            return False
        _raster_debug(f"  pixels {pixels.shape} min={float(pixels.min()):.3f} "
                      f"max={float(pixels.max()):.3f} mean={float(pixels.mean()):.3f}")

        rgb = pixels[..., :3]
        if float(rgb.max()) <= 1.0 + 1e-3:              # manim hands back 0..1 floats
            rgb = rgb * 255.0
        image = np.empty(pixels.shape[:2] + (4,), dtype=np.uint8)
        image[..., :3] = np.clip(rgb, 0, 255).astype(np.uint8)
        if pixels.shape[2] >= 4:
            alpha = pixels[..., 3]
            if float(alpha.max()) <= 1.0 + 1e-3:
                alpha = alpha * 255.0
            image[..., 3] = np.clip(alpha, 0, 255).astype(np.uint8)
        else:
            image[..., 3] = 255

        height, width = image.shape[:2]
        data = np.ascontiguousarray(image)
        buf = (ctypes.c_ubyte * data.nbytes).from_buffer_copy(data.tobytes())
        quad = (ctypes.c_float * 8)(
            0.0, 0.0, float(self.win_w), 0.0,
            float(self.win_w), float(self.win_h), 0.0, float(self.win_h))
        key = int.from_bytes(hashlib.blake2b(data.tobytes(), digest_size=8).digest(),
                             "little")
        self.dll.AddImageQuad(_RASTER_TOKEN, key, buf, int(width), int(height), quad, 1.0)
        return True

    def sync(self, scene, angle=0.0):
        # Phase 5: publish this frame's camera viewport (None for a plain Camera,
        # so non-camera scenes keep the fixed default frame).
        from real_time_manim.camera_state import set_viewport_from_scene
        set_viewport_from_scene(scene)
        self.dll.ClearShapes()
        self._publish_background_color(scene)
        # Phase 5.4: a custom camera's frame comes back as pixels, not geometry.
        if self._rasterise_custom_camera(scene):
            return
        skip_ids = getattr(self, '_skip_mob_ids', None)
        # Also skip any root that is a descendant of another root (prevents double render)
        def _search(node, target):
            if node is target:
                return True
            for sub in getattr(node, 'submobjects', []):
                if _search(sub, target):
                    return True
            return False
        extra_skip = set()
        roots = list(scene.mobjects)
        for i, r in enumerate(roots):
            for j, other in enumerate(roots):
                if i == j:
                    continue
                if _search(other, r):
                    extra_skip.add(id(r))
                    break
        # The camera frame is a helper mobject, not scene content (Phase 5.1).
        cam_frame = getattr(getattr(scene, "camera", None), "frame", None)
        if cam_frame is not None:
            extra_skip.add(id(cam_frame))
        if skip_ids is None:
            skip_ids = extra_skip
        else:
            skip_ids |= extra_skip
        # Same-font Text roots on one visual line that need baseline alignment.
        self._row_text_ids = self._text_row_ids(scene, skip_ids)
        for mob in scene.mobjects:
            if skip_ids and id(mob) in skip_ids:
                continue
            self._send(mob, angle, parent_alpha=1.0)

    def _glyph_baseline(self, mob):
        """Approximate the x-height baseline of a Text from its glyph bottoms.

        Descender glyphs (g/p/j/y/q...) are the minority of deepest bottoms;
        the shallow half of letter bottoms cluster on the typographic baseline.
        """
        bottoms = []
        stack = list(getattr(mob, 'submobjects', []))
        while stack:
            s = stack.pop()
            pts = getattr(s, 'points', None)
            if pts is not None and len(pts):
                bottoms.append(float(pts[:, 1].min()))
            if getattr(s, 'submobjects', None):
                stack.extend(s.submobjects)
        if not bottoms:
            return None
        bottoms.sort()
        n = len(bottoms)
        shallow = bottoms[max(0, int(n * 0.5)):]
        return float(np.median(shallow))

    def _text_baseline_dy(self, mob):
        """Approach A: the vertical (manim-unit) offset that moves this Text's
        typographic baseline to ``center_y - ascent/2``, independent of its
        bounding box (which manim pads downward by descender depth).

        Clean words (no descenders) return ~0 and stay put; descender-heavy
        words are lowered, so same-font words sharing a center after arrange()
        fall onto one baseline.  Applied as a draw-time offset — the mobject's
        points are never mutated, so it cannot cause positional jitter.
        """
        base = self._glyph_baseline(mob)
        if base is None:
            return 0.0
        try:
            center = mob.get_center()[1]
        except Exception:
            return 0.0
        try:
            top = float(np.max([
                s.points[:, 1].max()
                for s in mob.family_members_with_points()
                if s.points is not None and len(s.points)
            ]))
        except Exception:
            return 0.0
        if top - base <= 1e-6:
            return 0.0
        dy = (center - (top - base) / 2.0) - base
        return dy if abs(dy) > 1e-9 else 0.0

    def _text_row_ids(self, scene, skip_ids=None):
        """Return ids of visible, same-font Text roots that sit on one visual
        line (vertical spans overlap) with at least one other such word.

        Only multi-word lines need baseline alignment — isolated words and
        titles are deliberately excluded so the offset never moves them.
        """
        roots = []
        for mob in scene.mobjects:
            if skip_ids and id(mob) in skip_ids:
                continue
            if not isinstance(mob, Text) or not getattr(mob, 'submobjects', None):
                continue
            if get_anim_opacity(mob) < 0.5:
                continue
            try:
                font_size = mob._font_size
            except Exception:
                continue
            try:
                bottom = mob.get_bottom()[1]
                top = mob.get_top()[1]
            except Exception:
                continue
            roots.append({'id': id(mob), 'font': font_size,
                          'b': bottom, 't': top})
        ids = set()
        for i in range(len(roots)):
            for j in range(i + 1, len(roots)):
                a, b = roots[i], roots[j]
                if a['font'] == b['font'] and a['b'] < b['t'] and b['b'] < a['t']:
                    ids.add(a['id'])
                    ids.add(b['id'])
        return ids

    @staticmethod
    def _edges_are_straight(pts):
        """True when every closed cubic-bezier edge keeps its two control
        points collinear with the chord between its anchors (i.e. the edges
        are straight segments, as for an axis-aligned or merely rotated quad).
        Any non-affine warp (e.g. Homotopy y += A*sin(x)) bends a control point
        off the chord, giving a non-zero perpendicular deviation, so the edge
        is a curve and must be rendered as a bezier path."""
        n = len(pts)
        if n < 4:
            return True
        # Straight segments have control points exactly collinear (dev ~ 0.0);
        # even a faint Homotopy warp yields dev >= ~1e-3.  1e-4 cleanly splits.
        TOL = 1e-4
        for i in range(0, n, 4):
            if i + 3 >= n:
                break
            p0 = pts[i][:2]
            p3 = pts[i + 3][:2]
            cx = p3[0] - p0[0]
            cy = p3[1] - p0[1]
            L2 = cx * cx + cy * cy
            if L2 <= 0.0:
                continue
            for c in (pts[i + 1][:2], pts[i + 2][:2]):
                vx = c[0] - p0[0]
                vy = c[1] - p0[1]
                cross = vx * cy - vy * cx
                dist = abs(cross) / (L2 ** 0.5)
                if dist > TOL:
                    return False
        return True

    def _send(self, *args, **kwargs):
        """Entry point: guard against a container that iterates itself.

        The real fix is ``container_subs`` (iterate ``submobjects``); this keeps a
        future mistake from turning into a RecursionError.
        """
        stack = getattr(self, '_send_stack', None)
        if stack is None:
            stack = self._send_stack = set()
        key = id(args[0]) if args else None
        if key in stack:
            return
        stack.add(key)
        try:
            return self._send_impl(*args, **kwargs)
        finally:
            stack.discard(key)

    def _send_impl(self, mob, angle=0.0, parent_alpha=1.0, parent_offset=None, parent_transforming=False, parent_is_text=False):
        w, h = self.win_w, self.win_h
        own_alpha = get_anim_opacity(mob)
        a = parent_alpha * own_alpha
        if a <= 0:
            return

        rot = get_anim_rotation(mob) + angle
        grow_rot = getattr(mob, '_grow_rot', 0.0)
        rot += grow_rot

        is_text = isinstance(mob, Text) or getattr(mob, '_is_text', False) or parent_is_text

        if isinstance(mob, Text) and hasattr(mob, 'submobjects') and mob.submobjects:
            # Tag all text characters so they're recognized as text even
            # when rendered through an intermediate Group (e.g. LaggedStartMap).
            # This prevents the _transforming stroke logic in _send_vmobject
            # from adding unwanted borders to text characters during animation.
            dy = getattr(mob, '_baseline_dy', None)
            if dy is None:
                # Bake the Approach-A baseline shift only once the word is at
                # rest (fully opaque) AND is part of a same-font multi-word line
                # (set by sync in self._row_text_ids).  Isolated text / titles
                # are left untouched, so the offset never disturbs single lines.
                # During a fade/scale pose the geometry is transient, so leave
                # dy unset and retry on a later frame instead of caching a
                # wrong zero.
                in_row = id(mob) in getattr(self, '_row_text_ids', ())
                if in_row and get_anim_opacity(mob) >= 0.95:
                    dy = self._text_baseline_dy(mob)
                    mob._baseline_dy = dy
                else:
                    dy = 0.0
            for sub in mob.submobjects:
                sub._is_text = True
                if dy != 0.0:
                    sub._baseline_dy = dy
                elif hasattr(sub, '_baseline_dy'):
                    del sub._baseline_dy
            if getattr(mob, '_letter_alphas', None) is not None:
                self._send_text_write(mob, mob._letter_alphas, w, h, a)
            else:
                self._send_vmobject(mob, a, w, h, parent_offset, 0.0, is_text=is_text)
            return

        # MathTexPart is a VMobject (not VGroup) but holds Text submobjects
        # added by _build_math_part; its children carry the actual glyph data.
        elif isinstance(mob, (VGroup, Group, MathTexPart)):
            effective_alpha = parent_alpha * own_alpha
            if effective_alpha <= 0:
                return
            # Propagate VGroup stroke_width to descendants that have stroke
            # color but no own stroke_width (e.g. AnimatedBoundary's text chars)
            vg_stroke_w = 0
            try:
                vg_stroke_w = mob.get_stroke_width()
            except Exception:
                pass
            stroke_propagated = set()
            if vg_stroke_w > 0:
                for desc in mob.family_members_with_points():
                    try:
                        dsw = desc.stroke_width
                    except Exception:
                        continue
                    if dsw <= 0:
                        try:
                            sc = desc.get_stroke_color()
                            if sc is not None and sc != '#000000' and sc != '#000':
                                desc.stroke_width = vg_stroke_w
                                stroke_propagated.add(id(desc))
                        except Exception:
                            pass
            vgroup_progress = getattr(mob, '_vulkan_progress', 1.0)
            subs = container_subs(mob)
            num_subs = len(subs)
            about = getattr(mob, '_rotation_about_point', None)
            is_3d = getattr(mob, '_rotation_3d', False)
            vgroup_center = np.array(mob.get_center(), dtype=float)
            try:
                pts = mob.get_points()
                original_center = np.array(pts.mean(axis=0) if len(pts) > 0 else mob.get_center(), dtype=float)
            except Exception:
                original_center = vgroup_center.copy()
            offset = vgroup_center - original_center
            if parent_offset is not None:
                offset = offset + parent_offset
            if is_3d:
                for sub in mob.family_members_with_points():
                    if hasattr(sub, 'points') and len(sub.points) > 0:
                        pg_gs, pg_gp = getattr(mob, '_grow_scale', None), getattr(mob, '_grow_point', None)
                        need_gs = pg_gs is not None and not hasattr(sub, '_grow_scale')
                        need_gp = pg_gp is not None and not hasattr(sub, '_grow_point')
                        if need_gs:
                            sub._grow_scale = pg_gs
                        if need_gp:
                            sub._grow_point = pg_gp
                        self._send_vmobject(sub, effective_alpha, w, h, offset, 0.0, is_text=is_text)
                        if need_gs:
                            del sub._grow_scale
                        if need_gp:
                            del sub._grow_point
                return
            for i, sub in enumerate(subs):
                sub_offset = offset
                if about is not None and rot != 0.0:
                    sub_center = np.array(sub.get_center(), dtype=float)
                    rel = sub_center - np.array(about, dtype=float)
                    cos_a = math.cos(rot)
                    sin_a = math.sin(rot)
                    rx = rel[0] * cos_a - rel[1] * sin_a
                    ry = rel[0] * sin_a + rel[1] * cos_a
                    new_center = np.array(about, dtype=float) + np.array([rx, ry, 0.0])
                    sub_offset = sub_offset + (new_center - sub_center)
                if vgroup_progress < 1.0 and num_subs > 1:
                    full_length = (num_subs - 1) * 1.0 + 1
                    value = vgroup_progress * full_length
                    lower = i * 1.0
                    sub_progress = max(0.0, min(1.0, value - lower))
                    sub._vulkan_progress = sub_progress
                sub_rot = rot
                sub_is_text = isinstance(sub, Text) or getattr(sub, '_is_text', False)
                effective_sub_offset = None if sub_is_text else sub_offset
                # Propagate _grow_scale/_grow_point from parent VGroup to submobjects
                # so animations like Indicate that set these on the VGroup correctly
                # scale individual characters/text pieces.
                pg_gs, pg_gp = getattr(mob, '_grow_scale', None), getattr(mob, '_grow_point', None)
                need_gs = pg_gs is not None and not hasattr(sub, '_grow_scale')
                need_gp = pg_gp is not None and not hasattr(sub, '_grow_point')
                if need_gs:
                    sub._grow_scale = pg_gs
                if need_gp:
                    sub._grow_point = pg_gp
                self._send(sub, sub_rot, parent_alpha=effective_alpha, parent_offset=effective_sub_offset, parent_transforming=getattr(mob, '_transforming', False) or parent_transforming, parent_is_text=is_text)
                if need_gs:
                    del sub._grow_scale
                if need_gp:
                    del sub._grow_point
            return

        # During generic VMobject transforms we default to bezier path rendering.
        # However, axis-aligned quads (Square/Rectangle) render more robustly
        # via the polygon path — unless they're morphing into a curved shape
        # (e.g. square→circle) which produces many vertices and needs bezier
        # smoothing.  Use vertex count to distinguish: 4-vert quad = rotating
        # (test 72, polygon path); >4 verts = morphing (test 3, bezier path).
        if getattr(mob, '_transforming', False) or parent_transforming:
            try:
                vert_count = len(mob.get_vertices()) if hasattr(mob, 'get_vertices') else 0
            except AttributeError:
                vert_count = 0
            # A transforming Square/Rectangle with <=4 anchors is only a true
            # quad — safe to render through the straight-edged _send_polygon —
            # when its edges are genuinely straight (an affine/rotational warp
            # keeps each edge's two bezier control points collinear with the
            # chord between its anchors).  A non-affine point warp such as
            # Homotopy (y += A*sin(x)) bends the control points off the chord,
            # so the top/bottom edges become curves and must be rendered as a
            # bezier path (_send_vmobject).  Collapsing them to the 4 straight
            # corner-to-corner chords makes the square a rigid parallelogram —
            # the "moving top/bottom edges should be flexible" complaint.
            quad_edges_straight = True
            if isinstance(mob, (Square, Rectangle)):
                try:
                    quad_edges_straight = self._edges_are_straight(mob.get_points())
                except Exception:
                    quad_edges_straight = True
            is_quad_morph = (isinstance(mob, (Square, Rectangle)) and vert_count <= 4
                             and not getattr(mob, '_apply_method', False)
                             and quad_edges_straight)
            if not is_quad_morph:
                # FocusOn: route through _send_dot so the dot renders
                # as a proper circle instead of bezier path
                if getattr(mob, '_focus_on_dot', False):
                    self._send_dot(mob, a, w, h)
                    return
                # Arrow: during Rotating/transforms, _send_vmobject only
                # renders the shaft bezier — the tip polygon is a submobject
                # that never gets drawn. Route through _send_arrow instead.
                if isinstance(mob, Arrow):
                    screen_rot = -rot
                    self._send_arrow(mob, a, w, h, screen_rot, None if is_text else parent_offset)
                    return
                self._send_vmobject(mob, a, w, h, None if is_text else parent_offset, 0.0, is_text=is_text)
                return

        screen_rot = -rot

        # Images have no rgba arrays and four corner points, so the shape
        # senders below cannot express them (they used to fall through to
        # _send_vmobject as an opaque white quad).  Plan 4.4B routes them to the
        # native texture pipeline instead.
        if isinstance(mob, AbstractImageMobject) and not is_text:
            from real_time_manim.vulkan_image import send_image
            if send_image(self, mob, a):
                return

        # For squares/rectangles whose points are already rotated (e.g. by
        # .animate.rotate()), the native rect dispatcher computes from the
        # axis-aligned width/height and would lose the true corner geometry.
        # Route those through the polygon path rather than _send_vmobject so
        # the fill stays a full convex quad instead of going through Bezier
        # tessellation.
        if isinstance(mob, (Square, Rectangle)) and not is_text:
            try:
                # Always route axis-aligned quads through the polygon path.
                # This keeps fills solid both for .animate.rotate() (points already
                # rotated) and for Rotating/Rotate (rotation supplied in screen_rot).
                self._send_polygon(
                    mob,
                    mob.get_vertices(),
                    a,
                    rot_override=screen_rot,
                    parent_offset=parent_offset,
                )
                return
            except Exception:
                pass

        if isinstance(mob, Square):
            self._send_square(mob, a, w, h, screen_rot, parent_offset)
        elif isinstance(mob, Rectangle):
            self._send_rectangle(mob, a, w, h, screen_rot, parent_offset)
        elif isinstance(mob, Ellipse):
            self._send_ellipse(mob, a, w, h, screen_rot, parent_offset)
        elif isinstance(mob, Dot):
            self._send_dot(mob, a, w, h)
        elif isinstance(mob, Circle):
            # same reasoning as the Arc branch: a partially drawn circle keeps the
            # real radius on the point path (native progress counts segments of a
            # full-radius circle, and `mob.width/2` is the chord early on).
            _c_progress = getattr(mob, '_vulkan_progress', 1.0)
            if 0.0 < _c_progress < 1.0:
                self._send_vmobject(mob, a, w, h, None if is_text else parent_offset,
                                    rot, is_text=is_text)
            else:
                self._send_circle(mob, a, w, h, screen_rot, parent_offset)
        elif isinstance(mob, Arrow):
            self._send_arrow(mob, a, w, h, screen_rot, parent_offset)
        elif isinstance(mob, DashedLine):
            self._send_dashed_line(mob, a, w, h, screen_rot, parent_offset)
        elif isinstance(mob, Line):
            self._send_line(mob, a, w, h, screen_rot, parent_offset)
        elif isinstance(mob, Arc):
            # `_send_arc` reads mob.radius / start_angle -- construction-time
            # attributes that a partial draw (`Create`) or a scale does not
            # update, so an arc that is being drawn or morphed has to go through
            # the point path, which tessellates the actual points and honours
            # `_vulkan_progress` (plan 4.2).
            _arc_progress = getattr(mob, '_vulkan_progress', 1.0)
            if 0.0 < _arc_progress < 1.0 or getattr(mob, '_transforming', False):
                self._send_vmobject(mob, a, w, h, None if is_text else parent_offset,
                                    rot, is_text=is_text)
            else:
                self._send_arc(mob, a, w, h)
        elif isinstance(mob, Polygon):
            self._send_polygon(mob, mob.get_vertices(), a)
        elif isinstance(mob, Polygram):
            self._send_polygon(mob, mob.get_vertices(), a)
        elif isinstance(mob, PMobject):
            # 点云/PMobject：逐点画，别走贝塞尔填充（实测会糊成实心，ink 差 4 倍）
            self._send_point_cloud(mob, a, w, h, rot=rot, parent_offset=parent_offset)
        elif isinstance(mob, Point):
            self._send_point(mob, a, w, h)
        else:
            try:
                pts = mob.get_points()
                if len(pts) >= 2:
                    self._send_vmobject(mob, a, w, h, parent_offset, rot, is_text=is_text)
            except Exception:
                pass

        # Some non-VGroup types (e.g. NumberLine) hold submobjects
        # (tick marks, etc.) that must be rendered separately. Arrow is
        # already fully handled by _send_arrow.
        if (not isinstance(mob, (Text, VGroup, Group, MathTexPart, Arrow, DashedLine))
                and hasattr(mob, 'submobjects') and mob.submobjects):
            for sub in mob.submobjects:
                self._send(sub, rot, parent_alpha=a, parent_offset=parent_offset,
                           parent_transforming=parent_transforming, parent_is_text=is_text)

    def tick(self):
        self.frame_count += 1
        result = self.dll.Vulkan_Tick()
        if result == 0:
            return False
        self.win_w = (result >> 16) & 0xFFFF
        self.win_h = result & 0xFFFF
        return True

    def _extract_add_mobjects(self, anim):
        mobjects = []
        if isinstance(anim, Add):
            mobjects.extend(anim.mobjects)
        elif isinstance(anim, Succession):
            for sub in anim.animations:
                mobjects.extend(self._extract_add_mobjects(sub))
        elif isinstance(anim, AnimationGroup):
            for sub in anim.animations:
                mobjects.extend(self._extract_add_mobjects(sub))
        return mobjects

    def play(self, *animations, **kwargs):
        """Timeline-driven playback (2.0.0).

        Animations are scheduled on one Timeline and every frame is produced by
        evaluating that schedule at time ``t`` -- the same O(1) ``render_at``
        path that powers seeking.  The legacy fork-aware pipeline is preserved
        as :meth:`_play_legacy` for reference during the migration.
        """
        if not self.scene:
            return

        if type(self)._schedule_mode:
            self._schedule_play(animations, kwargs)
            return

        from real_time_manim.timeline import Timeline
        from manim.mobject.mobject import _AnimationBuilder

        # resolve .animate builders
        resolved = []
        for anim in animations:
            if isinstance(anim, _AnimationBuilder):
                anim.anim_args['suspend_mobject_updating'] = False
                resolved.append(anim.build())
            else:
                resolved.append(anim)
        animations = tuple(resolved)

        # Add() only makes mobjects visible; it is not a timed animation.
        add_mobs = []
        for anim in animations:
            add_mobs.extend(self._extract_add_mobjects(anim))
        real_anims = [a for a in animations if not isinstance(a, Add)]

        # manim resolves a lone Wait's frozen-vs-stepping decision inside its
        # renderer, which RTM replaces -- so do it here, before the timeline is
        # built, because it decides whether the wait is counted int() or ceil().
        from real_time_manim.timeline import resolve_static_wait
        resolve_static_wait(self.scene, real_anims)

        # shared kwargs
        if 'run_time' in kwargs:
            for a in real_anims:
                a.run_time = kwargs['run_time']
        if 'rate_func' in kwargs:
            for a in real_anims:
                a.rate_func = kwargs['rate_func']

        for mob in add_mobs:
            set_anim_opacity(mob, 1.0)
            if mob not in self.scene.mobjects:
                self.scene.mobjects.append(mob)

        # make sure every animated mobject is present in the scene
        for a in real_anims:
            m = getattr(a, 'mobject', None)
            if m is not None and m not in self.scene.mobjects:
                self.scene.mobjects.append(m)
            for mob in (getattr(a, 'mobjects', None) or []):
                if mob not in self.scene.mobjects:
                    self.scene.mobjects.append(mob)
            cur = getattr(a, 'cursor', None)
            if cur is not None and cur not in self.scene.mobjects:
                self.scene.mobjects.append(cur)

        tl = Timeline(self, self.scene)
        for a in real_anims:
            tl.add(a, 0.0)
        tl.finalize()

        self._run_timeline(tl, real_anims)

    def _run_timeline(self, tl, anims=None):
        """Walk a finalized Timeline forward, drawing and capturing each frame.

        The frame count comes from ``timeline.ce_frame_count`` so a recording has
        exactly as many frames as manim would emit for the same play -- ceil for an
        animation, truncation for a wait.  Rounding both to nearest drifted by a
        frame per segment.
        """
        from real_time_manim.timeline import ce_frame_count
        fps = self._fast_record_fps if self._fast_record else 30
        dt = 1.0 / fps
        if anims is None:
            anims = [e.get("anim") for e in getattr(tl, "_entries", [])]
        n_frames = ce_frame_count(anims, tl.duration, fps)

        if self._fast_record:
            self._fast_record_sim_time = time.time()
            self._last_frame_time = self._fast_record_sim_time - dt

        for k in range(n_frames):
            frame_start = time.time()
            tl.render_at(k * dt)

            if self._fast_record:
                if getattr(self, '_fast_record_count_only', False):
                    pass
                elif getattr(self, '_fast_record_pipe_mode', True):
                    self._capture_screenshot_to_pipe()
                else:
                    self.screenshot(os.path.join(
                        self._fast_record_path,
                        f"frame_{self._fast_record_frame_idx:06d}.bmp"))
                self._fast_record_frame_idx += 1
            else:
                self._capture_frame()
                elapsed = time.time() - frame_start
                if elapsed < dt:
                    time.sleep(dt - elapsed)

        for entry in tl._entries:
            anim = entry['anim']
            if hasattr(anim, 'clean_up_from_scene'):
                try:
                    anim.clean_up_from_scene(self.scene)
                except Exception:
                    pass

    def _schedule_play(self, animations, kwargs):
        """Record a play() call on the global timeline instead of rendering.

        Mobjects are still added to the scene (so everything exists for later
        evaluation) but nothing is drawn.  Later, ``build_timeline()`` turns the
        whole recording into a Timeline whose every frame can be produced on
        demand.
        """
        from manim.mobject.mobject import _AnimationBuilder

        resolved = []
        for anim in animations:
            if isinstance(anim, _AnimationBuilder):
                anim.anim_args['suspend_mobject_updating'] = False
                resolved.append(anim.build())
            else:
                resolved.append(anim)
        animations = tuple(resolved)

        add_mobs = []
        for anim in animations:
            add_mobs.extend(self._extract_add_mobjects(anim))
        real = [a for a in animations if not isinstance(a, Add)]

        if 'run_time' in kwargs:
            for a in real:
                a.run_time = kwargs['run_time']
        if 'rate_func' in kwargs:
            for a in real:
                a.rate_func = kwargs['rate_func']

        for mob in add_mobs:
            set_anim_opacity(mob, 1.0)
            if mob not in self.scene.mobjects:
                self.scene.mobjects.append(mob)
        for a in real:
            m = getattr(a, 'mobject', None)
            if m is not None and m not in self.scene.mobjects:
                self.scene.mobjects.append(m)
            for mob in (getattr(a, 'mobjects', None) or []):
                if mob not in self.scene.mobjects:
                    self.scene.mobjects.append(mob)
            cur = getattr(a, 'cursor', None)
            if cur is not None and cur not in self.scene.mobjects:
                self.scene.mobjects.append(cur)

        duration = max((float(getattr(a, 'run_time', 1.0) or 1.0) for a in real),
                       default=0.0)
        for a in real:
            self._sched.append((self._cursor, a))
        self._cursor += duration

    def build_timeline(self):
        """Turn the recorded schedule into a Timeline (begin() once)."""
        from real_time_manim.timeline import Timeline
        tl = Timeline(self, self.scene)
        for start, anim in self._sched:
            tl.add(anim, start)
        tl.finalize()
        return tl

    def _play_legacy(self, *animations, **kwargs):
        if not self.scene:
            return

        self._skip_mob_ids = set()

        screenshot_at = kwargs.get('screenshot_at', None)

        resolved = []
        for anim in animations:
            from manim.mobject.mobject import _AnimationBuilder
            if isinstance(anim, _AnimationBuilder):
                anim.anim_args['suspend_mobject_updating'] = False
                built = anim.build()
                resolved.append(built)
            elif isinstance(anim, AnimationGroup):
                sub_resolved = []
                for sub in anim.animations:
                    if isinstance(sub, _AnimationBuilder):
                        sub.anim_args['suspend_mobject_updating'] = False
                        built = sub.build()
                        sub_resolved.append(built)
                    else:
                        sub_resolved.append(sub)
                anim.animations = sub_resolved
                resolved.append(anim)
            else:
                resolved.append(anim)
        animations = tuple(resolved)

        add_mobs = []
        for anim in animations:
            add_mobs.extend(self._extract_add_mobjects(anim))

        all_mobjects = list(add_mobs)
        for anim in animations:
            if isinstance(anim, (Create, Write, DrawBorderThenFill, FadeIn, Rotating, Rotate, GrowArrow, Indicate, ShowPassingFlash)) and anim.mobject:
                if isinstance(anim, (Create, DrawBorderThenFill)):
                    anim.mobject._vulkan_progress = 0.0
                if anim.mobject not in all_mobjects:
                    all_mobjects.append(anim.mobject)
            elif isinstance(anim, (FadeIn, FadeOut)):
                for mob in anim.mobjects:
                    if isinstance(anim, FadeIn):
                        set_anim_opacity(mob, 0.0)
                    if mob not in all_mobjects:
                        all_mobjects.append(mob)
            elif isinstance(anim, TransformMatchingAbstractBase):
                if anim.mobject not in all_mobjects:
                    all_mobjects.append(anim.mobject)
                # Don't add target_mobject here — clean_up_from_scene handles it
                # after all transforms complete, to avoid premature rendering.
                set_anim_opacity(anim.target_mobject, 0.0)
                anim.mobject._transforming = True
                for sub_anim in getattr(anim, '_anims', []):
                    if isinstance(sub_anim, (FadeIn, FadeOut)):
                        for mob in sub_anim.mobjects:
                            if isinstance(sub_anim, FadeIn):
                                set_anim_opacity(mob, 0.0)
                            if mob not in all_mobjects:
                                all_mobjects.append(mob)
                    elif isinstance(sub_anim, (Transform, _ManimTransform)):
                        if sub_anim.mobject not in all_mobjects:
                            all_mobjects.append(sub_anim.mobject)
                        if sub_anim.target_mobject not in all_mobjects:
                            all_mobjects.append(sub_anim.target_mobject)
                        set_anim_opacity(sub_anim.target_mobject, 0.0)
            elif isinstance(anim, FadeTransform):
                if anim.mobject not in all_mobjects:
                    all_mobjects.append(anim.mobject)
                if anim.target_mobject not in all_mobjects:
                    all_mobjects.append(anim.target_mobject)
                ghost = getattr(anim, '_ghost', None)
                if ghost is not None and ghost not in all_mobjects:
                    all_mobjects.append(ghost)
                is_manim_ft = type(anim).__module__.startswith('manim')
                if is_manim_ft and hasattr(anim.mobject, 'submobjects'):
                    for sub in anim.mobject.submobjects:
                        for existing in self.scene.mobjects:
                            if sub is existing:
                                if not hasattr(self, '_skip_mob_ids'):
                                    self._skip_mob_ids = set()
                                self._skip_mob_ids.add(id(existing))
                                break
            elif isinstance(anim, (Transform, _ManimTransform)):
                if anim.mobject not in all_mobjects:
                    all_mobjects.append(anim.mobject)
                # ApplyMethod subclasses (Restore, ApplyPointwiseFunction, etc.)
                # modify the mobject's points away from the original geometric shape.
                # They need _transforming=True so the renderer uses _send_vmobject
                # (point-based bezier path) instead of the shape-specific dispatcher
                # (like _send_square) which ignores point changes.
                # Restore interpolates BACK to the original shape — the native
                # dispatcher handles it fine.
                from manim.animation.transform import ApplyMethod as _ManimApplyMethod
                if isinstance(anim, _ManimApplyMethod) and type(anim).__name__ != 'Restore':
                    anim.mobject._transforming = True
                    # ApplyMethod warps bezier handles into curves — _send_polygon
                    # (straight edges) can't represent them.  Route through
                    # _send_vmobject instead so the bezier path is preserved.
                    anim.mobject._apply_method = True
                # Manim Transform subclasses (ClockwiseTransform, CounterclockwiseTransform,
                # and plain manim Transform) modify mobject points but don't set _transforming.
                # Without _transforming=True the renderer ignores point changes and draws
                # the native shape (e.g. _send_dot instead of _send_vmobject).
                if isinstance(anim, _ManimTransform) and not isinstance(anim, Transform):
                    Transform._set_transforming(anim.mobject, True)
                # Tag FocusOn starting dot so it routes through _send_dot
                # (not the generic _send_vmobject) — renders as a proper circle
                if type(anim).__name__ == 'FocusOn':
                    anim.mobject._focus_on_dot = True
                    # Subtle-but-visible spotlight: 0.4 was too strong, 0.03
                    # invisible under the accurate UNORM swapchain.
                    anim.mobject._dot_max_opacity = 0.15
                if anim.replace_mobject_with_target_in_scene:
                    if anim.target_mobject not in all_mobjects:
                        all_mobjects.append(anim.target_mobject)
                    set_anim_opacity(anim.target_mobject, 0.0)
                if isinstance(anim, _ManimFadeTransform) and hasattr(anim.mobject, 'submobjects'):
                    for sub in anim.mobject.submobjects:
                        for existing in self.scene.mobjects:
                            if sub is existing:
                                self._skip_mob_ids.add(id(existing))
                                break
            elif isinstance(anim, Succession):
                for sub in anim.animations:
                    if isinstance(sub, (Create, Write, DrawBorderThenFill, FadeIn, Rotating, Rotate)) and sub.mobject:
                        if isinstance(sub, (Create, DrawBorderThenFill)):
                            sub.mobject._vulkan_progress = 0.0
                        if sub.mobject not in all_mobjects:
                            all_mobjects.append(sub.mobject)
                    elif isinstance(sub, (FadeIn, FadeOut)):
                        for mob in sub.mobjects:
                            if isinstance(sub, FadeIn):
                                set_anim_opacity(mob, 0.0)
                            if mob not in all_mobjects:
                                all_mobjects.append(mob)
                    elif isinstance(sub, TransformMatchingAbstractBase):
                        if sub.mobject not in all_mobjects:
                            all_mobjects.append(sub.mobject)
                        if sub.target_mobject not in all_mobjects:
                            all_mobjects.append(sub.target_mobject)
                        sub.mobject._transforming = True
                        for sub_anim in getattr(sub, '_anims', []):
                            if isinstance(sub_anim, (FadeIn, FadeOut)):
                                for mob in sub_anim.mobjects:
                                    set_anim_opacity(mob, 0.0)
                                    if mob not in all_mobjects:
                                        all_mobjects.append(mob)
                            elif isinstance(sub_anim, (Transform, _ManimTransform)):
                                if sub_anim.mobject not in all_mobjects:
                                    all_mobjects.append(sub_anim.mobject)
                                if sub_anim.target_mobject not in all_mobjects:
                                    all_mobjects.append(sub_anim.target_mobject)
                    elif isinstance(sub, FadeTransform):
                        if sub.mobject not in all_mobjects:
                            all_mobjects.append(sub.mobject)
                        if sub.target_mobject not in all_mobjects:
                            all_mobjects.append(sub.target_mobject)
                        ghost = getattr(sub, '_ghost', None)
                        if ghost is not None and ghost not in all_mobjects:
                            all_mobjects.append(ghost)
                        is_manim_ft = type(sub).__module__.startswith('manim')
                        if is_manim_ft and hasattr(sub.mobject, 'submobjects'):
                            for child in sub.mobject.submobjects:
                                for existing in self.scene.mobjects:
                                    if child is existing:
                                        self._skip_mob_ids.add(id(existing))
                                        break
            elif isinstance(anim, AnimationGroup):
                for sub in anim.animations:
                    if isinstance(sub, (Create, Write, DrawBorderThenFill, FadeIn, Rotating, Rotate, GrowArrow)) and sub.mobject:
                        if isinstance(sub, (Create, DrawBorderThenFill)):
                            sub.mobject._vulkan_progress = 0.0
                        if isinstance(sub, FadeIn):
                            set_anim_opacity(sub.mobject, 0.0)
                        if sub.mobject not in all_mobjects:
                            all_mobjects.append(sub.mobject)
                    elif isinstance(sub, (FadeIn, FadeOut)):
                        for mob in sub.mobjects:
                            if isinstance(sub, FadeIn):
                                set_anim_opacity(mob, 0.0)
                            if mob not in all_mobjects:
                                all_mobjects.append(mob)
                    elif isinstance(sub, Transform):
                        if sub.mobject not in all_mobjects:
                            all_mobjects.append(sub.mobject)
                        if sub.target_mobject not in all_mobjects:
                            all_mobjects.append(sub.target_mobject)
                        sub.mobject._transforming = True
                    elif isinstance(sub, FadeTransform):
                        # FadeTransform subs (e.g. per-piece FadeTransformPieces)
                        # need their target and ghost added too, otherwise the
                        # target shape never renders during the crossfade.
                        if sub.mobject not in all_mobjects:
                            all_mobjects.append(sub.mobject)
                        if sub.target_mobject not in all_mobjects:
                            all_mobjects.append(sub.target_mobject)
                        gh = getattr(sub, '_ghost', None)
                        if gh is not None and gh not in all_mobjects:
                            all_mobjects.append(gh)
                    else:
                        # Catch-all for ApplyMethod, etc. — track their mobjects
                        # so _is_descendant_of_scene can prevent double-rendering
                        if hasattr(sub, 'mobject') and sub.mobject is not None:
                            if sub.mobject not in all_mobjects:
                                all_mobjects.append(sub.mobject)
            else:
                from manim.animation.composition import AnimationGroup as _ManimAG
                if isinstance(anim, _ManimAG):
                    for sub in anim.animations:
                        if hasattr(sub, 'mobject') and sub.mobject is not None:
                            if sub.mobject not in all_mobjects:
                                all_mobjects.append(sub.mobject)
                        if hasattr(sub, 'target_mobject') and sub.target_mobject is not None:
                            if not isinstance(sub, _ManimTransform) or type(sub) is _ManimTransform:
                                if sub.target_mobject not in all_mobjects:
                                    all_mobjects.append(sub.target_mobject)

        def _is_descendant_of_scene(mob):
            """Check if mob is already somewhere in the scene mobject tree."""
            def _search(node, target):
                if node is target:
                    return True
                for sub in getattr(node, 'submobjects', []):
                    if _search(sub, target):
                        return True
                return False

            for root in self.scene.mobjects:
                if root is mob:
                    continue
                if _search(root, mob):
                    return True
            return False

        for mob in all_mobjects:
            if _is_descendant_of_scene(mob):
                self._skip_mob_ids.add(id(mob))
                continue
            if mob not in self.scene.mobjects:
                self.scene.add(mob)

        for anim in animations:
            if hasattr(anim, 'mobject') and anim.mobject is not None:
                if anim.mobject not in self.scene.mobjects:
                    self.scene.mobjects.append(anim.mobject)
            cursor = getattr(anim, 'cursor', None)
            if cursor is not None and cursor not in self.scene.mobjects:
                self.scene.mobjects.append(cursor)

        for mob in add_mobs:
            set_anim_opacity(mob, 0.0)

        for a in animations:
            if isinstance(a, Add):
                for mob in a.mobjects:
                    set_anim_opacity(mob, 1.0)

        real_anims = [a for a in animations if not isinstance(a, Add)]

        if 'run_time' in kwargs:
            shared_rt = kwargs['run_time']
            for a in real_anims:
                if isinstance(a, (Wait, Succession)):
                    continue
                a.run_time = shared_rt
        if 'rate_func' in kwargs:
            shared_rf = kwargs['rate_func']
            for a in real_anims:
                if isinstance(a, (Wait, Succession)):
                    continue
                a.rate_func = shared_rf

        # Fast record: seed simulated time so start_time uses a consistent clock
        if self._fast_record:
            self._fast_record_sim_time = time.time()
            _frame_interval = 1.0 / self._fast_record_fps

        for a in real_anims:
            is_manim = type(a).__module__.startswith('manim')
            if is_manim:
                # don't render an invisible source. The target was set to 0.0
                # by the previous animation's target setup at line 513.
                if getattr(a, 'mobject', None) is not None:
                    set_anim_opacity(a.mobject, 1.0)
                _setup_anim_scene(a, self.scene)
                a.start_time = self._fast_record_sim_time if self._fast_record else time.time()
                a.begin()
                tm = getattr(a, 'target_mobject', None)
                if tm is not None and hasattr(tm, 'get_updaters') and tm.get_updaters():
                    for upd in tm.get_updaters():
                        upd(tm)
                    tc = getattr(a, 'target_copy', None)
                    if tc is not None:
                        tc.move_to(tm.get_center())
                if a.mobject is not None and a.mobject not in self.scene.mobjects:
                    self.scene.mobjects.append(a.mobject)
            else:
                a.begin(self._fast_record_sim_time if self._fast_record else time.time())

        for a in real_anims:
            if isinstance(a, TransformMatchingAbstractBase):
                # Remove the source VGroup from scene — sub-anims' Transform
                # handles rendering of individual MathTexPart children.
                # This prevents ghost copies where eq2's own submobjects
                # render at original positions while transform_source
                # renders copies at interpolated positions.
                if a.mobject in self.scene.mobjects:
                    self.scene.remove(a.mobject)
                set_anim_opacity(a.mobject, 0.0)
                for sub_anim in getattr(a, '_anims', []):
                    if isinstance(sub_anim, (Transform, _ManimTransform)):
                        if sub_anim.mobject not in self.scene.mobjects:
                            self.scene.add(sub_anim.mobject)
                        if sub_anim.target_mobject not in self.scene.mobjects:
                            self.scene.add(sub_anim.target_mobject)
                        # Hide the target VGroup — it's only a shape reference;
                        # the source mobject morphs into its shape during interpolate.
                        set_anim_opacity(sub_anim.target_mobject, 0.0)
                    elif isinstance(sub_anim, FadeOut):
                        # Add fade_source VGroup so unmatched source parts
                        # (e.g. x, y, z) render and fade progressively.
                        if sub_anim.mobject not in self.scene.mobjects:
                            self.scene.add(sub_anim.mobject)
                    elif isinstance(sub_anim, FadeIn):
                        # Add fade_target_copy so unmatched target parts
                        # fade in. Start fully transparent.
                        if sub_anim.mobject not in self.scene.mobjects:
                            self.scene.add(sub_anim.mobject)
                        set_anim_opacity(sub_anim.mobject, 0.0)

        self._active_anims = real_anims
        self._last_frame_time = time.time() - (1.0 / 30.0)

        # Fast record: align _last_frame_time with simulated clock so the
        # first frame's dt equals _frame_interval.
        if self._fast_record:
            self._last_frame_time = self._fast_record_sim_time - _frame_interval

        _orig_vgroup_rotate = {}
        _prev_vg_rotation = {}

        def _rotation_pivot(vg):
            if hasattr(vg, '_rotation_about_point'):
                return np.array(vg._rotation_about_point, dtype=float)
            # Use the first submobject's center as pivot instead of the
            # VGroup aggregate center. This prevents vertical vibration when a
            # dot on the circumference shifts the VGroup center (rolling circle).
            if hasattr(vg, 'submobjects') and len(vg.submobjects) > 0:
                return np.array(vg.submobjects[0].get_center(), dtype=float)
            return vg.get_center()

        def _maybe_clear_prev_vg_rotation(anim):
            """After interpolate() resets mobject points, clear prev-rotation
            tracking so the VGroup delta loop reapplies the FULL accumulated
            rotation, not just the increment since last frame."""
            mob = getattr(anim, 'mobject', None)
            if mob is None:
                return
            for scene_mob in self.scene.mobjects:
                if isinstance(scene_mob, (VGroup, Group)):
                    # Check if anim.mobject is this VGroup or a descendant
                    if mob is scene_mob or (
                        hasattr(scene_mob, 'family_members_with_points') and
                        mob in scene_mob.family_members_with_points()
                    ):
                        _prev_vg_rotation.pop(id(scene_mob), None)

        def _patch_vgroup(vg):
            if id(vg) in _orig_vgroup_rotate:
                return
            _orig_vgroup_rotate[id(vg)] = vg.rotate
            def _propagating_rotate(angle, axis=OUT, about_point=None, about_edge=None, **kwargs):
                alpha = _anim_alpha[0]
                effective = angle * alpha
                pivot = _rotation_pivot(vg)
                for m in vg.family_members_with_points():
                    if hasattr(m, 'points') and len(m.points) > 0:
                        c, s = np.cos(effective), np.sin(effective)
                        rot_matrix = np.array([[c, -s, 0], [s, c, 0], [0, 0, 1]])
                        m.points = (m.points - pivot) @ rot_matrix.T + pivot
                current = get_anim_rotation(vg)
                set_anim_rotation(vg, current + effective)
                return vg
            vg.rotate = _propagating_rotate

        def _unpatch_vgroup(vg):
            if id(vg) in _orig_vgroup_rotate:
                vg.rotate = _orig_vgroup_rotate.pop(id(vg))

        frame_count = 0
        # Mutable container so _patch_vgroup's closure reads the latest alpha
        _anim_alpha = [1.0]
        while True:
            if self._fast_record:
                now = self._fast_record_sim_time
                dt = _frame_interval
                self._fast_record_sim_time += _frame_interval
            else:
                frame_start = time.time()
                now = frame_start
                dt = now - self._last_frame_time

            self._last_frame_time = now
            all_done = True

            # Time-based rotation: original manim uses -0.3 rad/frame at 30fps
            # which is -9 rad/s.  current_alpha = dt * 30 gives:
            #   30fps → 1.0, 60fps → 0.5, etc.
            current_alpha = dt * 30
            _anim_alpha[0] = current_alpha

            for a in self._active_anims:
                is_manim = type(a).__module__.startswith('manim')
                if is_manim:
                    elapsed = now - a.start_time
                    alpha = elapsed / a.run_time if a.run_time > 0 else 1.0
                    alpha = max(0.0, min(1.0, alpha))
                    a.interpolate(alpha)
                    # interpolate() resets mobject points, erasing accumulated rotation.
                    # Clear _prev_vg_rotation so the delta loop reapplies the FULL rotation.
                    _maybe_clear_prev_vg_rotation(a)

                    if not getattr(a, 'finished', False) and elapsed >= a.run_time:
                        a.finish()
                        a.finished = True
                        if hasattr(a, 'clean_up_from_scene'):
                            a.clean_up_from_scene(self.scene)
                        mob = getattr(a, 'mobject', None)
                        if mob:
                            mob.resume_updating()
                            # After the animation ends, clear _transforming only when
                            # the mobject's appearance reverts to its original shape.
                            # Keep it for permanent morphs:
                            #   - ApplyMethod (WarpSquare, etc.) except Restore
                            #   - _ManimTransform without replacement (ClockwiseTransform
                            #     permanently morphs the mobject's points to the target)
                            from manim.animation.transform import ApplyMethod as _ManimApplyMethod2
                            keep = False
                            if isinstance(a, _ManimApplyMethod2):
                                keep = type(a).__name__ != 'Restore'
                            elif isinstance(a, _ManimTransform) and not getattr(a, 'replace_mobject_with_target_in_scene', False):
                                keep = True
                            if not keep:
                                Transform._set_transforming(mob, False)
                            if hasattr(mob, '_was_transforming_text'):
                                del mob._was_transforming_text
                            if hasattr(mob, '_dot_max_opacity'):
                                del mob._dot_max_opacity
                            if hasattr(mob, '_focus_on_dot'):
                                del mob._focus_on_dot
                            if hasattr(mob, '_apply_method') and not keep:
                                del mob._apply_method
                            target = getattr(a, 'target_mobject', None) or getattr(a, 'target', None)
                            if target and isinstance(mob, Text) and hasattr(mob, 'text') and hasattr(target, 'text'):
                                mob.text = target.text
                            if getattr(a, 'replace_mobject_with_target_in_scene', False):
                                set_anim_opacity(mob, 1.0)
                        if hasattr(a, 'animations'):
                            for sub in a.animations:
                                sub_mob = getattr(sub, 'mobject', None)
                                if sub_mob and hasattr(sub_mob, '_transforming'):
                                    sub_mob._transforming = False
                        if hasattr(a, '_anims'):
                            for sub in a._anims:
                                sub_mob = getattr(sub, 'mobject', None)
                                if sub_mob and hasattr(sub_mob, '_transforming'):
                                    sub_mob._transforming = False
                else:
                    a.interpolate(now)
                    if not a.finished and (now - a.start_time) >= a.run_time:
                        a.finish()
                        a.finished = True
                        if hasattr(a, 'clean_up_from_scene'):
                            a.clean_up_from_scene(self.scene)
                if not getattr(a, 'finished', False):
                    all_done = False

            # Apply rotation delta per VGroup.
            for mob in self.scene.mobjects:
                if isinstance(mob, (VGroup, Group)):
                    if getattr(mob, '_rotation_about_point', None) is not None or getattr(mob, '_rotation_3d', False):
                        # Rotation is handled by the VGroup handler in _send().
                        continue
                    vg_rot = get_anim_rotation(mob)
                    prev_rot = _prev_vg_rotation.get(id(mob), 0.0)
                    delta = vg_rot - prev_rot
                    if abs(delta) > 1e-12:
                        pivot = _rotation_pivot(mob)
                        c, s = np.cos(delta), np.sin(delta)
                        rot_matrix = np.array([[c, -s, 0], [s, c, 0], [0, 0, 1]])
                        for sub in mob.family_members_with_points():
                            if hasattr(sub, 'points') and len(sub.points) > 0:
                                sub.points = (sub.points - pivot) @ rot_matrix.T + pivot
                    _prev_vg_rotation[id(mob)] = vg_rot

            _drive_mobject_updaters(self.scene, dt, _patch_vgroup, _unpatch_vgroup)

            clear_anim_rotation_delta()

            if self._fast_record:
                seg = self._fast_record_segment
                idx = self._fast_record_frame_idx
                
                if seg is not None and idx >= seg[1]:
                    break
                
                in_segment = (seg is None) or (seg[0] <= idx < seg[1])
                if in_segment:
                    if getattr(self, '_fast_record_count_only', False):
                        pass  # count only — no GPU
                    else:
                        # Queue this frame's state first, then draw + capture it:
                        # tick() renders whatever is queued, so drawing before
                        # sync() would capture the previous frame.  The readback
                        # request must also be armed before the draw, so the
                        # frame copies itself out while it still owns the image.
                        self.sync(self.scene)
                        self.request_readback()
                        if not self.tick():
                            break
                        if getattr(self, '_fast_record_pipe_mode', True):
                            self._capture_screenshot_to_pipe()
                        else:
                            bmp = os.path.join(
                                self._fast_record_path,
                                f"frame_{idx:06d}.bmp")
                            self.screenshot(bmp)
                
                self._fast_record_frame_idx += 1
            else:
                self.sync(self.scene)
                self.request_readback()
                if not self.tick():
                    break
                self._capture_frame()

            frame_count += 1

            if screenshot_at:
                for a in self._active_anims:
                    if a in screenshot_at:
                        alpha = (now - a.start_time) / a.run_time if a.run_time > 0 else 1.0
                        alpha = max(0.0, min(1.0, alpha))
                        alpha = a.rate_func(alpha)
                        for threshold, path in screenshot_at[a]:
                            if abs(alpha - threshold) < 0.02:
                                self.screenshot(path)
                                del screenshot_at[a][screenshot_at[a].index((threshold, path))]
                                break

            if all_done:
                break

            if not self._fast_record:
                elapsed = time.time() - frame_start
                if elapsed < FRAME_DURATION:
                    time.sleep(FRAME_DURATION - elapsed)

        for a in real_anims:
            if hasattr(a, 'clean_up_from_scene'):
                a.clean_up_from_scene(self.scene)

    def screenshot(self, path):
        path_bytes = path.encode('utf-8') if isinstance(path, str) else path
        return self.dll.SaveScreenshot(path_bytes)

    def request_readback(self):
        """Arm the next drawn frame to copy itself for readback.

        Must be called *before* the tick that draws the frame you want.  A
        presented swapchain image is owned by the presentation engine, so
        copying it afterwards returns undefined pixels; the engine copies the
        frame while it still owns it instead.
        """
        fn = getattr(self.dll, 'Vulkan_RequestReadback', None)
        if fn is not None:
            fn()

    def screenshot_printwindow(self, path):
        if sys.platform != "win32":
            # macOS: no GDI — the swapchain framebuffer readback is the
            # reliable capture path (TCC-free, immune to occlusion).
            return bool(self.screenshot(path))
        import ctypes.wintypes as wt
        user32 = ctypes.windll.user32
        gdi32 = ctypes.windll.gdi32
        hwnd = user32.FindWindowW(None, "Real Time Manim")
        if not hwnd:
            hwnd = self.hwnd
            if not hwnd:
                return False

        # Client area dimensions
        rc = wt.RECT()
        user32.GetClientRect(hwnd, ctypes.byref(rc))
        w, h = rc.right - rc.left, rc.bottom - rc.top

        # Client area screen position
        pt = wt.POINT(0, 0)
        user32.ClientToScreen(hwnd, ctypes.byref(pt))
        x, y = pt.x, pt.y

        # Capture from screen at client area position
        hdc_screen = user32.GetDC(None)
        hdc_mem = gdi32.CreateCompatibleDC(hdc_screen)
        hbitmap = gdi32.CreateCompatibleBitmap(hdc_screen, w, h)
        gdi32.SelectObject(hdc_mem, hbitmap)
        gdi32.BitBlt(hdc_mem, 0, 0, w, h, hdc_screen, x, y, 0x00CC0020)  # SRCCOPY

        bi = BITMAPINFOHEADER()
        bi.biSize = ctypes.sizeof(BITMAPINFOHEADER)
        bi.biWidth = w
        bi.biHeight = -h
        bi.biPlanes = 1
        bi.biBitCount = 24
        bi.biCompression = 0
        row_bytes = ((w * 3 + 3) & ~3)
        buf = (ctypes.c_ubyte * (row_bytes * h))()
        gdi32.GetDIBits(hdc_mem, hbitmap, 0, h, buf, ctypes.byref(bi), 0)
        bfh = BITMAPFILEHEADER()
        bfh.bfType = 0x4D42
        bfh.bfOffBits = ctypes.sizeof(BITMAPFILEHEADER) + ctypes.sizeof(BITMAPINFOHEADER)
        bfh.bfSize = bfh.bfOffBits + row_bytes * h
        path_b = path.encode('utf-8') if isinstance(path, str) else path
        hdr_buf = ctypes.string_at(ctypes.addressof(bfh), ctypes.sizeof(bfh)) + \
                  ctypes.string_at(ctypes.addressof(bi), ctypes.sizeof(bi))
        with open(path_b, 'wb') as f:
            f.write(hdr_buf)
            f.write(ctypes.string_at(ctypes.addressof(buf), len(buf)))
        gdi32.DeleteObject(hbitmap)
        gdi32.DeleteDC(hdc_mem)
        user32.ReleaseDC(None, hdc_screen)
        return True

    def enable_fast_record(self, path, fps=60, segment=None, hidden=True, count_only=False):
        """Enable fast offline recording.

        Args:
            path: Output path (MP4 file for pipe mode, directory for BMP mode)
            fps: Frame rate
            segment: (start_frame, end_frame) for multi-segment BMP mode,
                     None for single-process pipe mode
            hidden: Hide the Vulkan window
            count_only: Only count frames — no capture, no GPU rendering
        """
        self._fast_record = True
        self._fast_record_path = os.path.abspath(path) if path else ""
        self._fast_record_fps = fps
        self._fast_record_segment = segment
        self._fast_record_frame_idx = 0
        self._fast_record_count_only = count_only
        w, h = self.win_w, self.win_h

        # Hide window for faster rendering (no compositing)
        if hidden and sys.platform == "win32":
            import ctypes.wintypes
            user32 = ctypes.windll.user32
            hwnd = user32.FindWindowW(None, "Real Time Manim")
            if hwnd:
                user32.ShowWindow(hwnd, 0)  # SW_HIDE

        if count_only:
            self._fast_record_pipe_mode = False
        elif segment is not None:
            # BMP mode: each frame saved via SaveScreenshot (no pipe overhead)
            os.makedirs(self._fast_record_path, exist_ok=True)
            self._fast_record_pipe_mode = False
            print(f"[FastRecord] BMP mode {segment} → {path}/")
        else:
            # Pipe mode: SaveScreenshot → parse BMP → pipe BGR to ffmpeg
            self._fast_record_pipe_mode = True
            self._fast_w = w
            self._fast_h = h
            self._fast_row_size = w * 3
            self._fast_row_padded = ((w * 3 + 3) // 4) * 4
            ffmpeg_cmd = [
                "ffmpeg", "-y",
                "-f", "rawvideo", "-pixel_format", "bgr24",
                "-video_size", f"{w}x{h}",
                "-framerate", str(fps),
                "-i", "-",
                "-c:v", "libx264", "-pix_fmt", "yuv420p",
                "-crf", "18", "-preset", "fast",
                self._fast_record_path,
            ]
            self._ffmpeg = subprocess.Popen(
                ffmpeg_cmd, stdin=subprocess.PIPE, stderr=subprocess.DEVNULL)
            self._fast_tmp_bmp = os.path.join(tempfile.gettempdir(),
                f"manim_fast_{os.getpid()}_{id(self)}.bmp")
            print(f"[FastRecord] Pipe: {w}x{h} @ {fps} fps → {path}")

    def set_visible(self, visible=True):
        """Show or hide the window after it was created.

        Used to build a window hidden (offline frame export / fast record) and
        only reveal it when a human is meant to watch (FrameServer.show_frame).
        """
        visible = bool(visible)
        fn = getattr(self.dll, 'Vulkan_SetWindowVisible', None)
        if fn is not None:
            fn(1 if visible else 0)
        elif sys.platform == "win32":
            # Older DLL without the export: hide/show by window title.
            user32 = ctypes.windll.user32
            hwnd = user32.FindWindowW(None, "Real Time Manim")
            if hwnd:
                user32.ShowWindow(hwnd, 5 if visible else 0)  # SW_SHOW / SW_HIDE
        self.hidden = not visible

    def close(self):
        if getattr(self, '_defer_close', False):
            return                    # keep the window alive for on-demand frames
        self._unregister()
        self.dll.Vulkan_Shutdown()

    def _unregister(self):
        """Drop this window from the class registry.

        Every constructed MLWindow registers itself there; without this a process
        that opens many windows (batch runs, harnesses) keeps them all alive.
        Pure bookkeeping -- safe to call in any state, no GPU involved.
        """
        reg = type(self)._registry
        while self in reg:
            reg.remove(self)

    def _capture_screenshot_to_pipe(self):
        """SaveScreenshot → parse BMP → pipe tightly packed BGR to ffmpeg.

        BMP rows are padded to a 4-byte boundary ((w*3 + 3) & ~3 == 2564 bytes
        at 854 px wide), but ffmpeg's ``bgr24`` with ``-video_size w x h`` expects
        tightly packed rows.  Piping the payload verbatim therefore lands every
        row 2 bytes late, which shears the picture horizontally by ~0.67 px per
        row -- a vertical line comes out as a diagonal.  The padding has to be
        stripped here (this is what _fast_row_padded exists for).
        """
        tmp = self._fast_tmp_bmp
        self.dll.SaveScreenshot(tmp.encode('utf-8'))
        with open(tmp, 'rb') as f:
            f.seek(54)
            data = f.read()

        row_size = self._fast_row_size                 # w * 3, what ffmpeg wants
        padded = self._fast_row_padded                 # what the BMP carries
        if padded == row_size:
            self._ffmpeg.stdin.write(data)
            return

        height = self._fast_h
        try:
            import numpy as np
            rows = np.frombuffer(data, dtype=np.uint8, count=padded * height)
            self._ffmpeg.stdin.write(rows.reshape(height, padded)[:, :row_size].tobytes())
        except Exception:                              # numpy unavailable
            out = bytearray(row_size * height)
            for y in range(height):
                src = y * padded
                out[y * row_size:(y + 1) * row_size] = data[src:src + row_size]
            self._ffmpeg.stdin.write(bytes(out))

    def _finish_fast_record(self):
        """Finish recording: close ffmpeg pipe or report BMP count."""
        if not self._fast_record:
            return
        if getattr(self, '_fast_record_count_only', False):
            print(f"[FastRecord] Count: {self._fast_record_frame_idx} frames")
        elif getattr(self, '_fast_record_pipe_mode', False):
            try:
                self._ffmpeg.stdin.close()
                self._ffmpeg.wait()
                sz = os.path.getsize(self._fast_record_path) / 1024
                print(f"[FastRecord] Saved: {self._fast_record_path} "
                      f"({self._fast_record_frame_idx} frames, {sz:.0f} KB)")
            except Exception as e:
                print(f"[FastRecord] ffmpeg failed: {e}")
            try:
                os.unlink(self._fast_tmp_bmp)
            except Exception:
                pass
        else:
            bmps = [f for f in os.listdir(self._fast_record_path) if f.endswith('.bmp')]
            print(f"[FastRecord] BMP: {len(bmps)} frames in {self._fast_record_path}")
        self._fast_record = False

    def start_record(self, path="output.mp4", fps=60):
        if self._recording:
            return
        self._record_path = os.path.abspath(path)
        self._record_fps = fps
        self._record_dir = tempfile.mkdtemp(prefix="manim_record_")
        self._record_frame_idx = 0
        self._recording = True
        self._record_start_time = time.time()
        import threading
        self._record_stop_event = threading.Event()
        self._record_thread = threading.Thread(target=self._record_worker, daemon=True)
        self._record_thread.start()
        print(f"[Record] Recording to {self._record_path} at {fps} fps")

    def _record_worker(self):
        # Captures the Vulkan framebuffer directly via SaveScreenshot (real
        # readback), NOT the composited screen. This is immune to window
        # occlusion/scaling that would corrupt a screen-based capture.
        # On macOS SaveScreenshot is two-phase (arm → next frame copies),
        # so only advance the frame index when a BMP was actually written —
        # gaps in the file sequence would otherwise truncate ffmpeg's input.
        interval = 1.0 / self._record_fps
        next_slot = time.time()
        while not self._record_stop_event.is_set():
            try:
                path = os.path.join(self._record_dir, f"frame_{self._record_frame_idx:06d}.bmp")
                if self.screenshot(path):
                    self._record_frame_idx += 1
                    # pace writes at the nominal fps; poll aggressively
                    # between the arm and read phases (two-phase readback)
                    next_slot += interval
                    wait = next_slot - time.time()
                    if wait > 0:
                        self._record_stop_event.wait(wait)
                    continue
            except Exception:
                pass
            # arm cycle: retry shortly — each capture needs one arm + one read
            self._record_stop_event.wait(0.004)
        self._record_thread = None

    def stop_record(self):
        if not self._recording:
            return
        self._record_stop_event.set()
        self._recording = False
        if self._record_thread:
            self._record_thread.join(timeout=2.0)
            self._record_thread = None
        frame_dir = self._record_dir
        output = self._record_path
        total = self._record_frame_idx
        duration = time.time() - getattr(self, '_record_start_time', time.time())
        # Use actual capture fps as input framerate so video duration
        # matches wall-clock scene time — avoids speed-up from slow GDI.
        fps = max(total / duration, 1.0) if duration > 0 else float(self._record_fps)
        print(f"[Record] Captured {total} frames in {duration:.1f}s "
              f"({fps:.1f} fps), encoding to {output} ...")
        if total == 0:
            print("[Record] No frames captured, aborting.")
            if os.path.isdir(frame_dir):
                shutil.rmtree(frame_dir, ignore_errors=True)
            return

        pattern = os.path.join(frame_dir, "frame_%06d.bmp")
        cmd = [
            "ffmpeg", "-y",
            "-framerate", str(fps),
            "-i", pattern,
            "-r", "60",
            "-c:v", "libx264",
            "-pix_fmt", "yuv420p",
            "-vf", "scale=trunc(iw/2)*2:trunc(ih/2)*2",
            "-crf", "18",
            "-preset", "fast",
            output,
        ]
        try:
            subprocess.run(cmd, check=True, capture_output=True)
            print(f"[Record] Saved: {output}")
        except FileNotFoundError:
            print("[Record] ffmpeg not found. Install ffmpeg and add it to PATH.")
            print(f"[Record] Frames are in: {frame_dir}")
            return
        except subprocess.CalledProcessError as e:
            print(f"[Record] ffmpeg failed: {e.stderr.decode(errors='replace')}")
            print(f"[Record] Frames are in: {frame_dir}")
            return
        if os.path.isdir(frame_dir):
            shutil.rmtree(frame_dir, ignore_errors=True)

    def _get_screen_bbox(self):
        if sys.platform != "win32":
            return None
        import ctypes.wintypes as wt
        user32 = ctypes.windll.user32
        hwnd = user32.FindWindowW(None, "Real Time Manim")
        if not hwnd:
            return None
        rc = wt.RECT()
        user32.GetClientRect(hwnd, ctypes.byref(rc))
        pt = wt.POINT(0, 0)
        user32.ClientToScreen(hwnd, ctypes.byref(pt))
        return (pt.x, pt.y, pt.x + rc.right, pt.y + rc.bottom)

    def _capture_frame(self):
        pass
