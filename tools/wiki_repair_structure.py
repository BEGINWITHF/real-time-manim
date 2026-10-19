"""Repair the mechanical wiki-spec gaps that need no editorial judgement.

1. Every chapter's ``assets/ManimCE code/`` must carry ``manimce_shim.py``
   (99-写作规范.md 三: "直接复制，勿改逻辑") -- copy the canonical one into the
   chapters that lack it (never overwrite an existing file).
2. Every chapter with published videos must have ``assets/README.md`` holding
   the RTM/ManimCE comparison table (99-写作规范.md 二).  Tables are generated
   from the files themselves: sample = the clip name, frames/duration measured
   with ffprobe, CE twin = the ``-manimce`` sibling, 帧数对齐 = a frame-count
   comparison.  Existing READMEs are left untouched.

Usage:  python tools/wiki_repair_structure.py [--dry-run]
"""
import argparse
import glob
import io
import json
import os
import shutil
import subprocess
import sys

WIKI = r"C:\Users\begin\Desktop\RTM-Wiki"
CANON_SHIM = os.path.join(WIKI, "01-场景与相机", "专用场景", "assets",
                         "ManimCE code", "manimce_shim.py")
LEGACY = ("sample.mp4",)

HEADER = """# {chapter} 样例视频（RTM / ManimCE 对照）

本目录的成片由 `RTM code/` 与 `ManimCE code/` 下的同源脚本渲染：页面只引用
**RTM** 那一版（`RTM output/`），带 `-manimce` 的是同一份类代码用 ManimCE 渲的
对照件（`ManimCE output/`），仅供比对，不进页面。
"""

FOOTER = """
## 复现

```powershell
# RTM 版（不带参数=渲全部片段并拼接；带参数=只渲指定片段）
{rtm_cmds}

# ManimCE 对照版（同一个 shim 把 win.play 转成 self.play）
{ce_cmds}
```

RTM 只支持 1920×1080@60，脚本里写 `MLWindow(960, 540)` 会被强制纠正并打印一行提示，属正常。
"""


def probe(path):
    out = subprocess.run(
        ["ffprobe", "-v", "error", "-select_streams", "v:0",
         "-show_entries", "stream=nb_frames,duration", "-of", "json", path],
        capture_output=True, text=True, encoding="utf-8", errors="replace")
    try:
        st = json.loads(out.stdout)["streams"][0]
        return int(st.get("nb_frames") or 0), float(st.get("duration") or 0.0)
    except Exception:
        return 0, 0.0


def secs(d):
    return "%.2fs" % d


def fragments_map(chapter_dir, page):
    """{'sample or frag name': 'frag1 + frag2' or 'frag'} from the page script.

    Parsed textually -- importing the demo module would render nothing but
    would still execute its imports (and needs the repo on sys.path).
    """
    path = os.path.join(chapter_dir, "RTM code", page + ".py")
    try:
        src = io.open(path, encoding="utf-8").read()
    except Exception:
        return {}
    import re
    out = {}
    m = re.search(r"^PAIRS\s*=\s*\[(.*?)\n\]", src, re.S | re.M)
    if m:
        for name, frags in re.findall(r'\(\s*"([^"]+)"\s*,\s*\[([^\]]*)\]', m.group(1)):
            names = re.findall(r'"([^"]+)"', frags)
            out[name] = " + ".join(names)
    m = re.search(r"^SCENES\s*=\s*\[(.*?)\n\]", src, re.S | re.M)
    if m:
        for name in re.findall(r'\(\s*"([^"]+)"', m.group(1)):
            out.setdefault(name, name)
    return out


