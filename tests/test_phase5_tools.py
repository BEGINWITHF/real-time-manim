"""Phase 5 -- tools domain: rate functions and color utilities.

The wiki marks 08-工具 rate functions and colors as "only 11 built-in / rest
relies on fallback". RTM's animations accept `rate_func` as a plain callable,
so manim's full rate-function set should pass straight through. This proves it
by rendering an animation with a spread of manim rate functions (including the
ease_* family well beyond RTM's internal 12) and asserting each animates.

Run standalone:  python -X utf8 tests/test_phase5_tools.py
Or with pytest:  pytest tests/test_phase5_tools.py -q
"""
import os, sys
REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if REPO not in sys.path:
    sys.path.insert(0, REPO)

import pytest
from tools.rtm_verify import window_available, verify

if not window_available():                              # pragma: no cover
    pytest.skip("Vulkan window unavailable", allow_module_level=True)

import numpy as np
import manim
from manim import Scene, Square, Circle, BLUE, RED, GREEN, Create, FadeIn, Rotate, UP

# A representative spread: RTM's internal set + manim's ease_* family beyond it.
# NB: not_quite_there / squish_rate_func are FACTORIES (func, proportion) ->
# RateFunction, not plain rate functions; they are exercised separately below.
RATE_FUNCTIONS = [
    "smooth", "linear", "rush_into", "rush_from", "there_and_back",
    "slow_into", "double_smooth", "wiggle", "lingering", "exponential_decay",
    "ease_in_sine", "ease_out_sine", "ease_in_out_sine",
    "ease_in_cubic", "ease_out_cubic", "ease_in_out_cubic",
    "ease_in_back", "ease_out_back", "ease_in_out_back",
    "ease_in_bounce", "ease_out_bounce", "ease_in_out_bounce",
    "ease_in_elastic", "ease_out_elastic", "ease_in_out_elastic",
    "running_start", "there_and_back_with_pause",
]


def _rf(name):
    return getattr(manim.rate_functions, name)


def _play_with(rate):
    class S(Scene):
        def construct(self):
            from real_time_manim.vulkan_bind import MLWindow
            win = MLWindow(1920, 1080); win.scene = self
            sq = Square(side_length=1.5).set_fill(BLUE, 0.6)
            win.play(Create(sq, rate_func=rate), run_time=0.6)
            win.close()
    return S


@pytest.mark.parametrize("name", RATE_FUNCTIONS)
def test_rate_function_drives_animation(name):
    info = verify(_play_with(_rf(name)), "rf_" + name)
    assert info["render"] == "OK", info
    assert not info["all_blank"], info


@pytest.mark.parametrize("factory_name", ["not_quite_there", "squish_rate_func"])
def test_rate_function_factory(factory_name):
    # These return a RateFunction from a (func, proportion/a, b) signature; call
    # them to get a usable rate function, then drive an animation with it.
    factory = getattr(manim.rate_functions, factory_name)
    if factory_name == "squish_rate_func":
        rate = factory(manim.rate_functions.smooth, 0.2, 0.8)
    else:
        rate = factory()                       # defaults: (smooth, 0.7)
    info = verify(_play_with(rate), "rff_" + factory_name)
    assert info["render"] == "OK", info
    assert not info["all_blank"], info


def test_color_interpolation():
    # Color tools are pure-python/manim utilities; assert they work and that a
    # colour-driven animation renders. A fill-only colour lerp has small
    # per-pixel deltas (no motion), so use a lower change threshold here.
    from manim import ManimColor, interpolate_color, color_to_rgb, rgb_to_color
    c = interpolate_color(ManimColor(RED), ManimColor(GREEN), 0.5)
    assert c is not None
    assert len(color_to_rgb(c)) == 3

    class S(Scene):
        def construct(self):
            from real_time_manim.vulkan_bind import MLWindow
            win = MLWindow(1920, 1080); win.scene = self
            sq = Square(side_length=3.0).set_fill(RED, 0.8)
            win.play(sq.animate.set_fill(GREEN, 0.8), run_time=0.8)
            win.close()

    info = verify(S, "color_interpolate")
    assert info["render"] == "OK", info
    assert not info["all_blank"], info
    # colour-only: accept a small but non-zero frame delta (motion-based
    # animations clear the default 8/255 bar; a fill lerp peaks around 7).
    assert info["max_frame_diff"] > 2.0, info


def test_indicate_color_tint():
    # Indicate's colour-tint path (a colour channel animation) renders and animates.
    class S(Scene):
        def construct(self):
            from real_time_manim.vulkan_bind import MLWindow
            win = MLWindow(1920, 1080); win.scene = self
            sq = Square(side_length=1.5).set_fill(BLUE, 0.6)
            from manim import Indicate
            win.play(Indicate(sq, color=RED), run_time=0.8)
            win.close()

    info = verify(S, "indicate_color")
    assert info["render"] == "OK", info
    assert not info["all_blank"], info
    assert not info["static"], info


if __name__ == "__main__":
    passed = failed = 0
    for name in RATE_FUNCTIONS:
        try:
            test_rate_function_drives_animation(name); print("PASS rf", name); passed += 1
        except Exception as e:
            print("FAIL rf", name, "->", str(e)[:160]); failed += 1
    for fn in (test_color_interpolation, test_indicate_color_tint):
        try:
            fn(); print("PASS", fn.__name__); passed += 1
        except Exception as e:
            print("FAIL", fn.__name__, "->", str(e)[:160]); failed += 1
    print(f"\n{passed} passed, {failed} failed")
