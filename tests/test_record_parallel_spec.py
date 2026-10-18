# -*- coding: utf-8 -*-
"""The decisions behind a frame-parallel fast record (no window / no GPU).

``fast_record_scene(..., jobs=N)`` splits a scene's frame range across worker
processes and concatenates their segments.  What may be split, how the range is
divided and what the workers are told are pure decisions; they are pinned here
so a regression shows up as a test failure rather than a wrong video.
"""
import os
import sys

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if REPO not in sys.path:
    sys.path.insert(0, REPO)

from real_time_manim import Scene  # noqa: E402
from real_time_manim._record_worker import frame_block  # noqa: E402
from real_time_manim.record import (  # noqa: E402
    _AUTO_MIN_FRAMES,
    _NotParallelizable,
    _has_main_guard,
    _parallel_plan,
    _planned_jobs,
    _scene_token,
)
from real_time_manim.window.recording import fast_pipe_ffmpeg_args  # noqa: E402


class ModuleLevelScene(Scene):        # importable by name: `module:qualname`
    def construct(self):
        pass


# ---------------------------------------------------------------------------
# frame_block: the partition must be exact, ordered and contiguous
# ---------------------------------------------------------------------------

def test_blocks_partition_the_range_in_order():
    for n in (1, 2, 7, 40, 150, 151):
        for jobs in (1, 2, 3, 4, 8):
            blocks = [frame_block(n, jobs, i) for i in range(jobs)]
            # contiguous, in worker order, covering [0, n) exactly once
            assert blocks[0][0] == 0
            for (s0, e0), (s1, e1) in zip(blocks, blocks[1:]):
                assert e0 == s1, (n, jobs, blocks)
            assert blocks[-1][1] == n, (n, jobs, blocks)
            assert sum(e - s for s, e in blocks) == n


def test_blocks_are_balanced_within_one_frame():
    blocks = [frame_block(150, 4, i) for i in range(4)]
    lengths = [e - s for s, e in blocks]
    assert max(lengths) - min(lengths) <= 1
    assert lengths[0] == 38                     # 150 = 4*37 + 2 -> first two


def test_blocks_clamp_out_of_range_indexes_and_never_go_backwards():
    assert frame_block(10, 4, -3) == frame_block(10, 4, 0)
    assert frame_block(10, 4, 99) == frame_block(10, 4, 3)
    # more workers than frames: trailing workers get an empty block, not a
    # negative one (the worker then writes no segment at all).
    assert [frame_block(2, 5, i) for i in range(5)] == [(0, 1), (1, 2), (2, 2),
                                                       (2, 2), (2, 2)]


# ---------------------------------------------------------------------------
# how many workers, and whether the scene may be split at all
# ---------------------------------------------------------------------------

def test_planned_jobs_defaults_to_a_capped_cpu_count_and_honours_ints():
    assert _planned_jobs(1) == 1
    assert _planned_jobs(6) == 6
    auto = _planned_jobs("auto")
    assert 1 <= auto <= 4
    assert auto == 1 or auto <= (os.cpu_count() or 2) - 1


def test_the_default_never_probes_and_never_splits():
    # Deciding needs a probe pass (window + Vulkan device, ~1.4 s), so the
    # default must return before any of that -- ModuleLevelScene() below would
    # otherwise be prepared here.
    for jobs in (None, 1):
        assert _parallel_plan(ModuleLevelScene, jobs, 60, True, False, None,
                              False) is None


def test_probe_modes_are_out_of_scope_for_the_single_pass_knobs():
    # count_only, BMP segment mode and a visible window cannot be split.
    assert _parallel_plan(ModuleLevelScene, 4, 60, True, True, None, False) is None
    assert _parallel_plan(ModuleLevelScene, 4, 60, True, False, (0, 10),
                          False) is None
    assert _parallel_plan(ModuleLevelScene, 4, 60, False, False, None, False) is None


def test_a_worker_never_splits_again(monkeypatch):
    monkeypatch.setenv("RTM_IN_WORKER", "1")
    assert _parallel_plan(ModuleLevelScene, 4, 60, True, False, None, False) is None


