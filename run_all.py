"""
run_all.py — render every demo scene automatically.

Each scene runs in its OWN subprocess (crash isolation), rendered via the fast
Vulkan framebuffer readback (no visible window, no screen capture), so a single
bad scene cannot stop the rest and the whole run is quick.

Usage:
    python run_all.py            # render all scenes not yet recorded
    python run_all.py --force    # re-render everything
    python run_all.py 3 7 42     # render only those scene numbers
    python run_all.py --list     # show the scene table

Output: downloaded_videos/<NN>_<safe_desc>.mp4
"""
import os
import sys
import subprocess

PROJECT = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, PROJECT)

OUT_DIR = os.path.join(PROJECT, "downloaded_videos")
VENV_PY = r"C:\Users\begin\Documents\envs\venv-manim-live\Scripts\python.exe"
if not os.path.exists(VENV_PY):
    VENV_PY = sys.executable


def _scene_table():
    from run import SCENES
    return SCENES  # list of (num, desc, cls)


def _safe(desc):
    return "".join(c if c.isalnum() or c in "._" else "_" for c in desc)


def _runner_script(num, desc, cls_name):
    out = os.path.join(OUT_DIR, f"{num.zfill(2)}_{_safe(desc)}.mp4")
    return (
        "import sys, os, shutil\n"
        f"sys.path.insert(0, {PROJECT!r})\n"
        "import real_time_manim.vulkan_bind as vb\n"
        f"from scenes.demo_scene import {cls_name}\n"
        f"out = {out!r}\n"
        "os.makedirs(os.path.dirname(out), exist_ok=True)\n"
        "# restore cached LaTeX SVGs so MathTex scenes skip recompiling\n"
        "tex_cache = os.path.join(" + repr(PROJECT) + ", 'tex_cache')\n"
        "media_tex = os.path.join(" + repr(PROJECT) + ", 'media', 'Tex')\n"
        "if os.path.isdir(tex_cache):\n"
        "    os.makedirs(media_tex, exist_ok=True)\n"
        "    for fn in os.listdir(tex_cache):\n"
        "        dst = os.path.join(media_tex, fn)\n"
        "        if not os.path.exists(dst):\n"
        "            shutil.copy2(os.path.join(tex_cache, fn), dst)\n"
        "oi = vb.MLWindow.__init__; oc = vb.MLWindow.close\n"
        "def pi(s, *a, **k):\n"
        "    oi(s, *a, **k)\n"
        "    s.enable_fast_record(out, fps=60, hidden=True)\n"
        "def pc(s):\n"
        "    s._finish_fast_record(); oc(s)\n"
        "vb.MLWindow.__init__ = pi; vb.MLWindow.close = pc\n"
        f"{cls_name}().construct()\n"
        "print('SCENE_DONE')\n"
    )


def render_one(num, desc, cls_name, force):
    out = os.path.join(OUT_DIR, f"{num.zfill(2)}_{_safe(desc)}.mp4")
    if os.path.exists(out) and os.path.getsize(out) > 1000 and not force:
        print(f"[skip] {num}. {desc}")
        return True
    code = _runner_script(num, desc, cls_name.__name__)
    print(f"[render] {num}. {desc}")
    r = subprocess.run([VENV_PY, "-c", code], cwd=PROJECT,
                       capture_output=True, text=True)
    if r.returncode != 0:
        print(f"[FAIL] {num}. {desc} (exit {r.returncode})")
        print("  " + (r.stderr.strip().splitlines() or ["?"])[-1][:160])
        return False
    ok = os.path.exists(out) and os.path.getsize(out) > 1000
    print(f"[{'ok' if ok else 'EMPTY'}] {num}. {desc} -> {os.path.basename(out)}")
    return ok


def main():
    args = sys.argv[1:]
    scenes = _scene_table()
    if "--list" in args:
        for num, desc, _ in scenes:
            print(f"{num:>3}. {desc}")
        return
    force = "--force" in args
    nums = [a for a in args if not a.startswith("-")]
    want = set(nums) if nums else {n for n, _, _ in scenes}

    os.makedirs(OUT_DIR, exist_ok=True)
    done = fail = skip = 0
    for num, desc, cls in scenes:
        if num not in want:
            continue
        out = os.path.join(OUT_DIR, f"{num.zfill(2)}_{_safe(desc)}.mp4")
        if os.path.exists(out) and os.path.getsize(out) > 1000 and not force:
            skip += 1
        elif render_one(num, desc, cls, force):
            done += 1
        else:
            fail += 1
    print("-" * 50)
    print(f"rendered={done} failed={fail} skipped={skip}  (dir: {OUT_DIR})")


if __name__ == "__main__":
    main()
