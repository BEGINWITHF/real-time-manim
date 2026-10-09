"""A ``Create`` over a group must leave *every* child fully drawn.

``_send_impl``'s container branch splits the container's own
``_vulkan_progress`` across its children -- a lagged ``Create`` draws child
*i* over ``[i, i + 1)`` -- by stamping ``_vulkan_progress`` onto each child
for the leaf sender to window its stroke with.

Two things were missing, and together they left the last child permanently
short:

1. ``_run_timeline`` only called ``finish()`` (manim's ``interpolate(1)``) for
   manim's animations.  RTM's own ``Create`` takes an *absolute* time, and
   ``ce_frame_count`` is arange's exclusive end -- so the container's progress
   stopped at 0.9973 and never reached 1.0.
2. Nothing ever cleared the per-child stamps.  Once the container hit 1.0 the
   split stopped updating them, so every later frame re-painted the last child
   at its leftover fraction.

The split multiplies the shortfall by the number of children: the final square
of ``Create(VGroup(n))`` drew ``n * 0.27%`` less than its outline -- 8% short
at n = 30 -- and a ``Write`` never closed its last letter.

Both halves are fixed at the point CE finishes an animation, after the frame
loop: evaluate the terminal state, then drop the stamps the split wrote (only
while they still hold what the split wrote, so an ``Uncreate`` of a single
child in the same ``play()`` survives).

Run with::

    python -X utf8 -m pytest tests/test_create_completes.py -q
"""

import os
import sys

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if REPO not in sys.path:
    sys.path.insert(0, REPO)

import math

import pytest

try:
    import real_time_manim.vulkan_bind as vb
    from manim import BLUE, RIGHT, Scene, Square, VGroup
    from real_time_manim.vulkan_bind import Create
except Exception as e:                                  # pragma: no cover
    pytest.skip("manim/RTM unavailable: %s" % e, allow_module_level=True)


class _Recorder(object):
    """Stands in for the native DLL and keeps every submitted call."""

    def __init__(self):
        self.calls = []

    def __getattr__(self, name):
        def _call(*args, **kwargs):
            self.calls.append((name, args))
            return 0
        return _call


N_CHILDREN = 4
WIN_W, WIN_H = 1920, 1080
# world units across the window's height (manim's default frame height)
UNITS_TALL = 8.0
SPACING = 3.0                    # far enough apart to bucket strokes by x


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


def _group(n=N_CHILDREN):
    return VGroup(*[Square(side_length=1.0, color=BLUE)
                    .shift((i * SPACING - (n - 1) * SPACING / 2) * RIGHT)
                    for i in range(n)])


def _scene_with(vg):
    scene = Scene()
    scene.setup()
    scene.add(vg)
    return scene


def _frames(rec, n):
    """Per-frame total stroke length, bucketed onto the n children by x."""
    centres = _centres(n)
    out, cur = [], None
    for name, args in rec.calls:
        if name == 'ClearShapes':
            if cur is not None:
                out.append(cur)
            cur = [0.0] * n
            continue
        if name != 'AddLine' or cur is None:
            continue
        x0, y0, x1, y1 = (float(args[0]), float(args[1]),
                          float(args[2]), float(args[3]))
        cx = (x0 + x1) / 2.0
        j = min(range(n), key=lambda k: abs(cx - centres[k]))
        cur[j] += math.hypot(x1 - x0, y1 - y0)
    if cur is not None:
        out.append(cur)
    return out


WIN_W, WIN_H = 1920, 1080


def _centres(n):
    """Screen-x of each child, matching the group built by ``_group``."""
    scale = WIN_H / UNITS_TALL
    return [((i * SPACING - (n - 1) * SPACING / 2) * scale + WIN_W / 2)
            for i in range(n)]


# --------------------------------------------------------------------------- #
# terminal state
# --------------------------------------------------------------------------- #

