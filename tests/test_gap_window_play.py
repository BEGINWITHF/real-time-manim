"""Gap tests for the RTM play / scene surface: A6, A7, A27, A31, A33, A34.

Report pages (RTM-Wiki):

* **A6** -- ``win.play(..., subcaption=, subcaption_duration=,
  subcaption_offset=)`` used to vanish into ``**kwargs``.  RTM has no file
  writer, so the cue is now collected *in memory on the window* (start =
  the cursor position where the play began + offset, duration = what the play
  actually took) and written out as ``.srt`` by ``export_srt`` -- automatically
  at record end through ``audio_track.apply_sounds``, which ``record._run``
  calls for every recording.
* **A7** -- ``Scene.add_updater`` registered a scene-level updater that no
  driver ever walked (the wiki red square stood still).  ``_drive_mobject_updaters``
  now walks ``scene.updaters`` after every mobject updater; asserted here
  *through* ``win.play`` rather than on the driver alone.
* **A27** -- ``.animate(lag_ratio=...)``: nothing in ``play.py`` drops the
  keyword (manim's own ``_AnimationBuilder.build()`` ``setattr``-s it onto the
  built animation); it is inert because only ``AnimationGroup`` reads
  ``lag_ratio``.  manim CE does exactly the same, so the fix point is not this
  session's files.
* **A31** -- ``run_time=0`` must raise manim's friendly ``ValueError`` from
  ``win.play`` itself (both the live and the schedule branch).
* **A33** -- ``Scene.add_sound(**kwargs)``: the keywords RTM's mix implements
  (``gain_to_background``) are passed through; anything else is named in a
  warning instead of being dropped in silence.
* **A34** -- unknown play-level keywords (``lag_ratio=`` ...) print a warning
  naming them instead of disappearing.

Stubs only: no DLL, no GPU.  The timeline-mode tests render at most ~0.3 s of
frames through a window whose ``sync``/``tick`` do nothing, so they stay fast.
"""
import inspect
import os
import sys

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if REPO not in sys.path:
    sys.path.insert(0, REPO)

import pytest

from manim import (
    FadeIn,
    RIGHT,
    Scene,
    Square,
    Wait as ManimWait,
)

from real_time_manim.window import play as play_mod
from real_time_manim.window.play import (
    PlayMixin,
    collect_subcaptions,
    compose_srt,
    export_srt,
    record_subcaption,
)


class TimelineStub(PlayMixin):
    """A play window with no DLL: frames go nowhere, the timeline still runs.

    This is the LIVE branch of ``play()`` (``_schedule_mode`` False): a real
    ``Timeline`` is built and walked, but ``sync``/``tick``/``_capture_frame``
    are no-ops, so nothing is drawn and no GPU is involved.
    """

    _schedule_mode = False

    def __init__(self, scene):
        self.scene = scene
        self._fast_record = False
        self._cursor = 0.0
        self._sched = []

    def sync(self, scene):
        pass

    def tick(self):
        return True

    def _capture_frame(self):
        pass


class ScheduleStub(TimelineStub):
    """The ``FrameServer`` branch: ``play()`` records, never renders."""

    _schedule_mode = True


@pytest.fixture(autouse=True)
def clean_subcaption_store():
    """The flat store is module state: isolate every test from it."""
    play_mod.clear_subcaptions()
    yield
    play_mod.clear_subcaptions()


# ---------------------------------------------------------------------------
# A6 -- play(..., subcaption=...)
# ---------------------------------------------------------------------------

def test_play_without_subcaption_records_nothing():
    win = TimelineStub(Scene())
    win.play(ManimWait(0.1))
    assert collect_subcaptions() == []
    assert win._cursor == pytest.approx(0.1, abs=1e-9)


def test_subcaption_is_stamped_at_the_play_that_declared_it():
    """Report: ``subcaption=`` was silently ignored (gap A6)."""
    win = TimelineStub(Scene())
    win.play(ManimWait(0.1))                       # first 0.1 s of timeline
    win.play(ManimWait(0.2), subcaption="hello")

    entries = collect_subcaptions()
    assert len(entries) == 1, entries
    entry = entries[0]
    assert entry["content"] == "hello"
    assert entry["start"] == pytest.approx(0.1)     # where that play began
    assert entry["duration"] == pytest.approx(0.2)   # defaults to the run_time
    # the same cue is mirrored onto the window that played it
    assert collect_subcaptions([win]) == entries


def test_subcaption_duration_and_offset_follow_manim_semantics():
    """manim: start = play start + offset; duration defaults to run_time."""
    win = TimelineStub(Scene())
    win.play(ManimWait(0.1))
    win.play(ManimWait(0.3), subcaption="cue",
             subcaption_duration=0.5, subcaption_offset=0.25)

    entry = collect_subcaptions()[0]
    assert entry["start"] == pytest.approx(0.1 + 0.25)
    assert entry["duration"] == pytest.approx(0.5)


