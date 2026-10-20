"""Move a page's `> 状态：` block into the chapter's assets/README.md.

99-写作规范.md 一.5: a page starts with `# 标题` + 白话导语, no status line;
一.6: CE/对照 information belongs in assets/README.md.  The status blocks carry
exactly that kind of information, so they are MOVED (never dropped).

Usage:  python tools/wiki_move_status.py [--dry-run]
"""
import argparse
import io
import os
import re
import sys

WIKI = r"C:\Users\begin\Desktop\RTM-Wiki"

# page -> (chapter assets dir, README section heading to append the note to)
TARGETS = [
    (r"05-坐标系与图表\08-图表BarChart.md", r"05-坐标系与图表\assets", "08-图表BarChart"),
    (r"05-坐标系与图表\09-概率与SampleSpace.md", r"05-坐标系与图表\assets",
     "09-概率与SampleSpace"),
    (r"05-坐标系与图表\10-刻度与缩放.md", r"05-坐标系与图表\assets", "10-刻度与缩放"),
    (r"00-快速开始\05-任意帧预览.md", None, None),
]
STATUS = re.compile(r"^>\s*状态[：:]")


def note_from(status):
    """Rewrite the status line as an assets/README bullet."""
    body = STATUS.sub("", status).strip()
    body = body.replace("｜", "；")
    parts = [p.strip() for p in body.split("；") if p.strip()]
    return "- **验证**：" + "；".join(parts) + "\n"


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--dry-run", action="store_true")
    args = ap.parse_args()
    for rel, assets_rel, section in TARGETS:
        page = os.path.join(WIKI, rel)
        src = io.open(page, encoding="utf-8").read()
        lines = src.splitlines(keepends=True)
        status = None
        keep = []
        for line in lines:
            if status is None and STATUS.match(line):
                status = line.strip()
                continue
            keep.append(line)
        if status is None:
            print("%-46s no status line (already moved?)" % rel)
            continue
        # drop the now-double blank after the title
        text = "".join(keep)
        text = re.sub(r"^(#\s[^\n]*\n)\n\n+", r"\1\n", text)
        print("%-46s status -> %s" % (rel, "README" if assets_rel else "(dropped, no assets)"))
        if args.dry_run:
            continue
        io.open(page, "w", encoding="utf-8", newline="\n").write(text)
        if not assets_rel:
            # No assets dir: keep the substance as an allowed `> 提醒` block
            # (99-写作规范 一: 温馨提醒 is a permitted element; only the
            # `> 状态：` form and CE comparison content are not).
            reminder = ("> 提醒：交互预览是 RTM 专属能力，窗口与控件条见下；"
                        "回归测试 `tests/test_preview_spec.py`（20 项），"
                        "跳帧耗时见下面的实测表。\n")
            text = io.open(page, encoding="utf-8").read()
            head, sep, rest = text.partition("\n\n")
            if sep:
                text = head + sep + reminder + "\n" + rest
            io.open(page, "w", encoding="utf-8", newline="\n").write(text)
            continue
        readme = os.path.join(WIKI, assets_rel, "README.md")
        rm = io.open(readme, encoding="utf-8").read()
        heading = "## " + section
        idx = rm.find(heading)
        if idx < 0:
            print("   ! section %s missing in README; appending note at the end" % section)
            rm = rm.rstrip("\n") + "\n\n" + heading + "\n\n" + note_from(status)
        else:
            nxt = rm.find("\n## ", idx + 1)
            insert_at = len(rm) if nxt < 0 else nxt + 1
            block = rm[idx:insert_at].rstrip("\n")
            rm = rm[:idx] + block + "\n" + note_from(status) + rm[insert_at:]
        io.open(readme, "w", encoding="utf-8", newline="\n").write(rm)
    return 0


if __name__ == "__main__":
    sys.exit(main())