def test_auto_splits_only_scenes_long_enough_to_pay_for_the_workers(monkeypatch):
    import real_time_manim.frames as frames

    class FakeServer:
        duration = 0.0

        def __init__(self, scene, **kwargs):
            pass

        def close(self):
            pass

    monkeypatch.setattr(frames, "FrameServer", FakeServer)
    monkeypatch.setattr(frames, "_LAST_WINDOWS", [object()])

    FakeServer.duration = (_AUTO_MIN_FRAMES - 1) / 60.0
    assert _parallel_plan(ModuleLevelScene, "auto", 60, True, False, None,
                          False) is None

    FakeServer.duration = (_AUTO_MIN_FRAMES + 60) / 60.0
    plan = _parallel_plan(ModuleLevelScene, "auto", 60, True, False, None, False)
    assert plan is not None
    assert plan["n_frames"] == _AUTO_MIN_FRAMES + 60
    assert 2 <= plan["jobs"] <= 4
    assert plan["scene_ref"]["qual"] == "ModuleLevelScene"


def test_a_multi_window_scene_is_not_split(monkeypatch):
    import real_time_manim.frames as frames

    class FakeServer:
        duration = 100.0

        def __init__(self, scene, **kwargs):
            pass

        def close(self):
            pass

    monkeypatch.setattr(frames, "FrameServer", FakeServer)
    monkeypatch.setattr(frames, "_LAST_WINDOWS", [object(), object()])
    assert _parallel_plan(ModuleLevelScene, 4, 60, True, False, None,
                          False) is None


def test_module_level_scene_gets_a_module_handle():
    ref = _scene_token(ModuleLevelScene)
    assert ref["kind"] == "module"
    assert ref["qual"] == "ModuleLevelScene"
    assert ref["target"].endswith("test_record_parallel_spec")


def test_unimportable_scenes_are_refused():
    for scene in (ModuleLevelScene(),            # an instance
                  lambda: None):                 # not a class
        try:
            _scene_token(scene)
        except _NotParallelizable:
            continue
        raise AssertionError("expected _NotParallelizable for %r" % (scene,))

    def local():                                 # defined inside a function
        class Inner(Scene):
            pass
        return Inner

    try:
        _scene_token(local())
    except _NotParallelizable:
        pass
    else:
        raise AssertionError("a <locals> class must not be handed to workers")


def test_main_guard_is_required_before_a_script_may_be_imported(tmp_path):
    guarded = tmp_path / "guarded.py"
    guarded.write_text("class S:\n    pass\n\n\nif __name__ == '__main__':\n"
                       "    S()\n", encoding="utf-8")
    unguarded = tmp_path / "unguarded.py"
    unguarded.write_text("class S:\n    pass\n\nS()\n", encoding="utf-8")
    guarded_single = tmp_path / "single.py"
    guarded_single.write_text("class S:\n    pass\n\nif __name__ == \"__main__\":\n"
                              "    pass\n", encoding="utf-8")

    assert _has_main_guard(str(guarded))
    assert _has_main_guard(str(guarded_single))
    assert not _has_main_guard(str(unguarded))
    assert not _has_main_guard(str(tmp_path / "missing.py"))


# ---------------------------------------------------------------------------
# the workers must encode exactly like the single-pass pipe
# ---------------------------------------------------------------------------

def test_worker_encoder_matches_the_live_pipe_settings():
    from real_time_manim._record_worker import segment_ffmpeg

    live = fast_pipe_ffmpeg_args(1920, 1080, 60, "bgra", "a.mp4")
    worker = segment_ffmpeg(1920, 1080, 60, "bgra", "a.mp4")
    assert worker == live
    joined = " ".join(worker)
    for flag in ("-pixel_format bgra", "-c:v libx264", "-pix_fmt yuv420p",
                 "-color_range pc", "scale=out_range=pc", "-crf 18",
                 "-preset fast", "-framerate 60"):
        assert flag in joined