def test_subcaption_uses_the_time_actually_played_when_a_wait_stops_early():
    """``wait_until`` ends after one frame -> the cue is one frame long."""
    win = TimelineStub(Scene())
    win.play(ManimWait(0.5, stop_condition=lambda: True), subcaption="snap")

    entry = collect_subcaptions()[0]
    assert entry["duration"] == pytest.approx(1.0 / 60.0)
    assert win._cursor == pytest.approx(1.0 / 60.0)


def test_schedule_mode_records_subcaptions_too():
    """The FrameServer branch returns before the live one -- it must record too."""
    win = ScheduleStub(Scene())
    win.play(ManimWait(0.5), subcaption="recorded")

    assert win._sched, win._sched
    assert win._cursor == pytest.approx(0.5)
    entry = collect_subcaptions()[0]
    assert entry["start"] == pytest.approx(0.0)
    assert entry["duration"] == pytest.approx(0.5)


def test_export_srt_writes_cues_in_start_order(tmp_path):
    win = TimelineStub(Scene())
    record_subcaption(win, "second", 1.0, 1.5)
    record_subcaption(win, "first", 0.0, 0.8)

    path = export_srt(str(tmp_path / "out.srt"))
    text = open(path, encoding="utf-8").read()

    assert "1\n00:00:00,000 --> 00:00:00,800" in text
    assert "2\n00:00:01,000 --> 00:00:02,500" in text
    assert text.index("first") < text.index("second")


def test_export_srt_writes_nothing_when_there_are_no_cues(tmp_path):
    win = TimelineStub(Scene())
    target = tmp_path / "empty.srt"
    assert export_srt(str(target), windows=[win]) is None
    assert export_srt(str(target)) is None
    assert not target.exists()


def test_compose_srt_formats_timestamps():
    text = compose_srt([{"content": "a", "start": 61.5, "duration": 1.0}])
    assert "00:01:01,500 --> 00:01:02,500" in text
    assert text.strip().endswith("a")


def test_export_srt_can_be_called_with_explicit_entries(tmp_path):
    """The little tool is usable on its own (timestamps the caller computed)."""
    entries = [{"content": "hi", "start": 0.25, "duration": 1.0}]
    path = export_srt(str(tmp_path / "manual.srt"), entries=entries)
    text = open(path, encoding="utf-8").read()
    assert "00:00:00,250 --> 00:00:01,250" in text
    assert "hi" in text
    assert text.strip().endswith("hi")


def test_all_windows_reads_the_manim_registry():
    """The registry is the per-window view -- note ``close()`` unregisters."""
    from real_time_manim.window import MLWindow
    assert play_mod._all_windows() == list(MLWindow._registry)


def test_subcaption_survives_the_window_close():
    """``MLWindow.close()`` unregisters the window -- the cue must not vanish.

    A recording closes its window before ``record._run`` reaches the export
    step, so the flat store (not the registry) is what ``export_srt`` reads.
    A stub window is never registered, i.e. exactly a closed window's state.
    """
    win = TimelineStub(Scene())
    record_subcaption(win, "kept", 0.5, 1.0)

    assert win not in play_mod._all_windows()

    entries = collect_subcaptions()
    assert [e["content"] for e in entries] == ["kept"]


def test_record_end_writes_the_srt_next_to_the_output(tmp_path):
    """Auto-export choice: hook into ``audio_track.apply_sounds``.

    ``record._run`` calls it (with the produced files) at the end of every
    recording, so the ``.srt`` lands next to the MP4 without record.py -- which
    another session owns -- having to change.  The window is already closed
    (unregistered) by then, exactly as in a real recording.
    """
    from real_time_manim import audio_track

    out = tmp_path / "clip.mp4"
    out.write_bytes(b"")
    win = TimelineStub(Scene())
    record_subcaption(win, "hi", 0.0, 1.0)
    assert win not in play_mod._all_windows()         # the window is "closed"

    assert audio_track.apply_sounds([str(out)]) == []   # no sounds to mux

    srt = tmp_path / "clip.srt"
    assert srt.exists(), "the record end did not export the collected cues"
    assert "hi" in srt.read_text(encoding="utf-8")


def test_reset_clears_collected_subcaptions():
    """A fresh recording run must not inherit the previous run's cues."""
    from real_time_manim import audio_track

    win = TimelineStub(Scene())
    record_subcaption(win, "stale", 0.0, 1.0)

    audio_track.reset()
    assert collect_subcaptions() == []


# ---------------------------------------------------------------------------
# A7 -- scene-level updaters must be driven
# ---------------------------------------------------------------------------

