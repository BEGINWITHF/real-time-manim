"""Regression tests: a play-level ``run_time=`` must stretch the children, and
``FadeTransformPieces`` must ease exactly once.

Report: wiki ``03-动画/变换/05-淡出淡入式变换`` -- "一处圆和三角没消失同时速率错误".

Two separate defects produced it.

**1. Duration -- ``animation_group.AnimationGroup.interpolate``.**
manim normalises with ``rate_func(alpha) * self.max_end_time`` and its own
comment says why the distinction matters::

    Note, if the run_time of AnimationGroup has been set to something other
    than its default, these times might not correspond to actual times ...
    Instead they'd be a rescaled version. But that's okay!

RTM multiplied by ``self.run_time`` instead, so the play-level override
(``Scene.play``/``MLWindow.play`` write ``run_time`` onto the GROUP only) re-scaled
the children's clock against themselves.  ``FadeTransformPieces`` is two 1.0 s
children under a group whose ``run_time`` ``win.play`` sets to 1.5 s, so the
crossfade finished at ``smooth(t/1.5) * 1.5 == 1.0`` -- t = 0.87 s -- and the
remaining 0.63 s of the play froze.  Measured on the rendered clip: RTM steps
0.000 for frames 376..392 while CE is still stepping 0.40..0.52.

**2. Easing -- ``fade_transform.FadeTransformPieces``.**
manim's own ``FadeTransformPieces`` is a SINGLE ``FadeTransform``, so ``rate_func``
is applied once.  RTM's is an ``AnimationGroup`` of per-piece ``FadeTransform``s
and each child eases itself, so a play-level ``rate_func=smooth`` landed twice:
source opacity 0.976 where CE has 0.846 at the halfway frame, 0.024 where CE
has 0.154 two thirds through.  The group now owns the single easing (its
default is manim's ``smooth``) and the children pass it through linearly;
``stretch`` / ``dim_to_match`` are forwarded to the pieces, where they live.

Pure Python: no window, no GPU, no images.
"""
import os
import sys

import numpy as np
import pytest

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if REPO not in sys.path:
    sys.path.insert(0, REPO)

from manim import (  # noqa: E402
    RIGHT,
    Circle,
    Scene,
    Square,
    Triangle,
    VGroup,
    smooth,
)

from real_time_manim.animations.animation_group import AnimationGroup  # noqa: E402
from real_time_manim.animations.fade_out import FadeOut  # noqa: E402
from real_time_manim.rate_functions import _linear  # noqa: E402
from real_time_manim.state import get_anim_opacity  # noqa: E402
from real_time_manim.timeline import Timeline  # noqa: E402


class _StubWindow:
    dll = None

    def sync(self, scene):
        return None

    def tick(self):
        return True

    def request_readback(self):
        return None


def _pair():
    """The page's ``grp`` / ``grp2`` (square+circle -> circle+triangle)."""
    grp = VGroup(Square(side_length=1.0, color="BLUE"),
                 Circle(radius=0.5, color="GREEN").shift(RIGHT * 1.6))
    grp2 = VGroup(Circle(radius=0.5, color="RED"),
                  Triangle(color="YELLOW").scale(0.55).shift(RIGHT * 1.6))
    return grp, grp2


def _rtm_curve(frames=96, **ftp_kwargs):
    scene = Scene()
    grp, grp2 = _pair()
    scene.add(grp)
    from real_time_manim.vulkan_bind import FadeTransformPieces
    anim = FadeTransformPieces(grp, grp2, **ftp_kwargs)
    anim.run_time = 1.5                       # what win.play(..., run_time=1.5)
    anim.rate_func = smooth                   # and win.play(..., rate_func=...)
    tl = Timeline(_StubWindow(), scene)
    tl.add(anim, 0.0)
    tl.finalize()
    src = grp.submobjects[0]
    out = []
    for k in range(frames):
        tl.render_at(k / 60.0)
        out.append(float(get_anim_opacity(src)))
    return anim, out


