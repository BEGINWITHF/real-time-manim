"""A LabeledArrow's label must be drawn, and its tip drawn exactly once.

Report R10-2: `BracesAndLabels` "the last row's arrow is missing its label".
The last row is

    flow = LabeledArrow("flow", start=3.4*LEFT + 3.0*DOWN,
                        end=0.4*LEFT + 3.0*DOWN, label_position=0.5, ...)

Measured, last frame, 854x480:

    CE  region x[280..350] y[398..442]  330 px in 7 components  (the glyphs)
    RTM same region                     284 px in 1 component   (the shaft,
                                                                y418..421 only)

Why nothing drew it (label_probe.py, real dispatch, DLL calls captured):

    type = LabeledArrow   isinstance(Arrow) = True
    submobjects = [0] ArrowTriangleFilledTip (the tip), [1] Label
    emitted for the WHOLE LabeledArrow: {'AddLine': 2, 'AddBezierPath': 1}
    emitted for the LABEL alone:        {'AddPolygon': 1, 'AddBezierPath': 4,
                                         'AddLine': 4}

`vulkan_bind.py` routes `isinstance(mob, Arrow)` to `_send_arrow` (shaft + tip)
and then deliberately skips the generic submobject walk for Arrow -- the
comment says "Arrow is already fully handled by _send_arrow".  True for `tip`,
false for a `Label`: it was never walked, so it was never drawn.

Pure Python: captures the DLL calls, no GPU, no ffmpeg, no DTW.
"""
import math
import os
import sys

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if REPO not in sys.path:
    sys.path.insert(0, REPO)

import pytest

try:
    import real_time_manim.vulkan_bind as vb
    from manim import LEFT, DOWN, LabeledArrow
except Exception as e:  # pragma: no cover - import guard
    pytest.skip("manim/RTM unavailable: %s" % e, allow_module_level=True)


def _scene_arrow():
    """The scene's exact mobject (scenes/05_mobject_classes.py, `flow`)."""
    return LabeledArrow(
        "flow",
        start=3.4 * LEFT + 3.0 * DOWN,
        end=0.4 * LEFT + 3.0 * DOWN,
        label_position=0.5,
        label_config={"font_size": 22},
    )


class _Recorder(object):
    def __init__(self):
        self.calls = []

    def __getattr__(self, name):
        def _call(*args, **kwargs):
            self.calls.append((name, args))
            return 0
        return _call


def _capture(mob):
    renderer = vb.MLWindow(854, 480)
    rec = _Recorder()
    real_dll = renderer.dll
    renderer.dll = rec
    try:
        renderer._send(mob)
    finally:
        renderer.dll = real_dll
        renderer.close()
    counts = {}
    for name, _args in rec.calls:
        counts[name] = counts.get(name, 0) + 1
    return counts, rec.calls


def _points(calls):
    """Screen-space points of every primitive submitted (documented layouts)."""
    pts = []
    for name, args in calls:
        if name == "AddLine":
            pts.append((float(args[0]), float(args[1])))
            pts.append((float(args[2]), float(args[3])))
        elif name == "AddLineStrip":
            flat = list(args[0]); n = int(args[2])
            st = len(flat) // n if n else 0
            for i in range(n):
                pts.append((float(flat[st * i]), float(flat[st * i + 1])))
        elif name == "AddBezierPath":
            flat = list(args[0]); n = int(args[1])
            st = len(flat) // n if n else 0
            for i in range(n):
                pts.append((float(flat[st * i]), float(flat[st * i + 1])))
        elif name == "AddPolygon":
            raw = args[10]; n = int(args[9])
            for i in range(n):
                pts.append((float(raw[2 * i]), float(raw[2 * i + 1])))
    return pts


def test_labeled_arrow_draws_its_label():
    """Red before the fix: the label produced no primitive at all.

    Ask the label alone where it wants to be, then check the whole arrow's
    submission actually covers it.  Mechanism independent -- whatever the fix
    draws, it has to land on the glyphs.
    """
    arrow = _scene_arrow()
    lab = arrow.label
    lab_pts = _points(_capture(lab)[1])
    assert lab_pts, "the label itself renders nothing: %r" % _capture(lab)[0]

    all_pts = _points(_capture(arrow)[1])
    assert all_pts, "the arrow itself renders nothing"
    hit = 0
    for p in lab_pts:
        if min(math.hypot(p[0] - q[0], p[1] - q[1]) for q in all_pts) <= 3.0:
            hit += 1
    frac = hit / float(len(lab_pts))
    assert frac >= 0.6, (
        "LabeledArrow drew only %d of %d label points (%.0f %%): the Label "
        "submobject is never walked because Arrow is excluded from the family "
        "walk and `_send_arrow` only draws shaft + tip"
        % (hit, len(lab_pts), 100.0 * frac))


def test_labeled_arrow_tip_is_drawn_exactly_once():
    """The fix must walk everything BUT `tip` -- `_send_arrow` already drew it.

    Bezier primitives: 1 for the tip (the shaft is AddLine) + however many the
    label needs on its own.  Walking the tip as well would double it; skipping
    the label would leave the count at 1.
    """
    arrow = _scene_arrow()
    whole, _ = _capture(arrow)
    label_only, _ = _capture(arrow.label)
    label_count = label_only.get("AddBezierPath", 0)
    expected = 1 + label_count
    got = whole.get("AddBezierPath", 0)
    assert got == expected, (
        "AddBezierPath %d, expected %d = 1 tip + %d label"
        % (got, expected, label_count))


def test_plain_arrow_tip_is_not_double_drawn():
    """Non-regression for report #9: a plain Arrow still draws tip + shaft once.

    `ArrowTriangleFilledTip` is a Polygram, so `_send(tip)` alone goes down the
    polygon path and says nothing about what `_send_arrow` submits -- the count
    itself is the invariant: shaft (2 AddLine) + tip (1 AddBezierPath), before
    and after the label walk.
    """
    from manim import RIGHT, Arrow
    plain = Arrow(start=LEFT, end=RIGHT)
    whole, _ = _capture(plain)
    assert whole.get("AddBezierPath", 0) == 1, (
        "a plain Arrow emits %d bezier paths, expected exactly 1 (the tip) -- "
        "the label walk must skip `mob.tip`, which `_send_arrow` already drew"
        % whole.get("AddBezierPath", 0))
    assert whole.get("AddLine", 0) == 2, (
        "a plain Arrow emits %d AddLine, expected 2 (the shaft)"
        % whole.get("AddLine", 0))