def test_scene_updater_runs_on_every_frame_of_a_play():
    """The reported case: ``Scene.add_updater`` registered but never called."""
    scene = Scene()
    win = TimelineStub(scene)
    dts = []
    scene.add_updater(lambda dt: dts.append(dt))

    win.play(ManimWait(0.1))

    assert len(dts) >= 5, dts          # one call per frame (+ the dt=0 pass)
    assert any(dt > 0 for dt in dts), dts
    assert dts[-1] == 0.0, dts         # the trailing CE-style re-anchor pass


def test_scene_updater_moves_its_mobject_and_stops_when_removed():
    """The wiki red square: it climbs during the first wait, stands still after."""
    scene = Scene()
    win = TimelineStub(scene)
    sq = Square().shift(RIGHT * 3)
    scene.add(sq)
    start = sq.get_center()[0]

    def scene_updater(dt):
        sq.shift(RIGHT * 0.05)

    scene.add_updater(scene_updater)
    win.play(ManimWait(0.1))
    moved = sq.get_center()[0]
    assert moved > start, (start, moved)

    scene.remove_updater(scene_updater)
    win.play(ManimWait(0.1))
    assert sq.get_center()[0] == moved, "the removed scene updater still ran"


def test_scene_updater_runs_after_mobject_updaters_during_play():
    """CE order (``update_mobjects`` then ``update_self``) through ``win.play``."""
    scene = Scene()
    win = TimelineStub(scene)
    order = []
    mob = Square()
    mob.add_updater(lambda m: order.append("mobject"))
    scene.add(mob)
    scene.add_updater(lambda dt: order.append("scene"))

    win.play(ManimWait(0.05))

    assert "mobject" in order and "scene" in order, order
    assert order.index("scene") > order.index("mobject"), order


# ---------------------------------------------------------------------------
# A31 -- validate_run_time at the play entry
# ---------------------------------------------------------------------------

def test_play_zero_run_time_raises_manims_value_error():
    """Report: ``win.play(..., run_time=0)`` produced nothing, silently."""
    win = TimelineStub(Scene())
    with pytest.raises(ValueError):
        win.play(FadeIn(Square()), run_time=0)


def test_schedule_play_zero_run_time_raises_manims_value_error():
    """The schedule branch used to return before the validator entirely."""
    win = ScheduleStub(Scene())
    with pytest.raises(ValueError):
        win.play(FadeIn(Square()), run_time=0)


def test_play_negative_run_time_raises():
    win = ScheduleStub(Scene())
    with pytest.raises(ValueError):
        win.play(FadeIn(Square()), run_time=-1)


def test_play_normal_run_time_still_renders():
    """Sanity: a valid run_time is untouched by the validation."""
    win = TimelineStub(Scene())
    win.play(FadeIn(Square()), run_time=0.1)
    assert win._cursor == pytest.approx(0.1, abs=1e-9)


# ---------------------------------------------------------------------------
# A33 -- Scene.add_sound kwargs
# ---------------------------------------------------------------------------

@pytest.fixture
def audio():
    """A clean audio_track plus a scene carrying the add_sound hook."""
    from real_time_manim import audio_track
    audio_track.reset()
    scene = Scene()
    audio_track.install_add_sound_hook(scene)
    yield scene, audio_track
    audio_track.reset()


def test_add_sound_warns_naming_the_unsupported_parameter(audio, capsys):
    scene, audio_track = audio
    scene.add_sound("beep.wav", time_offset=0.5, gain=6.0,
                    gain_to_background=-3.0, room_size=0.3)
    out = capsys.readouterr().out

    line = [l for l in out.splitlines() if "unsupported parameter" in l]
    assert len(line) == 1, out
    line = line[0]
    assert "unsupported parameter(s) 'room_size'" in line
    assert "RTM 不支持该参数" in line


def test_add_sound_still_records_the_clip_and_the_supported_kwarg(audio):
    scene, audio_track = audio
    scene.add_sound("beep.wav", time_offset=0.5, gain=6.0,
                    gain_to_background=-3.0, room_size=0.3)

    sounds = audio_track.sounds()
    assert len(sounds) == 1, sounds
    path, start, gain = sounds[0]
    assert path.endswith("beep.wav") and os.path.isabs(path)
    assert start == pytest.approx(0.5)
    assert gain == pytest.approx(6.0)
    # the keyword RTM's mix implements is kept for build_track
    assert audio_track._sound_kwargs[0] == {"gain_to_background": -3.0}


def test_add_sound_with_only_supported_parameters_prints_no_warning(audio,
                                                                   capsys):
    scene, audio_track = audio
    scene.add_sound("beep.wav", gain_to_background=-6.0)
    out = capsys.readouterr().out
    assert "unsupported parameter" not in out, out
    assert audio_track._sound_kwargs[0] == {"gain_to_background": -6.0}


