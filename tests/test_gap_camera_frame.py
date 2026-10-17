"""Gap tests for the camera/frame work items A28 + A29 (wiki 01-场景与相机).

A28 -- "写入 ``config.frame_x_radius`` / ``config.frame_y_radius`` 后曲线图形不跟直线图形
一起缩放" (wiki ``01-场景与相机/配置/02-画幅坐标.md`` 样例「改写画幅」、
``配置/assets/README.md`` 对比结论).

Root cause (two different notions of "how tall is the frame"):

* POSITIONS -- a Square's points, a Circle's centre, every flattened curve
  vertex -- go through ``manim_to_screen`` -> ``camera_state.screen_scale(w, h)``
  = ``w / config.frame_width``.
* SIZES -- a Circle's native radius, a Dot's radius, a stroke width -- go
  through ``h / StrokeMixin._visible_frame_height()``.  With no camera frame
  that used to be the HARDCODED 8.0, so it ignored a ``config`` override while
  the position path followed it: halving the frame doubled the Square (its
  *size* rides its points) but left the Circle/Dot at half the size.

``StrokeMixin._visible_frame_height`` now falls back to ``config.frame_height``
(still 8.0 by default, so a 1920x1080 default render is byte-identical).  The
tests below pin that invariant end to end, at the level the dispatch actually
uses:

* straight lines: ``_send_square`` (quad rebuild, ``render/shapes/primitives.py``)
  and ``_send_line`` (endpoints, ``render/shapes/arrow.py``);
* curves: ``_send_circle`` (native disc, ``primitives.py``), ``_send_dot``
  (``points.py``) and ``_send_arc`` (bezier flattening, ``paths.py``).

A29 -- ``self.camera.frame`` 是辅助对象还是场景内容 (wiki
``01-场景与相机/相机/02-MovingCamera.md`` 表格 ``default_frame_stroke_*`` 行、
``相机/assets/README.md`` 已知不一致清单).  ``MLWindow.sync`` drops the frame
unconditionally (``window/core.py`` lines ~479-482, "the camera frame is a
helper mobject, not scene content"), so even an EXPLICITLY added
``self.camera.frame`` never reaches the shape senders, while Manim CE draws it.
The skip point lives in ``window/core.py`` (owned by another work item), so the
desired behaviour is pinned here as a non-strict xfail; the companion test
records the safety property that makes the skip removable: a DEFAULT frame
(stroke width 0, fill opacity 0) emits no draw calls at all, so every existing
``MovingCameraScene`` render stays pixel-identical once the skip is gone.

Pure Python for A28 (fake DLL, no GPU); the two A29 tests need a real window
``sync`` and skip when Vulkan is unavailable.
"""
import os
import sys
from contextlib import contextmanager

import pytest

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if REPO not in sys.path:
    sys.path.insert(0, REPO)

try:
    from manim import (
        LEFT, RIGHT, WHITE, Arc, Circle, Dot, Line, MovingCameraScene,
        Square, config,
    )
    import real_time_manim.camera_state as camera_state
    import real_time_manim.vulkan_bind as vb
    from real_time_manim.camera_state import screen_scale
    from real_time_manim.render.shapes import ShapeMixin
except Exception as e:                                  # pragma: no cover
    pytest.skip("manim/RTM unavailable: %s" % e, allow_module_level=True)


W, H = 1920, 1080            # the only output format MLWindow supports
HALF_HEIGHT = 4.0            # frame_y_radius 2.0 -> frame_height 4.0
HALF_WIDTH = HALF_HEIGHT * 16 / 9

# The wiki sample's literal numbers (frame_x_radius=3.555, frame_y_radius=2.0).
# 7.11 / 4.0 is 16:9 up to 0.016 %, so straight and curve scales may differ by
# that much; the bug was a factor of TWO, not 0.016 %.
WIKI_X_RADIUS, WIKI_Y_RADIUS = 3.555, 2.0

_FRAME_KEYS = (
    "frame_x_radius", "frame_y_radius", "frame_width", "frame_height",
)


