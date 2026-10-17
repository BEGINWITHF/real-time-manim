# -*- coding: utf-8 -*-
"""`TransformableLabel` morphs a label whose glyph count changes.

The wiki's `01-场景与相机/专用场景/05-线性变换场景-compose` sample ends with::

    v = self.add_vector([2, 1], color=YELLOW, animate=True)
    self.add_transformable_label(v, "w", transformation_name="L",
                                 label_scale_factor=0.8)
    self.apply_matrix([[0, -1], [1, 0]], run_time=1.4)

`add_transformable_label` records `target_text = "L(w)"`, so the following
`apply_matrix` has to morph a **1 glyph** label into a **4 glyph** one
(measured: 1 family / 128 points -> 4 families / 312 points).

ManimCE 0.21 cannot: its `Transform.get_all_families_zipped()` zips the three
families with ``strict=True`` (``manim/animation/transform.py:236-240``), so the
render dies in ``Transform.begin()`` with::

    ValueError: zip() argument 3 is longer than arguments 1-2

(relaxing ``strict`` only moves the failure to
``ValueError: operands could not be broadcast together with shapes (16,3)
(76,3)`` inside ``Transform.interpolate_submobject``).  That is why that clip
has no ManimCE twin.  RTM has its own ``Transform`` and re-families the points,
so the same source renders -- these tests pin that capability so it cannot
regress silently.

Pure Python: no window, no GPU, no images.
"""
import inspect
import os
import sys

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if REPO not in sys.path:
    sys.path.insert(0, REPO)

from manim import LinearTransformationScene, MathTex, YELLOW  # noqa: E402

from real_time_manim.animations import Transform as RtmTransform  # noqa: E402
from real_time_manim.record import scene_lifecycle  # noqa: E402


def _points(mob):
    return sum(len(m.points) for m in mob.family_members_with_points())


def test_rtm_transform_morphs_a_label_that_gains_glyphs():
    short = MathTex("w")
    long = MathTex("L(w)")
    assert len(short.family_members_with_points()) == 1
    assert len(long.family_members_with_points()) == 4
    assert _points(short) != _points(long), "the pair must differ in point count"

    anim = RtmTransform(short, long, run_time=1.0)
    anim.begin(0.0)
    for alpha in (0.0, 0.25, 0.5, 0.75, 1.0):
        anim.interpolate(alpha)
    anim.finish()

    # it lands exactly on the target: 4 glyphs, 312 points
    assert len(short.family_members_with_points()) == 4
    assert _points(short) == _points(long)


class _RunAnimations:
    """A `self.play` replacement that runs the animations, drawing nothing.

    RTM's own animations spell ``begin(t)`` while the bundled-manim ones
    (``Write`` ...) keep manim's no-argument ``begin()``; call whichever the
    object actually implements.
    """

    def __init__(self, steps=5):
        self.steps = steps

    @staticmethod
    def _begin(anim):
        if len(inspect.signature(anim.begin).parameters) >= 1:
            anim.begin(0.0)
        else:
            anim.begin()

    def play(self, *animations, **kwargs):
        for anim in animations:
            run_time = kwargs.get("run_time")
            if run_time is not None:
                anim.run_time = run_time
            self._begin(anim)
            for i in range(1, self.steps + 1):
                anim.interpolate(i / self.steps)
            anim.finish()


class _ComposeLike(LinearTransformationScene):
    """The compose sample without a window (vector + transformable label)."""

    def construct(self):
        self.play = _RunAnimations().play
        vector = self.add_vector([2, 1], color=YELLOW)
        self.label = self.add_transformable_label(
            vector, "w", transformation_name="L", label_scale_factor=0.8)
        self.before = len(self.label.family_members_with_points())
        self.apply_matrix([[0, -1], [1, 0]], run_time=0.2)
        self.after = len(self.label.family_members_with_points())


def test_apply_matrix_morphs_the_transformable_label():
    """Driving the scene is the part ManimCE 0.21 cannot do (it raises)."""
    scene = _ComposeLike()
    scene_lifecycle(scene)          # setup() then construct()

    label = scene.label
    assert label.target_text.startswith("L("), label.target_text
    assert scene.before >= 1, scene.before          # the "\vec{w}" label
    assert scene.after > scene.before, (
        "the label was never transformed: %d -> %d"
        % (scene.before, scene.after))
