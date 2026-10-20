"""Rebuild stale page-level concat videos in the RTM-Wiki.

Every wiki page script (`assets/RTM code/<page>.py`) renders its fragments
into `assets/RTM code/final/` and concatenates a *subset* of them into the
page video that the markdown embeds from `assets/RTM output/`.  When a single
fragment is re-rendered by hand (or by `tools/wiki_render.py <script> <frag>`)
the page video keeps whatever it was built from -- it silently goes stale and
carries the old, broken fragment forever.

This tool re-derives the fragment list from the page script's own
`SCENES` / `PAIRS` / `OUTPUTS` table (the same source of truth
`tools/wiki_render.py` uses), compares mtimes, and rebuilds only what is
newer than its page video.

    python tools/wiki_concat.py --check                     # report only
    python tools/wiki_concat.py --fix                       # rebuild stale ones
    python tools/wiki_concat.py --fix "03-动画/移动与旋转"   # one folder
    python tools/wiki_concat.py --fix --force "..."         # rebuild everything

Whole-page videos
-----------------
A few pages also embed a *whole-page* video (`assets/RTM output/<PAGE>.mp4`)
which no table in the page script declares -- it is a leftover build artifact
from when the page script concatenated every fragment itself.  Those go stale
silently: `03-动画/移动与旋转/README.md` even carried a warning that
`01-旋转.mp4` (540 frames) predated the 10-16 re-render of its own fragments
(186+174+186 = 546).  `--pages` rebuilds them from the page's `PAIRS` fragments,
and rebuilds the ManimCE twin from the *same* fragment list so the two sides
stay frame-aligned (they were originally built together and had drifted apart
on both sides).

    python tools/wiki_concat.py --pages --check "03-动画/移动与旋转"
    python tools/wiki_concat.py --pages --fix  "03-动画/移动与旋转"

Text only: prints a table, never opens media.
"""
import argparse
import importlib.util
import os
import subprocess
import sys

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if REPO not in sys.path:
    sys.path.insert(0, REPO)

WIKI = r"C:\Users\begin\Desktop\RTM-Wiki"
RTM_OUT = "RTM output"


