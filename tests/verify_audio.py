"""Phase 6 check: a scene that calls add_sound must produce an mp4 with audio.

    <venv21-python> tests/verify_audio.py
"""
import json
import os
import subprocess
import sys

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, REPO)

from manim import BLUE, Scene, Square                     # noqa: E402
from real_time_manim.record import fast_record_scene      # noqa: E402
from real_time_manim.vulkan_bind import Create, MLWindow, Wait   # noqa: E402

TMP = os.environ["TEMP"]
tone = os.path.join(TMP, "_rtm_tone.wav")
subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-f", "lavfi",
                "-i", "sine=frequency=440:duration=1", tone], check=True)


class SoundProbe(Scene):
    def construct(self):
        win = MLWindow(480, 360, hidden=True)
        win.scene = self
        try:
            self.add_sound(tone)
            win.play(Create(Square(side_length=1.5, color=BLUE)), run_time=0.5)
            self.add_sound(tone, time_offset=0.2)
            win.play(Wait(0.5))
        finally:
            win._defer_close = False
            win.close()


class SilentProbe(Scene):
    def construct(self):
        win = MLWindow(480, 360, hidden=True)
        win.scene = self
        try:
            win.play(Create(Square(side_length=1.5, color=BLUE)), run_time=0.5)
            win.play(Wait(0.5))
        finally:
            win._defer_close = False
            win.close()


def streams(path):
    out = subprocess.run(["ffprobe", "-v", "error", "-show_streams", "-of", "json", path],
                         capture_output=True, text=True).stdout
    try:
        return [(s.get("codec_type"), s.get("codec_name"), s.get("nb_frames"))
                for s in json.loads(out).get("streams", [])]
    except Exception:
        return []


ok = True
for cls, expect_audio in ((SoundProbe, True), (SilentProbe, False)):
    out = os.path.join(TMP, f"_rtm_{cls.__name__}.mp4")
    if os.path.exists(out):
        os.remove(out)
    res = fast_record_scene(cls, out, fps=15, hidden=True, overwrite=True, verbose=False)
    st = streams(out)
    has_audio = any(t == "audio" for t, _, _ in st)
    frames = next((n for t, _, n in st if t == "video"), "?")
    print(f"  {cls.__name__:<12} streams={st}  with_audio={len(res.get('with_audio', []))}")
    if has_audio != expect_audio:
        ok = False
        print(f"    !! expected audio={expect_audio}")
    if not has_audio and expect_audio:
        ok = False
print("RESULT:", "PASS" if ok else "FAIL")
raise SystemExit(0 if ok else 1)
