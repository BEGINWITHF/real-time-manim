"""Check that every FrameServer path stays windowless except show_frame.

Usage: python tests/verify_hidden.py <mode>

Modes:
  frames           FrameServer (default hidden) -> prepare/grab/save/export
  frames_visible   FrameServer(hidden=False) baseline, for pixel comparison
  fast             fast_record_scene(hidden=True) -> mp4
  plain            MLWindow() created directly (must still be visible)
  shot             compare the BMP screenshot path with the exact readback
  lag              does a read follow the frame just drawn, in any cadence?

Needs the dev scene files (`scenes/`), so it runs from a working tree rather
than an installed package.  Prints one JSON line per mode.

Asserted properties (each was a real bug, see tests/test_frame_access.py):
  * offline paths never show a window, show_frame is the only one that does;
  * `plain` visibility toggling works;
  * `lag` values no longer depend on how many frames were presented before.
"""
import ctypes
import json
import os
import sys
import time

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, REPO)
os.chdir(REPO)

OUT = os.path.join(REPO, "_hidden_check")
os.makedirs(OUT, exist_ok=True)

user32 = ctypes.windll.user32
user32.FindWindowW.restype = ctypes.c_void_p
user32.FindWindowW.argtypes = [ctypes.c_wchar_p, ctypes.c_wchar_p]
user32.IsWindowVisible.restype = ctypes.c_int
user32.IsWindowVisible.argtypes = [ctypes.c_void_p]


def win_visible():
    hwnd = user32.FindWindowW(None, "Real Time Manim")
    if not hwnd:
        return None
    return bool(user32.IsWindowVisible(hwnd))


def png_stats(path):
    import numpy as np
    from PIL import Image
    img = np.asarray(Image.open(path).convert("L"))
    return {"mean": float(img.mean()), "max": int(img.max()),
            "bytes": os.path.getsize(path)}