def _manim_curve(frames=96, **ftp_kwargs):
    import manim

    scene = Scene()
    grp, grp2 = _pair()
    scene.add(grp)
    anim = manim.FadeTransformPieces(grp, grp2, **ftp_kwargs)
    anim.run_time = 1.5
    anim.rate_func = smooth
    scene.animations = [anim]
    anim._setup_scene(scene)
    anim.begin()
    scene.last_t = 0
    src = grp.submobjects[0]
    out = []
    for k in range(frames):
        scene.update_to_time(k / 60.0)
        best = 0.0
        for fm in src.family_members_with_points():
            for name in ("fill_rgbas", "stroke_rgbas"):
                arr = getattr(fm, name, None)
                if arr is not None and len(arr):
                    best = max(best, float(np.asarray(arr)[:, 3].max()))
        out.append(best)
    anim.clean_up_from_scene(scene)
    return out


def test_group_run_time_override_no_longer_finishes_early():
    """Two 1.0 s children under ``run_time=1.5`` must still be moving at 0.87 s."""
    scene = Scene()
    a, b = Square(), Circle()
    scene.add(a)
    group = AnimationGroup(FadeOut(a), FadeOut(b))
    assert group.run_time == pytest.approx(1.0)
    group.run_time = 1.5                      # the play-level override
    group.rate_func = smooth                  # ...and the play-level easing
    tl = Timeline(_StubWindow(), scene)
    tl.add(group, 0.0)
    tl.finalize()

    opacities = []
    for k in range(96):
        tl.render_at(k / 60.0)
        opacities.append(float(get_anim_opacity(a)))
    # frame 52 is t = 0.867 s -- where the old code had already frozen solid
    # (group_time = smooth(t/1.5)*1.5 hit the children's 1.0 s end at 0.87 s)
    assert opacities[52] > 0.05, (
        "the group froze at t=0.87s even though play gave it 1.5s")
    # it must only bottom out when the play ends, and never turn around
    assert opacities[90] == pytest.approx(opacities[-1])
    assert (np.diff(opacities) <= 1e-9).all()


def test_fade_transform_pieces_uses_the_whole_play():
    """The reported clip: still crossfading at 1.2 s, done at 1.5 s."""
    _, curve = _rtm_curve()
    assert curve[72] > 0.001, (
        "FadeTransformPieces finished long before the 1.5 s play ended")
    assert curve[-1] == pytest.approx(0.0, abs=1e-6)


def test_fade_transform_pieces_matches_manims_easing():
    """Same curve as manim's own class, sampled every 3 frames."""
    _, ours = _rtm_curve()
    theirs = _manim_curve()
    assert len(ours) == len(theirs)
    worst = float(np.max(np.abs(np.array(ours) - np.array(theirs))))
    assert worst < 2e-3, (
        f"RTM's crossfade easing deviates from manim's by {worst:.4f} -- the "
        "group's rate_func is being applied twice (or not at all)")


def test_fade_transform_pieces_eases_once_without_a_play_override():
    """No ``rate_func=`` at all: the group's own default must still be smooth."""
    scene = Scene()
    grp, grp2 = _pair()
    scene.add(grp)
    from real_time_manim.vulkan_bind import FadeTransformPieces
    anim = FadeTransformPieces(grp, grp2)
    assert anim.rate_func(0.5) == pytest.approx(0.5, abs=1e-6)  # smooth, not wild
    assert anim.animations[0].rate_func is _linear, (
        "each piece must pass the group's progress through uneased")
    tl = Timeline(_StubWindow(), scene)
    tl.add(anim, 0.0)
    tl.finalize()
    src = grp.submobjects[0]
    curve = []
    for k in range(61):
        tl.render_at(k / 60.0)
        curve.append(float(get_anim_opacity(src)))
    # A linear ramp would sit at 0.75 / 0.25 at the quarter marks; manim's
    # `smooth` (which the group must own, since its children are linear now)
    # sits near 0.90 / 0.10 there.
    assert curve[15] > 0.8, curve[15]
    assert curve[45] < 0.2, curve[45]


def test_fade_transform_pieces_forwards_stretch_and_dim_to_match():
    """The documented parameters belong to the pieces, not to the group."""
    from real_time_manim.vulkan_bind import FadeTransformPieces

    scene = Scene()
    grp, grp2 = _pair()
    anim = FadeTransformPieces(grp, grp2, stretch=False, dim_to_match=0)
    for child in anim.animations:
        assert child.stretch is False, (
            "stretch=False never reached the per-piece FadeTransforms")
        assert child.dim_to_match == 0