@contextmanager
def frame_radii(x_radius=None, y_radius=None):
    """Write ``config.frame_*_radius`` for the block, then restore everything."""
    saved = {k: getattr(config, k) for k in _FRAME_KEYS}
    try:
        if x_radius is not None:
            config.frame_x_radius = x_radius
        if y_radius is not None:
            config.frame_y_radius = y_radius
        yield
    finally:
        for k, v in saved.items():
            setattr(config, k, v)
        camera_state.set_viewport(None)


class _FakeDll:
    """Records every draw call instead of issuing it."""

    def __init__(self):
        self.calls = []

    def __getattr__(self, name):
        def _record(*args, **kwargs):
            self.calls.append((name, args))
            return 0
        return _record


class _Sender(ShapeMixin):
    """A ShapeMixin host with no window behind it (pure coordinate tests)."""

    win_w, win_h = W, H

    def __init__(self):
        self.dll = _FakeDll()

    @staticmethod
    def _dbg_emit(*args, **kwargs):                     # pragma: no cover
        pass


def _coords(args):
    """A ctypes point list handed to AddLineStrip as a plain python list."""
    return list(args[0])


def _extent(calls):
    """(width, height) in pixels of everything a sender emitted, or None."""
    xs, ys = [], []
    for name, a in calls:
        if name == "AddCircle":
            xs += [a[0] - a[2], a[0] + a[2]]
            ys += [a[1] - a[2], a[1] + a[2]]
        elif name == "AddRect":
            xs += [a[0] - a[2], a[0] + a[2]]
            ys += [a[1] - a[3], a[1] + a[3]]
        elif name == "AddLine":
            xs += [a[0], a[2]]
            ys += [a[1], a[3]]
        elif name == "AddLineStrip":
            pts = _coords(a)[: a[2] * 2]
            xs += pts[0::2]
            ys += pts[1::2]
        elif name == "AddPolygon":
            pts = list(a[10])[: a[9] * 2]
            xs += pts[0::2]
            ys += pts[1::2]
    if not xs:
        return None
    return max(xs) - min(xs), max(ys) - min(ys)


def _send(kind, sender):
    """Emit one mobject of ``kind`` through the sender the dispatch uses."""
    if kind == "square":
        sender._send_square(Square(side_length=1.6), 1.0, W, H, 0.0, None)
    elif kind == "circle":
        sender._send_circle(Circle(radius=0.8), 1.0, W, H, 0.0, None)
    elif kind == "dot":
        sender._send_dot(Dot(radius=0.1), 1.0, W, H)
    elif kind == "arc":                                 # curve via paths.py
        sender._send_arc(Arc(radius=0.8), 1.0, W, H, 0.0, None)
    elif kind == "line":                                # straight via arrow.py
        sender._send_line(Line(LEFT * 2, RIGHT * 2), 1.0, W, H, 0.0, None)
    else:                                               # pragma: no cover
        raise AssertionError(kind)
    return _extent(sender.dll.calls)


# ---------------------------------------------------------------------------
# A28 -- curve and straight must scale with a config.frame_*_radius write
# ---------------------------------------------------------------------------

def test_default_frame_keeps_the_pre_override_baseline():
    """Default 1920x1080: sizes convert with frame height 8, exactly as before.

    This is the "两者行为不变" anchor every other A28 assertion is a ratio of.
    """
    camera_state.set_viewport(None)
    assert config.frame_height == 8.0
    per_unit = H / 8.0                                 # 135 px per manim unit
    assert _send("square", _Sender())[0] == pytest.approx(1.6 * per_unit, abs=1e-9)
    assert _send("circle", _Sender())[0] == pytest.approx(1.6 * per_unit, abs=1e-9)
    assert _send("dot", _Sender())[0] == pytest.approx(0.2 * per_unit, abs=1e-9)


