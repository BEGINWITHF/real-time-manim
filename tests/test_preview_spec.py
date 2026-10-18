# -*- coding: utf-8 -*-
"""The frame-preview input grammar and bar layout (no window / no GPU).

``real_time_manim.preview`` opens a window and docks a native input bar under
it, so it cannot be exercised end to end here.  Everything that decides *what*
a typed line means, and *where* the bar goes, is pure and pinned below.
"""
import os
import sys

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if REPO not in sys.path:
    sys.path.insert(0, REPO)

from real_time_manim.preview import (  # noqa: E402
    FramePreview,
    bar_geometry,
    clamp_frame,
    frame_of_time,
    parse_spec,
    time_of_frame,
)

FPS = 60
N = 600          # frames 0..599


def spec(text, current=100):
    return parse_spec(text, FPS, current, N)


# ---------------------------------------------------------------------------
# units
# ---------------------------------------------------------------------------

def test_bare_integer_is_a_frame_number():
    assert spec("123") == ("seek", 123)
    assert spec("  0  ") == ("seek", 0)
    assert spec("123f") == ("seek", 123)


def test_bare_float_is_seconds():
    assert spec("1.5") == ("seek", 90)
    assert spec("2s") == ("seek", 120)
    assert spec("0.25s") == ("seek", 15)


def test_time_and_frame_helpers_round_trip():
    assert time_of_frame(150, 60) == 2.5
    assert frame_of_time(2.5, 60) == 150


def test_relative_steps_are_frames():
    assert spec("+1") == ("seek", 101)
    assert spec("-10") == ("seek", 90)
    assert spec("+0.5") == ("seek", 101)       # rounds to a frame


def test_seeks_are_clamped_to_the_scene():
    assert spec("-999") == ("seek", 0)
    assert spec("+9999") == ("seek", N - 1)
    assert spec("99999") == ("seek", N - 1)
    assert clamp_frame(-5, N) == 0
    assert clamp_frame(10 ** 9, N) == N - 1


# ---------------------------------------------------------------------------
# commands
# ---------------------------------------------------------------------------

def test_commands_and_noops():
    assert spec("").kind == "noop"
    assert spec("   ").kind == "noop"
    for word in ("q", "quit", "exit", "Q"):
        assert spec(word).kind == "quit", word
    assert spec("s").kind == "save"
    assert spec("save").kind == "save"
    assert spec("p").kind == "play"
    assert spec("?").kind == "help"
    assert spec("help").kind == "help"


def test_nonsense_is_an_error_not_a_crash():
    cmd = spec("frame twelve")
    assert cmd.kind == "error"
    assert "cannot read" in cmd.value
    cmd = spec("+abc")
    assert cmd.kind == "error"
    assert "+1" in cmd.value


# ---------------------------------------------------------------------------
# bar layout
# ---------------------------------------------------------------------------

def test_bar_is_docked_under_the_window_edges():
    win = (100, 200, 1380, 1000)              # left, top, right, bottom
    x, y, w, h = bar_geometry(win, 38, gap=4)
    assert (x, y) == (100, 1004)              # same left, just below the window
    assert w == 1280                          # same width
    assert h == 38


def test_bar_keeps_a_usable_minimum_width():
    x, y, w, h = bar_geometry((0, 0, 200, 150), 38)
    assert w >= 360
    assert y == 154


def test_bar_follows_a_negative_origin_display():
    """A second monitor to the left has negative coordinates -- must pass through."""
    x, y, w, h = bar_geometry((-1920, 0, -640, 1080), 38)
    assert x == -1920
    assert y == 1084
    assert w == 1280


# ---------------------------------------------------------------------------
# which control the caller asked for
# ---------------------------------------------------------------------------

def test_controls_accepts_the_obvious_spellings():
    from real_time_manim.preview import normalize_controls

    for word in ("input", "box", "text", "edit", "INPUT", " text ", "Edit"):
        assert normalize_controls(word) == "input", word
    for word in ("slider", "bar", "progress", "progressbar", "scrub",
                 "Slider", "progress-bar", "progress_bar"):
        assert normalize_controls(word) == "slider", word
    assert normalize_controls(None) == "input"
    assert normalize_controls("") == "input"


