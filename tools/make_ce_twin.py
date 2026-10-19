# -*- coding: utf-8 -*-
"""Generate a page's CE twin from its RTM demo, guaranteeing identical bodies.

The spec requires the two demos to be the same class code with only the
imports differing, so build the CE file mechanically:

  * keep the RTM file's class block byte-for-byte;
  * rewrite the header: `from real_time_manim import (...)` -> `from manim
    import (...)`, `from real_time_manim.vulkan_bind import MLWindow, Wait` ->
    `from manimce_shim import MLWindow, render, concat`, drop the
    `fast_record_scene` import and the `Wait` from the manim list becomes
    redundant only if already imported (it is added when missing);
  * append the CE trailer (GROUPS / CONCATS / render+concat) derived from the
    RTM SCENES/PAIRS tables.

Usage: python make_ce_twin.py "<page name>" [--write]
"""
import io
import os
import re
import sys

WIKI = r"C:\Users\begin\Desktop\RTM-Wiki"
PAGE_DIR = None

RTM_HEADER = re.compile(
    r"from real_time_manim import \((.*?)\)\n"
    r"from real_time_manim\.vulkan_bind import MLWindow, Wait\n"
    r"(?:from real_time_manim\.record import fast_record_scene\n)?", re.S)


def build(page, assets):
    rtm_path = os.path.join(assets, "RTM code", page + ".py")
    src = io.open(rtm_path, encoding="utf-8").read()

    m = RTM_HEADER.search(src)
    if not m:
        raise SystemExit("header not recognised in " + rtm_path)
    names = [n.strip() for n in m.group(1).replace("\n", " ").split(",") if n.strip()]
    if "Wait" not in names:
        names.append("Wait")
    ce_imports = "from manim import (\n    " + ", ".join(names) + ",\n)\n"
    # carry the RTM file's plain third-party imports (numpy/math/random/...):
    # they sit above HERE=... in the RTM script and the class bodies use them.
    prefix = src[:src.find("HERE = ")]
    extra = [ln for ln in prefix.splitlines()
             if re.match(r"^(import|from)\s+(numpy|math|random|itertools|"
                         r"functools|re|collections|PIL|svgelements)\b", ln.strip())]
    extra_block = "".join(ln + "\n" for ln in extra)
    if extra_block:
        extra_block += "\n"
    head_end = m.end()
    trailer_start = src.find("SCENES = ")
    if trailer_start < 0:
        raise SystemExit("no SCENES table in " + rtm_path)
    body = src[head_end:trailer_start].rstrip() + "\n"
    # Drop module-level imports of RTM-only modules: they only exist so the
    # RTM-only samples below can run, and the CE file must not fail to import.
    body = "".join(
        ln + "\n" for ln in body.splitlines()
        if not re.match(r"^from real_time_manim\.(?!vulkan_bind|record)\S+ import", ln)
    )
    scenes = re.findall(r'\(\s*"([^"]+)"\s*,\s*([A-Za-z_]\w*)\s*\)',
                        src[trailer_start:])
    pairs = re.findall(r'\(\s*"([^"]+)"\s*,\s*\[([^\]]*)\]',
                       src[src.find("PAIRS = "):])
    # Samples whose SCENES row is marked `# RTM-only` use an API ManimCE does
    # not have (e.g. TextDecimalNumber): they get no CE twin at all, so their
    # class stays in the file as dead code but is never rendered.
    rtm_only = set(re.findall(
        r'\(\s*"([^"]+)"\s*,\s*[A-Za-z_]\w*\s*\)[^\n]*#\s*RTM-only',
        src[trailer_start:]))
    scenes = [(f, c) for f, c in scenes if f not in rtm_only]
    pairs = [(n, f) for n, f in pairs
             if not rtm_only & {x.strip().strip('"') for x in f.split(",")}]

    out = [
        "# -*- coding: utf-8 -*-\n",
        '"""%s.md 的样例在 **ManimCE** 下的渲染（对比 RTM 用）。\n\n'
        "class 里的代码与页面里的代码块逐字一致，唯一的区别是 MLWindow 来自\n"
        "manimce_shim（它把 win.play 转成 manim 的 self.play）。\n\n"
        "跑法：python %s-manimce.py            # 全部\n"
        "      python %s-manimce.py %s      # 只跑一个\n"
        '"""\n' % (page, page, page, scenes[0][0] if scenes else ""),
        "import os\nimport sys\n\n",
        "HERE = os.path.dirname(os.path.abspath(__file__))\n",
        "ASSETS = os.path.dirname(HERE)\n",
        "sys.path.insert(0, HERE)\n\n",
        extra_block,
        ce_imports,
        "from manimce_shim import MLWindow, render, concat\n",
        body,
        "\nGROUPS = {\n",
    ]
    for frag, cls in scenes:
        out.append('    "%s": [("%s-%s-manimce", "%s")],\n'
                   % (frag, page, frag, cls))
    out.append("}\n\nCONCATS = [\n")
    for name, frags in pairs:
        frag_list = [f.strip().strip('"') for f in frags.split(",") if f.strip()]
        out.append('    ("%s", "%s-%s-manimce", [%s]),\n'
                   % (name, page, name,
                      ", ".join('"%s-%s-manimce"' % (page, f) for f in frag_list)))
    out.append("]\n\n\n")
    out.append('if __name__ == "__main__":\n')
    out.append("    wanted = sys.argv[1:] or list(GROUPS)\n")
    out.append("    names = []\n")
    out.append("    for key in wanted:\n")
    out.append("        for out_name, cls_name in GROUPS[key]:\n")
    out.append("            names.append((out_name, cls_name, os.path.abspath(__file__)))\n")
    out.append("    render(names)\n\n")
    out.append("    if not sys.argv[1:]:\n")
    out.append('        ce_out = os.path.join(ASSETS, "ManimCE output")\n')
    out.append("        os.makedirs(ce_out, exist_ok=True)\n")
    out.append("        for key, out_name, parts in CONCATS:\n")
    out.append("            concat(parts, os.path.join(ce_out, out_name + \".mp4\"))\n")
    return "".join(out)


def main():
    page = sys.argv[1]
    write = "--write" in sys.argv
    assets = None
    for root, dirs, files in os.walk(WIKI):
        if root.endswith(os.path.join("assets", "RTM code")) or \
                os.path.basename(os.path.dirname(root)) == "assets" and \
                os.path.basename(root) == "RTM code":
            if os.path.exists(os.path.join(root, page + ".py")):
                assets = os.path.dirname(root)
                break
    if assets is None:
        raise SystemExit("RTM demo not found for " + page)
    text = build(page, assets)
    dst = os.path.join(assets, "ManimCE code", page + "-manimce.py")
    if write:
        io.open(dst, "w", encoding="utf-8", newline="\n").write(text)
        print("wrote", dst, len(text), "bytes")
    else:
        print(text[:1200])


if __name__ == "__main__":
    main()
