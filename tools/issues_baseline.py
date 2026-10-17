"""Numeric baseline for every entry in Desktop\\issues.txt.

Pairs each `path.mp4` line with its ManimCE twin and prints the mean |diff|
plus how many frames cross the threshold -- the objective stand-in for
"watching the clip".  Text-only by design.

    python tools/issues_baseline.py            # baseline table
    python tools/issues_baseline.py --only 10  # only entries whose path has "10"
    python tools/issues_baseline.py --ascii 2  # text diagnosis of 2 worst frames
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

ISSUES = os.path.join(os.path.expanduser("~"), "Desktop", "issues.txt")
SCALE = (480, 270)


def entries(path=ISSUES):
    with open(path, encoding="utf-8") as fh:
        lines = [ln.strip() for ln in fh]
    out = []
    for i, ln in enumerate(lines):
        if ln.startswith('"') and ln.lower().endswith('.mp4"'):
            p = ln.strip('"')
            desc = lines[i + 1] if i + 1 < len(lines) else ""
            out.append((p, desc))
    return out


def twin(rtm):
    d, base = os.path.split(rtm)
    ce_dir = os.path.join(os.path.dirname(d), "ManimCE output")
    return os.path.join(ce_dir, base[:-4] + "-manimce.mp4")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--only", default="", help="substring filter on the path")
    ap.add_argument("--idx", default="", help="comma separated entry indexes")
    ap.add_argument("--ascii", type=int, default=0, dest="ascii_frames")
    ap.add_argument("--scale", default="480x270")
    ap.add_argument("--threshold", type=float, default=4.0)
    args = ap.parse_args()
    w, h = args.scale.lower().split("x")
    scale = (int(w), int(h))

    want = ({int(x) for x in args.idx.split(",") if x.strip()}
            if args.idx else None)
    for i, (rtm, desc) in enumerate(entries()):
        if args.only and args.only not in rtm:
            continue
        if want is not None and i not in want:
            continue
        ce = twin(rtm)
        tag = os.path.basename(rtm)[:-4]
        if not os.path.exists(rtm):
            print(f"{'MISSING':>8}  {tag}  (rtm not found)")
            continue
        if not os.path.exists(ce):
            print(f"{'NO-CE':>8}  {tag}  ({desc})")
            continue
        buf = io.StringIO()
        try:
            with contextlib.redirect_stdout(buf):
                mean, diff = compare(rtm, ce, threshold=args.threshold,
                                     top=4, scale=scale, quiet=True)
            nbig = int((diff > args.threshold).sum())
            print(f"{mean:8.3f}  {tag}  bad={nbig}/{len(diff)}  {desc}")
        except Exception as exc:
            print(f"{'ERR':>8}  {tag}  {type(exc).__name__}: {exc}")
        if args.ascii_frames:
            with contextlib.redirect_stdout(io.StringIO()):
                compare(rtm, ce, threshold=args.threshold, top=4,
                        scale=scale, quiet=False,
                        ascii_frames=args.ascii_frames)


if __name__ == "__main__":
    main()