def test_container_reaches_full_progress_after_the_play(window):
    """Fix half 1: an RTM animation is stepped to its exact end of segment."""
    vg = _group()
    scene = _scene_with(vg)
    real = window.dll
    window.dll = _Recorder()
    try:
        window.scene = scene
        window.play(Create(vg), run_time=0.3)
    finally:
        window.dll = real
    assert vg._vulkan_progress == pytest.approx(1.0), (
        "the container stopped at %r -- ce_frame_count is arange's exclusive "
        "end, so _run_timeline has to evaluate the terminal state itself"
        % vg._vulkan_progress)


def test_split_stamps_are_released_after_the_play(window):
    """Fix half 2: nothing may keep the fraction the split wrote."""
    vg = _group()
    scene = _scene_with(vg)
    real = window.dll
    window.dll = _Recorder()
    try:
        window.scene = scene
        window.play(Create(vg), run_time=0.3)
        for sub in vg.submobjects:
            assert '_vsplit_progress' not in sub.__dict__, (
                "split stamp left on %r" % sub)
            assert '_vulkan_progress' not in sub.__dict__, (
                "stale split progress %r left on %r -- the next frame would "
                "repaint this child short of its outline"
                % (sub._vulkan_progress, sub))
    finally:
        window.dll = real


def test_release_split_keeps_progress_an_animation_wrote():
    """A stamp is only dropped while it still holds the split's own value."""
    from real_time_manim.vulkan_bind import release_split

    vg = _group()

    # the split's own stamp goes away, and takes the stale progress with it
    child = vg.submobjects[0]
    child._vulkan_progress = 0.25
    child._vsplit_progress = 0.25
    release_split(vg)
    assert '_vsplit_progress' not in child.__dict__
    assert '_vulkan_progress' not in child.__dict__

    # ...but a child another animation has moved on is left alone -- this is
    # what keeps Create(vg) followed by Create(vg[0]) working
    other = vg.submobjects[1]
    other._vsplit_progress = 0.5
    other._vulkan_progress = 0.1            # an Uncreate of this child only
    release_split(vg)
    assert other._vulkan_progress == pytest.approx(0.1)
    assert '_vsplit_progress' not in other.__dict__


# --------------------------------------------------------------------------- #
# what actually reaches the GPU
# --------------------------------------------------------------------------- #

def test_last_child_paints_a_full_outline_after_the_play(window):
    """The regression, end to end: every child's stroke must be complete."""
    n = N_CHILDREN
    vg = _group(n)
    scene = _scene_with(vg)
    rec = _Recorder()
    real = window.dll
    window.dll = rec
    try:
        window.scene = scene
        window.play(Create(vg), run_time=0.3)
        rec.calls.clear()
        window.sync(scene)                 # one frame, after the play
    finally:
        window.dll = real

    frames = _frames(rec, n)
    assert frames, "the post-play sync emitted no AddLine calls"
    lengths = frames[-1]
    full = max(lengths)
    assert full > 0.0, "nothing was drawn: %r" % (lengths,)
    for i, length in enumerate(lengths):
        assert length == pytest.approx(full, rel=1e-6), (
            "child %d drew %.1f of %.1f (%.1f%%) after the play finished -- "
            "the container's split left it at a stale fraction"
            % (i, length, full, 100.0 * length / full))


def test_children_still_draw_progressively_during_the_play(window):
    """Guard: the fix must not flatten the lag that makes Create a reveal."""
    n = N_CHILDREN
    vg = _group(n)
    scene = _scene_with(vg)
    rec = _Recorder()
    real = window.dll
    window.dll = rec
    try:
        window.scene = scene
        window.play(Create(vg), run_time=0.3)
    finally:
        window.dll = real

    frames = [f for f in _frames(rec, n) if max(f) > 0.0]
    assert len(frames) >= 2, "expected several painted frames"
    last_child = [f[-1] for f in frames]
    assert min(last_child) < max(last_child), (
        "the last child was drawn at %r in every frame -- the per-child split "
        "is not lagging at all" % (last_child,))
