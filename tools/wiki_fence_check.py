"""Markdown fence audit for the wiki.

Catches the class of breakage that made a few pages render as a wall of text:

  * an odd number of ``` fence lines (a fence left open);
  * a Python demo's module docstring (`\"\"\"RTM-Wiki`) sitting *outside* a fence;
  * a closing fence glued to the end of a code line (`...verbose=True)```);
  * Python statements (`class` / `import` / `from ... import` / `def`) outside
    any fence -- markdown then renders the demo as prose/tables.

Usage: python tools/wiki_fence_check.py [--wiki DIR]
Exit code 1 when anything is found.
"""
import argparse
import glob
import io
import os
import re
import sys

WIKI = r"C:\Users\begin\Desktop\RTM-Wiki"
FENCE = chr(96) * 3
PY = re.compile(r"^(class\s+\w+|import\s+\w+|from\s+\S+\s+import|def\s+\w+\()")


def check(md):
    lines = io.open(md, encoding="utf-8").read().splitlines()
    problems = []
    n = sum(1 for l in lines if l.strip().startswith(FENCE))
    if n % 2:
        problems.append("unbalanced fences (%d fence lines)" % n)
    in_f = False
    for i, line in enumerate(lines, 1):
        s = line.strip()
        if s.startswith(FENCE):
            in_f = not in_f
            continue
        if in_f:
            continue
        if line.startswith('"""RTM-Wiki'):
            problems.append("L%d: demo docstring outside a fence" % i)
        if s and not s.startswith(FENCE) and s.endswith(FENCE):
            problems.append("L%d: closing fence glued to code" % i)
        if PY.match(line):
            problems.append("L%d: unfenced python (%s)" % (i, s[:40]))
    return problems


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--wiki", default=WIKI)
    args = ap.parse_args()
    bad = 0
    for md in sorted(glob.glob(os.path.join(args.wiki, "**", "*.md"),
                               recursive=True)):
        rel = os.path.relpath(md, args.wiki)
        if rel.startswith("99-"):
            continue
        problems = check(md)
        if problems:
            bad += 1
            print(rel)
            for p in problems[:6]:
                print("   ", p)
    print("pages with fence problems:", bad)
    return 1 if bad else 0


if __name__ == "__main__":
    sys.exit(main())
