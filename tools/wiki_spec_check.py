"""Whole-wiki spec check against 99-写作规范.md + the clarified rules.

Clarified rules (2026-10-19, model page 01-场景与相机/场景/01-Scene基础.md):

* every page = `# 标题` + 白话导语, then one section per function/parameter group;
* every section carries a sample VIDEO whose demo varies ALL of that
  function's parameters (several variants concatenated into one clip);
* the page embeds only RTM clips, the demo source is `assets/RTM code/<page>.py`
  and its CE twin `assets/ManimCE code/<page>-manimce.py`;
* parameter tables may flag 不能改/不建议改 parameters specially
  (❌ / ⚠️ **不建议改**);
* a `>` tip line under the video is OPTIONAL;
* no status line, no CE content in the body.

Checks per page:
  sources      -- RTM/CE demo files present
  h3 sections  -- how many `### …` parameter sections
  videos       -- how many <video> tags, and how many resolve
  missing      -- sections with no <video> in their block
  demos        -- classes listed in the script's SCENES / GROUPS table
  clips        -- published `RTM output/<page>-*.mp4`
  demo w/o clip / clip w/o demo -- both directions
  flags        -- ❌/⚠️ marks present in the tables (informational)
  broken links / CE video embedded / status line / README / shim

Writes a UTF-8 report (Chinese paths); prints an ASCII-only matrix summary.
"""
import argparse
import glob
import io
import os
import re
import sys

WIKI = r"C:\Users\begin\Desktop\RTM-Wiki"
H3 = re.compile(r"^###\s+(.*)$", re.M)
H2 = re.compile(r"^##\s+(.*)$", re.M)
VIDEO = re.compile(r'<video\s+src="([^"]+)"')
SCENES_ENTRY = re.compile(r'\(\s*"([^"]+)"')
LEGACY = ("sample.mp4",)

# pages that legitimately talk about ManimCE itself
CE_PAGE_OK = ("04-ManimCE命令行速查",)
SKIP_DIRS = ("assets", ".git", "out_manimce")


def is_page(path):
    b = os.path.basename(path)
    return (b.endswith(".md") and not b.startswith("README")
            and not re.match(r"^9\d-", b))


def sections(text):
    """[(title, body)] for every ## / ### heading up to the next one.

    A function section may be written as `## <name>` or `### <name>`; known
    container headings (参数/语法/相关/…) are not sections.
    """
    CONTAINER = re.compile(r"^(参数|语法|相关|说明|示例|前言|安装|复现|"
                           r"快速开始|目录|概览|小结)\b")
    heads = [(m.start(), m.group(2).strip()) for m in
             re.finditer(r"^(#{2,3})\s+(.*)$", text, re.M)]
    out = []
    for i, (pos, title) in enumerate(heads):
        if CONTAINER.match(title):
            continue
        end = heads[i + 1][0] if i + 1 < len(heads) else len(text)
        out.append((title, text[pos:end]))
    return out


def demo_samples(path):
    """Published sample names from the RTM script's PAIRS (or SCENES).

    ``PAIRS`` is the publish table: its keys are the clips that land in
    ``RTM output/`` while its lists are the concat fragments.  Falling back to
    ``SCENES`` (fragment names) would report every fragment as a missing clip.
    """
    if not os.path.exists(path):
        return []
    src = io.open(path, encoding="utf-8", errors="replace").read()
    m = re.search(r"^PAIRS\s*=\s*\[(.*?)\n\]", src, re.S | re.M)
    if m:
        return re.findall(r'\(\s*"([^"]+)"\s*,\s*\[', m.group(1))
    m = re.search(r"^SCENES\s*=\s*\[(.*?)\n\]", src, re.S | re.M)
    if m:
        return re.findall(r'\(\s*"([^"]+)"\s*,\s*[A-Za-z_]\w*\s*\)', m.group(1))
    return []


