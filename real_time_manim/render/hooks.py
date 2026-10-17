"""Give manim's own animations the render-state channels RTM's senders read.

This is the public half: `install_hooks` wraps a manim animation's
`interpolate`, `derive_channels` re-derives the channels from the
animation's own state every frame, `clear_hooks` unwraps it.
`Timeline.finalize` installs the hooks; `install_hooks` is idempotent
and recurses into composite animations."""

from __future__ import annotations

import logging

from real_time_manim.render.hook_channels import (
    _write_fade,
    _write_grow,
    _write_indicate,
    _write_passing_flash,
    _write_progress,
    _write_rotate,
    _write_transform,
    _write_updates,
)
from real_time_manim.render.hook_rules import (
    _children,
    _is_container,
    _kind_of,
    _refresh_opacity,
)

logger = logging.getLogger(__name__)



def _is_rtm_animation(anim):
    """RTM's own classes write the channels themselves -- leave them alone.

    That includes ``_RtmAnimationAdapter`` (window/patches.py): the shell a
    manim composite drives around one RTM animation.  It is a *manim*
    Animation for the composite's sake, but its channels come from the
    wrapped child, so wrapping the shell's ``interpolate`` again would only
    derive nothing and log "no render hook" every frame.
    """
    inner = getattr(anim, "_rtm_inner", None)
    if inner is not None:
        return True
    try:
        from real_time_manim.animations.base import Animation as RtmAnimation
    except Exception:                     # pragma: no cover
        return False
    return isinstance(anim, RtmAnimation)


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
            # recurse=False: children derive themselves through their own
            # wrapped interpolate, already driven by manim with their sub_alpha.
            # Recursing here would re-derive them from THIS animation's alpha.
            derive_channels(anim, alpha, recurse=False)
        except Exception:                # a hook must never break a render
            logger.debug("render hook failed for %s", type(anim).__name__, exc_info=True)
        return out

    anim.interpolate = interpolate
    anim._rtm_orig_interpolate = original
    anim._rtm_hooks_installed = True
    _snapshot_pivots(anim, getattr(anim, "mobject", None))

    # derive the begin state too, so frame 0 is not rendered from the defaults.
    # recurse=True here (the opposite of the wrapper above): at install time no
    # child has been driven yet, so this is what gives them their start state.
    try:
        derive_channels(anim, 0.0, recurse=True)
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


def install_hooks_from_updaters(mob) -> int:
    """Arm the hooks of every manim animation a mobject's UPDATER drives.

    ``manim.turn_animation_into_updater`` / ``cycle_animation`` close the
    animation over a per-frame ``update(m, dt)`` closure and hang that closure
    on the mobject.  Such an animation never becomes a timeline entry, and
    ``Timeline.finalize`` is the only place ``install_hooks`` runs -- so it
    plays back with no render channels at all.

    The visible casualty is a manim ``Write`` driven that way: with
    ``_letter_alphas`` unarmed it falls back to ``_send_vmobject``, and for
    TEXT that sender switches the outline off as soon as the fill reports any
    visibility::

        if is_text and vis_fill > 0.01:
            do_stroke = False

    manim's ``DrawBorderThenFill`` spends a glyph's whole second half ramping
    the fill from 0 while it keeps the outline at full width, so for those
    frames RTM drew a few-percent fill and NO outline and the letter
    disappeared.  Measured on the wiki
    ``03-动画/更新器动画/01b-更新工具与自动变化``: at each of ``Welcome``'s
    seven outline->fill boundaries the word's ink fell 31571 -> 9504 (-70 %) in
    one frame and took ~10 frames to come back, while CE's curve never drops.
    A 120-frame probe render of that scene with the hooks armed reports 0
    drops; the un-hooked one reports exactly 7.

    Detection is deliberately narrow: only a *closure cell* holding a manim
    ``Animation`` matches -- precisely what those two helpers build, and what
    an ordinary lambda, ``always`` or ``always_redraw`` updater never does.

    Returns how many animations were newly hooked (0 for the overwhelmingly
    common mobject whose updaters are plain lambdas).
    """
    try:
        from manim.animation.animation import Animation as ManimAnimation
    except Exception:                       # pragma: no cover - manim is required
        return 0
    hooked = 0
    for fn in (getattr(mob, "updaters", None) or ()):
        cells = getattr(fn, "__closure__", None)
        if not cells:
            continue
        for cell in cells:
            try:
                value = cell.cell_contents
            except ValueError:              # empty cell, not filled in yet
                continue
            if isinstance(value, ManimAnimation) and not getattr(
                    value, "_rtm_hooks_installed", False):
                install_hooks(value)
                hooked += 1
    return hooked


# ---------------------------------------------------------------------------
# channel derivation
# ---------------------------------------------------------------------------

def derive_channels(anim, alpha, recurse=True) -> None:
    """Write the render-state channels for `anim` at `alpha`.

    ``recurse`` matters only for composites, and it must differ per call site:

    * ``True`` (the default) is right for the install-time call, because that
      is what gives every child its **start** state before any playback.
    * ``False`` is required from a composite's own wrapper.  manim's
      ``AnimationGroup.interpolate``/``Succession.interpolate`` already drive
      each child with that child's *own* sub_alpha, and ``install_hooks`` has
      wrapped every child, so those calls write correct channels; deriving the
      children again here -- with the **group's** alpha, because a composite
      matches no ``_RULES`` bucket and falls straight through to the recursion
      below -- overwrites them.  Measured effect of getting this wrong:
      ``Succession(Create, Rotate, FadeOut)`` re-derived its Create child at the
      group alpha, so at group 0.5 a finished Create (sub_alpha 1.0) was written
      back to 0.5 and the circle sat half-drawn.
    """
    mob = getattr(anim, "mobject", None)
    if mob is None:
        if recurse:
            for sub in _children(anim):             # composite: children carry mobjects
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
            _refresh_opacity(mob)
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
    elif kind == "updates":
        _write_updates(anim, mob, alpha)
    else:
        # Unknown class: log it (the plan wants the mapping table visible) and
        # write NOTHING.  Guessing "it is probably a morph" and setting
        # `_transforming` made `.animate.scale()` render as a static final state.
        logger.debug("no render hook for %s", type(anim).__name__)

    if recurse:
        for sub in _children(anim):
            derive_channels(sub, alpha)
