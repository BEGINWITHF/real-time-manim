"""A fade must reach the screen exactly ONCE.

manim's ``FadeIn``/``FadeOut`` are ``Transform``s whose starting copy sits at
opacity 0, so their ``interpolate`` writes the eased value straight into
``fill_rgbas``/``stroke_rgbas`` -- and CE composites the mobject with that
value, once.

RTM multiplies two things into every primitive it submits: the registry
(``a = parent_alpha * get_anim_opacity(mob)``, ``vulkan_bind``:_send_impl) and
the mobject's own array alpha (``alpha * fo`` in ``_send_polygon``,
``stroke_alpha = min(1, so * a)`` in ``_send_vmobject``, the RGB scaled by
``so`` in ``_send_line``).  Registering the animated value in the registry as
well applied the fade **twice**.

Measured end to end on a one-square ``FadeIn`` scene, peak luma per frame::

        frame      16    20    24    28    32    36
    CE         20.00 39.00 67.00 105.0 149.0 187.0
    RTM (old)   1.01  5.03 17.05  43.05 86.12 136.2     <- 0.084 vs 0.084**2
    RTM (new)  21.02 40.02 68.02 105.0 148.0 186.0

Every ``FadeIn`` in the suite was that far behind through the ramp -- the shape
stayed nearly invisible for a third of the animation and then raced to catch
up.

The registry is kept for the one shape whose drawn primitive does not follow
its own arrays: a ``DashedLine``, submitted as a single ``AddDashedLine`` from
the container's start/end while CE strokes the faded dash children
(``test_render_hooks.py::test_a_fading_dashed_line_keeps_the_registry``).

The probes here drive a real ``MLWindow`` against a stub DLL and read the
alpha back off the submitted calls.  Run with::

    python -X utf8 -m pytest tests/test_fade_registry.py -q
"""

import os
import sys

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if REPO not in sys.path:
    sys.path.insert(0, REPO)

import pytest

try:
    import real_time_manim.vulkan_bind as vb
    from manim import (Arc, Circle, Dot, FadeIn, FadeOut, Line, Scene, Square,
                       VGroup)
    from real_time_manim.render_hooks import install_hooks
    from real_time_manim.state import get_anim_opacity
except Exception as e:                                  # pragma: no cover
    pytest.skip("manim/RTM unavailable: %s" % e, allow_module_level=True)


# --------------------------------------------------------------------------- #
# fixture / helpers
# --------------------------------------------------------------------------- #

class _Recorder(object):
    """Stands in for the native DLL and keeps every submitted call."""

    def __init__(self):
        self.calls = []

    def __getattr__(self, name):
        def _call(*args, **kwargs):
            self.calls.append((name, args))
            return 0
        return _call


@pytest.fixture(scope="module")
def window():
    try:
        w = vb.MLWindow(1920, 1080, hidden=True)
    except Exception as e:                              # pragma: no cover
        pytest.skip("Vulkan window unavailable: %s" % e)
    yield w
    try:
        w.close()
    except Exception:
        pass


def prepared(anim, alpha=0.0):
    """begin() + hooks, the way Timeline.finalize does it."""
    anim.begin()
    install_hooks(anim)
    anim.interpolate(alpha)
    return anim


def submitted(window, mobject):
    """Sync a one-mobject scene against a stub DLL; return the calls."""
    scene = Scene()
    scene.add(mobject)
    rec = _Recorder()
    real_dll = window.dll
    window.dll = rec
    try:
        window.sync(scene)
    finally:
        window.dll = real_dll
    return rec.calls


# The alpha each primitive carries.  Every one of these is the alpha native
# blends with, so it is the number CE's compositing has to match.
ALPHA_AT = {
    "AddPolygon": 12,     # AddPolygon(sx, sy, rgb, pad, n, verts, emitted, a, closed)
    "AddRect": 13,
    "AddCircle": 11,
    "AddEllipse": 13,
    "AddLineStrip": 7,
    "AddLine": 8,
    "AddDashedLine": 10,
    "AddBezierPath": 13,
}


def submitted_alphas(calls, primitive):
    idx = ALPHA_AT[primitive]
    return [float(args[idx]) for name, args in calls if name == primitive]


def array_alpha(mob, kind="fill"):
    arr = getattr(mob, "%s_rgbas" % kind, None)
    if arr is None or not len(arr):
        return None
    return float(arr[:, 3].max())


# --------------------------------------------------------------------------- #
# the registry must not repeat what the arrays already carry
# --------------------------------------------------------------------------- #