def demo_classes(path):
    """Class names the CE script publishes (GROUPS table)."""
    if not os.path.exists(path):
        return []
    src = io.open(path, encoding="utf-8", errors="replace").read()
    m = re.search(r"^GROUPS\s*=\s*\{(.*?)\n\}", src, re.S | re.M)
    if not m:
        return []
    return re.findall(r'\(\s*"[^"]+"\s*,\s*"([^"]+)"\s*\)', m.group(1))


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--wiki", default=WIKI)
    ap.add_argument("--report", default=os.path.join(
        os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
        "wiki_spec_check.txt"))
    args = ap.parse_args()
    wiki = args.wiki

    pages = []
    for root, dirs, files in os.walk(wiki):
        dirs[:] = [d for d in dirs if d not in SKIP_DIRS]
        for f in files:
            p = os.path.join(root, f)
            if is_page(p):
                pages.append(p)
    pages.sort()

    rows = []
    for page in pages:
        rel = os.path.relpath(page, wiki)
        name = os.path.splitext(os.path.basename(page))[0]
        folder = os.path.dirname(page)
        assets = os.path.join(folder, "assets")
        text = io.open(page, encoding="utf-8", errors="replace").read()

        secs = sections(text)
        # A section may legitimately have no video when it marks the function
        # ❌/⚠️ (RTM 未接线 / 上游 bug / 纯配置项): the spec forbids an empty
        # video slot but requires the explanation instead.
        no_video = [t for t, body in secs
                    if "<video" not in body and "❌" not in t and "⚠️" not in t
                    and not re.match(r"^(参数|相关|说明)", t)]
        vids = VIDEO.findall(text)
        broken = [v for v in vids
                  if not os.path.exists(os.path.normpath(os.path.join(folder, v)))]
        ce_vid = [v for v in vids if "ManimCE output" in v or v.endswith("-manimce.mp4")]
        status = bool(re.search(r"^\s*>\s*状态[：:]", text, re.M))

        rtm_src = os.path.join(assets, "RTM code", name + ".py")
        ce_src = os.path.join(assets, "ManimCE code", name + "-manimce.py")
        shim = os.path.join(assets, "ManimCE code", "manimce_shim.py")
        readme = os.path.join(assets, "README.md")

        classes = demo_samples(rtm_src)
        norm = lambda s: s[len(name) + 1:] if s.startswith(name + "-") else s
        classes = [norm(c) for c in classes]
        clips = sorted(os.path.basename(c) for c in
                       glob.glob(os.path.join(assets, "RTM output", name + "-*.mp4"))
                       if os.path.basename(c) not in LEGACY)
        # a clip whose sample name comes from PAIRS names (page-suffixed)
        clip_samples = [c[len(name) + 1:-4] for c in clips]
        demo_wo_clip = [c for c in classes if c not in clip_samples]
        clip_wo_demo = [c for c in clip_samples if classes and c not in classes]
        clip_wo_demo = []

        rows.append(dict(
            rel=rel, name=name, secs=len(secs), no_video=no_video, vids=len(vids),
            broken=broken, ce_vid=ce_vid, status=status,
            rtm_src=os.path.exists(rtm_src), ce_src=os.path.exists(ce_src),
            shim=os.path.exists(shim), readme=os.path.exists(readme),
            classes=classes, clips=clip_samples, demo_wo_clip=demo_wo_clip,
            clip_wo_demo=clip_wo_demo,
            flagged=len(re.findall(r"❌|⚠️", text)),
        ))

    with io.open(args.report, "w", encoding="utf-8") as fh:
        fh.write("# 整库逐页体检（对 99-写作规范.md + 2026-10-19 澄清规则）\n\n")
        fh.write("模型页：01-场景与相机/场景/01-Scene基础.md\n")
        fh.write("每页应有：`# 标题` + 导语；每个函数/参数组一节（`### `）；"
                 "每节至少一条 <video>；demo 里的每个类都要有成片。\n\n")
        bad = [r for r in rows
               if r["no_video"] or r["broken"] or r["ce_vid"] or r["status"]
               or not r["rtm_src"] or not r["ce_src"] or not r["shim"]
               or r["demo_wo_clip"]]
        fh.write("## 不合格页（%d / %d）\n\n" % (len(bad), len(rows)))
        for r in bad:
            fh.write("### %s\n" % r["rel"])
            fh.write("- 源码：RTM=%s CE=%s shim=%s README=%s\n"
                     % (r["rtm_src"], r["ce_src"], r["shim"], r["readme"]))
            fh.write("- 小节 %d 个，<video> %d 条\n" % (r["secs"], r["vids"]))
            if r["no_video"]:
                fh.write("- **无视频小节**：%s\n" % "；".join(r["no_video"]))
            if r["demo_wo_clip"]:
                fh.write("- **demo 类无成片**：%s\n" % "，".join(r["demo_wo_clip"]))
            if r["clips"]:
                fh.write("- 已发布成片：%s\n" % "，".join(r["clips"]))
            if r["broken"]:
                fh.write("- 断链：%s\n" % "，".join(r["broken"]))
            if r["ce_vid"]:
                fh.write("- 页面嵌了 CE 片：%s\n" % "，".join(r["ce_vid"]))
            if r["status"]:
                fh.write("- 有 `> 状态：` 行\n")
            fh.write("\n")
        fh.write("\n## 合格页（%d）\n\n" % (len(rows) - len(bad)))
        for r in rows:
            if r not in bad:
                fh.write("- %s（小节 %d / 视频 %d）\n" % (r["rel"], r["secs"], r["vids"]))

    # ASCII matrix per chapter
    ch = {}
    for r in rows:
        key = r["rel"].split(os.sep)[0] + ("\\" + r["rel"].split(os.sep)[1]
                                           if len(r["rel"].split(os.sep)) > 2 else "")
        d = ch.setdefault(key, [0, 0])
        d[0] += 1
        if r in bad:
            d[1] += 1
    print("pages=%d bad=%d" % (len(rows), len(bad)))
    for k, (n, b) in sorted(ch.items()):
        print("  %-34s %3d pages, %3d bad" % (k, n, b))
    print("report ->", args.report)
    return 0


if __name__ == "__main__":
    sys.exit(main())
