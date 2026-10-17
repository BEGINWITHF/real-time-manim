# -*- coding: utf-8 -*-
"""Which sender draws the homotopied Rectangle, and with which points?

Runs the wiki's HomotopyDemo shape headless (hidden window), swaps the native
dll for a recording proxy ONLY inside the leaf senders, and prints per frame:
the sender that drew the rect and the geometry it submitted.

    python tools/_probe_homotopy_send.py
"""
import os
import sys

import numpy as np

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if REPO not in sys.path:
    sys.path.insert(0, REPO)

from manim import Scene, Rectangle, YELLOW, DOWN, linear  # noqa: E402
from real_time_manim.vulkan_bind import MLWindow, Homotopy, Wait  # noqa: E402

RECORD = ("AddBezierPath", "AddPolygon", "AddRect", "AddLineStrip", "AddLine")

LEAF_SENDERS = ("_send_vmobject", "_send_polygon", "_send_square",
                "_send_rectangle", "_send_ellipse", "_send_dot",
                "_send_circle", "_send_line", "_send_arc")


class Proxy(object):
    """Records the shape calls; every other call goes to the real dll."""

    def __init__(self, real):
        self.real = real
        self.calls = []

    def __getattr__(self, name):
        real_fn = getattr(self.real, name, None)

        def _call(*args, **kwargs):
            if name in RECORD:
                self.calls.append((name, args))
            if real_fn is not None:
                return real_fn(*args, **kwargs)
            return 0
        return _call


def wave(x, y, z, t):
    return (x, y + 0.45 * np.sin(2.2 * x + 2.0 * np.pi * t), z)


def dump(tag, name, args):
    if name == "AddBezierPath":
        n = int(args[1])
        pts = np.ctypeslib.as_array(args[0])[:n * 3].reshape(-1, 3)
        print("    %s %s n=%d\n      x: %s\n      y: %s" % (
            tag, name, n, np.round(pts[:, 0], 1).tolist(),
            np.round(pts[:, 1], 1).tolist()))
    elif name == "AddPolygon":
        n = int(args[9])
        pts = np.ctypeslib.as_array(args[10])[:n * 2].reshape(-1, 2)
        print("    %s %s n=%d\n      x: %s\n      y: %s" % (
            tag, name, n, np.round(pts[:, 0], 1).tolist(),
            np.round(pts[:, 1], 1).tolist()))
    elif name == "AddRect":
        print("    %s AddRect cx=%.1f cy=%.1f hw=%.1f hh=%.1f rot=%.2f" % (
            tag, args[0], args[1], args[2], args[3], args[4]))
    else:
        print("    %s %s (%d args)" % (tag, name, len(args)))


def main():
    win = MLWindow(960, 540, hidden=True)
    proxy = Proxy(win.dll)
    state = {"frame": 0, "sender": None, "senders": []}
    wrapped = []

    real_sync = win.sync

    def sync(*a, **k):
        state["frame"] += 1
        return real_sync(*a, **k)
    win.sync = sync
    wrapped.append(("sync", sync))

    for name in LEAF_SENDERS:
        fn = getattr(win, name, None)
        if fn is None or not callable(fn):
            continue

        def make(nm, f):
            def wrapper(*a, **k):
                mob = a[0] if a else None
                if mob is not None and type(mob).__name__ == "Rectangle":
                    state["sender"] = nm
                    real = win.dll
                    win.dll = proxy
                    try:
                        return f(*a, **k)
                    finally:
                        proxy.calls.append(("__end__", ()))
                        win.dll = real
                return f(*a, **k)
            return wrapper
        setattr(win, name, make(name, fn))
        wrapped.append((name, getattr(win, name)))

    scene = Scene()
    win.scene = scene
    rect = Rectangle(width=4.4, height=1.6, color=YELLOW).set_fill(YELLOW, 0.35).shift(DOWN * 1.2)
    scene.add(rect)
    frames = []
    try:
        # capture the sender name per sync by draining around each play
        win.play(Homotopy(wave, rect, run_time=0.5, rate_func=linear))
        win.play(Wait(0.05))
    finally:
        for n, f in wrapped:
            try:
                if getattr(win, n, None) is f:
                    delattr(win, n)
            except AttributeError:
                pass
        try:
            win.close()
        except Exception:
            pass

    groups = []
    cur = []
    for name, args in proxy.calls:
        if name == "__end__":
            groups.append(cur)
            cur = []
        else:
            cur.append((name, args))
    if cur:
        groups.append(cur)
    print("total recorded frames with rect calls: %d" % len(groups))
    print("sender used for the Rectangle: %s" % state["sender"])
    picks = sorted({0, len(groups) // 4, len(groups) // 2,
                    (3 * len(groups)) // 4, len(groups) - 1})
    for gi in picks:
        print("  ==== group %d / %d ====" % (gi, len(groups)))
        for name, args in groups[gi]:
            dump("g%d" % gi, name, args)


if __name__ == "__main__":
    main()
