"""Give manim's own animations the render-state channels RTM's senders read.

RTM's renderer has six dedicated channels (`_vulkan_progress`, its lower/upper
bounds, `_transforming`, `_letter_alphas`, `_grow_scale`/`_grow_point`/`_grow_rot`,
`_rotation_about_point`, and the `state` opacity registry).  Only RTM's *own*
animation classes ever wrote them, and the code that did so for manim-native
animations lives in `vulkan_bind._play_legacy`, which nothing calls.  A scene
written with `from manim import *` therefore ran every animation with the channels
at their defaults: `progress=1.0`, `transforming=False`, no letter alphas, full
opacity -- so `Create`, `FadeIn`, `Transform`, `Rotate`, `GrowFromCenter` … all
rendered as a static final state (the demo suite's SKIP-INTRO signature).

This module closes that gap once, in one place: it wraps a manim animation's
`interpolate` and derives the channels from the animation's **own** state, so the
values stay correct across manim versions instead of being re-guessed.

`Timeline.finalize` installs the hooks; `install_hooks` is idempotent and recurses
into composite animations, so `AnimationGroup(Create(sq), FadeIn(ci))` drives both.
"""

from __future__ import annotations

import logging

import numpy as np

from real_time_manim.state import set_anim_opacity

logger = logging.getLogger(__name__)


# ---------------------------------------------------------------------------
# class lookup (defensive: not every manim version ships every class)
# ---------------------------------------------------------------------------

def _load(module_name, *names):
    """Return the subset of `names` that exists in `module_name`."""
    out = []
    try:
        mod = __import__(module_name, fromlist=list(names))
    except Exception:                     # pragma: no cover - manim is required
        return tuple()
    for name in names:
        cls = getattr(mod, name, None)
        if isinstance(cls, type):
            out.append(cls)
    return tuple(out)


CREATION = _load("manim.animation.creation",
                 "ShowPartial", "ShowPassingFlash", "ShowPassingFlashWithThinningStrokeWidth",
                 "Create", "Uncreate", "DrawBorderThenFill", "Write", "Unwrite",
                 "ShowIncreasingSubsets", "SpiralIn", "ShowSubmobjectsOneByOne",
                 "AddTextLetterByLetter", "RemoveTextLetterByLetter",
                 "TypeWithCursor", "UntypeWithCursor")
FADING = _load("manim.animation.fading", "FadeIn", "FadeOut")
TRANSFORM = _load("manim.animation.transform",
                  "Transform", "ReplacementTransform", "TransformAnimations",
                  "TransformMatchingAbstractBase", "ApplyMethod", "ApplyFunction",
                  "ApplyPointwiseFunction", "ApplyPointwiseFunctionToCenter",
                  "ApplyMatrix", "ApplyComplexFunction", "ClockwiseTransform",
                  "CounterclockwiseTransform", "Restore", "FadeToColor",
                  "ScaleInPlace", "ShrinkToCenter", "MoveToTarget", "ApplyWave",
                  "CyclicReplace", "Swap")
MOVEMENT = _load("manim.animation.movement",
                 "Homotopy", "SmoothedVectorizedHomotopy", "ComplexHomotopy",
                 "PhaseFlow", "MoveAlongPath")
GROWING = _load("manim.animation.growing",
                "GrowFromCenter", "GrowFromEdge", "GrowFromPoint", "GrowArrow",
                "SpinInFromNothing")
INDICATION = _load("manim.animation.indication",
                   "Indicate", "Flash", "Circumscribe", "Blink", "FocusOn")
ROTATION = _load("manim.animation.rotation", "Rotate", "Rotating")
COMPOSITION = _load("manim.animation.composition",
                    "AnimationGroup", "Succession", "LaggedStart", "LaggedStartMap")

# Loaded by name, not by slicing: the earlier slicing put `ShowPartial` (the base
# of Create/Write/…) into the passing-flash rule, so Create took the flash branch
# (`alpha + width`), and `Transform` came too early for its many subclasses
# (FadeIn, GrowFromCenter, Rotate …).
_PASSING = _load("manim.animation.creation",
                 "ShowPassingFlash", "ShowPassingFlashWithThinningStrokeWidth")
_PROGRESS = _load("manim.animation.creation",
                  "ShowPartial", "ShowIncreasingSubsets", "Create", "Uncreate",
                  "DrawBorderThenFill", "Write", "Unwrite", "SpiralIn",
                  "ShowSubmobjectsOneByOne", "AddTextLetterByLetter",
                  "RemoveTextLetterByLetter", "TypeWithCursor", "UntypeWithCursor")
_GROW = _load("manim.animation.growing",
              "GrowFromCenter", "GrowFromEdge", "GrowFromPoint", "GrowArrow",
              "SpinInFromNothing")
_ROTATE = _load("manim.animation.rotation", "Rotate", "Rotating")
_FADE = _load("manim.animation.fading", "FadeIn", "FadeOut")
_INDICATE = _load("manim.animation.indication",
                  "Indicate", "Flash", "Circumscribe", "Blink", "FocusOn")
