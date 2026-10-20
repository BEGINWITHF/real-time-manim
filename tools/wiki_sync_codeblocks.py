"""Sync a page's ```python sample blocks with its demo file (verbatim).

99-写作规范.md 一.3 requires the sample code in the page to be exactly the demo
source.  Hand-editing a page after fixing the demo is error-prone, so this tool
rewrites every ```python fence whose first code line is `class <Name>Demo(...)`
with the demo's own import block + that class's source (the page dedents
nothing; the demo's class body is copied line for line).

Fences that do not start with a class definition (signature blocks, shell
snippets) are left alone.

Usage:  python tools/wiki_sync_codeblocks.py "<page name>" [--write] [--wiki DIR]
"""
import argparse
import io
import os
import re
import sys

WIKI = r"C:\Users\begin\Desktop\RTM-Wiki"
FENCE = re.compile(r"```python\n(.*?)```", re.S)
CLASS = re.compile(r"^class\s+([A-Za-z_]\w*)\s*\(", re.M)


def find_assets(wiki, page):
    for root, dirs, files in os.walk(wiki):
        if os.path.basename(root) == "RTM code" and page + ".py" in files:
            return os.path.dirname(root)
    return None


def demo_parts(src):
    """(import block, {class name: source}) from a demo file."""
    marks = [(m2.start(), m2.group(1)) for m2 in CLASS.finditer(src)]
    head = src[:marks[0][0]] if marks else src
    imports = []
    in_par = False
    for line in head.splitlines():
        if line.startswith(("import ", "from ")):
            imports.append(line)
            in_par = line.rstrip().endswith("(")
        elif in_par:
            imports.append(line)
            if line.rstrip().endswith(")"):
                in_par = False
    classes = {}
    for i, (pos, name) in enumerate(marks):
        end = marks[i + 1][0] if i + 1 < len(marks) else len(src)
        chunk = src[pos:end]
        # drop the trailing SCENES/PAIRS/... tables of the last class
        cut = min([x for x in (chunk.find("\nSCENES = "), chunk.find("\nPAIRS = "),
                              chunk.find("\nPAGE = ")) if x > 0] or [len(chunk)])
        classes[name] = chunk[:cut].rstrip() + "\n"
    return "\n".join(imports) + "\n", classes


def imports_cont(line):
    return False


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("page")
    ap.add_argument("--write", action="store_true")
    ap.add_argument("--wiki", default=WIKI)
    args = ap.parse_args()
    page = args.page
    assets = find_assets(args.wiki, page)
    if assets is None:
        raise SystemExit("RTM demo not found for " + page)
    demo = io.open(os.path.join(assets, "RTM code", page + ".py"),
                   encoding="utf-8").read()
    imports, classes = demo_parts(demo)
    md_path = None
    for p in os.listdir(os.path.dirname(assets)):
        if p == page + ".md":
            md_path = os.path.join(os.path.dirname(assets), p)
    if md_path is None or not os.path.exists(md_path):
        raise SystemExit("page md not found for " + page)
    md = io.open(md_path, encoding="utf-8").read()

    replaced, missing = 0, set(classes)
    def sub(m):
        nonlocal replaced
        body = m.group(1)
        cm = CLASS.search(body)
        if cm is None:
            return m.group(0)
        name = cm.group(1)
        if name not in classes:
            return m.group(0)
        missing.discard(name)
        replaced += 1
        return "```python\n" + imports + "\n" + classes[name] + "```"
    new = FENCE.sub(sub, md)

    print("page:", page)
    print("code blocks replaced:", replaced)
    print("demo classes not used in the page:", sorted(missing) or "none")
    if args.write:
        io.open(md_path, "w", encoding="utf-8", newline="\n").write(new)
        print("written:", md_path)
    return 0


if __name__ == "__main__":
    sys.exit(main())
