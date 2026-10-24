# -*- coding: utf-8 -*-
"""Full source of the only sample in 04-Subcaptions-and-Sound.md that produces a clip (Scene.add_sound).

Usage: python 04-Subcaptions-and-Sound.py
After rendering, the MP4 carries a muxed audio track (RTM captures add_sound through the audio_track hook while recording).
"""
import os
import shutil
import subprocess
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ASSETS = os.path.dirname(HERE)
OUT = os.path.join(HERE, "final",
                        os.path.splitext(os.path.basename(__file__))[0])
os.makedirs(OUT, exist_ok=True)
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), *[".."] * 6)))

from real_time_manim import Scene, Circle, ORANGE, Create, Indicate
from real_time_manim.vulkan_bind import MLWindow, Wait
from real_time_manim.record import fast_record_scene


# ===== Sample 1: Scene.add_sound ===========================================
class AddSoundDemo(Scene):
    GAIN = 6.0   #volume gain (dB): change it to 0 for the original volume, or -6 for something quieter

    def construct(self):
        win = MLWindow(960, 540)   #create an RTM window
        win.scene = self   #bind the manim scene named "self" to the RTM window named "win"
        self.play = win.play   #a scene method calls self.play internally, so wire it up first
        beep = os.path.join(os.path.dirname(os.path.abspath(__file__)), "beep.wav")   #the demo "beep"
        self.add_sound(beep, time_offset=0.5, gain=self.GAIN)   #beep once 0.5s in (louder)
        dot = Circle(radius=0.9, color=ORANGE)   #a circle
        self.add(dot)   #put the circle on screen
        win.play(Create(dot), run_time=1.0)   #draw this circle over 1.0s
        self.add_sound(beep, time_offset=0, gain=0)   #beep once more right now (at 1.0s), with no gain, as a control
        win.play(Indicate(dot), run_time=0.6)   #Indicate the circle to emphasize it, keeping time with the second sound
        win.play(Wait(0.6))   #wait 0.6s, leaving room for the sound's tail
        win.close()   #close the RTM window


PAGE = "04-Subcaptions-and-Sound"

SCENES = [
    ("sound", AddSoundDemo),
]

SAMPLES = [
    ("sound", ["sound"]),
]


def concat(names, dst):
    os.makedirs(os.path.dirname(dst) or ".", exist_ok=True)
    lst = os.path.join(HERE, "concat.txt")
    with open(lst, "w", encoding="utf-8") as fh:
        for n in names:
            fh.write("file '%s'\n" % os.path.join(OUT, n + ".mp4"))
    subprocess.run(
        ["ffmpeg", "-y", "-loglevel", "error", "-f", "concat", "-safe", "0",
         "-i", lst, "-c", "copy", dst],
        check=True)
    return dst


if __name__ == "__main__":
    only = set(sys.argv[1:])
    for name, cls in SCENES:
        if only and name not in only:
            continue
        print("=" * 30, name)
        try:
            fast_record_scene(cls, out_path=os.path.join(OUT, name + ".mp4"),
                              verbose=True)
        except Exception:
            import traceback
            traceback.print_exc()

    if not only:
        for out_name, names in SAMPLES:
            dst = os.path.join(ASSETS, "RTM output", "%s-%s.mp4" % (PAGE, out_name))
            concat(names, dst)
            print("concat ->", dst, os.path.getsize(dst), "bytes")
            if len(names) > 1:
                #multi-clip sample: copy each clip into assets/ too, for segment-by-segment comparison
                for n in names:
                    shutil.copyfile(os.path.join(OUT, n + ".mp4"),
                                    os.path.join(ASSETS, "%s-%s.mp4" % (PAGE, n)))
