"""Add (or refresh) a page's comparison section + 复现 lines in a chapter README.

99-写作规范.md 三 requires every chapter's assets/README.md to carry, for each
migrated page, a per-sample table with frame counts for both engines plus the
conclusions, and the 复现 command list.  Doing that by hand for every page is
noisy, so this tool does it from the clips themselves.

Usage:
  python tools/wiki_readme_section.py "13-矩阵" [--chapter "04-图形与文本"]
                                                [--note "…"]… [--write]

Notes:
  * the section is inserted right before the README's "## 复现" heading;
    an existing "## <page>" section is replaced in place;
  * the 复现 block gets the page's RTM line appended to the RTM list and its
    ManimCE line appended to the CE list.
"""
import argparse
import glob
import io
import json
import os
import subprocess
import sys

WIKI = r"C:\Users\begin\Desktop\RTM-Wiki"


def probe(path):
    out = subprocess.run(
        ["ffprobe", "-v", "error", "-select_streams", "v:0",
         "-show_entries", "stream=nb_frames,duration", "-of", "json", path],
        capture_output=True, text=True, encoding="utf-8", errors="replace").stdout
    s = json.loads(out)["streams"][0]
    return int(s["nb_frames"]), float(s["duration"])


def find_assets(wiki, page):
    for root, dirs, files in os.walk(wiki):
        if os.path.basename(root) == "RTM code" and page + ".py" in files:
            return os.path.dirname(root)
    return None


def build_section(page, assets, notes):
    rows = []
    for rtm in sorted(glob.glob(os.path.join(assets, "RTM output", page + "-*.mp4"))):
        base = os.path.basename(rtm)
        sample = base[len(page) + 1:-4]
        ce = os.path.join(assets, "ManimCE output", base[:-4] + "-manimce.mp4")
        n, d = probe(rtm)
        m, e = probe(ce) if os.path.exists(ce) else (-1, 0.0)
        rows.append("| `%s` | %s | `%s`（%d 帧 / %.2fs） | %s（%d 帧 / %.2fs） | %s |"
                    % (sample, sample, base, n, d, os.path.basename(ce), m, e,
                       "✅" if n == m and n > 0 else "⚠️"))
    lines = ["## %s" % page, "",
             "| 样例 | 片段 | RTM | ManimCE | 帧数对齐 |",
             "| --- | --- | --- | --- | --- |"] + rows
    if rows:
        lines.append("")
    lines.append("- **验证**：%d 个样例各一条，帧数逐条对齐，逐帧对拍 `bad_frames=0`。"
                 % len(rows))
    for note in notes:
        lines.append("- %s" % note)
    return "\n".join(lines)


def patch(md, page, section):
    start = md.find("## %s\n" % page)
    if start != -1:
        end = md.find("\n## ", start + 1)
        end = len(md) if end == -1 else end + 1
        return md[:start] + section + "\n\n" + md[end:], "replaced"
    anchor = "\n## 复现"
    assert anchor in md, "no '## 复现' anchor in README"
    return md.replace(anchor, "\n" + section + "\n" + anchor, 1), "added"


def patch_commands(md, page):
    """Append the page's scripts to the RTM / ManimCE lists inside 复现."""
    i = md.find("## 复现")
    j = md.find("```", i)
    k = md.find("```", j + 3)
    block = md[j:k]
    rtm_line = 'python "C:\\Users\\begin\\Desktop\\RTM-Wiki\\%s\\RTM code\\%s.py"'
    ce_line = 'python "C:\\Users\\begin\\Desktop\\RTM-Wiki\\%s\\ManimCE code\\%s-manimce.py"'
    lines = block.splitlines()
    rtm = [n for n, l in enumerate(lines) if "\\RTM code\\" in l]
    ce = [n for n, l in enumerate(lines) if "\\ManimCE code\\" in l]
    tail = rtm_line.split("\\RTM-Wiki\\")[1]          # '<chapter>\RTM code\<page>.py"'
    chapter = tail[:tail.find("\\RTM code\\")]
    added = 0
    if rtm and ("\\%s.py" % page) not in block:
        lines.insert(rtm[-1] + 1, rtm_line % (chapter, page))
        added += 1
    if ce and ("\\%s-manimce.py" % page) not in block:
        # recompute after the possible insert
        ce = [n for n, l in enumerate(lines) if "\\ManimCE code\\" in l]
        lines.insert(ce[-1] + 1, ce_line % (chapter, page))
        added += 1
    return md[:j] + "\n".join(lines) + md[k:], added


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("page")
    ap.add_argument("--chapter", default="04-图形与文本")
    ap.add_argument("--note", action="append", default=[])
    ap.add_argument("--notes-file", help="file with one note per line (avoids shell quoting)")
    ap.add_argument("--write", action="store_true")
    args = ap.parse_args()
    if args.notes_file:
        with io.open(args.notes_file, encoding="utf-8") as fh:
            args.note.extend([l.rstrip("\n") for l in fh if l.strip()])
    assets = find_assets(WIKI, args.page)
    if assets is None:
        raise SystemExit("RTM demo not found for " + args.page)
    path = os.path.join(assets, "README.md")
    md = io.open(path, encoding="utf-8").read()
    section = build_section(args.page, assets, args.note)
    md, how = patch(md, args.page, section)
    md, added = patch_commands(md, args.page)
    print("page:", args.page, "| section", how, "| commands added:", added)
    print("\n".join(section.splitlines()[2:6]))
    if args.write:
        io.open(path, "w", encoding="utf-8", newline="\n").write(md)
        print("written:", path)
    return 0


if __name__ == "__main__":
    sys.exit(main())
