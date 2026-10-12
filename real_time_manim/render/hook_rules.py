"""What kind of animation is this?  Class lookup tables and shared helpers.

Everything in here is pure classification: which manim class a given
animation is, and the mobject/opacity queries the channel writers share.
Kept separate so the writers and the hook installer can both use it
without importing each other."""

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
# `ShowIncreasingSubsets`, `ShowSubmobjectsOneByOne` and `SpiralIn` are
# DELIBERATELY absent.  None of them is a `ShowPartial` subclass and none draws a
# partial path: manim reveals their submobjects with **binary whole-shape opacity**
# (`int(floor(rate_func(alpha)*n))` then `set_opacity(1)`/`set_opacity(0)`, and for
# SpiralIn a whole-shape move+rotate+fade) -- all of which land in `fill_rgbas` /
# `stroke_rgbas`, already read by every sender.  Listing them here set
# `_vulkan_progress` on the container instead, which `vulkan_bind` distributes as
# `sub_progress = clamp(p*N - i)`: at alpha 0.5 a 3-shape group had its middle shape
# drawn HALF and left visible where CE has it invisible.  Reported as "some shapes
# are incomplete" (PartialAndSubsetAnimations, measured first_bad=33 = inside the
# scene's SpiralIn window).
# The *text* subclasses stay listed: they take the per-glyph `_letter_alphas` path.
_PROGRESS = _load("manim.animation.creation",
                  "ShowPartial", "Create", "Uncreate",
                  "DrawBorderThenFill", "Write", "Unwrite",
                  "AddTextLetterByLetter",
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
# Updater-driven animations: they rewrite points/colours each frame and carry no
# channel of their own (see the rule comment below).  Loaded from their own module
# *and* the manim namespace, because class locations move between versions.
_UPDATES = (_load("manim.animation.update", "UpdateFromFunc", "UpdateFromAlphaFunc",
                  "MaintainPositionRelativeTo")
            + _load("manim.animation.numbers", "ChangingDecimal",
                    "ChangeDecimalToValue")
            + _load("manim.animation.indication", "Wiggle")
            + _load("manim.animation.speedmodifier", "ChangeSpeed")
            + _load("manim", "UpdateFromFunc", "UpdateFromAlphaFunc",
                    "MaintainPositionRelativeTo", "ChangingDecimal",
                    "ChangeDecimalToValue", "Wiggle", "ChangeSpeed"))

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
    ("updates", _UPDATES),
)



def _children(anim):
    return [a for a in (getattr(anim, "animations", None) or ()) if a is not None]




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


def _has_rgba_arrays(mob):
    """True when the mobject has a `fill_rgbas` / `stroke_rgbas` array to read.

    An array-less mobject (``ImageMobject``) carries its opacity in an
    attribute instead, and is the only case where the registry can still add
    something the draw path does not already have.
    """
    for kind in ("stroke", "fill"):
        arr = getattr(mob, "%s_rgbas" % kind, None)
        try:
            if arr is not None and len(arr):
                return True
        except Exception:
            continue
    return False


def _refresh_opacity(mob):
    """Keep the opacity registry from repeating what the rgba arrays already say.

    The registry is a *multiplier*: ``_send_impl`` computes
    ``a = parent_alpha * get_anim_opacity(mob)`` and every sender then folds in
    the mobject's own array alpha again (``alpha * fo``, ``alpha * so``,
    ``stroke_alpha = min(1, so * a)``).  Registering that same array alpha made
    the opacity apply **twice** -- manim's ``FadeIn`` writes the eased value into
    ``fill_rgbas``/``stroke_rgbas``, so RTM drew ``s * s`` where CE draws ``s``
    (measured end to end on FadeProbe: at raw alpha 0.267 CE peaks at 20/255 and
    RTM at 1/255, i.e. ``0.084`` vs ``0.084 ** 2``).  A mobject with arrays has
    nothing left to add, so the registry is cleared to 1.0; only an array-less
    one still falls back to its own opacity attribute.
    """
    set_anim_opacity(mob, _mob_alpha(mob) if not _has_rgba_arrays(mob) else 1.0)


def _is_text_like(mob):
    """True for the mobjects whose children are glyphs (`Text`, `MathTexPart`)."""
    from manim import Text
    return isinstance(mob, Text) or bool(getattr(mob, "_is_text", False))


def _eased_sub_bound(anim, alpha):
    """manim's own eased sub-progress for a **single-family** animation, else None.

    ``Animation.get_sub_alpha`` (animation.py:364-391) is where manim applies
    ``rate_func`` *and* ``reverse_rate_function``; ``ShowPartial`` then hands the
    result to ``pointwise_become_partial``.  Returning None means "keep the
    raw-alpha channel": that happens for a VGroup, where the channel is not a
    drawn fraction but a *stagger driver* -- ``vulkan_bind`` distributes it as
    ``clamp(p*N - i)``, and manim's per-sub values ``smooth(alpha*(N+1) - i)``
    cannot be expressed through it, so the existing stagger is left alone.
    """
    try:
        family = list(anim.get_all_families_zipped())
    except Exception:
        return None
    if len(family) != 1:
        return None
    try:
        return float(anim.get_sub_alpha(alpha, 0, 1))
    except Exception:
        return None


def _family_members(anim):
    """Every member of ``anim``'s family whose points manim cuts.

    ``get_all_families_zipped`` is the same iterator
    ``Animation.interpolate_mobject`` walks: it yields
    ``(member, starting_member)`` pairs over ``family_members_with_points``,
    i.e. exactly the mobjects that receive ``pointwise_become_partial``.
    """
    try:
        return [pair[0] for pair in anim.get_all_families_zipped()]
    except Exception:
        return []
