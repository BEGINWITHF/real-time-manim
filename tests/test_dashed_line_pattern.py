"""`_send_dashed_line` must reproduce Manim CE's dash pattern EXACTLY.

Manim CE does not tile ``dash_length`` along a DashedLine.  It picks

    num_dashes = max(2, ceil(length / dash_length * dashed_ratio))

(``DashedLine._calculate_num_dashes``) and then splits the WHOLE line so
that ``num_dashes`` dashes and ``num_dashes - 1`` gaps exactly fill it --
dash first, full dash flush at the end
(``DashedVMobject``, open curve):

    dash = dashed_ratio / num_dashes * length
    gap  = (1 - dashed_ratio) / (num_dashes - 1) * length

The sender used to tile ``dash = dash_length`` / ``gap = dash*(1-r)/r``
instead, which drifts against that pattern and runs off the end of the
line.  Measured on the demo suite's ``LinesAnglesAndVectors``
(DashedLine of length 2.2, ``dash_length=0.18``): CE draws 7 equal
0.157-long dashes with 0.183 gaps, flush at both ends; RTM drew six
0.18-long dashes plus a 0.04 stub (videos_ce_hq vs videos_rtm_hq
08_geometry, dashed region mean |diff| 8.4 -> 1.7 after the fix).

These tests need no Vulkan window: the native dll is stubbed and the
emitted ``AddDashedLine`` geometry is replayed through the exact tiling
``draw_dashed_line.c`` performs, then compared against the dash
submobjects CE itself builds.
"""
import math

import numpy as np
import pytest
from manim import DashedLine

import real_time_manim.vulkan_shapes as vs


class _StubDll:
    def __init__(self):
        self.calls = []

    def AddDashedLine(self, *args):
        self.calls.append(tuple(float(x) for x in args))
        return 0


class _StubRenderer(vs.ShapeMixin):
    """ShapeMixin over a recording dll -- no window, no GPU."""

    def __init__(self, h=1080):
        self.dll = _StubDll()
        self.win_h = h


def _tile(length, dash, gap):
    """Intervals ``draw_dashed_line.c`` emits along a line of ``length`` px.

    The native loop starts in the "drawing" state (a dash), alternates
    dash/gap, and clamps the final segment to the line end.
    """
    pos, drawing, spans = 0.0, True, []
    while pos < length:
        seg_len = dash if drawing else gap
        end_pos = min(pos + seg_len, length)
        if drawing and end_pos - pos > 1e-4:    # native skips dlen < 1e-4 px
            spans.append((pos, end_pos))
        pos, drawing = end_pos, not drawing
    return spans


def _ce_dash_spans(mob):
    """(start, end) distance-from-line-start of every dash CE builds."""
    start = np.asarray(mob.get_start(), dtype=float)
    return [(float(np.linalg.norm(np.asarray(ch.get_start(), dtype=float) - start)),
             float(np.linalg.norm(np.asarray(ch.get_end(), dtype=float) - start)))
            for ch in mob.submobjects]


def _emit(mob, h=1080, w=1920):
    r = _StubRenderer(h)
    r._send_dashed_line(mob, 1.0, w, h)
    assert r.dll.calls, "_send_dashed_line emitted nothing"
    call = r.dll.calls[0]
    x1, y1, x2, y2 = call[0], call[1], call[2], call[3]
    scale = h / 8.0                       # unzoomed frame: px per manim unit
    spans = _tile(math.hypot(x2 - x1, y2 - y1), call[8], call[9])
    return [(s / scale, e / scale) for s, e in spans]      # manim units


CASES = [
    # the demo-suite regression (08_geometry LinesAnglesAndVectors)
    ("scene line L=2.2 dash=0.18",
     dict(start=[-5.9, 0.1, 0], end=[-3.7, 0.1, 0], dash_length=0.18)),
    ("defaults L=2", dict(start=[-1, 0, 0], end=[1, 0, 0])),
    ("long line L=6", dict(start=[-3, 0, 0], end=[3, 0, 0])),
    # fewer than 2 dashes worth of length: CE clamps to 2 dashes
    ("short line L=0.3 dash=0.25",
     dict(start=[0, 0, 0], end=[0.3, 0, 0], dash_length=0.25)),
    ("ratio 0.1", dict(start=[-2, 0, 0], end=[2, 0, 0], dash_length=0.3,
                       dashed_ratio=0.1)),
    ("ratio 0.9", dict(start=[-2, 0, 0], end=[2, 0, 0], dash_length=0.3,
                       dashed_ratio=0.9)),
    ("diagonal", dict(start=[-1.5, -1, 0], end=[1.5, 1, 0], dash_length=0.18)),
]


