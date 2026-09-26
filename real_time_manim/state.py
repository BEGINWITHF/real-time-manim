"""Shared renderer/animation state.

Mobobject-keyed opacity and rotation, plus timing constants.  These live outside
the animation classes because the *renderer* (`vulkan_bind` / `vulkan_text` /
`vulkan_shapes`) reads them every frame; keeping them here lets 2.0.0 retire the
hand-written ``real_time_manim.animations`` package without touching the render
path.  ``real_time_manim.animations.base`` re-exports these names, so existing
imports keep sharing the SAME dicts.
"""

DEFAULT_ANIMATION_RUN_TIME = 1.0
DEFAULT_ANIMATION_LAG_RATIO = 0.0
TARGET_FPS = 60
FRAME_DURATION = 1.0 / TARGET_FPS

_anim_opacity = {}
_anim_rotation = {}
_anim_rotation_delta = {}


def set_anim_opacity(mob, val):
    _anim_opacity[id(mob)] = val


def get_anim_opacity(mob):
    return _anim_opacity.get(id(mob), 1.0)


def set_anim_rotation(mob, val):
    _anim_rotation[id(mob)] = val


def get_anim_rotation(mob):
    return _anim_rotation.get(id(mob), 0.0)


def set_anim_rotation_delta(mob, val):
    _anim_rotation_delta[id(mob)] = val


def get_anim_rotation_delta(mob):
    return _anim_rotation_delta.get(id(mob), 0.0)


def clear_anim_rotation_delta():
    _anim_rotation_delta.clear()