def test_controls_rejects_nonsense():
    import pytest

    from real_time_manim.preview import normalize_controls
    with pytest.raises(ValueError):
        normalize_controls("dial")


def test_position_parsing():
    from real_time_manim.preview import parse_position

    assert parse_position("100,200") == (100, 200)
    assert parse_position(" 100 , 200 ") == (100, 200)
    assert parse_position("100;200") == (100, 200)
    assert parse_position("-1920,0") == (-1920, 0)
    assert parse_position("(100, 80)") == (100, 80)      # PowerShell arrays
    assert parse_position("[100, 80]") == (100, 80)
    assert parse_position((100, 80)) == (100, 80)
    assert parse_position("") is None
    assert parse_position(None) is None


def test_position_rejects_nonsense():
    import pytest

    from real_time_manim.preview import parse_position
    for bad in ("100", "a,b", "1,2,3"):
        with pytest.raises(ValueError):
            parse_position(bad)


# ---------------------------------------------------------------------------
# module surface
# ---------------------------------------------------------------------------

def test_preview_is_exported_lazily():
    import real_time_manim as rtm
    assert rtm.FramePreview is FramePreview               # PEP 562 lazy export
    assert rtm.FrameServer.__name__ == "FrameServer"


def test_no_bar_falls_back_to_the_terminal():
    """`use_bar=True` off Windows (or with --no-bar) must not need win32."""
    preview = FramePreview.__new__(FramePreview)          # no scene/GPU
    preview.use_bar = False
    assert preview.use_bar is False


# ---------------------------------------------------------------------------
# the queue protocol the input widgets speak
# ---------------------------------------------------------------------------

def _bare_preview(n_frames=600, current=0):
    """A FramePreview with no scene and no window: just the input plumbing."""
    import queue

    pv = FramePreview.__new__(FramePreview)
    pv.fps = 60
    pv.n_frames = n_frames
    pv.current = current
    pv.running = True
    pv.use_bar = False
    pv._bar = None
    pv._queue = queue.Queue()
    pv.saved = []
    pv.verbose = False
    pv._print = lambda *a: None
    pv._log = lambda *a: None
    return pv


def test_input_callbacks_only_enqueue():
    pv = _bare_preview()
    submit, save, quit_ = pv._input_callbacks()
    submit("120")
    save()
    quit_()
    assert [pv._queue.get_nowait() for _ in range(3)] == [
        ("text", "120"), ("save", None), ("quit", None)]


class _StubWindow:
    def __init__(self):
        self.ticks = 0

    def tick(self):
        self.ticks += 1
        return True


class _StubServer:
    def __init__(self, window):
        self.window = window
        self.rendered = []

    def render_frame(self, t):
        self.rendered.append(t)


def test_loop_speaks_the_queue_protocol_and_stops_on_quit():
    pv = _bare_preview()
    pv.window = _StubWindow()
    pv.server = _StubServer(pv.window)
    pv._queue.put_nowait(("text", "120"))     # seek 120 -> t=2.0
    pv._queue.put_nowait(("text", "?"))       # help: prints, no draw
    pv._queue.put_nowait(("quit", None))
    pv._loop()

    assert pv.current == 120
    assert pv.server.rendered == [2.0], "only the seek should draw"


def test_a_scrubber_drag_draws_only_the_newest_frame():
    """Dragging queues one seek per pixel; only the last one may be drawn."""
    pv = _bare_preview()
    pv.window = _StubWindow()
    pv.server = _StubServer(pv.window)
    for frame in (1, 2, 3, 4, 5):                 # a drag: 5 events
        pv._queue.put_nowait(("seek", frame))
    pv._queue.put_nowait(("quit", None))
    pv._loop()

    assert pv.server.rendered == [5 / 60.0], pv.server.rendered
    assert pv.current == 5


def test_a_save_queued_behind_a_drag_still_runs():
    pv = _bare_preview()
    pv.window = _StubWindow()
    pv.server = _StubServer(pv.window)
    saves = []
    pv._save = lambda: saves.append(pv.current)
    pv._queue.put_nowait(("seek", 2))
    pv._queue.put_nowait(("seek", 3))
    pv._queue.put_nowait(("save", None))
    pv._queue.put_nowait(("quit", None))
    pv._loop()

    assert pv.current == 3
    assert saves == [3], "the save must see the newest frame, and still run"
