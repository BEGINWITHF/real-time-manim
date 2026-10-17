"""ASCII diff-map probe (numbers only, never displays an image).

For each CE/RTM pair, prints a coarse grid of per-cell bad-pixel counts, the
bounding box of the disagreement and the per-frame mean.  Used to hand a fix
agent a precise localisation without anyone having to look at a picture.

    python tools/_probe_diffmap.py --pattern 05-线性变换场景 --grid 16
"""
from __future__ import annotations

import argparse
import os
import sys
from pathlib import Path

import numpy as np

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if REPO not in sys.path:
    sys.path.insert(0, REPO)

from tools.wiki_diff import decode  # noqa: E402

sys.stdout.reconfigure(encoding="utf-8", errors="replace")

ROOT = Path(r"C:\Users\begin\Desktop\RTM-Wiki")
THRESH = 4.0
RAMP = " .:-=+*#%@"


def pairs():
    out = []
    for mp4 in ROOT.rglob("*.mp4"):
        if mp4.name.startswith("~$"):
            continue
        rel = str(mp4.relative_to(ROOT)).replace("\\", "/")
        if "/assets/" not in rel or "/RTM output/" not in rel:
            continue
        stem = mp4.stem
        cands = [
            mp4.parent.parent / f"{stem} CE.mp4",
            mp4.parent.parent / "CE" / f"{stem}.mp4",
            mp4.parent.parent / "CE" / f"{stem} CE.mp4",
            mp4.parent.parent.parent / "CE" / f"{stem}.mp4",
            mp4.parent.parent.parent / "CE" / f"{stem} CE.mp4",
            mp4.parent.parent / "ManimCE output" / f"{stem}-manimce.mp4",
        ]
        ce = next((c for c in cands if c.is_file()), None)
        if ce is None:
            continue
        out.append((rel, ce, mp4))
    out.sort()
    return out


def diffmap(ce: Path, rtm: Path, grid: int, limit: int, scale):
    a = decode(str(rtm), scale)
    b = decode(str(ce), scale)
    n = min(len(a), len(b))
    if limit:
        n = min(n, limit)
    a, b = a[:n], b[:n]
    h, w = a.shape[1], a.shape[2]
    gr, gc = max(1, h // grid), max(1, w // grid)
    grids = np.zeros((grid, grid), dtype=np.int64)
    total_bad = 0
    frames = 0
    means = np.zeros(n, dtype=np.float64)
    minr, minc, maxr, maxc = h, w, -1, -1
    for i in range(n):
        d = np.abs(a[i].astype(np.int16) - b[i].astype(np.int16)).max(axis=2)
        means[i] = float(d.mean())
        m = d >= THRESH
        if not m.any():
            continue
        ys, xs = np.nonzero(m)
        minr = min(minr, int(ys.min()))
        maxr = max(maxr, int(ys.max()))
        minc = min(minc, int(xs.min()))
        maxc = max(maxc, int(xs.max()))
        total_bad += int(m.sum())
        frames += 1
        for gy in range(grid):
            y0, y1 = gy * gr, min(h, (gy + 1) * gr)
            if y0 >= h:
                break
            for gx in range(grid):
                x0, x1 = gx * gc, min(w, (gx + 1) * gc)
                if x0 >= w:
                    break
                grids[gy, gx] += int(m[y0:y1, x0:x1].sum())
    return dict(size=(w, h), frames=frames, bad=total_bad,
                mean=float(means.mean()) if n else 0.0,
                fmax=float(means.max()) if n else 0.0,
                worst=int(means.argmax()) if n else -1,
                bbox=None if maxr < 0 else (minc, minr, maxc, maxr),
                grid=grids, curve=means)


def ascii_grid(grids):
    mx = int(grids.max()) or 1
    return ["".join(RAMP[int((int(v) / mx) * (len(RAMP) - 1))]
                    for v in row) for row in grids]


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--grid", type=int, default=16)
    ap.add_argument("--limit", type=int, default=0)
    ap.add_argument("--pattern", default="")
    ap.add_argument("--min-bad", type=int, default=1)
    ap.add_argument("--scale", default="480x270")
    a = ap.parse_args()
    w, h = a.scale.lower().split("x")
    scale = (int(w), int(h))

    rows = []
    for rel, ce, rtm in pairs():
        if a.pattern and a.pattern not in rel:
            continue
        r = diffmap(ce, rtm, a.grid, a.limit, scale)
        if r["bad"] < a.min_bad:
            continue
        rows.append((rel, r))
    rows.sort(key=lambda t: -t[1]["bad"])
    for rel, r in rows:
        print(f"\n=== {rel}")
        print(f"  {r['size'][0]}x{r['size'][1]} frames={r['frames']} "
              f"bad={r['bad']} mean={r['mean']:.3f} worst_f={r['worst']}"
              f"({r['fmax']:.2f}) bbox(x0,y0,x1,y1)={r['bbox']}")
        for line in ascii_grid(r["grid"]):
            print("  " + line)
        print(f"  grid-max={int(r['grid'].max())}")
        c = r["curve"]
        step = max(1, len(c) // 12)
        print("  mean/12ths: " + " ".join(
            f"{float(c[i:i + step].mean()):.2f}" for i in range(0, len(c), step)))
    print(f"\n{len(rows)} pairs with bad>={a.min_bad}")


if __name__ == "__main__":
    main()