def test_wiki_override_scales_square_circle_and_dot_together():
    """The wiki repro (3.555 / 2.0): all three grow ~2x, none stays behind.

    Before the fix the Square followed ``config.frame_width`` while the
    Circle/Dot radius sat on the hardcoded 8-unit frame -- the circle came out
    exactly half the square, which is the video evidence in
    ``02-画幅坐标-frame_override.mp4``.
    """
    camera_state.set_viewport(None)
    base = {k: _send(k, _Sender()) for k in ("square", "circle", "dot")}
    with frame_radii(WIKI_X_RADIUS, WIKI_Y_RADIUS):
        over = {k: _send(k, _Sender()) for k in ("square", "circle", "dot")}
    for kind in base:
        scale = over[kind][0] / base[kind][0]
        assert 1.998 < scale < 2.002, (
            "%s did not follow the frame override: %.4fx instead of ~2x "
            "(default extent %s, override extent %s)"
            % (kind, scale, base[kind], over[kind]))
    sq = over["square"][0] / base["square"][0]
    circ = over["circle"][0] / base["circle"][0]
    assert abs(sq - circ) / circ < 0.001, (
        "curve and straight diverged under the override: square %.4fx vs "
        "circle %.4fx (the A28 bug is a factor of two; the residual must stay "
        "below the wiki's own 0.016 %% aspect rounding)" % (sq, circ))


def test_exact_16_9_override_puts_sizes_on_the_position_scale():
    """One mapping for positions AND sizes when the override is exact 16:9.

    Positions: ``screen_scale(w, h)`` = ``w / config.frame_width``.  Sizes:
    ``h / _visible_frame_height()`` = ``h / config.frame_height``.  With an
    exact 16:9 pair the two must agree to the bit -- that is what makes a
    Square and a Circle scale identically no matter which sender draws them.
    """
    camera_state.set_viewport(None)
    with frame_radii(HALF_WIDTH / 2.0, HALF_HEIGHT / 2.0):
        pos = screen_scale(W, H)
        size = H / ShapeMixin._visible_frame_height()
    assert pos == pytest.approx(2 * 135.0, rel=1e-9)
    assert size == pytest.approx(2 * 135.0, rel=1e-9)
    assert pos == pytest.approx(size, rel=1e-9), (pos, size)


def test_flattened_curve_and_straight_endpoints_scale_together():
    """The second conversion path: bezier flattening (paths.py) vs endpoints.

    ``_send_arc`` rebuilds its polyline vertex by vertex through
    ``manim_to_screen`` while ``_send_line`` projects only its endpoints --
    both are "curve/straight" coordinate paths that must respond to the
    override the same way the native-size senders do.
    """
    camera_state.set_viewport(None)
    base_arc = _send("arc", _Sender())
    base_line = _send("line", _Sender())
    assert base_arc is not None and base_line is not None
    with frame_radii(HALF_WIDTH / 2.0, HALF_HEIGHT / 2.0):
        over_arc = _send("arc", _Sender())
        over_line = _send("line", _Sender())
    arc_scale = over_arc[0] / base_arc[0]
    line_scale = over_line[0] / base_line[0]
    assert arc_scale == pytest.approx(2.0, rel=1e-9), (arc_scale, over_arc, base_arc)
    assert line_scale == pytest.approx(2.0, rel=1e-9), (line_scale, over_line, base_line)


def test_dispatch_scales_square_circle_and_dot_together(renderer, clean_viewport):
    """End to end through the dispatch -- the wiki's exact repro.

    Uses the module-scoped ``renderer`` window (defined in the A29 section
    below) because the routing decision itself lives in ``window/paint.py``.

    ``_send_impl`` routes a straight-edged ``Square`` through ``_send_polygon``
    (every vertex projected by ``manim_to_screen``, i.e. the
    ``config.frame_width`` source) but a ``Circle`` through ``_send_circle``
    (native radius, i.e. the ``config.frame_height`` source) and a ``Dot``
    through ``_send_dot``.  Both sources must answer the same
    ``frame_*_radius`` write with the same ~2x, or the video shows the circle
    at half the square (``02-画幅坐标-frame_override.mp4``).
    """
    camera_state.set_viewport(None)

    def extents():
        out = {}
        for kind, mob in (("square", Square(side_length=1.6)),
                          ("circle", Circle(radius=0.8)),
                          ("dot", Dot(radius=0.1))):
            with _record(renderer.dll) as calls:
                renderer._send(mob, 0.0, parent_alpha=1.0)
            out[kind] = _extent(calls)
            assert out[kind] is not None, "%s emitted nothing" % kind
        return out

    base = extents()
    with frame_radii(WIKI_X_RADIUS, WIKI_Y_RADIUS):
        over = extents()
    scales = {k: over[k][0] / base[k][0] for k in base}
    for kind, scale in scales.items():
        assert 1.998 < scale < 2.002, (
            "dispatch: %s did not follow the frame override (%.4fx): %s -> %s"
            % (kind, scale, base[kind], over[kind]))
    assert max(scales.values()) - min(scales.values()) < 0.001, (
        "dispatch: curve and straight scaled differently: %r" % scales)


