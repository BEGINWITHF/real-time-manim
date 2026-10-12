"""Driving manim scenes and mobject updaters the way manim itself does.

`_setup_anim_scene` mirrors `Scene.play`'s animation setup, the updater
drivers mirror `Scene.update_mobjects`, and `_raster_debug` traces the
phase-5.4 camera fallback."""

import inspect
from manim import (
    VGroup, Group
)


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


def _run_mobject_updaters(mob, dt):
    """Run ``mob``'s updaters and then every descendant's, as manim does.

    manim drives this through ``Scene.update_mobjects`` -> ``Mobject.update(dt)``,
    which recurses into ``submobjects``.  Walking only ``scene.mobjects`` ran the
    updaters of *top-level* mobjects and silently skipped every nested one, so a
    ``ValueTracker``-driven ``Integer`` living inside a ``VGroup`` never ticked
    (measured: the counter stayed at 0 where CE reached 3).

    Suspension prunes the whole subtree, exactly like ``Mobject.update``, which
    returns before recursing when ``updating_suspended`` is set.
    """
    if getattr(mob, 'updating_suspended', False):
        return
    updaters = getattr(mob, 'updaters', None)
    if updaters:
        for updater in updaters:
            nparams = len(inspect.signature(updater).parameters)
            if nparams == 0:
                updater()
            elif nparams == 1:
                updater(mob)
            else:
                updater(mob, dt)
    # Snapshot: an updater may rebuild this mobject's children (DecimalNumber
    # set_value does), which would otherwise mutate the list under the walk.
    for sub in list(getattr(mob, 'submobjects', None) or ()):
        _run_mobject_updaters(sub, dt)


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

    # CE order: Scene.update_mobjects walks self.mobjects FORWARD (dot before
    # its always_redraw dependents).  reversed() made dependents read the
    # PREVIOUS frame's movers -- e.g. SineCurveUnitCircle's horizontal line
    # rendered 1 frame stale and detached from the dot.  Forward = CE parity.
    for mob in scene.mobjects:
        _run_mobject_updaters(mob, dt)

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
