"""Trace what a wiki sample actually displays, frame by frame -- no images.

Pixel diffing tells you *that* two renders disagree but not *what* either one
says.  When the complaint is "the readout counts wrong" you need the sequence
of values, so this hooks the interesting mutator (``DecimalNumber.set_value``,
``ValueTracker.set_value``, a mobject transform ...) while the sample runs and
prints, per ``win.play`` segment, exactly what was applied and how often.

    python tools/updater_trace.py "<...>/assets/RTM code/10-ValueTracker.py" \
            basic --hook DecimalNumber.set_value

Markers ``[play N]`` delimit the segments; ``xN`` is how many times the hook
fired in that segment.  Run it once against the RTM script and once against
the ManimCE twin (they share the class names) to compare sequences.
"""
import argparse
import importlib.util
import os
import sys

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if REPO not in sys.path:
    sys.path.insert(0, REPO)


def _load(path):
    spec = importlib.util.spec_from_file_location("_trace_mod", path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def _resolve(target):
    """'DecimalNumber.set_value' -> (class, attr)."""
    parts = target.split(".")
    obj = __import__("manim", fromlist=["*"])
    for p in parts[:-1]:
        obj = getattr(obj, p)
    return obj, parts[-1]


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("page_py")
    ap.add_argument("fragment")
    ap.add_argument("--hook", action="append", default=[],
                    help="Class.attr to record, repeatable")
    ap.add_argument("--max", type=int, default=400,
                    help="cap on recorded values per segment")
    ap.add_argument("--engine", choices=("rtm", "ce"), default="rtm",
                    help="rtm: fast_record_scene; ce: manim Scene.render()")
    args = ap.parse_args()

    mod = _load(os.path.abspath(args.page_py))
    scenes = dict(getattr(mod, "SCENES", []))
    cls = scenes[args.fragment]
    print(f"scene {cls.__module__}.{cls.__name__}  fragment={args.fragment}")

    hooks = []
    for spec in args.hook:
        klass, attr = _resolve(spec)
        orig = getattr(klass, attr)
        log = []
        hooks.append((spec, log, orig, klass, attr))

        def make(orig=orig, log=log, spec=spec):
            def wrapper(self, *a, **k):
                val = a[0] if a else k.get("value", None)
                if len(log) < args.max:
                    log.append(val)
                return orig(self, *a, **k)
            return wrapper

        setattr(klass, attr, make())

    # mark each win.play segment (works for both the RTM window and the
    # ManimCE shim, since the page module imports its own MLWindow)
    cls_win = getattr(mod, "MLWindow", None)
    seg = []
    orig_play = None
    if cls_win is not None and hasattr(cls_win, "play"):
        orig_play = cls_win.play

        def play_mark(self, *a, **k):
            seg.append(len([x for log in hooks for x in log]))
            return orig_play(self, *a, **k)

        cls_win.play = play_mark
        print(f"window class: {cls_win.__module__}.{cls_win.__name__}")

    try:
        fast = getattr(mod, "fast_record_scene", None) or getattr(
            mod, "render", None)
        out = os.path.join(os.path.dirname(os.path.abspath(args.page_py)),
                           "final", "_trace.mp4")
        if fast is None:
            raise SystemExit("page module exposes neither fast_record_scene nor render")
        fast(cls, out_path=out, verbose=False, overwrite=True, cleanup=True)
    finally:
        for spec, log, orig, klass, attr in hooks:
            setattr(klass, attr, orig)
        if orig_play is not None:
            cls_win.play = orig_play

    marks = [0] + seg + [len([x for log in hooks for x in log])]
    print(f"play() calls: {len(seg)}")
    for spec, log, *_ in hooks:
        print(f"\nhook {spec}: {len(log)} calls")
        for i in range(len(marks) - 1):
            lo, hi = marks[i], min(marks[i + 1], len(log))
            chunk = log[lo:hi]
            if i < len(seg):
                head = f"  [play {i+1}] x{len(chunk)}: "
            else:
                head = f"  [after last play] x{len(chunk)}: "
            shown = ", ".join(repr(v) for v in chunk[:args.max])
            print(head + shown)


if __name__ == "__main__":
    main()