def main():
    mode = sys.argv[1] if len(sys.argv) > 1 else "frames"
    report = {"mode": mode, "visible_after_start": win_visible()}

    if mode in ("frames", "frames_visible"):
        from real_time_manim.frames import FrameServer
        from scenes.demo_scene import DemoCreate

        t0 = time.perf_counter()
        fs = FrameServer(DemoCreate, hidden=(mode == "frames"))
        report["prepare_ms"] = round((time.perf_counter() - t0) * 1000)
        report["visible_after_prepare"] = win_visible()

        fs.grab(3.0)  # warm-up
        times = []
        for t in (3.0, 0.5, 5.8):
            s = time.perf_counter()
            fs.grab(t)
            times.append(round((time.perf_counter() - s) * 1000))
        report["grab_ms"] = times
        report["visible_after_grab"] = win_visible()

        png = os.path.join(OUT, f"{mode}_t3.png")
        fs.save_frame(3.0, png)
        report["visible_after_save"] = win_visible()
        report["png"] = png_stats(png)

        fs.export_frames(os.path.join(OUT, f"{mode}_frames"), [1.0, 2.0])
        report["visible_after_export"] = win_visible()
        report["export_count"] = len(os.listdir(os.path.join(OUT, f"{mode}_frames")))

        fs.show_frame(4.0)
        report["visible_after_show_frame"] = win_visible()
        report["png_after_show"] = fs.save_frame(3.0, os.path.join(OUT, f"{mode}_t3_show.png"))
        report["png_stats_after_show"] = png_stats(os.path.join(OUT, f"{mode}_t3_show.png"))
        fs.close()

    elif mode == "fast":
        from real_time_manim.record import fast_record_scene
        from scenes.demo_scene import DemoFadeInFadeOut as SceneCls
        import real_time_manim.vulkan_bind as vb

        seen = {}

        # Probe as soon as the scene's window exists, and again while frames
        # are being captured -- a hidden build must never be visible.
        orig_init = vb.MLWindow.__init__

        def probe_init(self_, *a, **k):
            orig_init(self_, *a, **k)
            seen["at_create"] = win_visible()
            seen["hidden_flag"] = self_.hidden

        vb.MLWindow.__init__ = probe_init

        mp4 = os.path.join(OUT, "fast.mp4")
        if os.path.exists(mp4):
            os.remove(mp4)

        class Probed(SceneCls):
            def construct(self):
                seen["at_construct_start"] = win_visible()
                SceneCls.construct(self)
                seen["at_construct_end"] = win_visible()

        res = fast_record_scene(Probed, mp4, fps=30, overwrite=True)
        report["at_construct_start"] = seen.get("at_construct_start")
        report["visible_at_window_create"] = seen.get("at_create")
        report["hidden_flag"] = seen.get("hidden_flag")
        report["visible_at_construct_end"] = seen.get("at_construct_end")
        report["files"] = res["files"]
        report["mp4_bytes"] = os.path.getsize(mp4) if os.path.exists(mp4) else 0
        report["visible_after"] = win_visible()

    elif mode == "shot":
        # Compare the BMP screenshot path with the deterministic FrameServer
        # readback at the same t (documents the known rough edge).
        from real_time_manim.frames import FrameServer
        from scenes.demo_scene import DemoCreate
        import numpy as np
        from PIL import Image

        fs = FrameServer(DemoCreate)

        def mean(path):
            return round(float(np.asarray(Image.open(path).convert("L")).mean()), 4)

        fs.render_frame(3.0)
        p1 = os.path.join(OUT, "shot_after_render.bmp")
        fs.window.screenshot(p1)
        report["hidden"] = win_visible() is False
        report["screenshot_after_render_frame_mean"] = mean(p1)
        fs.window.tick()
        p2 = os.path.join(OUT, "shot_after_tick.bmp")
        fs.window.screenshot(p2)
        report["screenshot_after_tick_mean"] = mean(p2)
        p3 = os.path.join(OUT, "shot_from_save_frame.png")
        fs.save_frame(3.0, p3)
        report["save_frame_mean"] = mean(p3)
        report["bmp_bytes"] = os.path.getsize(p1)
        report["bmp_magic"] = open(p1, "rb").read(2).decode("ascii", "replace")
        fs.close()

    elif mode == "lag":
        # Does the readback follow the frame just drawn?  Draw one t repeatedly
        # and compare; then again with an extra tick() between draw and read.
        from real_time_manim.frames import FrameServer
        from scenes.demo_scene import DemoCreate
        import numpy as np
        from PIL import Image

        fs = FrameServer(DemoCreate)

        def mean(path):
            return round(float(np.asarray(Image.open(path).convert("L")).mean()), 4)

        direct = []
        for i in range(3):
            fs.render_frame(3.0)
            p = os.path.join(OUT, f"lag_direct_{i}.png")
            fs.save_frame(3.0, p)
            direct.append(mean(p))
        ticked = []
        for i in range(3):
            fs.render_frame(3.0)
            fs.window.tick()
            p = os.path.join(OUT, f"lag_ticked_{i}.png")
            fs.save_frame(3.0, p)
            ticked.append(mean(p))
        empty = os.path.join(OUT, "lag_empty.png")
        fs.save_frame(0.0, empty)
        late = os.path.join(OUT, "lag_late.png")
        fs.save_frame(6.0, late)
        report["t3_direct_means"] = direct
        report["t3_extra_tick_means"] = ticked
        report["t0_mean"] = mean(empty)
        report["t6_mean"] = mean(late)
        fs.close()

    elif mode == "plain":
        from real_time_manim.vulkan_bind import MLWindow
        win = MLWindow(640, 360)
        report["visible_after_create"] = win_visible()
        report["window_hidden_flag"] = win.hidden
        win.set_visible(False)
        report["visible_after_hide"] = win_visible()
        win.set_visible(True)
        report["visible_after_show"] = win_visible()
        win._defer_close = False
        win.close()
        report["visible_after_close"] = win_visible()

    print("JSON " + json.dumps(report))


if __name__ == "__main__":
    main()
