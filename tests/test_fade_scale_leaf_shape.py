"""Regression: ``FadeIn``/``FadeOut`` ``scale=`` must actually scale a plain shape.

Report: wiki ``03-动画/通用`` ``assets/RTM output/02-play与wait参数.mp4``
-- "shift down被展示成了up".  The direction half was fixed earlier; what kept
that clip at the top of the issue table (mean 3.105 scaled / **2.802 at full
resolution**, worst in the whole list) was the *other* argument of the very
same call, ``FadeIn(ci, scale=0.5)``.

Root cause
----------
manim CE (``manim/animation/fading.py::_Fade._create_faded_mobject``) fades in
from ``mobject.copy().scale(scale)`` -- the whole family, including a plain
shape's own points -- then pointwise-interpolates back to full size.

RTM (``real_time_manim/animations/fade_in.py::begin`` / ``fade_out.py``) built
its snapshot list with::

    for fm in mob.family_members_with_points()
    if fm is not mob                       # <-- dropped the mobject itself

``family_members_with_points()`` of a leaf VMobject (Circle/Square/Dot/
Triangle) is exactly ``[mob]``, so the filter left an EMPTY list and ``scale=``
was silently ignored.  Only containers (Text/VGroup) have descendants, which
is why the bug never showed on text.

Measured (no GPU, both engines, ``rate_func=linear``)
----------------------------------------------------
``FadeIn(Circle(radius=0.68), scale=0.5)`` width at alpha 0/0.25/0.5/0.75/1:

    CE   0.6800  0.8500  1.0200  1.1900  1.3600
    RTM  1.3600  1.3600  1.3600  1.3600  1.3600   <-- scale ignored
    RTM  0.6800  0.8500  1.0200  1.1900  1.3600   <-- after the fix

with matching radius min/max/mean (0.4250/0.4397/0.4323 at alpha 0.25) and
point count (32) at every sampled alpha.

On the clip that mismatch was worth the entire residual: the circle region's
mean luma tracked ``alpha`` linearly in RTM (0.101 vs 0.104 predicted at
alpha 0.10) instead of CE's ``opacity * area`` curve
``alpha * (0.5 + 0.5*alpha)**2`` (0.283 measured vs 0.28 predicted at
alpha 0.5) -- a +7.07/255 per-pixel gap at mid-fade.
"""

import os
import sys

import pytest

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if REPO not in sys.path:
    sys.path.insert(0, REPO)

from real_time_manim import Circle, Square, VGroup  # noqa: E402
from real_time_manim.vulkan_bind import FadeIn, FadeOut  # noqa: E402

RUN = 1.6


def _linear(t):
    return t


def _widths(anim, mob, alphas=(0.0, 0.25, 0.5, 0.75, 1.0)):
    anim.begin(0.0)
    out = []
    for a in alphas:
        anim.interpolate(a * RUN)
        out.append(round(float(mob.width), 4))
    return out


def test_fade_in_scale_shrinks_a_leaf_shape_then_grows_it_back():
    """CE's numbers, to four decimals."""
    m = Circle(radius=0.68)
    anim = FadeIn(m, scale=0.5, run_time=RUN, rate_func=_linear)
    assert _widths(anim, m) == [0.6800, 0.8500, 1.0200, 1.1900, 1.3600]


def test_fade_out_scale_shrinks_a_leaf_shape():
    m = Circle(radius=0.68)
    anim = FadeOut(m, scale=0.5, run_time=RUN, rate_func=_linear)
    assert _widths(anim, m) == [1.3600, 1.1900, 1.0200, 0.8500, 0.6800]


