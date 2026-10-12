"""A pivot-rotated ``Line`` must draw, not raise.

``_write_rotate`` stamps ``_rotation_about_point`` on EVERY pivot rotation --
manim's ``Rotate``/``Rotating`` and RTM's own rotate classes alike -- but
``_send_line`` only converted that pivot inside its ``else`` branch, so the
screen-space ``rot`` applied at the end of the method read an unbound local::

    Rotate(Line([-2, 0, 0], [2, 0, 0]), PI / 2, about_point=ORIGIN)
    -> UnboundLocalError: scx

``rot`` is 0 for manim's own ``Rotate`` (manim turns the points themselves and
only the pivot is registered), so the missing piece is a pivot conversion --
and the line has to come out exactly on the mobject's own endpoints.

Run with::

    python -X utf8 -m pytest tests/test_pivot_rotated_line.py -q
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
    from manim import Line, ORIGIN, PI, Rotate
    from real_time_manim.vulkan_util import manim_to_screen
except Exception as e:                                  # pragma: no cover
    pytest.skip("manim/RTM unavailable: %s" % e, allow_module_level=True)

W, H = 1920, 1080


class _Recorder(object):
    def __init__(self):
        self.calls = []

    def __getattr__(self, name):
        def _call(*args, **kwargs):
            self.calls.append((name, args))
            return 0
        return _call


@pytest.fixture(scope="module")
def renderer():
    try:
        r = vb.MLWindow(W, H, hidden=True)
    except Exception as e:                              # pragma: no cover
        pytest.skip("Vulkan window unavailable: %s" % e)
    yield r
    try:
        r.close()
    except Exception:
        pass


def _capture(renderer, mob):
    rec = _Recorder()
    real = renderer.dll
    renderer.dll = rec
    try:
        renderer._send(mob)
    finally:
        renderer.dll = real
    return rec.calls


def _add_lines(calls):
    out = []
    for name, a in calls:
        if name == "AddLine":
            out.append((float(a[0]), float(a[1]), float(a[2]), float(a[3])))
    return out


def test_a_pivot_rotated_line_submits_its_own_endpoints(renderer):
    """rot == 0 (manim's Rotate): the endpoints are the mobject's, unrotated.

    `_send_line`'s pivot branch used to leave `scx`/`scy` undefined, and the
    `_rotate_point` calls at the end of the method read them whatever `rot` was
    -- so the no-op rotation manim's own `Rotate` asks for still raised.

    Note: with a non-zero `rot` this method hands the line to `_send_vmobject`
    instead (the pivot pre-rotation moves the chord away from the control
    points, which is exactly what its "warped path" check looks for), and that
    path turns about the mobject's centre, not the pivot.  That is the legacy
    `real_time_manim.animations.rotate.Rotate`'s combination and is untouched
    here; manim-native `Rotate`/`Rotating` never set `rot`.
    """
    mob = Line([-2, -1, 0], [2, 1, 0], stroke_width=6)
    mob._rotation_about_point = list(ORIGIN)
    lines = _add_lines(_capture(renderer, mob))
    assert lines, "the pivot-rotated Line submitted nothing -- it must not raise"

    start = manim_to_screen(-2.0, -1.0, W, H, 0.0)
    end = manim_to_screen(2.0, 1.0, W, H, 0.0)
    for x1, y1, x2, y2 in lines:
        assert (x1, y1) == pytest.approx(start, abs=0.5), (x1, y1, start)
        assert (x2, y2) == pytest.approx(end, abs=0.5), (x2, y2, end)


def test_a_real_rotate_line_still_draws(renderer):
    """End to end: manim's `Rotate` over a Line goes through the hooks.

    This is the shape that used to raise `UnboundLocalError: scx` on the very
    first frame of the render.
    """
    from real_time_manim.render_hooks import install_hooks

    mob = Line([-2, -1, 0], [2, 1, 0], stroke_width=6)
    anim = Rotate(mob, PI / 2, about_point=list(ORIGIN), run_time=1.0)
    anim.begin()
    install_hooks(anim)
    anim.interpolate(0.5)
    lines = _add_lines(_capture(renderer, mob))
    assert lines, "Rotate(Line) submitted no stroke at alpha 0.5"
