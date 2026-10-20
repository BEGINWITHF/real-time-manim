"""The `_write_*` functions that stamp RTM's render channels onto a mobject.

One function per channel rule (`_vulkan_progress`, `_letter_alphas`,
`_grow_*`, `_rotation_about_point`, the fade registry, ...); they are
called from `derive_channels` once per animation per frame."""

from __future__ import annotations

import logging

import numpy as np

from real_time_manim.state import set_anim_opacity
from real_time_manim.render.hook_rules import (
    _TRANSFORM_MORPH,
    _children,
    _eased_sub_bound,
    _family_members,
    _is_container,
    _is_text_like,
    _kind_of,
    _load,
    _refresh_opacity,
)

logger = logging.getLogger(__name__)



def _write_progress(anim, mob, alpha):
    """`Create` / `Uncreate` / `Write` / `DrawBorderThenFill` / `ShowIncreasingSubsets`."""
    bounds = getattr(anim, "_get_bounds", None)
    cut_points = False
    if callable(bounds):
        cut_points = True
        sub = _eased_sub_bound(anim, alpha)
        if sub is None:                         # VGroup: keep the stagger driver
            lower, upper = bounds(alpha)
        else:
            lower, upper = bounds(sub)
    else:
        sub_alpha = _eased_sub_bound(anim, alpha)
        if sub_alpha is None:
            # MULTI-family (Write over a VGroup/Text): `_vulkan_progress` here is
            # not a drawn fraction but the STAGGER driver `vulkan_bind` spreads
            # as `clamp(p*N - i)` across children; manim's per-sub eased values
            # cannot be expressed through it (see `_eased_sub_bound`).  Leave it
            # alone so the 逐字家族 keeps its timing.
            lower, upper = 0.0, alpha
        else:
            # `DrawBorderThenFill`/`Write`/`Unwrite` expose no `_get_bounds`, but
            # the DrawBorderThenFill family STILL cuts the points itself: phase 1
            # runs `pointwise_become_partial(outline, 0, sub)` and phase 2
            # `interpolate`s the full outline->starting geometry (manim
            # creation.py:274-288).  Handing a SINGLE-family target (a bare
            # Square/Circle/glyph -- exactly the wiki's border_fill) the raw-alpha
            # window made the senders cut the already-cut contour a SECOND time:
            # `point_path_bounds` returned (0.0, alpha) and only `alpha` of the
            # eased cut reached the screen.  Measured on wiki
            # 03-动画\\创建与擦除 01-Create与画线族-border_fill (Square,
            # DrawBorderThenFill, double_smooth): raw alpha 0.40 drew 40.0 % of
            # the perimeter where CE draws 95.9 %, and the fill phase drew 50-80 %
            # where CE draws 100 % -- the missing blue border of "改色时机错误".
            # Mirror Create for that case: tag the family partial (draw the whole
            # cut path) and set the channel to the fraction manim cut,
            # `min(1, 2 * sub_alpha)`, so primitive senders that read
            # `_vulkan_progress` directly (circle/ellipse) agree with the point
            # path.  `sub_alpha` is manim's eased `get_sub_alpha`; DrawBorderThenFill
            # then does `integer_interpolate(0, 2, sub_alpha)`, whose phase-1 cut is
            # `2 * sub_alpha` and whose phase-2 geometry is the full shape.
            cut_points = True
            lower, upper = 0.0, min(1.0, 2.0 * sub_alpha)
    # Only `_vulkan_progress` here: the lower/upper pair puts the senders into
    # "bounds mode" (ShowPassingFlash's sliding window).  Setting it for the
    # Create/Write family made whole scenes lose their content (measured on
    # PolygonOnAxes: ink 35541 -> 3891, and skipping this writer restores it).
    mob._vulkan_progress = float(upper)
    # Written on every call so the tag cannot outlive the writer that set it.
    mob._vulkan_points_partial = cut_points
    # manim cuts EVERY member of the family, not just the mobject the writer
    # is handed: `Animation.interpolate_mobject` walks `get_all_families_zipped`
    # and gives each member its own `sub_alpha`, and `ShowPartial` then calls
    # `pointwise_become_partial` on it.  Tag them all, so no member is windowed
    # a second time by `_vulkan_progress`.  Tagging only the single-family case
    # (the old rule) left the multi-member ones double-cut, because for them the
    # channel holds the *stagger driver* (`_eased_sub_bound` returns None):
    #
    # * `Create(CurvedArrow)` -- body cut to 0.959 at alpha 0.4, then stroked
    #   to 0.40 of that: measured on CutLineFamily, CE draws the whole arc
    #   while RTM draws 40 % of it.
    # * `Create(VGroup)` -- each child cut by manim at its own stagger value
    #   and then cut again by `vulkan_bind`'s `clamp(p*N - i)` distribution.
    if cut_points:
        members = _family_members(anim)
    else:
        members = []
    for member in members:
        member._vulkan_points_partial = True
    if cut_points:
        _snapshot_dashed_extent(anim, mob)
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

    # `ShowIncreasingSubsets` (and the four text subclasses built on it:
    # AddTextLetterByLetter, RemoveTextLetterByLetter, TypeWithCursor,
    # UntypeWithCursor) do NOT fade glyphs -- they reveal a BINARY PREFIX.
    # creation.py:527-541 computes
    #     value = (1 - rate_func(alpha)) if reverse_rate_function else rate_func(alpha)
    #     index = int(int_func(value * n))
    # then `set_opacity(1)` below index and `set_opacity(0)` above it, which
    # lands in fill_rgbas.  `get_sub_alpha` cannot express that: manim's
    # DEFAULT_ANIMATION_LAG_RATIO is 0, so it returns one *continuous* number
    # for every glyph at once, and `_send_text_write` fades the whole word
    # together (skip at <= 0.001, fill at >= 0.8).  Measured on
    # TextRevealAnimations: first_bad=38 = inside UntypeWithCursor's window,
    # C+ 0.31 = glyphs CE had already removed, B 0.471 = CE ink never reached.
    #
    # Read the verdict back off the mobjects rather than re-deriving the prefix:
    # manim has already applied rate_func, int_func and reverse_rate_function by
    # the time `original(alpha)` runs, so this channel cannot drift from manim's
    # own semantics across versions.
    try:
        from manim.animation.creation import ShowIncreasingSubsets
        if isinstance(anim, ShowIncreasingSubsets):
            return {i: (1.0 if float(getattr(s, "fill_opacity", 0.0)) > 0.5 else 0.0)
                    for i, s in enumerate(subs)}
    except Exception:
        pass

    get_sub_alpha = getattr(anim, "get_sub_alpha", None)
    if not callable(get_sub_alpha):
        return None
    try:
        return {i: get_sub_alpha(alpha, i, len(subs)) for i in range(len(subs))}
    except Exception:
        return None


