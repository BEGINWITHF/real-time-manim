"""Shared renderer/animation state.

Mobobject-keyed opacity and rotation, plus timing constants.  These live outside
the animation classes because the *renderer* (`vulkan_bind` / `vulkan_text` /
`vulkan_shapes`) reads them every frame; keeping them here lets 2.0.0 retire the
hand-written ``real_time_manim.animations`` package without touching the render
path.  ``real_time_manim.animations.base`` re-exports these names, so existing
imports keep sharing the SAME dicts.

The registries are keyed by the mobject ITSELF (weakly), never by
``id(mobject)``: an id-keyed entry outlives the object that earned it, CPython
reuses ids, and the next mobject allocated at that address inherits the verdict
-- a faded-out opacity 0.0 or a rotation it never had.  Measured before the
change: parking ``set_anim_opacity(t, 0.0)`` on a ``Text``, deleting it and
allocating fresh ``Text``s reused the id after ~123 allocations and handed the
stale verdict over 24 times in 400 allocations.  Weak keys make the entry die
with its owner instead.

Any object that cannot be weak-referenced (no manim ``Mobject`` qualifies --
``manim.mobject`` defines no ``__slots__``) falls back to an attribute on the
object, which is released with it too.
"""
from __future__ import annotations

from weakref import WeakKeyDictionary

DEFAULT_ANIMATION_RUN_TIME = 1.0
DEFAULT_ANIMATION_LAG_RATIO = 0.0
TARGET_FPS = 60
FRAME_DURATION = 1.0 / TARGET_FPS

_anim_opacity = WeakKeyDictionary()
_anim_rotation = WeakKeyDictionary()
_anim_rotation_delta = WeakKeyDictionary()


def _store(registry, attr, mob, val):
    """Park ``val`` on ``mob`` inside ``registry``, weakly where possible."""
    try:
        registry[mob] = val
    except TypeError:                       # not weak-referenceable
        try:
            setattr(mob, attr, val)
        except Exception:                   # no attribute either: give up
            pass


def _load(registry, attr, mob, default):
    """Read ``mob``'s verdict back, defaulting when it never earned one."""
    try:
        val = registry.get(mob, None)
    except TypeError:
        val = None
    if val is not None:
        return val
    return getattr(mob, attr, default)


def set_anim_opacity(mob, val):
    _store(_anim_opacity, '_rtm_anim_opacity', mob, val)


def get_anim_opacity(mob):
    return _load(_anim_opacity, '_rtm_anim_opacity', mob, 1.0)


def set_anim_rotation(mob, val):
    _store(_anim_rotation, '_rtm_anim_rotation', mob, val)


def get_anim_rotation(mob):
    return _load(_anim_rotation, '_rtm_anim_rotation', mob, 0.0)


def set_anim_rotation_delta(mob, val):
    _store(_anim_rotation_delta, '_rtm_anim_rotation_delta', mob, val)


def get_anim_rotation_delta(mob):
    return _load(_anim_rotation_delta, '_rtm_anim_rotation_delta', mob, 0.0)


def clear_anim_rotation_delta():
    _anim_rotation_delta.clear()
