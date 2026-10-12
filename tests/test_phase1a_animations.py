"""Phase 1a -- verify the animation classes the wiki marked ⚠️.

Each scene plays one target animation inside a real hidden Vulkan window and
asserts the render produced frames that (a) are not blank and (b) actually
change over time.  A class that "plays but renders as a static final state"
(the documented failure mode for a missing render hook) shows up as
``static=True`` and fails.

Run standalone:  python -X utf8 tests/test_phase1a_animations.py
Or with pytest:  pytest tests/test_phase1a_animations.py -q
"""
import os, sys
REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if REPO not in sys.path:
    sys.path.insert(0, REPO)

import pytest
from tools.rtm_verify import window_available, verify

if not window_available():                              # pragma: no cover
    pytest.skip("Vulkan window unavailable", allow_module_level=True)

from manim import (
    Scene, Square, Circle, Triangle, Dot, Text, MathTex, VGroup,
    UP, DOWN, LEFT, RIGHT, ORIGIN, PI,
    RED, GREEN, BLUE,
    LaggedStart, LaggedStartMap,
    SmoothedVectorizedHomotopy, ComplexHomotopy, PhaseFlow,
    AddTextLetterByLetter, RemoveTextLetterByLetter, AddTextWordByWord,
    UpdateFromFunc, UpdateFromAlphaFunc, MaintainPositionRelativeTo,
    Broadcast, TracedPath, AnimatedBoundary, FadeIn, Create, Write, Wait,
    Succession,
)
import numpy as np


def _sq(color=None):
    from manim import BLUE
    return Square(side_length=1.0, color=color or BLUE).set_fill(BLUE, 0.6)


# --------------------------------------------------------------------------
# 1a. classes already wired in render_hooks (wiki said "unverified")
# --------------------------------------------------------------------------

def test_lagged_start():
    class S(Scene):
        def construct(self):
            from real_time_manim.vulkan_bind import MLWindow
            win = MLWindow(1920, 1080); win.scene = self
            g = VGroup(Square(), Circle(), Triangle()).arrange(RIGHT, buff=0.6)
            win.play(LaggedStart(*[FadeIn(m) for m in g], lag_ratio=0.4),
                     run_time=1.0)
            win.close()
    info = verify(S, "lagged_start")
    assert info["render"] == "OK", info
    assert not info["all_blank"], info
    assert not info["static"], info


def test_lagged_start_map():
    class S(Scene):
        def construct(self):
            from real_time_manim.vulkan_bind import MLWindow
            win = MLWindow(1920, 1080); win.scene = self
            g = VGroup(Square(), Circle(), Triangle()).arrange(RIGHT, buff=0.6)
            win.play(LaggedStartMap(lambda m: FadeIn(m, shift=UP), g, lag_ratio=0.3),
                     run_time=1.0)
            win.close()
    info = verify(S, "lagged_start_map")
    assert info["render"] == "OK", info
    assert not info["all_blank"], info
    assert not info["static"], info


def test_complex_homotopy():
    class S(Scene):
        def construct(self):
            from real_time_manim.vulkan_bind import MLWindow
            win = MLWindow(1920, 1080); win.scene = self
            sq = _sq()
            def cf(z, t):
                return z * np.exp(1j * np.pi * t * 0.5)
            win.play(ComplexHomotopy(cf, sq), run_time=1.0)
            win.close()
    info = verify(S, "complex_homotopy")
    assert info["render"] == "OK", info
    assert not info["all_blank"], info
    assert not info["static"], info


def test_smoothed_vectorized_homotopy():
    class S(Scene):
        def construct(self):
            from real_time_manim.vulkan_bind import MLWindow
            win = MLWindow(1920, 1080); win.scene = self
            sq = _sq()
            def h(x, y, z, t):
                return np.array([x + 0.5 * np.sin(np.pi * t) * y, y, z])
            win.play(SmoothedVectorizedHomotopy(h, sq), run_time=1.0)
            win.close()
    info = verify(S, "smoothed_vectorized_homotopy")
    assert info["render"] == "OK", info
    assert not info["all_blank"], info
    assert not info["static"], info


def test_phase_flow():
    class S(Scene):
        def construct(self):
            from real_time_manim.vulkan_bind import MLWindow
            win = MLWindow(1920, 1080); win.scene = self
            d = Dot().shift(LEFT * 2)
            def vf(p):
                return np.array([-p[1], p[0], 0.0]) * 0.3
            win.play(PhaseFlow(vf, d), run_time=1.0)
            win.close()
    info = verify(S, "phase_flow")
    assert info["render"] == "OK", info
    assert not info["all_blank"], info
    assert not info["static"], info


def test_add_text_letter_by_letter():
    class S(Scene):
        def construct(self):
            from real_time_manim.vulkan_bind import MLWindow
            win = MLWindow(1920, 1080); win.scene = self
            t = Text("Hello")
            win.play(AddTextLetterByLetter(t), run_time=1.0)
            win.close()
    info = verify(S, "add_text_letter_by_letter")
    assert info["render"] == "OK", info
    assert not info["all_blank"], info
    assert not info["static"], info


def test_remove_text_letter_by_letter():
    class S(Scene):
        def construct(self):
            from real_time_manim.vulkan_bind import MLWindow
            win = MLWindow(1920, 1080); win.scene = self
            t = Text("Hello")
            self.add(t)
            win.play(RemoveTextLetterByLetter(t), run_time=1.0)
            win.close()
    info = verify(S, "remove_text_letter_by_letter")
    assert info["render"] == "OK", info
    assert not info["all_blank"], info
    assert not info["static"], info


