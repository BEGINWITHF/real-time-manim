"""End-to-end check of the ApplyPointwiseFunctionToCenter shim: does it RENDER?

The unit test only interpolates; this drives a real (hidden) window through
fast_record and requires actual frames, which is what the checklist counts.

Run: python _apwfc_render_check.py [--installed]
"""
import os
import subprocess
import sys

REPO = os.path.dirname(os.path.abspath(__file__))
if "--installed" not in sys.argv:
    sys.path.insert(0, REPO)

import real_time_manim                                     # noqa: E402  (applies shims)
from manim import Scene, Square                            # noqa: E402
from manim.animation.transform import ApplyPointwiseFunctionToCenter  # noqa: E402
from real_time_manim.record import fast_record_scene       # noqa: E402
from real_time_manim.vulkan_bind import MLWindow           # noqa: E402


class S(Scene):
    def construct(self):
        win = MLWindow(480, 360, hidden=True)
        win.scene = self
        try:
            win.play(ApplyPointwiseFunctionToCenter(lambda p: p, Square()), run_time=0.3)
        finally:
            win._defer_close = False
            win.close()


out = os.path.join(os.environ["TEMP"], "_apwfc_check.mp4")
if os.path.exists(out):
    os.remove(out)
fast_record_scene(S, out, fps=15, hidden=True, overwrite=True, verbose=False)
size = os.path.getsize(out) if os.path.exists(out) else 0
probe = subprocess.run(["ffprobe", "-v", "error", "-select_streams", "v:0",
                        "-show_entries", "stream=nb_frames,codec_name", "-of", "csv=p=0", out],
                       capture_output=True, text=True).stdout.strip()
print(f"file={size}B  ffprobe={probe!r}")
print("RESULT:", "PASS" if size > 1000 and "h264" in probe else "FAIL")
raise SystemExit(0 if size > 1000 and "h264" in probe else 1)
