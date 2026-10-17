"""Re-render one or more RTM-Wiki sample fragments and refresh `RTM output/`.

The wiki keeps each page's sources in `assets/RTM code/<page>.py`.  Those
scripts render every fragment of the page into `assets/RTM code/final/` and
then concatenate a *subset* into a page video.  Which fragment feeds which
page video is declared in the script's own `SCENES` / `PAIRS` (or `OUTPUTS`)
table, so this tool imports the module and asks it rather than guessing.

    # re-render one fragment and refresh the page video it feeds
    python tools/wiki_render.py "C:/.../assets/RTM code/10-ValueTracker.py" basic

    # re-render the whole page
    python tools/wiki_render.py "C:/.../assets/RTM code/10-ValueTracker.py"

The rendered page video is written straight into `assets/RTM output/`, which
is where the markdown embeds it from (the checked-in scripts still write to
`assets/` directly -- a leftover layout rename -- so we move it).
"""
import argparse
import importlib.util
import os
import shutil
import subprocess
import sys

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if REPO not in sys.path:
    sys.path.insert(0, REPO)

RTM_OUT = "RTM output"


def _load(path):
    spec = importlib.util.spec_from_file_location(
        "_wiki_page_" + str(abs(hash(path))), path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def _outputs(mod):
    """Normalise the page's (out_name, [fragment]) table."""
    table = getattr(mod, "PAIRS", None) or getattr(mod, "OUTPUTS", None)
    if not table:
        # single-fragment page: every scene is its own page video
        return [(name, [name]) for name, _cls in getattr(mod, "SCENES", [])]
    return [(out, list(frags)) for out, frags in table]


def _shared_fragments(here, page_py, mod):
    """Fragments this page declares that a *sibling* page script also declares.

    Several pages share one `final/` directory (`02-Mobject通用/assets/RTM code/`
    holds 16 scripts), so a fragment called `interpolate` or `points` is
    rendered by more than one page into the same file.  In `--refresh-only`
    mode nobody can tell whose render currently sits there, so publishing such
    a name is a coin flip -- skip it instead (the caller must re-render the
    page, which renders and publishes in one pass).
    """
    own = {name for name, _cls in getattr(mod, "SCENES", [])}
    shared = set()
    for f in sorted(os.listdir(here)):
        if not f.endswith(".py") or f.startswith("_probe"):
            continue
        other_py = os.path.join(here, f)
        if os.path.abspath(other_py) == os.path.abspath(page_py):
            continue
        try:
            other = _load(other_py)
        except Exception:
            continue
        for name, _cls in getattr(other, "SCENES", []):
            if name in own:
                shared.add(name)
    return shared


def render(page_py, fragments, keep_going=False, verbose=False,
           refresh_only=False):
    page_py = os.path.abspath(page_py)
    here = os.path.dirname(page_py)
    out_dir = os.path.join(here, "final")
    assets = os.path.dirname(here)
    rtm_out = os.path.join(assets, RTM_OUT)

    if not refresh_only:
        cmd = [sys.executable, page_py, *fragments]
        print("+ " + " ".join(cmd))
        proc = subprocess.run(cmd, cwd=here, capture_output=True, text=True,
                              encoding="utf-8", errors="replace",
                              env={**os.environ,
                                   "PYTHONPATH": REPO,
                                   "PYTHONIOENCODING": "utf-8"})
        if verbose or proc.returncode:
            sys.stdout.write(proc.stdout)
            sys.stderr.write(proc.stderr)
        if proc.returncode and not keep_going:
            raise SystemExit(f"{os.path.basename(page_py)} exited {proc.returncode}")

    mod = _load(page_py)
    page = getattr(mod, "PAGE", "")
    stem = os.path.splitext(os.path.basename(page_py))[0]
    wanted = set(fragments) if fragments else None

    def page_name(out_name):
        # the stock scripts build "%s-%s.mp4" % (PAGE, out_name); a few pages
        # have no PAGE constant and already carry the full name.
        if page:
            return f"{page}-{out_name}"
        # No PAGE.  A couple of scripts carry *bare* PAIRS names while the wiki
        # embeds `<script stem>-<out>.mp4` (`01-MovingCameraScene.py`'s
        # `camera_class` / `random_seed` / `camera_frame`).  Publishing the bare
        # name would create a clip nobody links to and leave the embedded one
        # unrefreshed forever, so prefer the name that already exists.
        stem_name = f"{stem}-{out_name}"
        if os.path.exists(os.path.join(rtm_out, stem_name + ".mp4")):
            return stem_name
        return out_name

    refreshed = []
    claimed = set()
    shared = _shared_fragments(here, page_py, mod) if refresh_only else set()
    for out_name, frags in _outputs(mod):
        if wanted and not (wanted & set(frags)):
            continue
        if refresh_only and (set(frags) & shared):
            print(f"  !! {out_name}: fragment(s) {sorted(set(frags) & shared)} "
                  f"are shared with a sibling page; skipping refresh-only "
                  f"publish (re-render this page to publish it)")
            continue
        srcs = [os.path.join(out_dir, f + ".mp4") for f in frags]
        if not all(os.path.exists(p) for p in srcs):
            print(f"  !! missing fragment render for {out_name}: {srcs}")
            continue
        os.makedirs(rtm_out, exist_ok=True)
        dst = os.path.join(rtm_out, page_name(out_name) + ".mp4")
        if len(srcs) == 1:
            shutil.copy2(srcs[0], dst)
        else:
            lst = os.path.join(out_dir, "concat.txt")
            with open(lst, "w", encoding="utf-8") as fh:
                for p in srcs:
                    fh.write("file '%s'\n" % p)
            subprocess.run(
                ["ffmpeg", "-y", "-loglevel", "error", "-f", "concat",
                 "-safe", "0", "-i", lst, "-c", "copy", dst], check=True)
        refreshed.append(dst)
        claimed.add(os.path.basename(dst))
        print(f"  -> {dst}  ({os.path.getsize(dst)} bytes)")

    # Scenes that PAIRS does not declare still render into `final/`, and the
    # wiki embeds them as `<PAGE>-<scene>.mp4` -- `01-场景与相机/专用场景` ships
    # `02-ThreeDScene-camera/-fixed/-rotation/-special` and
    # `05-线性变换场景-apply/-nonlinear/-compose` that way.  Before this, they
    # were copied once by hand and then went stale forever: PAIRS covered only
    # the concatenated `ctor` output, so re-rendering the page silently left
    # every other embedded clip at its old render.  Refresh any such clip that
    # is already published (never create new files -- sub-scenes that feed a
    # concatenated output must not leak into `RTM output/`).
    if wanted is None and os.path.isdir(rtm_out):
        published = [f for f in os.listdir(rtm_out) if f.endswith(".mp4")]
        stem = os.path.splitext(os.path.basename(page_py))[0]
        prefixes = [p for p in (getattr(mod, "PAGE", ""), stem) if p]
        # A scene that feeds a PAIRS output (a concat fragment) must never be
        # published on its own: `01-MovingCameraScene`'s `camera_class_moving` /
        # `camera_class_plain` are the two halves of the embedded
        # `...-camera_class.mp4`, and re-publishing them leaves `RTM output/`
        # with clips that have no ManimCE twin at all.
        fragments = {f for _out, frags in _outputs(mod) for f in frags}
        for scene_name, _cls in getattr(mod, "SCENES", []):
            if refresh_only and scene_name in shared:
                print(f"  !! {scene_name}: scene clip shared with a sibling "
                      f"page; skipping refresh-only publish")
                continue
            if scene_name in fragments:
                continue
            src = os.path.join(out_dir, scene_name + ".mp4")
            if not os.path.exists(src):
                continue
            # The published clip is `<prefix>-<scene>.mp4` when the page leaves
            # PAGE empty and carries the prefix in its PAIRS names instead, so
            # match what already exists rather than guessing a prefix -- but
            # only for *this* page's prefix: a bare `endswith("-interpolate")`
            # matched the sibling page's clip too and copied one page's render
            # over another's (02-Mobject通用 shares one `final/`).
            for name in published:
                if name in claimed:
                    continue
                if name == scene_name + ".mp4":
                    pass
                elif name.endswith("-" + scene_name + ".mp4") and any(
                        name.startswith(p + "-") for p in prefixes):
                    pass
                else:
                    continue
                dst = os.path.join(rtm_out, name)
                if os.path.getmtime(src) >= os.path.getmtime(dst):
                    shutil.copy2(src, dst)
                    refreshed.append(dst)
                    print(f"  -> {dst}  ({os.path.getsize(dst)} bytes, scene clip)")

    # Pages with no SCENES/PAIRS/OUTPUTS table are single-clip scripts that
    # still write straight into `assets/` (the pre-"RTM output/" layout) --
    # `03-动画/通用/01-生命周期与公共参数.py` is one.  Move their product into
    # the directory the markdown embeds from.
    if not _outputs(mod) and not getattr(mod, "SCENES", []):
        stem = os.path.splitext(os.path.basename(page_py))[0]
        stray = os.path.join(assets, stem + ".mp4")
        dst = os.path.join(rtm_out, stem + ".mp4")
        if os.path.exists(stray) and os.path.exists(dst):
            if os.path.getmtime(stray) >= os.path.getmtime(dst):
                os.makedirs(rtm_out, exist_ok=True)
                shutil.move(stray, dst)
                refreshed.append(dst)
                print(f"  -> {dst}  ({os.path.getsize(dst)} bytes, single-clip page)")

    # the stock scripts drop a copy next to themselves and/or in assets/ --
    # keep both places clean.  `01-MovingCameraScene.py` concatenates into its
    # *own* directory (`dst = os.path.join(HERE, ...)`) with bare PAIRS names,
    # which used to leave `RTM code/camera_class.mp4`-style duplicates behind.
    for out_name, _f in _outputs(mod):
        for stray in (os.path.join(assets, out_name + ".mp4"),
                      os.path.join(assets, page_name(out_name) + ".mp4"),
                      os.path.join(here, out_name + ".mp4"),
                      os.path.join(here, page_name(out_name) + ".mp4")):
            if os.path.exists(stray):
                os.remove(stray)
    return refreshed


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("page_py", help="path to assets/RTM code/<page>.py")
    ap.add_argument("fragments", nargs="*",
                    help="fragment names from the page's SCENES table")
    ap.add_argument("--keep-going", action="store_true")
    ap.add_argument("-v", "--verbose", action="store_true")
    ap.add_argument("--refresh-only", action="store_true",
                    help="do not run the page script; just re-publish whatever "
                         "already sits in final/ into RTM output/")
    args = ap.parse_args()
    render(args.page_py, args.fragments, args.keep_going, args.verbose,
           refresh_only=args.refresh_only)


if __name__ == "__main__":
    main()