def _eased_alpha(anim, alpha):
    """manim's ``get_sub_alpha`` for a single submobject: ease the raw alpha.

    Hooks are handed the RAW progress, while manim cuts/positions with
    ``get_sub_alpha`` = ``rate_func(clip(value - lower))`` (with
    ``reverse_rate_function`` flipping the input first).  Deriving a window
    from the raw value renders LINEARLY where CE eases -- see
    ``_write_passing_flash``.
    """
    value = max(0.0, min(1.0, float(alpha)))
    if getattr(anim, "reverse_rate_function", False):
        value = 1.0 - value
    rate = getattr(anim, "rate_func", None)
    try:
        return max(0.0, min(1.0, float(rate(value)) if callable(rate) else value))
    except Exception:
        return value


def _write_passing_flash(anim, mob, alpha):
    # The window has to be the one manim itself used, and it must be applied to
    # the WHOLE contour: `ShowPartial.interpolate_submobject` has already
    # replaced the points with the sliver (`pointwise_become_partial(start,
    # *_get_bounds(alpha))`), exactly like Create.  Parking a second
    # `[alpha, alpha + width]` window on those cut points cut the sliver again
    # and shifted its phase -- measured on
    # `ShowPassingFlash(Line([-3,0,0],[3,0,0]), time_width=0.5, run_time=1)`:
    # at t=0.5 RTM painted manim-units [-0.03, 1.53] where CE paints
    # [-1.50, 1.50] (the middle half), and at t=0.25 [-2.87, -2.50] instead of
    # [-3.00, -0.75].  Put the pristine contour back first, so the window is a
    # fraction of the full path again, and read the bounds off manim
    # (`_get_bounds` = `[alpha*(1+tw) - tw, alpha*(1+tw)]`, upper clamped to 1)
    # instead of re-deriving them.
    width = 0.2
    for attr in ("time_width", "width"):
        value = getattr(anim, attr, None)
        if isinstance(value, (int, float)):
            width = float(value)
            break
    # Ease the raw progress exactly as manim does before it asks for the
    # bounds: CE cuts the path with `get_sub_alpha(...)` =
    # `rate_func(clip(alpha))`, so its comet sweeps smoothly while a window
    # built from the raw alpha sweeps LINEARLY.  Measured on the wiki
    # 03-动画/强调与提示/01b-扫光与波纹 ring (the 12-piece thinning flash):
    # CE's arc head ran 0, 2, 3, 6, 10, 16, 23, 33, 48, 67, 91, 120 deg
    # against RTM's 3, 19, 33, 49, 63, 78, 94, 110 deg -- 3.8 deg/frame from
    # frame one, i.e. "第二个动画还是不太对".
    alpha = _eased_alpha(anim, alpha)
    bounds = getattr(anim, "_get_bounds", None)
    if callable(bounds):
        try:
            lower, upper = bounds(alpha)
        except Exception:
            lower, upper = alpha, min(1.0, alpha + width)
    else:
        lower, upper = alpha, min(1.0, alpha + width)
    start = getattr(anim, "starting_mobject", None)
    if start is not None:
        try:
            for live, pristine in zip(mob.get_family(), start.get_family()):
                pts = getattr(pristine, "points", None)
                if pts is None or not len(pts):
                    continue
                if len(getattr(live, "points", ())):
                    live.points = pts.copy()
        except Exception:
            pass
    mob._vulkan_progress_lower = lower
    mob._vulkan_progress_upper = upper
    mob._vulkan_progress = upper
    # The flash walks a window over the mobject's COMPLETE contour, so the
    # cut-path tag from an earlier Create on the same mobject no longer
    # describes it: leaving it set made `_send_polygon` rebuild the polyline
    # from that tag (a window over the cut groups, and no group split for a
    # multi-group Polygram).  Every writer that changes what the points mean
    # has to own the tag, exactly like `_write_progress` does.
    #
    # On the WHOLE family, not just the container: `_write_progress` sets the
    # tag on every family member, so a Create(...) followed by a
    # ShowPassingFlash(...) over the same group left every CHILD tagged even
    # though the container had been cleared -- the flash then drew each child
    # from its stale cut prefix instead of its full contour.
    mob._vulkan_points_partial = False
    for member in _family_members(anim):
        member._vulkan_points_partial = False


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
        _refresh_opacity(mob)


