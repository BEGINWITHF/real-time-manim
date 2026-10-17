"""Regression test: ``Create(DashedLine)`` must not re-space the dash pattern.

Report: wiki ``04-图形与文本`` ``assets/RTM output/02-线与箭头-lines.mp4``
-- "虚线在动画播放完后被拉伸了一下".

Root cause (``real_time_manim/render/shapes/points.py::_send_dashed_line``):
the dash pattern is derived from ``mob.get_start()`` / ``mob.get_end()``.
``Create`` is a ``ShowPartial`` with ``lag_ratio=1``, so ``begin()`` already
runs ``pointwise_become_partial`` over the 22 dashes: the LAST dash collapses
onto its own start point, and ``get_end()`` therefore reports
``0.4 - dash_length = 0.25`` instead of ``0.4`` for the whole animation (it
only grows back during the final 4.5 % of it).  Re-counting the dashes against
that short line re-spaced the pattern every frame: measured on
``02-线与箭头-lines.mp4`` the 6-unit line (810 px, 22 dashes, 38 px pitch once
finished) drew its dashes on a 36-37 px pitch for as long as the Create ran
(f120: dash #11 at x=474 against ManimCE's x=484; f137: last dash at x=865
against CE's x=902) and the pattern snapped outward on the frame the
animation ended -- the reported "stretch".  ManimCE never moves a dash:
``DashedVMobject`` splits the line once, at construction, and ``Create`` only
reveals them.

Fix: ``hook_channels._write_progress`` snapshots the pre-cut extent from
``anim.starting_mobject`` (``Animation.begin`` copies the mobject *before* the
first ``interpolate(0)``, so that copy is still whole) and the sender uses it
while the uncut START still matches.  The reveal itself stays in
``_vulkan_progress``, which is what cuts the drawn segment.

Headless: drives the sender against a stub DLL -- no GPU, no window, no image.
"""

import os
import sys

import pytest

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if REPO not in sys.path:
    sys.path.insert(0, REPO)

from manim import Create, DashedLine, TEAL  # noqa: E402

from real_time_manim.render.hooks import install_hooks  # noqa: E402
from real_time_manim.render.shapes import ShapeMixin  # noqa: E402

W, H = 480, 270


class _Recorder:
    """Stands in for the native DLL and keeps every submitted call."""

    def __init__(self):
        self.calls = []

    def __getattr__(self, name):
        def _call(*args, **kwargs):
            self.calls.append((name, args))
            return 0
        return _call


class _Probe(ShapeMixin):
    """The sender assembly MLWindow inherits, without a window."""

    def __init__(self):
        self.dll = _Recorder()


def _line():
    # verbatim from wiki 04-图形与文本 / 02-线与箭头.py
    return DashedLine([-5.6, -0.7, 0], [0.4, -0.7, 0], dash_length=0.15,
                      dashed_ratio=0.55, color=TEAL, stroke_width=5)


def _submit(alpha, allow_empty=False):
    """Run ``Create(dl)`` to ``alpha`` and return the AddDashedLine args."""
    probe = _Probe()
    dl = _line()
    if alpha is not None:
        anim = Create(dl, run_time=1.0)
        anim.begin()                       # cuts the dashes (interpolate(0))
        install_hooks(anim)                # snapshots the uncut extent
        anim.interpolate(alpha)
    probe._send_dashed_line(dl, 1.0, W, H)
    dashes = [args for name, args in probe.dll.calls if name == "AddDashedLine"]
    if not dashes:
        if allow_empty:
            return None
        raise AssertionError("nothing was submitted for the dashed line")
    return max(dashes, key=lambda a: a[4])   # widest stroke layer = the core


def test_pattern_during_create_equals_the_finished_pattern():
    """dl + gap must not depend on how much of the line is revealed yet.

    Before the fix the mid-animation run used a 5.85-unit line (the collapsed
    last dash) against the finished 6.0-unit one, i.e. dash 0.1463 vs 0.15 and
    gap 0.1254 vs 0.1286 units -- a 36-37 px pitch snapping to 38 px when the
    animation ended.
    """
    done = _submit(1.0)
    mid = _submit(0.6)
    dash_done, gap_done = float(done[8]), float(done[9])
    dash_mid, gap_mid = float(mid[8]), float(mid[9])
    assert dash_mid == pytest.approx(dash_done, rel=2e-3), (
        "dash length changed mid-Create: %.4f px at alpha 0.6 against "
        "%.4f px finished -- the pattern was re-counted from the CUT line"
        % (dash_mid, dash_done))
    assert gap_mid == pytest.approx(gap_done, rel=2e-3), (
        "gap length changed mid-Create: %.4f px at alpha 0.6 against "
        "%.4f px finished" % (gap_mid, gap_done))
    assert dash_mid + gap_mid == pytest.approx(dash_done + gap_done, rel=2e-3)


def test_reveal_tip_follows_the_full_line():
    """The drawn segment stops where ManimCE's reveal stops, on the FULL line.

    Without the snapshot the tip was ``0.6 * 5.85`` units instead of
    ``0.6 * 6.0`` -- the whole animation drew short and jumped at the end.
    """
    done = _submit(1.0)
    mid = _submit(0.6)
    full_span = float(done[2]) - float(done[0])
    mid_span = float(mid[2]) - float(mid[0])
    assert mid_span == pytest.approx(0.6 * full_span, rel=1e-3), (
        "reveal tip %.2f px, expected 0.6 * %.2f = %.2f px"
        % (mid_span, full_span, 0.6 * full_span))
    assert float(mid[0]) == pytest.approx(float(done[0]), abs=1e-3)


def test_an_untouched_dashed_line_keeps_its_pattern():
    """Non-regression: with no animation the sender must be unchanged."""
    bare = _submit(None)
    done = _submit(1.0)
    assert float(bare[8]) == pytest.approx(float(done[8]), rel=1e-6)
    assert float(bare[9]) == pytest.approx(float(done[9]), rel=1e-6)
    assert float(bare[2]) - float(bare[0]) == pytest.approx(
        float(done[2]) - float(done[0]), abs=1e-3)


def test_nothing_is_drawn_before_the_reveal_starts():
    """alpha 0 -> nothing is submitted at all (the line is not pre-drawn)."""
    start = _submit(0.0, allow_empty=True)
    full = _submit(1.0)
    assert start is None, (
        "a segment was submitted at alpha 0: span %.2f px of the finished "
        "%.2f px" % (float(start[2]) - float(start[0]),
                     float(full[2]) - float(full[0])))
