"""Example / self-test for the 2.0.0 time-addressable Timeline.

Run:
    python examples/timeline_seek.py

It drives MANIM's own animations (Transform + FadeIn) through our renderer and
asks for arbitrary frames directly (no replay). It then checks that per-frame
cost is flat w.r.t. t (i.e. seeking is O(1)) and saves the requested frames so
you can eyeball that each t really is a different point of the animation.

For the GPU-free correctness test (manim animations are pure functions of
alpha) run:
    python -m pytest tests/test_animation_purity.py -q
"""
import os
import sys
import time

# make the repo root importable when run as a script
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from manim import Scene, Square, Circle, Text, BLUE, YELLOW, WHITE
from manim.animation.fading import FadeIn
from manim.animation.transform import Transform

from real_time_manim.vulkan_bind import MLWindow
from real_time_manim.timeline import Timeline

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(HERE, "_seek_out")
os.makedirs(OUT, exist_ok=True)
RT = 2.0  # animation duration (seconds)


def main():
    scene = Scene()
    win = MLWindow(1280, 720)
    win.scene = scene
    sq = Square(side_length=2, color=BLUE).set_fill(BLUE, 0.6)
    txt = Text("seek", font_size=110, color=WHITE)
    circ = Circle(radius=1.2, color=YELLOW).set_fill(YELLOW, 0.6)
    scene.add(sq, txt)

    # prepare once: captures each animation's pristine start/target state
    tl = Timeline(win, scene).prepare(
        Transform(sq, circ, run_time=RT),   # manim animation
        FadeIn(txt, run_time=RT),           # manim animation
    )
    print("stateful animations:", tl.stateful_names() or "none")

    # warm-up (first GPU draw of a given pipeline is slower)
    tl.render_at(0.0)

    # ask for frames in a shuffled order — order must not matter
    targets = [1.50, 0.25, 1.99, 0.00, 1.00, 0.75, 1.90, 0.10]
    print(f"\n{'t (s)':>6}  {'frame':>5}  {'ms':>7}   saved")
    times = []
    for t in targets:
        s = time.perf_counter()
        tl.render_at(t)
        ms = (time.perf_counter() - s) * 1000.0
        times.append(ms)
        path = os.path.join(OUT, f"t_{t:0.2f}.png")
        win.screenshot(path)
        print(f"{t:>6.2f}  {int(t*60):>5}  {ms:>7.2f}   {os.path.basename(path)}")

    spread = max(times) - min(times)
    print(f"\nseek cost: min={min(times):.2f}ms max={max(times):.2f}ms "
          f"spread={spread:.2f}ms")
    print("=> FLAT (O(1)) — cost does not grow with t" if spread < 50
          else "=> NOT flat — investigate")

    win.close()
    print("frames written to", OUT)


if __name__ == "__main__":
    main()
