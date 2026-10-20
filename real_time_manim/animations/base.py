import math
import numpy as np
from functools import partialmethod
from manim import VGroup, Group, Rectangle, Circle, YELLOW, Text, ManimColor

TAU = 2.0 * math.pi


def release_hidden_channels(mob):
    """Put every partial-draw channel on ``mob`` back to "fully drawn".

    RTM's draw state (``_vulkan_progress``, the ``_vulkan_progress_lower/upper``
    window, ``_vulkan_points_partial``, ``_letter_alphas`` and the animated
    opacity registry) is a renderer-only concept -- a CE mobject carries none of
    it.  manim restores exactly this in ``ShowPartial.clean_up_from_scene``
    (``pointwise_become_partial(start, 0, 1)``), so a mobject that is shown
    again later (re-added, reused in a new animation) is WHOLE again.

    RTM's removers finished with the channel parked at "hidden" and never
    released it, so every later draw of the SAME mobject submitted nothing at
    all: measured on ``Uncreate(Square)`` followed by
    ``FadeIn(Square).begin()`` -- the sender emitted zero shape calls, while
    ``Unwrite(Text)`` left ``_letter_alphas = {0: 0.0, ...}`` and
    ``FadeOut`` left the opacity registry at 0.0.
    """
    nodes = [mob]
    getter = getattr(mob, "get_family", None)
    if callable(getter):
        try:
            nodes = list(getter())
        except Exception:
            pass
    for sub in nodes:
        d = getattr(sub, "__dict__", None)
        if d is None:
            continue
        for name in ("_vulkan_progress_lower", "_vulkan_progress_upper",
                     "_letter_alphas"):
            d.pop(name, None)
        if hasattr(sub, "_vulkan_progress"):
            sub._vulkan_progress = 1.0
        if d.get("_vulkan_points_partial"):
            sub._vulkan_points_partial = False
    try:
        set_anim_opacity(mob, 1.0)
    except Exception:
        pass


def color_to_rgb(color):
    """Normalize any Manim color spec to an ``(r, g, b)`` tuple of 0..1 floats.

    Accepts everything manim accepts: ``ManimColor``, ``'#33AADD'``, ``'blue'``,
    ``(1, 0, 0)``.  Colour arguments used to be indexed blindly (``color[0]``),
    which for a hex string silently took the characters of the string -- or
    crashed on ``float('#')``.
    """
    return tuple(float(c) for c in ManimColor(color).to_rgb())


def resolve_mobject(mobject, kwargs, class_name, alias="vmobject"):
    """CE-compatible mobject argument resolution.

    CE spells the first argument ``vmobject`` for ``Create`` / ``Write`` /
    ``DrawBorderThenFill`` / ``Uncreate`` / ``Unwrite`` and ``mobject`` for the
    rest; RTM used ``mobject`` everywhere, so a mechanically ported
    ``Create(vmobject=sq)`` raised ``TypeError: missing required positional
    argument: 'mobject'``.  Accept both spellings and fail with a clear
    message when neither is present.
    """
    if mobject is None and alias in kwargs:
        mobject = kwargs.pop(alias)
    if mobject is None:
        raise TypeError(
            "%s() missing required argument: 'mobject'%s" % (
                class_name,
                " (or CE spelling '%s')" % alias if alias else "",
            )
        )
    return mobject


from real_time_manim.rate_functions import (
    _smooth, _linear, _double_smooth, _there_and_back,
)


def place_cursor_after(cursor, glyph, buff):
    """Park ``cursor`` just to the right of ``glyph``, the way manim does.

    manim's ``TypeWithCursor``/``UntypeWithCursor`` position the caret with
    ``cursor.next_to(last_glyph, RIGHT, buff=self.buff)``, whose empirical
    contract is *the cursor's LEFT edge sits ``buff`` to the right of the
    glyph's right edge* (measured on ``Text("Inserting")[3]`` with a 0.14-wide
    ``Rectangle`` and ``buff=0.12``: glyph right ``-0.104`` -> cursor
    ``-0.016..0.156``).

    The old code did ``move_to(glyph_center)`` and then ``shift(width/2 +
    buff * 4)``: the mysterious ``* 4`` put the caret ``0.48`` right of the
    glyph instead of ``0.12`` -- the wiki report "光标过于偏右"
    (03-动画/文字与数字/01b-带光标打字), and it ignored the cursor's own width
    (a 0.5-wide caret needs its centre half a width further on).
    """
    centre = np.asarray(cursor.get_center(), dtype=float).copy()
    centre[0] = float(glyph.get_right()[0]) + float(buff) + float(cursor.get_width()) / 2.0
    cursor.move_to(centre)
    return cursor

# Shared state/helpers live in real_time_manim.state (so the renderer no longer
# depends on this package); re-exported here so existing imports keep working.
from real_time_manim.state import (
    DEFAULT_ANIMATION_RUN_TIME,
    DEFAULT_ANIMATION_LAG_RATIO,
    TARGET_FPS,
    FRAME_DURATION,
    set_anim_opacity,
    get_anim_opacity,
    set_anim_rotation,
    get_anim_rotation,
    set_anim_rotation_delta,
    get_anim_rotation_delta,
    clear_anim_rotation_delta,
)


