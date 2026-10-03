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
# `ShowPassingFlash` lives in `creation` from manim 0.21 on, but in `indication`
# before that -- load from both so the adapter works on either version.
_PASSING = tuple(dict.fromkeys(
    _load("manim.animation.creation",
          "ShowPassingFlash", "ShowPassingFlashWithThinningStrokeWidth") +
    _load("manim.animation.indication",
          "ShowPassingFlash", "ShowPassingFlashWithThinningStrokeWidth")))
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
# `_TRANSFORM_MORPH` interpolate *between two mobjects*: the geometry has to be
# re-tessellated every frame, so they take the point path (`_transforming`).
# `_TRANSFORM_METHOD` animate a single mobject through a method (scale / shift /
# colour); the specialised senders already handle those, and routing them to the
# point path silently **drops their fills** (measured: PolygonOnAxes lost 89% of
# its ink that way).
_TRANSFORM_MORPH = _load(
    "manim.animation.transform",
    "Transform", "ReplacementTransform", "TransformAnimations",
    "TransformMatchingAbstractBase", "ClockwiseTransform",
    "CounterclockwiseTransform", "Restore", "Swap", "CyclicReplace",
    "ApplyWave") + _load(
    "manim.animation.movement",
    "Homotopy", "SmoothedVectorizedHomotopy", "ComplexHomotopy", "PhaseFlow",
    "MoveAlongPath")
_TRANSFORM_METHOD = _load(
    "manim.animation.transform",
    "ApplyMethod", "ApplyFunction", "ApplyPointwiseFunction",
    "ApplyPointwiseFunctionToCenter", "ApplyMatrix", "ApplyComplexFunction",
    "FadeToColor", "ScaleInPlace", "ShrinkToCenter", "MoveToTarget",
    # `.animate.scale(...)` sugar: manim builds a Transform subclass, but the
    # mobject is only modified through a method -- treating it as a morph set
    # `_transforming` and made the animation render as a static final state.
    "_MethodAnimation")