@pytest.mark.parametrize("label,kwargs", CASES, ids=[c[0] for c in CASES])
def test_dash_pattern_matches_manim_ce(label, kwargs):
    mob = DashedLine(kwargs["start"], kwargs["end"],
                     **{k: v for k, v in kwargs.items()
                        if k not in ("start", "end")})
    rtm = _emit(mob)
    ce = _ce_dash_spans(mob)

    assert len(rtm) == len(ce), (
        "%s: CE draws %d dashes, RTM %d" % (label, len(ce), len(rtm)))
    for i, ((rs, re), (cs, ceend)) in enumerate(zip(rtm, ce)):
        assert rs == pytest.approx(cs, abs=5e-4), "%s: dash #%d start" % (label, i)
        assert re == pytest.approx(ceend, abs=5e-4), "%s: dash #%d end" % (label, i)


def test_line_ends_with_a_full_dash_not_a_stub():
    """The pattern that regressed on video: no clipped leftover dash.

    The old flat tiling overshot the CE period and left a 0.04 stub at the
    end of LinesAnglesAndVectors' 2.2-long line.
    """
    mob = DashedLine([-5.9, 0.1, 0], [-3.7, 0.1, 0], dash_length=0.18)
    spans = _emit(mob)
    length = 2.2
    assert spans[0][0] == pytest.approx(0.0, abs=5e-4)
    assert spans[-1][1] == pytest.approx(length, abs=5e-4)
    # every dash the same length (CE dashes are equal)
    lens = [e - s for s, e in spans]
    assert max(lens) - min(lens) < 5e-4
    assert min(lens) > 0.5 * np.mean(lens), "trailing stub detected"


def test_dash_pattern_scales_with_grow_but_keeps_its_dash_count():
    """GrowFromPoint only scales CE's dashes -- it must not re-count them.

    The pattern is fixed by the line's own length; `_grow_scale` stretches
    the drawn line, so the dash LENGTH halves with it while the COUNT stays.
    """
    mob = DashedLine([-1.6, 0, 0], [1.6, 0, 0], dash_length=0.18)
    full = _emit(mob)
    mob._grow_scale = 0.5
    mob._grow_point = mob.get_center()
    grown = _emit(mob)
    assert len(grown) == len(full)
    for (gs, ge), (fs, fe) in zip(grown, full):
        assert ge - gs == pytest.approx((fe - fs) * 0.5, abs=5e-4)
        assert gs == pytest.approx(fs * 0.5, abs=5e-4)


def test_partial_draw_windows_the_fixed_pattern():
    """`Create` clips the already-fixed pattern (CE clips its subcurves)."""
    mob = DashedLine([-1.6, 0, 0], [1.6, 0, 0], dash_length=0.18)
    full = _emit(mob)
    mob._vulkan_progress = 0.5
    partial = _emit(mob)
    # visible part starts identically and keeps the same dash sizes
    assert partial[0][0] == pytest.approx(full[0][0], abs=5e-4)
    assert partial[-1][1] == pytest.approx(3.2 * 0.5, abs=5e-4)
    lens = [e - s for s, e in partial[:-1]]
    full_lens = [e - s for s, e in full]
    assert all(any(abs(l - fl) < 5e-4 for fl in full_lens) for l in lens)


def test_zero_dash_length_does_not_hang_the_native_tile_loop():
    """CE divides by dash_length (its constructor raises on 0), so a 0 can
    only reach the sender through a mobject whose attribute was overwritten.
    The native loop would spin forever on a zero-length step: floor it."""
    mob = DashedLine([-1, 0, 0], [1, 0, 0], dash_length=0.1)
    mob.dash_length = 0.0
    spans = _emit(mob)
    assert spans, "degenerate dash_length emitted nothing sane"
    assert all(e - s > 0 for s, e in spans)
