# ruff: noqa: F401, F403, F405 -- star imports: the scene table below names every class
"""Batch-record every demo scene to MP4 via screen capture (mss + ffmpeg).

Run from the repository root::

    python -m examples.scenes.recorder

``run_all.py`` is the faster alternative (it reads the Vulkan framebuffer
directly instead of capturing the screen).
"""
from .common import *  # noqa: F401,F403
from .basics import *  # noqa: F401,F403
from .timing import *  # noqa: F401,F403
from .creation import *  # noqa: F401,F403
from .indication import *  # noqa: F401,F403
from .transform import *  # noqa: F401,F403
from .latex import *  # noqa: F401,F403


# ====================================================================
# Download all demo scenes to MP4 (mss screen capture)
# Run: python -m examples.scenes.recorder
# ====================================================================
def main():
    import os, time, subprocess, tempfile, threading, shutil, ctypes, ctypes.wintypes as wt
    import mss
    from PIL import Image

    REPO_ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    OUTPUT_DIR = os.path.join(REPO_ROOT, "downloaded_videos")
    os.makedirs(OUTPUT_DIR, exist_ok=True)

    user32 = ctypes.windll.user32
    _rec_state = [None, None, None, 0, None, None, ""]  # stop, thread, dir, count, mon, sct, path

    def find_win():
        h = user32.FindWindowW(None, "Real Time Manim")
        if not h: return None
        r = wt.RECT(); user32.GetClientRect(h, ctypes.byref(r))
        pt = wt.POINT(0, 0); user32.ClientToScreen(h, ctypes.byref(pt))
        return {"left": pt.x, "top": pt.y, "width": r.right, "height": r.bottom}

    _orig_init = MLWindow.__init__
    _orig_close = MLWindow.close
    _scene_name, _scene_num = "", 0

    def _rec_init(self, w=1920, h=1080):
        global _scene_name, _scene_num
        _orig_init(self, w, h)
        safe = "".join(c if c.isalnum() or c in "._" else "_" for c in _scene_name)
        _rec_state[6] = os.path.join(OUTPUT_DIR, f"{_scene_num:02d}_{safe}.mp4")
        print(f"[{_scene_num:02d}] {_scene_name}  →  {os.path.basename(_rec_state[6])}")
        time.sleep(0.3)
        mon = find_win()
        if not mon: print("     ⚠ window not found"); return
        _rec_state[4], _rec_state[5] = mon, mss.MSS()
        _rec_state[2] = tempfile.mkdtemp(prefix="mb_rec_")
        _rec_state[3] = 0
        _rec_state[0] = threading.Event()
        def worker():
            idx, iv = 0, 1.0 / 30.0
            while not _rec_state[0].is_set():
                t0 = time.time()
                try:
                    f = _rec_state[5].grab(_rec_state[4])
                    img = Image.frombytes("RGB", f.size, f.bgra, "raw", "BGRX")
                    img.save(os.path.join(_rec_state[2], f"f_{idx:06d}.bmp"))
                    idx += 1
                except: pass
                rem = iv - (time.time() - t0)
                if rem > 0: _rec_state[0].wait(rem)
            _rec_state[3] = idx
        _rec_state[1] = threading.Thread(target=worker, daemon=True)
        _rec_state[1].start()

    def _rec_close(self):
        if _rec_state[0] is not None:
            _rec_state[0].set()
            if _rec_state[1]: _rec_state[1].join(timeout=5)
            total = _rec_state[3]
            if total > 0 and _rec_state[2] and _rec_state[6]:
                p = os.path.join(_rec_state[2], "f_%06d.bmp")
                cmd = ["ffmpeg", "-y", "-framerate", "30", "-i", p,
                       "-c:v", "libx264", "-pix_fmt", "yuv420p",
                       "-crf", "18", "-preset", "fast", _rec_state[6]]
                try:
                    subprocess.run(cmd, check=True, capture_output=True)
                    sz = os.path.getsize(_rec_state[6]) / 1024
                    print(f"     ✓ saved ({total} frames, {sz:.0f} KB)")
                except FileNotFoundError:
                    print("     ✗ ffmpeg not found")
                except subprocess.CalledProcessError as e:
                    print(f"     ✗ ffmpeg: {(e.stderr or b'')[:200]}")
            elif total == 0: print("     ⚠ 0 frames")
            _rec_state[0], _rec_state[1] = None, None
            if _rec_state[5]: _rec_state[5].close(); _rec_state[5] = None
            if _rec_state[2]: shutil.rmtree(_rec_state[2], ignore_errors=True)
            _rec_state[2], _rec_state[3], _rec_state[4], _rec_state[6] = None, 0, None, ""
        _orig_close(self)

    MLWindow.__init__ = _rec_init
    MLWindow.close = _rec_close

    # -- cache helpers --
    TEX_CACHE = os.path.join(REPO_ROOT, "tex_cache")
    media_tex = os.path.join(REPO_ROOT, "media", "Tex")

    def restore_tex():
        if not os.path.exists(TEX_CACHE): return
        os.makedirs(media_tex, exist_ok=True)
        for fn in os.listdir(TEX_CACHE):
            s, d = os.path.join(TEX_CACHE, fn), os.path.join(media_tex, fn)
            if not os.path.exists(d): shutil.copy2(s, d)

    def save_tex():
        if not os.path.exists(media_tex): return
        os.makedirs(TEX_CACHE, exist_ok=True)
        for fn in os.listdir(media_tex):
            s, d = os.path.join(media_tex, fn), os.path.join(TEX_CACHE, fn)
            if not os.path.exists(d): shutil.copy2(s, d)

    def clean_media():
        d = os.path.join(REPO_ROOT, "media")
        if os.path.exists(d):
            for _ in range(3):
                try: shutil.rmtree(d); break
                except: time.sleep(0.5)

    ALL_SCENES = [
        (1, "Create", DemoCreate),
        (2, "Write_Unwrite", DemoWriteUnwrite),
        (3, "Transform", DemoTransform),
        (4, "ReplacementTransform", DemoReplacementTransform),
        (5, "FadeIn_FadeOut", DemoFadeInFadeOut),
        (6, "FadeTransform", DemoFadeTransform),
        (7, "Rotating", DemoRotating),
        (8, "TransformMatchingShapes", DemoTransformMatchingShapes),
        (9, "VGroup", DemoVGroup),
        (10, "AllShapes", DemoAllShapes),
        (11, "Succession", DemoSuccession),
        (12, "FadeInShift", DemoFadeInShift),
        (13, "TextFeatures", DemoTextFeatures),
        (14, "Combined", DemoCombined),
        (15, "DefaultAdd", DemoDefaultAdd),
        (16, "AddWithRunTime", DemoAddWithRunTime),
        (17, "LagRatios", DemoLagRatios),
        (18, "ChangeDefaultAnimation", DemoChangeDefaultAnimation),
        (19, "AnimatedBoundary", DemoAnimatedBoundary),
        (20, "TracedPath", DemoTracedPath),
        (21, "DissipatingPath", DemoDissipatingPath),
        (22, "LaggedStart", DemoLaggedStart),
        (23, "LaggedStartMap", DemoLaggedStartMap),
        (24, "SuccessionDots", DemoSuccessionDots),
        (25, "CreateSquare", DemoCreateSquare),
        (26, "DrawBorderThenFill", DemoDrawBorderThenFill),
        (27, "ShowIncreasingSubsets", DemoShowIncreasingSubsets),
        (28, "SpiralIn", DemoSpiralIn),
        (29, "TypeWithCursor", DemoTypeWithCursor),
        (30, "UntypeWithCursor", DemoUntypeWithCursor),
        (31, "Uncreate", DemoUncreate),
        (32, "Unwrite_RevTrue", DemoUnwriteReverseTrue),
        (33, "Unwrite_RevFalse", DemoUnwriteReverseFalse),
        (34, "ShowWrite", DemoShowWrite),
        (35, "ShowWriteReversed", DemoShowWriteReversed),
        (36, "FadeInExample", DemoFadeInExample),
        (37, "FadeOutExample", DemoFadeOutExample),
        (38, "GrowFromCenter", DemoGrowFromCenter),
        (39, "GrowArrow", DemoGrowArrow),
        (40, "GrowFromEdge", DemoGrowFromEdge),
        (41, "GrowFromPoint", DemoGrowFromPoint),
        (42, "SpinInFromNothing", DemoSpinInFromNothing),
        (43, "ApplyingWaves", DemoApplyingWaves),
        (44, "Blinking", DemoBlinking),
        (45, "Circumscribe", DemoCircumscribe),
        (46, "UsingFlash", DemoUsingFlash),
        (47, "FlashOnCircle", DemoFlashOnCircle),
        (48, "FocusOn", DemoFocusOn),
        (49, "UsingIndicate", DemoUsingIndicate),
        (50, "TimeWidthValues", DemoTimeWidthValues),
        (51, "Wiggle", DemoWiggle),
        (52, "Homotopy", DemoHomotopy),
        (53, "MoveAlongPath", DemoMoveAlongPath),
        (54, "ChangeDecimalToValue", DemoChangeDecimalToValue),
        (55, "ChangingDecimal", DemoChangingDecimal),
        (56, "UsingRotate", DemoUsingRotate),
        (57, "RotatingAbout", DemoRotatingAbout),
        (58, "Broadcast", BroadcastExample),
        (59, "SpeedModifier", SpeedModifierExample),
        (60, "SpeedModifierUpdater", SpeedModifierUpdaterExample),
        (61, "SpeedModifierUpdater2", SpeedModifierUpdaterExample2),
        (62, "ApplyMatrix", ApplyMatrixExample),
        (63, "WarpSquare", WarpSquare),
        (64, "ClockwiseTransform", ClockwiseExample),
        (65, "Counterclockwise", CounterclockwiseTransform_vs_Transform),
        (66, "CyclicReplace", DemoCyclicReplace),
        (67, "FadeToColor", DemoFadeToColor),
        (68, "DifferentFadeTransforms", DemoDifferentFadeTransforms),
        (69, "FadeTransformPieces", DemoFadeTransformPieces),
        (70, "MoveToTarget", DemoMoveToTarget),
        (71, "ReplacementTransformOr", DemoReplacementTransformOrTransform),
        (72, "Restore", DemoRestore),
        (73, "ScaleInPlace", DemoScaleInPlace),
        (74, "ShrinkToCenter", DemoShrinkToCenter),
        (75, "TransformPathArc", DemoTransformPathArc),
        (76, "Anagram", DemoAnagram),
        (77, "MatchingEquationParts", DemoMatchingEquationParts),
        (78, "TangentAnimation", DemoTangentAnimation),
        (79, "LatexWithoutLatex", DemoLatexWithoutLatex),
        (80, "FourierTransform", DemoFourierTransform),
        (81, "LorenzButterfly", DemoLorenzButterfly),
    ]

    print("=" * 55)
    print("  Real Time Manim — Download All Demo Scenes")
    print("=" * 55)
    ok, fail = [], []
    for num, name, cls in ALL_SCENES:
        _scene_name, _scene_num = name, num
        restore_tex()
        try:
            s = cls(); s.construct(); ok.append(name)
        except Exception as e:
            fail.append((name, str(e)))
            print(f"     ✗ ERROR: {e}")
        save_tex(); clean_media(); time.sleep(2.0)
    print(); print(f"  Done: {len(ok)}/{len(ALL_SCENES)}")
    for n, e in fail: print(f"    ✗ {n}: {e[:120]}")


if __name__ == "__main__":
    main()