_TRANSFORM = _load("manim.animation.transform",
                   "Transform", "ReplacementTransform", "TransformAnimations",
                   "TransformMatchingAbstractBase", "ApplyMethod", "ApplyFunction",
                   "ApplyPointwiseFunction", "ApplyPointwiseFunctionToCenter",
                   "ApplyMatrix", "ApplyComplexFunction", "ClockwiseTransform",
                   "CounterclockwiseTransform", "Restore", "FadeToColor",
                   "ScaleInPlace", "ShrinkToCenter", "MoveToTarget", "ApplyWave",
                   "CyclicReplace", "Swap") + \
             _load("manim.animation.movement",
                   "Homotopy", "SmoothedVectorizedHomotopy", "ComplexHomotopy",
                   "PhaseFlow", "MoveAlongPath")

# specific first, `Transform` last (it is the base class of most of the others)
_RULES = (
    ("passing_flash", _PASSING),
    ("progress", _PROGRESS),
    ("grow", _GROW),
    ("rotate", _ROTATE),
    ("fade", _FADE),
    ("indicate", _INDICATE),
    ("transform", _TRANSFORM),
)


def _is_rtm_animation(anim):
    """RTM's own classes write the channels themselves -- leave them alone."""
    try:
        from real_time_manim.animations.base import Animation as RtmAnimation
    except Exception:                     # pragma: no cover
        return False
    return isinstance(anim, RtmAnimation)


def _children(anim):
    return [a for a in (getattr(anim, "animations", None) or ()) if a is not None]


# ---------------------------------------------------------------------------
# install / clear
# ---------------------------------------------------------------------------

def _snapshot_pivots(anim, mob):
    """Capture begin-state pivots on the animation.

    The grow/rotate channels need the point that was valid at ``begin()``; reading
    the mobject's centre on every frame would drift once it starts scaling.
    """
    if mob is None:
        return
    kind = _kind_of(anim)
    try:
        if kind == "grow":
            point = getattr(anim, "point", None)
            if point is None and "GrowArrow" in type(anim).__name__ and hasattr(mob, "get_start"):
                point = mob.get_start()
            edge = getattr(anim, "edge", None)
            if point is None and edge is not None and hasattr(mob, "get_critical_point"):
                point = mob.get_critical_point(edge)
            if point is None and hasattr(mob, "get_center"):
                point = mob.get_center()
            anim._rtm_grow_point = point
        elif kind == "rotate":
            about = getattr(anim, "about_point", None)
            if about is None and hasattr(mob, "get_center"):
                about = mob.get_center()
            anim._rtm_pivot = about
    except Exception:                      # pragma: no cover - mapping aid only
        logger.debug("pivot snapshot failed for %s", type(anim).__name__, exc_info=True)


def install_hooks(anim) -> None:
    """Wrap `anim.interpolate` so a manim-native animation drives RTM's channels.

    Call it right after `anim.begin()`.  Idempotent, and it recurses into
    composite animations (`AnimationGroup`, `Succession`, `LaggedStart`, `Add`).
    """
    if getattr(anim, "_rtm_hooks_installed", False):
        return
    if _is_rtm_animation(anim):
        anim._rtm_hooks_installed = True          # it writes its own channels
        for sub in _children(anim):
            install_hooks(sub)
        return

    original = anim.interpolate

    def interpolate(alpha):
        out = original(alpha)
        try:
            derive_channels(anim, alpha)
        except Exception:                # a hook must never break a render
            logger.debug("render hook failed for %s", type(anim).__name__, exc_info=True)
        return out

    anim.interpolate = interpolate
    anim._rtm_orig_interpolate = original
    anim._rtm_hooks_installed = True
    _snapshot_pivots(anim, getattr(anim, "mobject", None))

    # derive the begin state too, so frame 0 is not rendered from the defaults
    try:
        derive_channels(anim, 0.0)
    except Exception:
        logger.debug("render hook (begin) failed for %s", type(anim).__name__, exc_info=True)

    for sub in _children(anim):
        install_hooks(sub)


def clear_hooks(anim) -> None:
    """Undo `install_hooks` (keeps a reused animation from double-wrapping)."""
    original = getattr(anim, "_rtm_orig_interpolate", None)
    if original is not None:
        anim.interpolate = original
        try:
            del anim._rtm_orig_interpolate
        except AttributeError:
            pass
    anim._rtm_hooks_installed = False
    for sub in _children(anim):
        clear_hooks(sub)


# ---------------------------------------------------------------------------
# channel derivation
# ---------------------------------------------------------------------------