def _write_updates(anim, mob, alpha):
    """Updater-driven animations: geometry changes every frame, so use the point path.

    Same reasoning as the transform family (plan 3.2) -- these classes rewrite the
    mobject's points (or a number's glyphs) through a callback each frame and carry
    no progress/opacity channel, so the renderer has to read the current points
    rather than a specialised shape sender.  Releasing the flag at alpha 1 keeps a
    finished animation from leaving the mobject on the slow path (the stale
    ``_grow_scale`` lesson).
    """
    _write_transform(anim, mob, alpha)


def _clear_grow(mob):
    """Take every grow channel off ``mob`` -- see :func:`_write_grow`."""
    for attr in ("_grow_scale", "_grow_point", "_grow_rot"):
        if hasattr(mob, attr):
            try:
                delattr(mob, attr)
            except Exception:
                pass


def _write_grow(anim, mob, alpha):
    if alpha >= 1.0:
        # A finished grow must not leave the mobject scaled: these channels are
        # read by every sender, and a stale `_grow_scale < 1` shrinks the mobject
        # forever (measured: PolygramFamily lost 31% of its ink that way).
        _clear_grow(mob)
        return
    if isinstance(anim, _TRANSFORM_MORPH):
        # manim's own grows (GrowFromCenter / GrowFromEdge / GrowFromPoint /
        # GrowArrow / SpinInFromNothing) are Transforms: their `interpolate` has
        # ALREADY scaled `mob.points` by `smooth(alpha)` about the grow point,
        # and those scaled points are exactly what CE draws.  Writing
        # `_grow_scale = alpha` on top of it applied the growth a second time:
        # every point-reading sender drew `alpha * smooth(alpha)` where CE draws
        # `smooth(alpha)`, while the ones that ignore the channel
        # (`_send_vmobject`) drew CE's size -- so the two halves of ONE figure
        # disagreed, which is what let 08_geometry.PolygramFamily's grid lines
        # run outside the Rectangle border they belong to (border 144 px against
        # the grid's 212 at t=0.8 s; CE has both at 212).  Measured the other way
        # round, the whole shape was also too small: a Polygon came out at
        # `alpha * smooth(alpha)` of its CE size over its whole 0.35 s grow.
        #
        # The animations that reach here WITHOUT moving the points -- Flash,
        # Circumscribe and Blink, relayed by `_write_indicate` -- are the ones
        # the channel is still for.
        _clear_grow(mob)
        if not _is_container(mob):
            _refresh_opacity(mob)
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
        _refresh_opacity(mob)