def table_for(chapter, page_prefix, rtm_dir, ce_dir, chapter_dir):
    rows = []
    frags = fragments_map(chapter_dir, page_prefix)
    clips = sorted(glob.glob(os.path.join(rtm_dir, "*.mp4")))
    for clip in clips:
        base = os.path.basename(clip)
        if base in LEGACY or base.startswith("probe_"):
            continue
        if page_prefix and not base.startswith(page_prefix + "-"):
            continue
        n, dur = probe(clip)
        sample = base[:-4]
        if page_prefix and base.startswith(page_prefix + "-"):
            sample = base[len(page_prefix) + 1:-4]
        # PAIRS entries are the published (concatenated) samples; a bare clip
        # that is only a fragment is skipped here.
        fragment = frags.get(sample, frags.get(sample + "_", "")) or sample
        if frags and sample not in frags and len(frags) and sample not in [
                v for v in frags.values()]:
            # a fragment that PAIRS folded into another sample
            if any(sample in v.split(" + ") for v in frags.values()):
                continue
        ce = os.path.join(ce_dir, base[:-4] + "-manimce.mp4")
        if os.path.exists(ce):
            cn, cdur = probe(ce)
            align = "✅" if n == cn else "⚠️（CE %d 帧）" % cn
            ce_cell = "%s（%d 帧 / %s）" % (os.path.basename(ce), cn, secs(cdur))
        else:
            ce_cell = "—（不产片，见页面 ❌/备注）"
            align = "❌"
        rows.append("| `%s` | %s | `%s`（%d 帧 / %s） | %s | %s |"
                    % (sample, fragment, base, n, secs(dur), ce_cell, align))
    if not rows:
        return ""
    return ("| 样例 | 片段 | RTM | ManimCE | 帧数对齐 |\n"
            "| --- | --- | --- | --- | --- |\n" + "\n".join(rows) + "\n")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--dry-run", action="store_true")
    args = ap.parse_args()

    copied, written = [], []

    # 1. shims
    for ce_dir in sorted(glob.glob(os.path.join(WIKI, "**", "assets", "ManimCE code"),
                                   recursive=True)):
        target = os.path.join(ce_dir, "manimce_shim.py")
        if os.path.exists(target):
            continue
        if not os.path.exists(CANON_SHIM):
            print("canonical shim missing, skipping", ce_dir)
            continue
        copied.append(os.path.relpath(ce_dir, WIKI))
        if not args.dry_run:
            shutil.copyfile(CANON_SHIM, target)

    # 2. chapter READMEs
    for ce_dir in sorted(glob.glob(os.path.join(WIKI, "**", "assets", "ManimCE code"),
                                   recursive=True)):
        chapter_dir = os.path.dirname(ce_dir)               # .../assets
        rel = os.path.relpath(chapter_dir, WIKI)
        readme = os.path.join(chapter_dir, "README.md")
        rtm_dir = os.path.join(chapter_dir, "RTM output")
        ce_out = os.path.join(chapter_dir, "ManimCE output")
        if os.path.exists(readme) or not os.path.isdir(rtm_dir):
            continue
        chapter = os.path.basename(os.path.dirname(chapter_dir))
        pages = sorted({os.path.basename(p)[:-3] for p in
                        glob.glob(os.path.join(os.path.dirname(chapter_dir), "*.md"))
                        if not os.path.basename(p).startswith(("README", "99-", "98-"))})
        body = [HEADER.format(chapter=chapter)]
        for page in pages:
            tbl = table_for(chapter, page, rtm_dir, ce_out, chapter_dir)
            if tbl:
                body.append("\n## %s\n\n%s" % (page, tbl))
        rtm_cmds = "\n".join("python \"%s\"" % os.path.join(chapter_dir, "RTM code",
                                                            page + ".py")
                             for page in pages
                             if os.path.exists(os.path.join(chapter_dir, "RTM code",
                                                            page + ".py")))
        ce_cmds = "\n".join("python \"%s\"" % os.path.join(ce_dir, page + "-manimce.py")
                            for page in pages
                            if os.path.exists(os.path.join(ce_dir, page + "-manimce.py")))
        body.append(FOOTER.format(rtm_cmds=rtm_cmds, ce_cmds=ce_cmds))
        written.append(rel)
        if not args.dry_run:
            io.open(readme, "w", encoding="utf-8", newline="\n").write("".join(body))

    print("shims copied: %d %s" % (len(copied), copied))
    print("readmes written: %d %s" % (len(written), written))
    if args.dry_run:
        print("(dry run: nothing written)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