def _load(path):
    spec = importlib.util.spec_from_file_location(
        "_wiki_concat_" + str(abs(hash(path))), path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def _outputs(mod):
    """Normalise the page's (out_name, [fragment]) table."""
    table = getattr(mod, "PAIRS", None) or getattr(mod, "OUTPUTS", None)
    if not table:
        return [(name, [name]) for name, _cls in getattr(mod, "SCENES", [])]
    return [(out, list(frags)) for out, frags in table]


def _page_name(mod, out_name):
    page = getattr(mod, "PAGE", "")
    return f"{page}-{out_name}" if page else out_name


def find_page_scripts(folder):
    """Every `assets/RTM code/<page>.py` under `folder` (recursive)."""
    out = []
    for root, dirs, files in os.walk(folder):
        norm = root.replace("/", "\\")
        if norm.endswith(os.path.join("assets", "RTM code")):
            for f in files:
                if f.endswith(".py") and not f.startswith("_"):
                    out.append(os.path.join(root, f))
    return sorted(out)


def plan(page_py, force=False):
    """Yield (status, page_video, [sources], mtime info) for one page script."""
    mod = _load(page_py)
    here = os.path.dirname(os.path.abspath(page_py))
    out_dir = os.path.join(here, "final")
    per_page = os.path.join(out_dir, os.path.splitext(os.path.basename(page_py))[0])
    if os.path.isdir(per_page):             # newer scripts: per-page fragments
        out_dir = per_page
    rtm_out = os.path.join(os.path.dirname(here), RTM_OUT)
    # Several pages share one `final/` dir, so a fragment called `points`,
    # `coords` or `interpolate` may have been written by a *sibling* page after
    # this page published.  Its mtime looks "newer" but the bytes are another
    # page's render -- rebuilding from it would corrupt this clip.  Skip those.
    try:
        from tools.wiki_render import _shared_fragments
        shared = _shared_fragments(here, os.path.abspath(page_py), mod)
    except Exception:
        shared = set()
    for out_name, frags in _outputs(mod):
        page_vid = os.path.join(rtm_out, _page_name(mod, out_name) + ".mp4")
        srcs = [os.path.join(out_dir, f + ".mp4") for f in frags]
        missing = [p for p in srcs if not os.path.exists(p)]
        if missing:
            yield ("no-src", page_vid, srcs, missing)
            continue
        if set(frags) & shared:
            yield ("shared", page_vid, srcs, sorted(set(frags) & shared))
            continue
        if not os.path.exists(page_vid):
            yield ("absent", page_vid, srcs, [])
            continue
        dst_m = os.path.getmtime(page_vid)
        newest = max(os.path.getmtime(p) for p in srcs)
        if newest > dst_m or force:
            yield ("stale", page_vid, srcs,
                   [os.path.basename(p) for p in srcs
                    if os.path.getmtime(p) > dst_m])
        else:
            yield ("fresh", page_vid, srcs, [])


def rebuild(page_vid, srcs):
    os.makedirs(os.path.dirname(page_vid), exist_ok=True)
    if len(srcs) == 1:
        data = open(srcs[0], "rb").read()
        with open(page_vid, "wb") as fh:
            fh.write(data)
        return
    lst = page_vid + ".concat.txt"
    with open(lst, "w", encoding="utf-8") as fh:
        for p in srcs:
            fh.write("file '%s'\n" % os.path.abspath(p))
    subprocess.run(
        ["ffmpeg", "-y", "-loglevel", "error", "-f", "concat",
         "-safe", "0", "-i", lst, "-c", "copy", page_vid], check=True)
    os.remove(lst)


def frames(path):
    """Frame count of a video (None when unreadable)."""
    if not os.path.exists(path):
        return None
    try:
        out = subprocess.run(
            ["ffprobe", "-v", "error", "-select_streams", "v:0",
             "-show_entries", "stream=nb_frames", "-of", "csv=p=0", path],
            capture_output=True, text=True, check=True).stdout.strip()
        return int(out.splitlines()[0])
    except Exception:
        return None


def page_plan(page_py):
    """(page_name, [(dst, [srcs])]) for the whole-page videos of one script.

    The whole-page video is every fragment in `PAIRS` order -- the recipe the
    page scripts' own `__main__` uses for the per-output concats, and the one
    the wiki's page video was originally built with.  The ManimCE twin is
    rebuilt from the same fragment list so the pair stays frame-aligned.
    """
    mod = _load(page_py)
    table = getattr(mod, "PAIRS", None) or getattr(mod, "OUTPUTS", None)
    if not table:
        return None
    page = getattr(mod, "PAGE", "")
    if not page:
        return None
    here = os.path.dirname(os.path.abspath(page_py))
    assets = os.path.dirname(here)
    rtm_out = os.path.join(assets, RTM_OUT)
    ce_out = os.path.join(assets, "ManimCE output")

    frags = [f for _out, names in table for f in names]
    per_page = os.path.join(here, "final", os.path.splitext(os.path.basename(page_py))[0])
    rtm_srcs = []
    for f in frags:
        cands = [os.path.join(rtm_out, f"{page}-{f}.mp4"),          # wiki_render naming
                 os.path.join(per_page, f + ".mp4"),                # per-page fragments
                 os.path.join(here, "final", f + ".mp4"),           # shared fragments
                 os.path.join(rtm_out, f + ".mp4")]                 # old layout
        rtm_srcs.append(next((c for c in cands if os.path.exists(c)), cands[0]))
    ce_srcs = []
    for f in frags:
        cands = [os.path.join(ce_out, f"{page}-{f}-manimce.mp4"),
                 os.path.join(ce_out, f + "-manimce.mp4")]
        ce_srcs.append(next((c for c in cands if os.path.exists(c)), cands[0]))
    return page, [(os.path.join(rtm_out, page + ".mp4"), rtm_srcs),
                  (os.path.join(ce_out, page + "-manimce.mp4"), ce_srcs)]


def do_pages(folder, fix=False, force=False):
    for page_py in find_page_scripts(folder):
        rel = page_py.replace(WIKI, "").lstrip("\\")
        try:
            plan_ = page_plan(page_py)
        except Exception as exc:
            print(f"ERR   {rel}: {type(exc).__name__}: {exc}")
            continue
        if not plan_:
            continue
        page, pairs = plan_
        for dst, srcs in pairs:
            missing = [s for s in srcs if not os.path.exists(s)]
            if missing:
                print(f"NO-SRC {os.path.basename(dst)}  "
                      f"(missing: {', '.join(os.path.basename(m) for m in missing)})")
                continue
            want = sum(frames(s) or 0 for s in srcs)
            have = frames(dst)
            if have is None and not os.path.exists(dst):
                if fix:
                    rebuild(dst, srcs)
                    print(f"NEW    {os.path.basename(dst)}  "
                          f"({frames(dst)} frames from {len(srcs)} fragments)")
                else:
                    print(f"absent {os.path.basename(dst)}  "
                          f"(fragments sum to {want}; embeds nothing today)")
                continue
            if have == want and not force:
                print(f"fresh  {os.path.basename(dst)}  ({have} frames)")
                continue
            if fix:
                rebuild(dst, srcs)
                print(f"FIXED  {os.path.basename(dst)}  {have} -> {frames(dst)} frames "
                      f"(= sum of {len(srcs)} fragments)")
            else:
                print(f"STALE  {os.path.basename(dst)}  {have} frames, "
                      f"fragments sum to {want}")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("folder", nargs="?", default=WIKI)
    ap.add_argument("--check", action="store_true", help="report only")
    ap.add_argument("--fix", action="store_true", help="rebuild stale page videos")
    ap.add_argument("--force", action="store_true", help="rebuild every one")
    ap.add_argument("--pages", action="store_true",
                    help="handle the whole-page <PAGE>.mp4 artifacts instead "
                         "of the per-output PAIRS videos")
    args = ap.parse_args()

    if args.pages:
        do_pages(args.folder, fix=args.fix and not args.check, force=args.force)
        return

    fix = args.fix and not args.check
    counts = {"fresh": 0, "stale": 0, "absent": 0, "no-src": 0, "shared": 0}
    rebuilt = []
    for page_py in find_page_scripts(args.folder):
        rel = page_py.replace(WIKI, "").lstrip("\\")
        try:
            rows = list(plan(page_py, force=args.force))
        except Exception as exc:
            print(f"ERR   {rel}: {type(exc).__name__}: {exc}")
            continue
        for status, page_vid, srcs, extra in rows:
            counts[status] += 1
            name = os.path.basename(page_vid)
            if status == "fresh":
                continue
            if status == "stale" and fix:
                try:
                    rebuild(page_vid, srcs)
                    rebuilt.append(name)
                    print(f"FIXED {name}  <- {', '.join(os.path.basename(s) for s in srcs)}")
                except Exception as exc:
                    print(f"ERR   {name}: {type(exc).__name__}: {exc}")
            elif status == "shared":
                print(f"SHARED {name}  (fragment(s) {', '.join(extra)} come "
                      f"from a sibling page -- re-render this page to refresh)")
            elif status == "no-src":
                print(f"NO-SRC {name}  (missing: {', '.join(os.path.basename(e) for e in extra)})")
            else:
                note = f"  (newer: {', '.join(extra)})" if extra else ""
                print(f"{status.upper():5} {name}{note}")

    print(f"\nchecked={sum(counts.values())}  fresh={counts['fresh']}  "
          f"stale={counts['stale']}  absent={counts['absent']}  "
          f"no-src={counts['no-src']}  shared={counts['shared']}  "
          f"rebuilt={len(rebuilt)}")
    if counts["stale"] and not fix:
        print("run again with --fix to rebuild the stale ones")


if __name__ == "__main__":
    main()