def test_add_text_word_by_word():
    # manim 0.21 caveat, not an RTM gap: AddTextWordByWord is a Succession of
    # ShowIncreasingSubsets(word) + Animation(word), but iterating a Text yields
    # *characters* (VMobjectFromSVGPath) that have no submobjects -- so
    # ShowIncreasingSubsets hides/reveals an empty list and the text stays fully
    # visible.  manim CE renders the same static result.  RTM faithfully draws
    # the mobject state.  Assert it at least renders non-blank (not a crash).
    class S(Scene):
        def construct(self):
            from real_time_manim.vulkan_bind import MLWindow
            win = MLWindow(1920, 1080); win.scene = self
            t = Text("hello world")
            win.play(AddTextWordByWord(t), run_time=1.0)
            win.close()
    info = verify(S, "add_text_word_by_word")
    assert info["render"] == "OK", info
    assert not info["all_blank"], info


def test_succession_schedules_children():
    # The real question for RTM: does a hand-built Succession animate its
    # children in order?  (AddTextWordByWord being static is a manim-Text quirk.)
    class S(Scene):
        def construct(self):
            from real_time_manim.vulkan_bind import MLWindow
            win = MLWindow(1920, 1080); win.scene = self
            sq = _sq()
            win.play(Succession(Create(sq), sq.animate.shift(UP)), run_time=1.0)
            win.close()
    info = verify(S, "succession_schedules")
    assert info["render"] == "OK", info
    assert not info["all_blank"], info
    assert not info["static"], info


def test_update_from_func():
    class S(Scene):
        def construct(self):
            from real_time_manim.vulkan_bind import MLWindow
            win = MLWindow(1920, 1080); win.scene = self
            sq = _sq()
            def updater(m):
                m.rotate(0.1)
            self.add(sq)
            win.play(UpdateFromFunc(sq, updater), run_time=1.0)
            win.close()
    info = verify(S, "update_from_func")
    assert info["render"] == "OK", info
    assert not info["all_blank"], info
    assert not info["static"], info


def test_update_from_alpha_func():
    class S(Scene):
        def construct(self):
            from real_time_manim.vulkan_bind import MLWindow
            win = MLWindow(1920, 1080); win.scene = self
            sq = _sq()
            def fn(m, a):
                m.set_fill(opacity=a)
            self.add(sq)
            win.play(UpdateFromAlphaFunc(sq, fn), run_time=1.0)
            win.close()
    info = verify(S, "update_from_alpha_func")
    assert info["render"] == "OK", info
    assert not info["all_blank"], info
    assert not info["static"], info


def test_maintain_position_relative_to():
    class S(Scene):
        def construct(self):
            from real_time_manim.vulkan_bind import MLWindow
            win = MLWindow(1920, 1080); win.scene = self
            sq = _sq()
            dot = Dot().shift(RIGHT * 2)
            self.add(sq, dot)
            win.play(sq.animate.shift(UP), run_time=0.4)
            win.play(MaintainPositionRelativeTo(dot, sq), run_time=0.6)
            win.close()
    info = verify(S, "maintain_position_relative_to")
    assert info["render"] == "OK", info
    assert not info["all_blank"], info
    assert not info["static"], info


def test_broadcast():
    class S(Scene):
        def construct(self):
            from real_time_manim.vulkan_bind import MLWindow
            win = MLWindow(1920, 1080); win.scene = self
            sq = _sq()
            win.play(Broadcast(sq, focal_point=ORIGIN, n_mobs=5,
                               initial_opacity=1.0, final_opacity=0.0),
                     run_time=1.0)
            win.close()
    info = verify(S, "broadcast")
    assert info["render"] == "OK", info
    assert not info["all_blank"], info
    assert not info["static"], info


def test_traced_path():
    class S(Scene):
        def construct(self):
            from real_time_manim.vulkan_bind import MLWindow
            win = MLWindow(1920, 1080); win.scene = self
            d = Dot(color=BLUE).shift(LEFT * 3)
            tp = TracedPath(d.get_center, stroke_width=6, stroke_color=BLUE)
            self.add(tp, d)
            # move along an arc so the trace has real length (a full Circle's
            # get_start() and get_end() are the same point -- no movement).
            win.play(d.animate(path_arc=PI / 2).shift(RIGHT * 6), run_time=1.0)
            win.close()
    info = verify(S, "traced_path")
    assert info["render"] == "OK", info
    assert not info["all_blank"], info
    assert not info["static"], info


def test_animated_boundary():
    # manim 0.21: AnimatedBoundary is a VGroup with an internal updater, not an
    # Animation -- the idiomatic use is self.add(...) + wait(), which also
    # exercises RTM driving mobject updaters during a Wait.
    class S(Scene):
        def construct(self):
            from real_time_manim.vulkan_bind import MLWindow
            win = MLWindow(1920, 1080); win.scene = self
            sq = _sq()
            ab = AnimatedBoundary(sq, colors=[RED, GREEN, BLUE], cycle_rate=3)
            self.add(sq, ab)
            win.play(Wait(1.0))
            win.close()
    info = verify(S, "animated_boundary")
    assert info["render"] == "OK", info
    assert not info["all_blank"], info
    assert not info["static"], info


if __name__ == "__main__":
    import json
    fns = [v for k, v in sorted(globals().items()) if k.startswith("test_")]
    for fn in fns:
        try:
            fn()
            print("PASS", fn.__name__)
        except Exception as e:
            print("FAIL", fn.__name__, "->", e)