def test_build_track_forwards_gain_to_background_to_the_overlay(audio,
                                                                tmp_path,
                                                                monkeypatch):
    """manim's ``gain_to_background`` is pydub's ``gain_during_overlay``."""
    import pydub

    scene, audio_track = audio
    wav = tmp_path / "beep.wav"
    pydub.AudioSegment.silent(duration=50).export(str(wav), format="wav")

    scene.add_sound(str(wav), gain_to_background=-12.0)
    seen = {}

    original = pydub.AudioSegment.overlay

    def spy(self, seg2, **kwargs):
        seen.update(kwargs)
        return original(self, seg2, **kwargs)

    monkeypatch.setattr(pydub.AudioSegment, "overlay", spy)
    audio_track.build_track(str(tmp_path / "track.wav"), duration=0.5)

    assert seen.get("gain_during_overlay") == pytest.approx(-12.0), seen


def test_build_track_without_extra_kwargs_leaves_the_overlay_alone(audio,
                                                                   tmp_path,
                                                                   monkeypatch):
    import pydub

    scene, audio_track = audio
    wav = tmp_path / "beep.wav"
    pydub.AudioSegment.silent(duration=50).export(str(wav), format="wav")
    scene.add_sound(str(wav), time_offset=0.0, gain=0)

    seen = {}
    original = pydub.AudioSegment.overlay

    def spy(self, seg2, **kwargs):
        seen.update(kwargs)
        return original(self, seg2, **kwargs)

    monkeypatch.setattr(pydub.AudioSegment, "overlay", spy)
    audio_track.build_track(str(tmp_path / "track.wav"), duration=0.5)

    assert "gain_during_overlay" not in seen, seen


# ---------------------------------------------------------------------------
# A34 -- unknown play-level keywords
# ---------------------------------------------------------------------------

def test_unknown_play_kwarg_is_named_in_a_warning(capsys):
    win = ScheduleStub(Scene())
    anim = FadeIn(Square())
    win.play(anim, lag_ratio=0.7, run_time=0.3)

    out = capsys.readouterr().out
    assert "unsupported keyword" in out, out
    assert "'lag_ratio'" in out, out
    assert "RTM 不支持该参数" in out, out
    # named, not applied: RTM has never implemented play-level lag_ratio
    assert anim.lag_ratio == pytest.approx(0.0)
    # ...while the keywords RTM does implement keep working
    assert anim.run_time == pytest.approx(0.3)
    assert win._sched[0][1].run_time == pytest.approx(0.3)


def test_supported_play_keywords_print_no_warning(capsys):
    win = ScheduleStub(Scene())
    win.play(FadeIn(Square()), run_time=0.2, rate_func=lambda t: t)
    out = capsys.readouterr().out
    assert "unsupported keyword" not in out, out


def test_multiple_unknown_keywords_are_all_listed(capsys):
    win = ScheduleStub(Scene())
    win.play(FadeIn(Square()), lag_ratio=0.5, nonsense=1, run_time=0.2)
    out = capsys.readouterr().out
    assert "'lag_ratio'" in out and "'nonsense'" in out, out


# ---------------------------------------------------------------------------
# A27 (boundary): .animate(lag_ratio=...)
# ---------------------------------------------------------------------------

def test_animate_lag_ratio_reaches_the_built_animation_but_is_inert():
    """Conclusion for A27: the fix point is *not* window/play.py.

    ``play()`` hands the builder to manim's own ``_AnimationBuilder.build()``,
    which ``setattr``-s every ``.animate(...)`` keyword onto the animation --
    so nothing RTM-side drops ``lag_ratio=`` (``anim.lag_ratio == 0.5`` below).
    It changes no picture because only ``AnimationGroup`` reads ``lag_ratio``
    when spreading time over CHILD animations, and a single
    ``_MethodAnimation`` built by ``.animate(...)`` has no children.  manim CE
    behaves identically (same ``build()``, same ``Animation.interpolate``), so
    anything that should change belongs in ``window/patches.py`` (owned by
    another session) -- not here.  That session has since added its warning for
    this very case; the value still lands on the animation, as asserted below.
    """
    from manim.mobject.mobject import _AnimationBuilder

    win = ScheduleStub(Scene())
    builder = Square().animate(lag_ratio=0.5, run_time=2.0).shift(RIGHT)
    win.play(builder)

    anim = win._sched[0][1]
    assert not isinstance(anim, _AnimationBuilder), "the builder was never built"
    assert anim.lag_ratio == pytest.approx(0.5)   # arrives, unprompted
    assert anim.run_time == pytest.approx(2.0)

    from manim.animation.animation import Animation
    from manim.animation.composition import AnimationGroup
    assert "lag_ratio" not in inspect.getsource(Animation.interpolate)
    assert "self.lag_ratio" in inspect.getsource(AnimationGroup)
