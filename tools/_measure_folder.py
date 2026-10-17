"""Measure every fragment clip in 03-动画/移动与旋转 vs its ManimCE twin.

Text-only (never views images).  Mirrors tools/issues_baseline.py but works
on a folder of clips instead of the issues.txt table.

    python tools/_measure_folder.py "C:/Users/begin/Desktop/RTM-Wiki/03-动画/移动与旋转"
"""
import argparse
import contextlib
import io
import os
import sys

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if REPO not in sys.path:
    sys.path.insert(0, REPO)

from tools.wiki_diff import compare  # noqa: E402


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("folder")
    ap.add_argument("--scale", default="480x270")
    ap.add_argument("--threshold", type=float, default=4.0)
    args = ap.parse_args()
    w, h = args.scale.lower().split("x")
    scale = (int(w), int(h))

    out_dir = os.path.join(args.folder, "assets", "RTM output")
    ce_dir = os.path.join(args.folder, "assets", "ManimCE output")
    rows = []
    for name in sorted(os.listdir(out_dir)):
        if not name.endswith(".mp4"):
            continue
        base = name[:-4]
        ce = os.path.join(ce_dir, base + "-manimce.mp4")
        if not os.path.exists(ce):
            rows.append((None, base, "NO-CE"))
            continue
        buf = io.StringIO()
        try:
            with contextlib.redirect_stdout(buf):
                mean, diff = compare(os.path.join(out_dir, name), ce,
                                     threshold=args.threshold, top=4,
                                     scale=scale, quiet=True)
            nbig = int((diff > args.threshold).sum())
            rows.append((mean, base, f"bad={nbig}/{len(diff)}"))
        except Exception as exc:
            rows.append((None, base, f"ERR {type(exc).__name__}: {exc}"))

    rows.sort(key=lambda r: (r[0] is None, -(r[0] or 0)))
    for mean, base, tag in rows:
        if mean is None:
            print(f"{'--':>8}  {base}  {tag}")
        else:
            print(f"{mean:8.3f}  {base}  {tag}")


if __name__ == "__main__":
    main()