SHAPES = {
    "Arc": lambda: Arc(radius=1.5, stroke_width=6),
    "Circle": lambda: Circle(fill_opacity=1, stroke_width=4),
    "Dot": lambda: Dot(radius=0.3),
    "Line": lambda: Line([-2, 0, 0], [2, 0, 0], stroke_width=6),
    "Square": lambda: Square(fill_opacity=1, stroke_width=4),
}


@pytest.mark.parametrize("kind", ["FadeIn", "FadeOut"])
@pytest.mark.parametrize("shape", sorted(SHAPES))
def test_the_registry_never_repeats_the_arrays(kind, shape):
    """`a * fo` in the senders already carries the fade, so the registry is 1.0.

    Pure Python: this is the invariant the GPU probes below then measure on
    the wire.
    """
    import manim

    mob = SHAPES[shape]()
    prepared(getattr(manim, kind)(mob, run_time=1.0), 0.4)

    faded = [v for v in (array_alpha(mob, "fill"), array_alpha(mob, "stroke"))
             if v is not None and 0.0 < v < 1.0]
    assert faded, "fixture: manim's %s did not fade %s's arrays" % (kind, shape)
    assert get_anim_opacity(mob) == pytest.approx(1.0), (
        "%s(%s) registered %.3f on top of its arrays' %s -- the senders fold "
        "the array alpha into the primitive too, so the fade applies twice"
        % (kind, shape, get_anim_opacity(mob),
           ", ".join("%.3f" % v for v in faded)))


def test_a_mobject_keeps_no_stale_fade_after_the_animation():
    """The registry is cleared even at the last frame, where the arrays are opaque."""
    mob = Square(fill_opacity=1, stroke_width=4)
    anim = prepared(FadeIn(mob, run_time=1.0), 0.4)
    assert get_anim_opacity(mob) == pytest.approx(1.0)
    anim.interpolate(1.0)
    assert get_anim_opacity(mob) == pytest.approx(1.0)


# --------------------------------------------------------------------------- #
# what actually reaches native
# --------------------------------------------------------------------------- #

def test_a_faded_fill_is_submitted_at_the_arrays_alpha(window):
    """AddPolygon's alpha must be the eased value, not its square."""
    sq = Square(fill_opacity=1, stroke_width=0)
    prepared(FadeIn(sq, run_time=1.0), 0.4)

    want = array_alpha(sq, "fill")
    assert want is not None and 0.0 < want < 1.0
    fills = submitted_alphas(submitted(window, sq), "AddPolygon")
    assert fills, "the faded Square submitted no fill"
    assert max(fills) == pytest.approx(want, rel=0.05), (
        "fill alpha %.4f where CE composites %.4f -- the fade is applied %s"
        % (max(fills), want, "twice" if max(fills) < want else "too strongly"))


def test_a_fade_out_fill_is_submitted_at_the_arrays_alpha(window):
    sq = Square(fill_opacity=1, stroke_width=0)
    prepared(FadeOut(sq, run_time=1.0), 0.4)

    want = array_alpha(sq, "fill")
    assert want is not None and 0.0 < want < 1.0
    fills = submitted_alphas(submitted(window, sq), "AddPolygon")
    assert fills, "the fading-out Square submitted no fill"
    assert max(fills) == pytest.approx(want, rel=0.05), (
        "fill alpha %.4f where CE composites %.4f" % (max(fills), want))


def test_a_faded_circle_is_submitted_at_the_arrays_alpha(window):
    ci = Circle(fill_opacity=1, stroke_width=0)
    prepared(FadeIn(ci, run_time=1.0), 0.4)

    want = array_alpha(ci, "fill")
    circles = submitted_alphas(submitted(window, ci), "AddCircle")
    assert circles, "the faded Circle submitted no disc"
    assert max(circles) == pytest.approx(want, rel=0.05)


def test_a_faded_group_fades_its_children_once(window):
    """A container registers nothing, so the child's arrays are the only source."""
    group = VGroup(Square(fill_opacity=1, stroke_width=0))
    prepared(FadeIn(group, run_time=1.0), 0.4)

    child = group[0]
    want = array_alpha(child, "fill")
    assert want is not None and 0.0 < want < 1.0
    fills = submitted_alphas(submitted(window, child), "AddPolygon")
    assert fills, "the faded group's Square submitted no fill"
    assert max(fills) == pytest.approx(want, rel=0.05), (
        "a child of a faded group came out at %.4f against CE's %.4f"
        % (max(fills), want))