# specific first, `Transform` last (it is the base class of most of the others)
_RULES = (
    ("passing_flash", _PASSING),
    ("progress", _PROGRESS),
    ("grow", _GROW),
    ("rotate", _ROTATE),
    ("fade", _FADE),
    ("indicate", _INDICATE),
    ("method", _TRANSFORM_METHOD),
    ("transform", _TRANSFORM_MORPH),
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
    elif kind == "method":
        # same mobject animated through a method: the specialised senders keep
        # drawing it (fills included), only the opacity registry needs a refresh
        if not _is_container(mob):
            set_anim_opacity(mob, _mob_alpha(mob))
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
        # Unknown class: log it (the plan wants the mapping table visible) and
        # write NOTHING.  Guessing "it is probably a morph" and setting
        # `_transforming` made `.animate.scale()` render as a static final state.
        logger.debug("no render hook for %s", type(anim).__name__)

    for sub in _children(anim):
        derive_channels(sub, alpha)


def _kind_of(anim):
    for kind, classes in _RULES:
        if classes and isinstance(anim, classes):
            return kind
    return None


def _is_container(mob):
    """True for a mobject that is only a group of children (no geometry itself).

    A container's own ``stroke_opacity`` / ``fill_opacity`` attributes are never
    updated -- they keep their construction value, which for a ``VGroup`` is
    **0**.  Reading them made ``FadeIn(ax)`` write ``opacity = 0`` for a whole
    Axes subtree: the shapes were still submitted, but drawn invisible (measured
    on PolygonOnAxes: CE's ink jumps 1675 -> 9333 pixels at frame 7, RTM stayed at
    ~1700).  Containers get no registry write; each child's rgba arrays carry the
    animated opacity and every sender reads those directly.
    """
    try:
        subs = getattr(mob, "submobjects", None) or ()
        pts = getattr(mob, "points", None)
        return bool(subs) and (pts is None or len(pts) == 0)
    except Exception:
        return False


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
        if not alphas:                     # ImageMobject has no rgba arrays
            for name in ("fill_opacity", "stroke_opacity"):
                value = getattr(mob, name, None)
                if isinstance(value, (int, float)):
                    alphas.append(float(value))
        return max(alphas) if alphas else default
    except Exception:
        return default


def _is_text_like(mob):
    """True for the mobjects whose children are glyphs (`Text`, `MathTexPart`)."""
    from manim import Text
    return isinstance(mob, Text) or bool(getattr(mob, "_is_text", False))


def _write_progress(anim, mob, alpha):
    """`Create` / `Uncreate` / `Write` / `DrawBorderThenFill` / `ShowIncreasingSubsets`."""
    bounds = getattr(anim, "_get_bounds", None)
    if callable(bounds):
        lower, upper = bounds(alpha)
    else:                                       # older/other manim: raw alpha
        lower, upper = 0.0, alpha
    # Only `_vulkan_progress` here: the lower/upper pair puts the senders into
    # "bounds mode" (ShowPassingFlash's sliding window).  Setting it for the
    # Create/Write family made whole scenes lose their content (measured on
    # PolygonOnAxes: ink 35541 -> 3891, and skipping this writer restores it).
    mob._vulkan_progress = float(upper)
    # Letter-by-letter reveal (Write/DrawBorderThenFill) reads this map -- but
    # ONLY for text-like mobjects.  `vulkan_bind._send` switches a mobject with
    # `_letter_alphas` onto the per-glyph text path, so setting it on a container
    # (e.g. `Write(ax)`) makes the whole Axes subtree draw as text: nothing comes
    # out and it never recovers (measured: ink pinned at 2.01 from frame 2 on).
    if _is_text_like(mob):
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
    if not _is_container(mob):
        set_anim_opacity(mob, _mob_alpha(mob))


def _write_grow(anim, mob, alpha):
    if alpha >= 1.0:
        # A finished grow must not leave the mobject scaled: these channels are
        # read by every sender, and a stale `_grow_scale < 1` shrinks the mobject
        # forever (measured: PolygramFamily lost 31% of its ink that way).
        for attr in ("_grow_scale", "_grow_point", "_grow_rot"):
            if hasattr(mob, attr):
                try:
                    delattr(mob, attr)
                except Exception:
                    pass
        return
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
    if not _is_container(mob):
        set_anim_opacity(mob, _mob_alpha(mob))


def _write_rotate(anim, mob, alpha):
    about = getattr(anim, "_rtm_pivot", None)          # begin-state snapshot
    if about is None:
        about = getattr(anim, "about_point", None)
    if about is None and hasattr(mob, "get_center"):
        about = mob.get_center()
    if about is not None:
        mob._rotation_about_point = about
    if not _is_container(mob):
        set_anim_opacity(mob, _mob_alpha(mob))


def _family(mob):
    """Every descendant of ``mob`` (structural walk, points or not).

    ``family_members_with_points()`` skips a DashedLine container because it has
    no points of its own -- the container is exactly what RTM draws, so it has to
    be reachable here.
    """
    out = []
    for sub in getattr(mob, "submobjects", None) or []:
        out.append(sub)
        out.extend(_family(sub))
    return out


def _fade_alpha(anim, alpha):
    """FadeIn/FadeOut's animated opacity for this frame.

    The hook is handed manim's raw alpha, so the animation's own rate function has
    to be applied here to match what manim does to the mobject.
    """
    rate = getattr(anim, "rate_func", None)
    try:
        a = float(rate(alpha)) if callable(rate) else float(alpha)
    except Exception:
        a = float(alpha)
    target = float(getattr(anim, "target_opacity", 1.0) or 1.0)
    value = (1.0 - a) if type(anim).__name__.startswith("FadeOut") else a
    return max(0.0, min(1.0, value * target))


def _arrays_carry_fade(mob):
    """True when the mobject's own rgba alpha already encodes the fade.

    *Every* present array must be below opaque: a stroke-only shape such as a
    DashedLine has fill alpha 0, so testing the arrays one at a time reported
    "already faded" and the dashed stroke was skipped.
    """
    seen = False
    for kind in ("stroke", "fill"):
        arr = getattr(mob, "%s_rgbas" % kind, None)
        try:
            if arr is None or not len(arr):
                continue
        except Exception:
            continue
        seen = True
        if max(float(rgba[3]) for rgba in arr) >= 0.999:
            return False
    return seen


def _write_fade(anim, mob, alpha):
    """Register the fade, including for what manim leaves at full opacity.

    Most mobjects carry the animated opacity in ``*_rgbas``; a DashedLine does not
    (only its dash children do, and RTM draws the line as one primitive from its
    start/end attributes).  So the animation's own alpha is registered on DashedLine
    containers -- and only on them, and only on the container rather than also its
    dashes, since registering both would square the fade (0.5 * 0.5).  Measured
    effect without this: one AddDashedLine at alpha 1.0 on the first frame, luma
    0.0954 where CE has 0.0.
    """
    value = _fade_alpha(anim, alpha)
    if not _is_container(mob):
        set_anim_opacity(mob, _mob_alpha(mob))
        return
    dashed = _load("manim", "DashedLine")
    if not dashed:
        return
    for desc in _family(mob):
        if not isinstance(desc, dashed) or _arrays_carry_fade(desc):
            continue
        kids = [k for k in (getattr(desc, "submobjects", None) or [])
                if getattr(k, "points", None) is not None and len(k.points)]
        if not kids:
            continue                      # a bare dash: drawn through its own arrays
        set_anim_opacity(desc, value)


def _write_indicate(anim, mob, alpha):
    if not _is_container(mob):
        set_anim_opacity(mob, _mob_alpha(mob))
    _write_grow(anim, mob, alpha)