class Animation:
    _original__init__ = None

    def __init__(
        self,
        mobject=None,
        lag_ratio=DEFAULT_ANIMATION_LAG_RATIO,
        run_time=DEFAULT_ANIMATION_RUN_TIME,
        rate_func=None,
        reverse_rate_function=False,
        name=None,
        remover=False,
        suspend_mobject_updating=True,
        introducer=False,
        **kwargs,
    ):
        self.mobject = mobject
        self.lag_ratio = lag_ratio
        self._run_time = run_time
        self.rate_func = rate_func if rate_func is not None else _smooth
        self.reverse_rate_function = reverse_rate_function
        self.name = name
        self.remover = remover
        self.suspend_mobject_updating = suspend_mobject_updating
        self.introducer = introducer
        self.start_time = 0.0
        self.finished = False

    @classmethod
    def set_default(cls, **kwargs):
        if cls._original__init__ is None:
            cls._original__init__ = cls.__init__
        if kwargs:
            cls.__init__ = partialmethod(cls.__init__, **kwargs)
        else:
            cls.__init__ = cls._original__init__

    def __init_subclass__(cls, **kwargs):
        super().__init_subclass__(**kwargs)
        if '_original__init__' not in cls.__dict__:
            cls._original__init__ = cls.__init__

    @property
    def run_time(self):
        return self._run_time

    @run_time.setter
    def run_time(self, value):
        self._run_time = value

    def __str__(self):
        return self.name or f"{type(self).__name__}({self.mobject})"

    def __repr__(self):
        return self.__str__()

    def begin(self, t=None):
        if t is None:
            import time as _time
            t = _time.time()
        self.start_time = t

    def finish(self):
        self.finished = True

    def interpolate(self, t):
        alpha = (t - self.start_time) / self.run_time if self.run_time > 0 else 1.0
        alpha = max(0.0, min(1.0, alpha))
        if self.reverse_rate_function:
            alpha = 1.0 - alpha
        self.interpolate_mobject(alpha)

    def interpolate_mobject(self, alpha):
        pass

    def get_sub_alpha(self, alpha, index, num_submobjects):
        lag_ratio = self.lag_ratio
        full_length = (num_submobjects - 1) * lag_ratio + 1
        value = alpha * full_length
        lower = index * lag_ratio
        raw_sub_alpha = max(0.0, min(1.0, value - lower))
        return self.rate_func(raw_sub_alpha)

    # ------------------------------------------------------------------
    # Getters/setters -- manim CE ``Animation`` parity.
    #
    # RTM used to implement ``set_rate_func`` only; every other chainable
    # accessor raised ``AttributeError`` the moment a script called it
    # (wiki 03-动画/通用/01-生命周期与公共参数: "其余链式方法…调用即
    # AttributeError").  manim's implementations are trivial attribute
    # accessors that return ``self`` so they can be chained, e.g.
    # ``anim.set_run_time(2).set_rate_func(linear)`` -- mirror them exactly
    # (see ``real_time_manim/manim/animation/animation.py``:``set_run_time``
    # .. ``is_introducer``).
    # ------------------------------------------------------------------
    def set_run_time(self, run_time):
        """Set the run time (seconds).  Returns ``self`` (chainable)."""
        self.run_time = run_time
        return self

    def get_run_time(self):
        """Return the run time in seconds."""
        return self.run_time

    def set_rate_func(self, func):
        """Set the rate function.  Returns ``self`` (chainable, as in manim)."""
        self.rate_func = func
        return self

    def get_rate_func(self):
        """Return the current rate function."""
        return self.rate_func

    def set_name(self, name):
        """Set the display name used by ``str()``/``repr()``.  Chainable."""
        self.name = name
        return self

    def is_introducer(self):
        """True when the animation adds its mobject to the scene on begin()."""
        return bool(self.introducer)

    def is_remover(self):
        """True when the animation removes its mobject from the scene on end()."""
        return bool(self.remover)

    def copy(self):
        """Deep copy of this animation (manim's ``Animation.copy`` is ``deepcopy``).

        The copy carries its own ``mobject`` and timing state, so it can be
        scheduled again without disturbing the original.
        """
        import copy as _copy
        return _copy.deepcopy(self)

    def clean_up_from_scene(self, scene):
        """Remove the animated mobject from the scene when this is a remover.

        manim's ``Animation.clean_up_from_scene`` does exactly this::

            if self.remover:
                self.scene.remove(self.mobject)

        RTM's base was a no-op, so ``FadeOut`` / ``Uncreate(remover=True)``
        only parked the mobject at opacity 0 and left it as a (transparent)
        scene ROOT forever: long scenes accumulated dead roots, and a later
        ``FadeOut(VGroup(...))`` or ``mobjects`` assertion saw them.  Only
        top-level roots may be removed -- animating a submobject must leave its
        parent in place, which is manim's behaviour too.
        """
        if not getattr(self, "remover", False) or self.mobject is None:
            return
        try:
            roots = getattr(scene, "mobjects", None)
            if roots is not None and self.mobject in roots:
                scene.remove(self.mobject)
        except Exception:
            pass

    def get_all_mobjects(self):
        if self.mobject is not None:
            return [self.mobject]
        return []
