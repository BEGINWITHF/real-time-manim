"""A fill-bearing arc must emit fill geometry, not nothing.

Report #8: `ArcsAndCurves` had two elements that did not appear at all.

    pie   Sector(radius=0.95, angle=PI/2)   CE ink 2626 px   RTM ink 0
    ring  AnnularSector(0.4, 0.95, PI/2)    CE ink 2124 px   RTM ink 0

Class hierarchy (manim 0.21):  Sector -> AnnularSector -> Arc, so both reach
the `elif isinstance(mob, Arc)` dispatch branch and `_send_arc`, which has only
a *stroke* branch -- it never reads `fill_rgbas`.  Both are built with
`fill_opacity=1, stroke_width=0`, so

    _stroke_width(mob) = 0.0 * 0.01 * (h / 8) = 0.0

and `_stroke_polyline_with_progress(..., sw=0, ...)` submits nothing at all:

    probe (arc_probe.py, real dispatch, DLL calls captured)
      Sector       fill=1.0 stroke_a=1.0 sw=0.0  EMITTED: NOTHING
      AnnularSector fill=1.0 stroke_a=1.0 sw=0.0 EMITTED: NOTHING
      Arc (control) fill=0.0 stroke_a=1.0 sw=4.0 EMITTED: 64 x AddLine

The predicted missing area (shoelace 2561 / 2107 px) matches the measured
missing components (2626 / 2124 px).

The fix routes *fill-bearing* arcs to the generic point path
(`_send_vmobject`), which already handles fill and is what `_transforming`
and partial (`Create`) arcs use today.  Pure Python: captures the DLL calls,
no GPU, no ffmpeg, no DTW.
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
    from manim import AnnularSector, Arc, Sector
except Exception as e:  # pragma: no cover - import guard
    pytest.skip("manim/RTM unavailable: %s" % e, allow_module_level=True)


class _Recorder(object):
    """Records every DLL call by name; returns 0 like the real stub."""

    def __init__(self):
        self.calls = []

    def __getattr__(self, name):
        def _call(*args, **kwargs):
            self.calls.append((name, args))
            return 0
        return _call


def _capture(mob):
    """Send `mob` through the real dispatch; return {dll_call_name: count}."""
    renderer = vb.MLWindow(400, 200)
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
    return counts


FILL_ONLY = ("AddBezierPath", "AddPolygon")


def test_fill_only_sector_emits_fill_geometry():
    """Red before the fix: `_send_arc` has no fill branch at all.

    `_send_arc` only stroked, and `_stroke_width(0) == 0.0`, so the wedge
    manim filled (CE 2626 px) produced no primitive whatsoever.
    """
    counts = _capture(Sector(radius=0.95, angle=math.pi / 2))
    emitted = [k for k in counts if k in FILL_ONLY]
    assert emitted, (
        "a Sector is fill_opacity=1 / stroke_width=0, so it can only appear as "
        "fill geometry; nothing fill-like was emitted (all calls: %r) -- "
        "the element cannot appear on screen" % counts)


def test_fill_only_annular_sector_emits_fill_geometry():
    """Same defect for the parent class, measured at CE 2124 px vs RTM 0."""
    counts = _capture(
        AnnularSector(inner_radius=0.4, outer_radius=0.95, angle=math.pi / 2))
    emitted = [k for k in counts if k in FILL_ONLY]
    assert emitted, (
        "AnnularSector (fill_opacity=1, stroke_width=0) emitted no fill "
        "geometry; all calls: %r" % counts)


def test_stroked_arc_stays_on_the_arc_fast_path():
    """The fix must not route *every* arc down the generic path.

    A plain Arc has fill_opacity=0, so it keeps its dedicated `_send_arc`
    stroked rendering (this is the shape the scene's bridge / tangential arc /
    curved arrow all take, and they already match CE).
    """
    counts = _capture(Arc(angle=math.pi / 2))
    assert counts.get("AddBezierPath", 0) == 0, (
        "a fill-less Arc was routed to the point path: %r -- the fill-only "
        "fix must not change the stroke-only case" % counts)
    assert counts.get("AddLine", 0) > 0 or counts.get("AddLineStrip", 0) > 0, (
        "a plain Arc must still be stroked; nothing was emitted: %r" % counts)
