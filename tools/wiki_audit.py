"""Audit the RTM-Wiki against 99-写作规范.md.

Checks (per page md, per chapter folder):

* the page's RTM / ManimCE demo sources exist (and, per chapter, a
  ``manimce_shim.py`` next to the CE sources);
* every ``<video src>`` resolves (no broken links);
* a PAGE never embeds a CE video (`ManimCE output` / ``-manimce.mp4``);
* no ``> 状态：`` line in the page body;
* no ManimCE code block / "ManimCE 等价写法" section in the body;
* every clip under ``assets/RTM output/`` (except the legacy ``sample.mp4``)
  is referenced by some md in that chapter, and has a ``-manimce`` twin;
* ``assets/README.md`` exists wherever there are videos.

Writes a UTF-8 report (the console cannot print the Chinese paths).

Usage:  python tools/wiki_audit.py [--wiki DIR] [--report FILE]
"""
import argparse
import glob
import io
import os
import re
import sys

WIKI = r"C:\Users\begin\Desktop\RTM-Wiki"
VIDEO_RE = re.compile(r'<video\s+src="([^"]+)"')
STATUS_RE = re.compile(r'^\s*>\s*状态[：:]', re.M)
CE_CODE_RE = re.compile(r'```(?:python|py)\b[^`]*?from\s+manim\s+import', re.S)
CE_MENTION_RE = re.compile(r'ManimCE')
CODE_BLOCK_RE = re.compile(r'```(?:python|py)\n(.*?)```', re.S)
LEGACY = ("sample.mp4",)

# pages that legitimately talk about ManimCE itself
CE_PAGE_OK = ("04-ManimCE命令行速查",)

SKIP_DIRS = ("assets", ".git")


def md_files(wiki):
    out = []
    for root, dirs, files in os.walk(wiki):
        dirs[:] = [d for d in dirs if d not in SKIP_DIRS]
        for f in files:
            if f.endswith(".md"):
                out.append(os.path.join(root, f))
    return sorted(out)