@contextmanager
def _record(dll):
    """Collect ``(name, args)`` for every native draw call in the block."""
    names = ("AddRect", "AddPolygon", "AddLine", "AddLineStrip", "AddCircle",
             "AddPoint", "AddImageQuad")
    calls = []
    saved = {}
    try:
        for name in names:
            saved[name] = getattr(dll, name, None)
            if saved[name] is None:
                continue

            def _mk(n):
                def _f(*a, **k):
                    calls.append((n, a))
                    return 0
                return _f

            setattr(dll, name, _mk(name))
        yield calls
    finally:
        for name, fn in saved.items():
            if fn is not None:
                setattr(dll, name, fn)


# ---------------------------------------------------------------------------
# A29 -- an explicitly added MovingCamera.frame must reach the draw pipeline
# ---------------------------------------------------------------------------

@pytest.fixture(scope="module")
def renderer():
    try:
        r = vb.MLWindow(W, H)
    except Exception as e:                              # pragma: no cover
        pytest.skip("Vulkan window unavailable: %s" % e)
    yield r
    try:
        r.close()
    except Exception:                                   # pragma: no cover
        pass
    camera_state.set_viewport(None)


@pytest.fixture
def clean_viewport():
    """sync() publishes a viewport globally; do not leak it into other tests."""
    camera_state.set_viewport(None)
    yield
    camera_state.set_viewport(None)


def _scene_with_added_frame(stroke_width):
    scene = MovingCameraScene()
    frame = scene.camera.frame
    if stroke_width:
        frame.set_stroke(WHITE, stroke_width)
    scene.add(frame)
    assert frame in scene.mobjects
    return scene, frame


def test_default_camera_frame_emits_no_draw_calls(renderer, clean_viewport):
    """A default frame is invisible, so NOT drawing it cannot change a frame.

    This is the safety property behind the A29 recommendation: ``sync`` drops
    ``camera.frame`` because it is a helper, and every stock MovingCameraScene
    (stroke width 0, fill opacity 0) would emit nothing even if the skip were
    removed -- so removing it cannot disturb any existing render.
    """
    scene, frame = _scene_with_added_frame(stroke_width=0)
    with _record(renderer.dll) as direct:
        renderer._send(frame, 0.0, parent_alpha=1.0)
    with _record(renderer.dll) as synced:
        renderer.sync(scene)
    assert not direct, "a default (stroke width 0) frame emitted draw calls"
    assert not synced


def test_explicitly_added_camera_frame_is_drawn(renderer, clean_viewport):
    """``self.camera.frame`` added to the scene gets drawn (parity with CE).

    Repro from the wiki (``相机/assets/README.md``): stroke the frame, add it,
    and CE paints the rectangle.  RTM used to drop ``camera.frame`` in
    ``MLWindow.sync`` (``window/core.py``) as a "helper mobject"; that skip is
    removed, so an explicitly added, visible frame now reaches the shape
    senders like any other root.
    """
    scene, _frame = _scene_with_added_frame(stroke_width=2)
    with _record(renderer.dll) as calls:
        renderer.sync(scene)
    assert calls, "sync() drew nothing for an explicitly added, visible frame"