def test_scale_leaves_the_points_the_right_shape():
    """Not just the width: the whole point cloud is a uniform scale of the end."""
    import numpy as np

    m = Circle(radius=0.68)
    anim = FadeIn(m, scale=0.5, run_time=RUN, rate_func=_linear)
    anim.begin(0.0)
    anim.interpolate(0.5 * RUN)
    pts = np.asarray(m.points, dtype=float)
    c = np.asarray(m.get_center(), dtype=float)
    r = np.linalg.norm(pts[:, :2] - c[:2], axis=1)
    assert (round(float(r.min()), 4), round(float(r.max()), 4),
            round(float(r.mean()), 4)) == (0.5100, 0.5276, 0.5188)


def test_container_behaviour_is_unchanged():
    """Text/VGroup only ever scaled their leaves; that must stay true."""
    g = VGroup(Square(side_length=0.6).shift([-0.5, 0, 0]),
               Circle(radius=0.3).shift([0.5, 0, 0]))
    before = [round(float(sub.width), 4) for sub in g.submobjects]
    w_full = float(g.width)                 # pristine width, before any begin()
    # a container is scaled about its centre exactly like a leaf: 0.5x .. 1.0x.
    # (_widths() issues the single begin() itself -- begin() snapshots the
    # geometry, so a second one would re-snapshot already-scaled points.)
    anim = FadeIn(g, scale=0.5, run_time=RUN, rate_func=_linear)
    assert _widths(anim, g) == [
        round(w_full * s, 4) for s in (0.5, 0.625, 0.75, 0.875, 1.0)]
    # at alpha 1 the fade has restored the pristine geometry exactly
    assert [round(float(sub.width), 4) for sub in g.submobjects] == before
    # the children are scaled about the GROUP centre, so their widths follow
    anim2 = FadeIn(g, scale=0.5, run_time=RUN, rate_func=_linear)
    anim2.begin(0.0)
    anim2.interpolate(0.0)
    kids = [round(float(sub.width), 4) for sub in g.submobjects]
    assert kids == [round(0.5 * w, 4) for w in before]


def test_default_scale_is_a_no_op():
    """``FadeIn(m)`` without ``scale`` must not touch the geometry at all."""
    m = Square(side_length=1.0)
    anim = FadeIn(m, run_time=RUN, rate_func=_linear)
    assert _widths(anim, m) == [1.0, 1.0, 1.0, 1.0, 1.0]


def test_explicit_scale_one_is_a_no_op():
    m = Square(side_length=1.0)
    anim = FadeIn(m, scale=1.0, run_time=RUN, rate_func=_linear)
    assert _widths(anim, m) == [1.0, 1.0, 1.0, 1.0, 1.0]


def test_scale_is_applied_about_the_mobjects_own_center():
    """A shifted shape must not drift while it is scaled."""
    import numpy as np

    m = Circle(radius=0.5).shift(np.array([2.0, 1.0, 0.0]))
    anim = FadeIn(m, scale=0.5, run_time=RUN, rate_func=_linear)
    anim.begin(0.0)
    for a in (0.0, 0.33, 0.66, 1.0):
        anim.interpolate(a * RUN)
        assert np.allclose(m.get_center(), [2.0, 1.0, 0.0], atol=1e-9)


def test_shift_still_works_together_with_scale():
    """The idx15 report is about ``shift``; it must keep working after the fix.

    manim CE (``fading.py::_Fade._create_faded_mobject``) shifts the STARTING
    copy by ``-shift`` (``direction_modifier = -1``), so the mobject begins at
    ``final - shift`` and travels BY ``shift`` into place: with ``shift=DOWN``
    it starts ABOVE and slides down.
    """
    import numpy as np

    m = Circle(radius=0.5)
    shift = np.array([0.0, -1.0, 0.0])
    anim = FadeIn(m, scale=0.5, shift=shift, run_time=RUN, rate_func=_linear)
    anim.begin(0.0)
    anim.interpolate(0.0)
    assert np.allclose(m.get_center(), -shift)      # starts at final - shift
    anim.interpolate(RUN)
    assert np.allclose(m.get_center(), [0.0, 0.0, 0.0])   # ends at final