def _write_rotate(anim, mob, alpha):
    about = getattr(anim, "_rtm_pivot", None)          # begin-state snapshot
    if about is None:
        about = getattr(anim, "about_point", None)
    if about is None and hasattr(mob, "get_center"):
        about = mob.get_center()
    if about is not None:
        mob._rotation_about_point = about
    if not _is_container(mob):
        _refresh_opacity(mob)


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


def _walk(mob):
    """``mob`` and every descendant, pre-order (self first)."""
    yield mob
    for sub in getattr(mob, "submobjects", None) or []:
        yield from _walk(sub)


def _snapshot_dashed_extent(anim, mob):
    """Pin every ``DashedLine`` under ``mob`` to its extent BEFORE the cut.

    ``Create(DashedLine)`` is a ``ShowPartial``: ``interpolate_mobject`` runs
    ``pointwise_become_partial`` on **every dash**, so from the first frame on
    ``mob.get_end()`` is the REVEAL TIP, not the end of the line.
    ``_send_dashed_line`` derives the whole dash pattern (``num_dashes``,
    dash, gap) from ``get_start()``/``get_end()``, so it re-counted the dashes
    against a half-length line every frame and re-spaced them.

    Measured on wiki ``04-图形与文本`` ``02-线与箭头-lines.mp4`` (the 6-unit
    DashedLine from -5.6 to 0.4, ``dash_length=0.15``, ``dashed_ratio=0.55``):
    once finished it is 810 px long with 22 dashes on a 38 px pitch, and
    ManimCE keeps that pitch for the whole Create -- RTM's dashes sat on a
    36-37 px pitch for as long as the animation ran (f120: dash #11 at x=474
    against CE's x=484; f137: last dash at x=865 against CE's x=902, i.e. a
    whole dash short) and the pattern jumped outward on the frame the
    animation ended -- the "虚线在动画播放完后被拉伸了一下" report.  CE never
    moves a dash: ``DashedVMobject`` splits the line once, at construction,
    and ``Create`` only reveals them.

    ``Animation.begin`` copies the mobject into ``starting_mobject`` *before*
    its first ``interpolate(0)``, so that copy still holds the uncut extent.
    The tree is walked in lockstep (the copy has the same shape), and the
    snapshot is only ever consumed while ``_vulkan_points_partial`` is set and
    the uncut START still matches -- a line that is later moved or resized
    falls back to its own live endpoints instead of a stale copy.
    """
    dashed = _load("manim", "DashedLine")
    if not dashed:
        return
    if not getattr(mob, "submobjects", None):
        return                       # nothing below this node can be a DashedLine
    start = getattr(anim, "starting_mobject", None)
    if start is None:
        return
    cur = list(_walk(mob))
    orig = list(_walk(start))
    if len(cur) != len(orig):
        return
    for c, o in zip(cur, orig):
        if not isinstance(c, dashed):
            continue
        try:
            # NOTE: a DashedLine CONTAINER has no points of its own -- its
            # extent comes from its dashes -- so this must not be gated on
            # ``o.points``; that check silently skipped every snapshot and
            # left the sender re-counting against the cut line.
            s0 = np.array(o.get_start(), dtype=float)
            e0 = np.array(o.get_end(), dtype=float)
            if not (np.all(np.isfinite(s0)) and np.all(np.isfinite(e0))):
                continue
            c._rtm_dash_full = (s0, e0)
        except Exception:                     # pragma: no cover - mapping aid only
            logger.debug("dashed extent snapshot failed", exc_info=True)


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
    """The fade already lives in the rgba arrays -- the registry must not repeat it.

    manim's ``FadeIn``/``FadeOut`` are ``Transform``s whose starting copy is at
    opacity 0, so ``interpolate`` writes the eased value straight into
    ``fill_rgbas``/``stroke_rgbas``, and every sender folds that array alpha
    into the primitive it submits (``alpha * fo``, ``alpha * so``).  Registering
    the animation's own value on top of it applied the fade **twice**: measured
    end to end on FadeProbe, at raw alpha 0.267 CE peaks at 20/255 and RTM at
    1/255 -- exactly ``0.084`` against ``0.084 ** 2``.  See ``_refresh_opacity``.

    The one shape whose drawn primitive does NOT follow its own arrays is a
    DashedLine: RTM submits a single ``AddDashedLine`` built from the
    container's start/end, while CE strokes the dash children, and it is those
    children's arrays that manim fades.  So the animation's own value is
    registered on the DashedLine -- and only on it, never on the dashes, since
    both would square the fade (0.5 * 0.5).  Measured effect without it: one
    AddDashedLine at alpha 1.0 on the first frame, luma 0.0954 where CE has 0.0.
    """
    value = _fade_alpha(anim, alpha)
    if not _is_container(mob):
        _refresh_opacity(mob)
        return
    dashed = _load("manim", "DashedLine")
    if not dashed:
        return
    # `(mob,) +`: a DashedLine is itself a container (its dashes are the
    # children, its own points list is empty), so the target has to be in this
    # walk -- `_family` returns descendants only, and skipping it left
    # `FadeIn(DashedLine)` drawn opaque on frame 0.
    for desc in (mob,) + tuple(_family(mob)):
        if not isinstance(desc, dashed) or _arrays_carry_fade(desc):
            continue
        kids = [k for k in (getattr(desc, "submobjects", None) or [])
                if getattr(k, "points", None) is not None and len(k.points)]
        if not kids:
            continue                      # a bare dash: drawn through its own arrays
        # The registry is a MULTIPLIER that outlives the animation (a
        # WeakKeyDictionary entry dies with the mobject, not with the fade), and
        # `_refresh_opacity` -- the only thing that resets it -- returns early
        # for containers, which is exactly what a DashedLine is.  A fade that
        # ended at 0 then left the dashes pinned at opacity 0 for every later,
        # unrelated frame in which the same object was still on screen.  Put it
        # back to neutral once the fade has run its course.
        set_anim_opacity(desc, value if alpha < 1.0 else 1.0)