def is_page(path):
    base = os.path.basename(path)
    return not base.startswith("README") and not base.startswith("99-") \
        and not base.startswith("98-") and not base.startswith("97-")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--wiki", default=WIKI)
    ap.add_argument("--report", default=os.path.join(
        os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
        "wiki_audit.txt"))
    args = ap.parse_args()

    wiki = args.wiki
    problems = []
    notes = []
    pages = [p for p in md_files(wiki) if is_page(p)]

    # chapter folders = any dir with an assets/RTM output/
    chapters = []
    for root, dirs, files in os.walk(wiki):
        if os.path.isdir(os.path.join(root, "assets", "RTM output")):
            chapters.append(root)

    for page in pages:
        rel = os.path.relpath(page, wiki)
        name = os.path.splitext(os.path.basename(page))[0]
        folder = os.path.dirname(page)
        assets = os.path.join(folder, "assets")
        try:
            text = io.open(page, encoding="utf-8").read()
        except Exception as e:
            problems.append("%s | cannot read: %s" % (rel, e))
            continue

        if STATUS_RE.search(text):
            problems.append("%s | has a '> 状态：' line (规范 一.5)" % rel)

        if name not in CE_PAGE_OK and "ManimCE-等价" in text:
            problems.append("%s | has a ManimCE 等价写法 section" % rel)

        for m in CE_CODE_RE.finditer(text):
            chunk = text[max(0, m.start() - 200):m.start() + 200]
            if "manimce_shim" in chunk or "-manimce" in chunk:
                problems.append("%s | ManimCE code block in the page body (规范 一.6)" % rel)
                break

        # videos
        for src in VIDEO_RE.findall(text):
            target = os.path.normpath(os.path.join(folder, src))
            if not os.path.exists(target):
                problems.append("%s | broken <video> link: %s" % (rel, src))
            if "ManimCE output" in src or src.endswith("-manimce.mp4"):
                problems.append("%s | embeds a CE video (规范 二): %s" % (rel, src))

        # sources present?
        rtm_src = os.path.join(assets, "RTM code", name + ".py")
        ce_src = os.path.join(assets, "ManimCE code", name + "-manimce.py")
        if os.path.isdir(assets):
            if not os.path.exists(rtm_src):
                problems.append("%s | missing assets/RTM code/%s.py" % (rel, name))
            if not os.path.exists(ce_src):
                problems.append("%s | missing assets/ManimCE code/%s-manimce.py"
                                % (rel, name))
            shim = os.path.join(assets, "ManimCE code", "manimce_shim.py")
            if not os.path.exists(shim):
                problems.append("%s | chapter has no ManimCE code/manimce_shim.py" % rel)

        if CE_MENTION_RE.search(text) and name not in CE_PAGE_OK:
            for line_no, line in enumerate(text.splitlines(), 1):
                if "ManimCE" in line:
                    notes.append("%s:%d | ManimCE mention in body: %s"
                                 % (rel, line_no, line.strip()[:90]))

        # 一.3: the sample code blocks must be verbatim from the demo script
        # (the page dedents the block, so compare stripped lines)
        if os.path.exists(rtm_src):
            demo_lines = {l.strip() for l in
                          io.open(rtm_src, encoding="utf-8").read().splitlines()}
            for block in CODE_BLOCK_RE.findall(text):
                for line in block.strip().splitlines():
                    s = line.strip()
                    if not s or s in demo_lines:
                        continue
                    if s.startswith(("def ", "from ", "import ", "class ")):
                        continue
                    if re.match(r"^[A-Za-z_][A-Za-z0-9_]*(\s*,\s*[A-Za-z_][A-Za-z0-9_]*)*,?$", s):
                        continue                                # import continuation
                    if re.match(r"^[A-Z]\w*\(", s):            # signature block
                        continue
                    notes.append("%s | code block line not found in the demo "
                                 "(may be an API/config listing, not a sample "
                                 "excerpt): %s" % (rel, s[:60]))

    # clips
    for chapter in chapters:
        rel = os.path.relpath(chapter, wiki)
        out_dir = os.path.join(chapter, "assets", "RTM output")
        ce_dir = os.path.join(chapter, "assets", "ManimCE output")
        clips = sorted(glob.glob(os.path.join(out_dir, "*.mp4")))
        page_mds = [p for p in glob.glob(os.path.join(chapter, "*.md"))
                    if is_page(p)]
        # A clip may legitimately live only in a chapter README (the
        # `03-动画/移动与旋转` 合集 videos are embedded by the chapter index, not
        # by a page): every markdown file in the chapter -- READMEs included --
        # counts as a reference, otherwise a cleanup deletes a clip the wiki
        # still links to.
        ref_mds = page_mds + sorted(
            p for p in glob.glob(os.path.join(chapter, "**", "*.md"), recursive=True)
            if not is_page(p))
        text = ""
        for p in ref_mds:
            try:
                text += io.open(p, encoding="utf-8").read()
            except Exception:
                pass
        for clip in clips:
            base = os.path.basename(clip)
            if base in LEGACY:
                continue
            if base not in text:
                problems.append("%s | clip never referenced by a page: %s" % (rel, base))
            ce = os.path.join(ce_dir, base[:-4] + "-manimce.mp4")
            if not os.path.exists(ce):
                notes.append("%s | no CE twin for %s" % (rel, base))
        readme = os.path.join(chapter, "assets", "README.md")
        if clips and not os.path.exists(readme):
            problems.append("%s | assets/README.md missing" % rel)

    with io.open(args.report, "w", encoding="utf-8") as fh:
        fh.write("# wiki audit vs 99-写作规范.md\n")
        fh.write("pages: %d, chapters: %d\n\n" % (len(pages), len(chapters)))
        fh.write("## violations (%d)\n" % len(problems))
        for p in problems:
            fh.write("- %s\n" % p)
        fh.write("\n## notes (%d)\n" % len(notes))
        for n in notes:
            fh.write("- %s\n" % n)
    print("pages=%d chapters=%d violations=%d notes=%d -> %s"
          % (len(pages), len(chapters), len(problems), len(notes), args.report))
    return 0


if __name__ == "__main__":
    sys.exit(main())