def derive_channels(anim, alpha) -> None:
    """Write the render-state channels for `anim` at `alpha`."""
    mob = getattr(anim, "mobject", None)
    if mob is None:
        for sub in _children(anim):                 # composite: children carry mobjects
            derive_channels(sub, alpha)
        return

    kind = _kind_of(anim)
    if kind == "passing_flash":
        _write_passing_flash(anim, mob, alpha)
    elif kind == "progress":
        _write_progress(anim, mob, alpha)
    elif kind == "transform":
        _write_transform(anim, mob, alpha)
    elif kind == "grow":
        _write_grow(anim, mob, alpha)
    elif kind == "rotate":
        _write_rotate(anim, mob, alpha)
    elif kind == "fade":
        _write_fade(anim, mob, alpha)
    elif kind == "indicate":
        _write_indicate(anim, mob, alpha)
    else:
        # Unknown class: say so (the plan wants the mapping table to be visible
        # in the logs) but fall back to the transform-style derive, which only
        # ever *adds* the point-path flag.
        logger.debug("no render hook for %s", type(anim).__name__)
        _write_transform(anim, mob, alpha)

    for sub in _children(anim):
        derive_channels(sub, alpha)


def _kind_of(anim):
    for kind, classes in _RULES:
        if classes and isinstance(anim, classes):
            return kind
    return None


def _mob_alpha(mob, default=1.0):
    """The mobject's current animated opacity, read from its rgba arrays.

    manim animates opacity **in the arrays** (``fill_rgbas`` / ``stroke_rgbas``);
    the stored ``fill_opacity`` / ``stroke_opacity`` attributes are not updated
    per frame.  Measured on ``FadeIn(Square())`` at alpha 0.5: the arrays hold
    0.5 while ``stroke_opacity`` still reads 1.0.
    """
    try:
        alphas = []
        for name in ("fill_rgbas", "stroke_rgbas"):
            arrays = getattr(mob, name, None)
            if arrays is not None and len(arrays):
                alphas.append(float(np.asarray(arrays)[:, 3].max()))
        return max(alphas) if alphas else default
    except Exception:
        return default


def _write_progress(anim, mob, alpha):
    """`Create` / `Uncreate` / `Write` / `DrawBorderThenFill` / `ShowIncreasingSubsets`."""
    bounds = getattr(anim, "_get_bounds", None)
    if callable(bounds):
        lower, upper = bounds(alpha)
    else:                                       # older/other manim: raw alpha
        lower, upper = 0.0, alpha
    mob._vulkan_progress_lower = float(lower)
    mob._vulkan_progress_upper = float(upper)
    mob._vulkan_progress = float(upper)
    # letter-by-letter reveal (Write/DrawBorderThenFill) reads this map
    letter_alphas = _letter_alphas(anim, alpha)
    if letter_alphas is not None:
        mob._letter_alphas = letter_alphas


def _letter_alphas(anim, alpha):
    subs = getattr(mob_subs := getattr(anim, "mobject", None), "submobjects", None) or ()
    if not subs:
        return None
    get_sub_alpha = getattr(anim, "get_sub_alpha", None)
    if not callable(get_sub_alpha):
        return None
    try:
        return {i: get_sub_alpha(alpha, i, len(subs)) for i in range(len(subs))}
    except Exception:
        return None


def _write_passing_flash(anim, mob, alpha):
    width = 0.2
    for attr in ("time_width", "width"):
        value = getattr(anim, attr, None)
        if isinstance(value, (int, float)):
            width = float(value)
            break
    lower = alpha
    upper = min(1.0, alpha + width)
    mob._vulkan_progress_lower = lower
    mob._vulkan_progress_upper = upper
    mob._vulkan_progress = upper


def _write_transform(anim, mob, alpha):
    """All Transform subclasses: the renderer must use the point path."""
    try:
        from real_time_manim.animations.transform import Transform as RtmTransform
        RtmTransform._set_transforming(mob, alpha < 1.0)
        target = getattr(anim, "target_mobject", None)
        if target is not None:
            RtmTransform._set_transforming(target, False)
    except Exception:
        mob._transforming = alpha < 1.0
    set_anim_opacity(mob, _mob_alpha(mob))


def _write_grow(anim, mob, alpha):
    point = getattr(anim, "_rtm_grow_point", None)     # begin-state snapshot
    if point is None:
        point = getattr(anim, "_grow_point", None)
    if point is None:
        point = getattr(anim, "point", None)
    if point is None:
        point = mob.get_center() if hasattr(mob, "get_center") else None
    mob._grow_scale = float(alpha)
    if point is not None:
        mob._grow_point = point
    angle = getattr(anim, "angle", None)        # SpinInFromNothing
    if isinstance(angle, (int, float)):
        mob._grow_rot = float(angle) * float(alpha)
    set_anim_opacity(mob, _mob_alpha(mob))


def _write_rotate(anim, mob, alpha):
    about = getattr(anim, "_rtm_pivot", None)          # begin-state snapshot
    if about is None:
        about = getattr(anim, "about_point", None)
    if about is None and hasattr(mob, "get_center"):
        about = mob.get_center()
    if about is not None:
        mob._rotation_about_point = about
    set_anim_opacity(mob, _mob_alpha(mob))


def _write_fade(anim, mob, alpha):
    set_anim_opacity(mob, _mob_alpha(mob))


def _write_indicate(anim, mob, alpha):
    set_anim_opacity(mob, _mob_alpha(mob))
    _write_grow(anim, mob, alpha)