def _write_indicate(anim, mob, alpha):
    """``Indicate`` already morphs its own swell -- never add a grow on top.

    manim's ``Indicate`` is a ``Transform`` whose target is a copy scaled by
    ``scale_factor`` (and recoloured), so the resize lives in ``mob.points``
    before this hook runs.  Delegating to ``_write_grow`` wrote a *second*
    scale, ``_grow_scale = raw alpha``, which starts at 0: the shape vanished
    on the first frame of its own Indicate instead of swelling (measured:
    IndicationAnimations frame 46 mean|d| 8.38, OptionalDependencyFallback
    2.74, PolygramsAndMatchers 1.60 -- all reported as "grows from no size").
    ``Flash`` and ``Circumscribe`` do not morph points, so they keep the grow
    channel.

    One exception: ``Blink`` is a ``Succession`` of ``UpdateFromFunc`` children
    that only step the mobject's opacity on and off -- nothing in CE resizes
    it, so the grow channel would scale the box from zero for its whole window
    (IndicationAnimations frames 8-16: box drawn at 0/3/10% of its size,
    mean|d| 6.16).  When *every* child resolves to the updater bucket the
    container has no visual life of its own: relay the children and drop the
    grow channels instead of writing them.

    The same holds for ``Flash`` and ``Circumscribe``: their children are
    ``ShowPassingFlash``/``Create``/``Fade*`` animations that draw their own
    reveal, and CE never resizes these shapes -- the flash lines are FIXED
    length and only the light sweeps along them.  Keeping the grow channel
    scaled the whole line group about the flash point by the raw alpha, so the
    star's tips grew from the centre: measured on the wiki
    03-动画/强调与提示/01-强调与闪烁 Flash (line_length=0.3, flash_radius=0.18
    -> 65 px lines) the lit star's mean radius ran 10, 18, 26, 34, 45, 57, 69,
    81, ... px against CE's 68, 85, 88, 94, 104, 111, 116, 116, 119, 126 --
    a 12.5x ramp where CE grows 1.9x, and its furthest tip sat at 35 px where
    CE's was at 111.  Any child that owns its geometry in a channel of its own
    therefore drops the grow.
    """
    if isinstance(anim, _TRANSFORM_MORPH):
        _write_transform(anim, mob, alpha)
        return
    kids = _children(anim)
    if kids and all(_kind_of(k) in ("updates", "passing_flash", "progress",
                                    "fade", "indicate") for k in kids):
        for attr in ("_grow_scale", "_grow_point", "_grow_rot"):
            if hasattr(mob, attr):
                try:
                    delattr(mob, attr)
                except Exception:
                    pass
        if not _is_container(mob):
            _refresh_opacity(mob)
        return
    if not _is_container(mob):
        _refresh_opacity(mob)
    _write_grow(anim, mob, alpha)
