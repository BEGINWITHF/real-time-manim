"""Full RTM-Wiki re-render: every page script through tools/wiki_render.py.

Sequential, one process per page (isolated Vulkan windows), logs per page, then
a `wiki_concat.py --check` / `--fix` pass for every chapter folder.

Usage:
    python tools/wiki_render_all.py [--only SUBSTR] [--dry-run]
"""
import argparse
import glob
import os
import subprocess
import sys
import time

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
WIKI = r"C:\Users\begin\Desktop\RTM-Wiki"
SKIP = ("demo_rtm.py", "_test_swap_vtk.py")


def page_scripts():
    pats = [
        os.path.join(WIKI, "*", "assets", "RTM code", "*.py"),
        os.path.join(WIKI, "*", "*", "assets", "RTM code", "*.py"),
    ]
    seen = {}
    for pat in pats:
        for p in glob.glob(pat):
            if os.path.basename(p) in SKIP:
                continue
            seen[os.path.relpath(p, WIKI)] = p
    return [seen[k] for k in sorted(seen)]


def chapter_folders():
    pats = [os.path.join(WIKI, "*", "assets"), os.path.join(WIKI, "*", "*", "assets")]
    out = set()
    for pat in pats:
        for p in glob.glob(pat):
            if os.path.isdir(os.path.join(p, "RTM output")):
                out.add(os.path.dirname(p))
    return sorted(out)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--only", default=None, help="substring filter on the script path")
    ap.add_argument("--dry-run", action="store_true")
    ap.add_argument("--log", default=os.path.join(REPO, "wiki_render_all.log"))
    args = ap.parse_args()

    scripts = page_scripts()
    if args.only:
        scripts = [s for s in scripts if args.only in s]
    print("pages to render:", len(scripts))
    if args.dry_run:
        for s in scripts:
            print("   ", os.path.relpath(s, WIKI))
        return 0

    env = dict(os.environ)
    env["PYTHONPATH"] = REPO
    env["PYTHONIOENCODING"] = "utf-8"
    started = time.time()
    ok, failed = [], []
    with open(args.log, "w", encoding="utf-8") as log:
        for i, script in enumerate(scripts, 1):
            rel = os.path.relpath(script, WIKI)
            t0 = time.time()
            log.write("\n===== [%d/%d] %s\n" % (i, len(scripts), rel))
            log.flush()
            try:
                proc = subprocess.run(
                    [sys.executable, os.path.join(REPO, "tools", "wiki_render.py"),
                     script, "--keep-going"],
                    cwd=REPO, env=env, capture_output=True, text=True,
                    encoding="utf-8", errors="replace", timeout=1800)
                out = (proc.stdout or "") + (proc.stderr or "")
                log.write(out[-4000:])
                status = "ok" if proc.returncode == 0 else "FAIL(%d)" % proc.returncode
            except subprocess.TimeoutExpired:
                status = "TIMEOUT"
            log.write("\n-- %s in %.1fs\n" % (status, time.time() - t0))
            log.flush()
            print("[%d/%d] %-52s %5.1fs  %s" % (i, len(scripts), rel, time.time() - t0, status))
            (ok if status == "ok" else failed).append(rel)

        print("\n-- concatenation pass")
        for folder in chapter_folders():
            for flag in ("--check",):
                proc = subprocess.run(
                    [sys.executable, os.path.join(REPO, "tools", "wiki_concat.py"),
                     folder, flag],
                    cwd=REPO, env=env, capture_output=True, text=True,
                    encoding="utf-8", errors="replace")
                log.write("\n===== concat %s %s\n%s%s" % (
                    os.path.relpath(folder, WIKI), flag, proc.stdout or "", proc.stderr or ""))
                tail = [l for l in (proc.stdout or "").splitlines() if "stale" in l.lower()]
                if tail:
                    print("   concat %s: %s" % (os.path.relpath(folder, WIKI), tail[0][:110]))

    print("\nrendered ok: %d   failed: %d   total %.1f min"
          % (len(ok), len(failed), (time.time() - started) / 60.0))
    for f in failed:
        print("   FAILED:", f)
    return 1 if failed else 0


if __name__ == "__main__":
    sys.exit(main())
