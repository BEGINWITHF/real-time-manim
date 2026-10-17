"""Baseline / regression sweep over the RTM-Wiki sample pairs.

For every `assets/RTM output/<name>.mp4` there is a twin
`assets/ManimCE output/<name>-manimce.mp4` rendered from the same source and
frame-aligned.  This walks the whole wiki, diffs each pair in parallel, and
prints a table sorted by how badly RTM disagrees with CE -- which is exactly
the issue list in `issues.txt`, but with a number attached to each entry.

    python tools/wiki_sweep.py                  # all 269 pairs, sorted table
    python tools/wiki_sweep.py --only 03-动画    # filter by path substring
    python tools/wiki_sweep.py --min 1.0 --out D # dump worst frames for the bad ones

Store the printed table before and after a fix and diff the two to see the
regression impact of a change.
"""
import argparse
import concurrent.futures as cf
import io
import contextlib
import os
import sys

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if REPO not in sys.path:
    sys.path.insert(0, REPO)

from tools.wiki_diff import compare  # noqa: E402

WIKI = r"C:\Users\begin\Desktop\RTM-Wiki"
DEFAULT_SCALE = (480, 270)


def pairs(wiki=WIKI):
    out = []
    for root, _dirs, files in os.walk(wiki):
        if os.path.basename(root) != "RTM output":
            continue
        ce_dir = os.path.join(os.path.dirname(root), "ManimCE output")
        for f in sorted(files):
            if not f.endswith(".mp4"):
                continue
            rtm = os.path.join(root, f)
            ce = os.path.join(ce_dir, f[:-4] + "-manimce.mp4")
            if os.path.exists(ce):
                out.append((rtm, ce))
    return out


def _one(args):
    rtm, ce, scale, threshold, top = args
    buf = io.StringIO()
    try:
        with contextlib.redirect_stdout(buf):
            mean, diff = compare(rtm, ce, threshold=threshold, top=top,
                                 scale=scale, quiet=True)
    except Exception as exc:
        return (float("nan"), rtm, ce, f"{type(exc).__name__}: {exc}", None)
    detail = buf.getvalue().strip()
    nbig = int((diff > threshold).sum()) if diff is not None else -1
    first = int(np_first(diff, threshold)) if diff is not None else -1
    return (mean, rtm, ce, f"bad_frames={nbig} first_bad={first}", diff)


def np_first(diff, threshold):
    import numpy as np
    idx = np.flatnonzero(diff > threshold)
    return idx[0] if len(idx) else -1


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--only", default="", help="substring filter on the RTM path")
    ap.add_argument("--out", default="", help="dump worst-frame PNGs for pairs >= --min")
    ap.add_argument("--min", type=float, default=1.0)
    ap.add_argument("--threshold", type=float, default=4.0)
    ap.add_argument("--top", type=int, default=6)
    ap.add_argument("--scale", default="480x270")
    ap.add_argument("--jobs", type=int, default=6)
    args = ap.parse_args()

    w, h = args.scale.lower().split("x")
    scale = (int(w), int(h))

    todo = [(r, c, scale, args.threshold, args.top)
            for r, c in pairs() if not args.only or args.only in r]
    rows = []
    with cf.ThreadPoolExecutor(max_workers=args.jobs) as ex:
        for res in ex.map(_one, todo):
            rows.append(res)

    rows.sort(key=lambda r: (r[0] != r[0], -r[0]))
    for mean, rtm, ce, note, _diff in rows:
        print(f"{mean:8.3f}  {os.path.relpath(rtm, WIKI)}  {note}")

    if args.out:
        for mean, rtm, ce, _note, _d in rows:
            if mean == mean and mean >= args.min:
                with contextlib.redirect_stdout(io.StringIO()):
                    compare(rtm, ce,
                            out=os.path.join(args.out,
                                             os.path.relpath(rtm, WIKI)
                                             .replace(os.sep, "__")[:-4]),
                            threshold=args.threshold, top=args.top, scale=scale)
    print(f"\n{len(rows)} pairs compared; "
          f"{sum(1 for r in rows if r[0] == r[0])} ok")


if __name__ == "__main__":
    main()
