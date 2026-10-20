# -*- coding: utf-8 -*-
"""Check that every <video src> in a page resolves to an existing file."""
import io
import os
import re
import sys

WIKI = r"C:\Users\begin\Desktop\RTM-Wiki"


def check(page_md):
    md = io.open(page_md, encoding="utf-8").read()
    assets = os.path.join(os.path.dirname(page_md), "assets")
    bad = 0
    for m in re.finditer(r'src="([^"]+)"', md):
        rel = m.group(1)
        p = os.path.join(os.path.dirname(page_md), rel.replace("/", os.sep))
        ok = os.path.exists(p)
        bad += 0 if ok else 1
        print(("OK  " if ok else "MISS"), rel)
    print("missing:", bad)
    return bad


if __name__ == "__main__":
    total = 0
    for arg in sys.argv[1:]:
        if arg.endswith(".md"):
            total += check(arg)
        else:                                  # page name -> find its md
            for root, dirs, files in os.walk(WIKI):
                if arg + ".md" in files:
                    total += check(os.path.join(root, arg + ".md"))
    sys.exit(1 if total else 0)
