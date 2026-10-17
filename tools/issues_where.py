"""Text-only per-issue diagnosis: where RTM and CE disagree, in ASCII.

    python tools/issues_where.py [--ascii N] [--only substr] [--scale 320x180]
"""
import argparse
import os
import sys

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if REPO not in sys.path:
    sys.path.insert(0, REPO)

from tools.issues_baseline import entries, twin  # noqa: E402
from tools.wiki_diff import compare  # noqa: E402


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--only", default="")
    ap.add_argument("--ascii", type=int, default=1, dest="ascii_frames")
    ap.add_argument("--scale", default="480x270")
    ap.add_argument("--top", type=int, default=4)
    ap.add_argument("--threshold", type=float, default=4.0)
    args = ap.parse_args()
    w, h = args.scale.lower().split("x")
    scale = (int(w), int(h))
    for rtm, desc in entries():
        if args.only and args.only not in rtm:
            continue
        ce = twin(rtm)
        if not (os.path.exists(rtm) and os.path.exists(ce)):
            print(f"### {os.path.basename(rtm)}: missing twin")
            continue
        print(f"### {os.path.basename(rtm)}  [{desc}]")
        compare(rtm, ce, threshold=args.threshold, top=args.top, scale=scale,
                quiet=False, ascii_frames=args.ascii_frames)


if __name__ == "__main__":
    main()
