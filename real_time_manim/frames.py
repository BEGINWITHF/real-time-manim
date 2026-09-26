"""On-demand frame rendering: prepare a scene once, then render ANY frame.

Goal (highest priority for RTM): "get whichever frame you want, immediately".
Preparing a scene costs one ``construct()`` pass (records the whole timeline
without drawing); after that every frame is O(1) -- just draw it at time ``t``.

    from real_time_manim.frames import FrameServer
    from scenes.demo_scene import DemoCreate

    fs = FrameServer(DemoCreate)          # build + record the timeline ONCE
    fs.show_frame(1.5)                    # draw t=1.5 in the window (~10 ms)
    fs.save_frame(1.5, "f.png")           # draw + screenshot readback (~+110 ms)
    fs.close()

CLI (renders ONLY the frames you ask for):

    python -m real_time_manim.frames 1 0 1.5 3.0 --out frames/
"""
import os
import sys


def _repo_root():
    return os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


class FrameServer:
    """A prepared scene whose every frame can be produced on demand."""

    def __init__(self, scene_cls, width=1920, height=1080, quiet=True):
        from real_time_manim.vulkan_bind import MLWindow

        prev_mode = MLWindow._schedule_mode
        MLWindow._schedule_mode = True          # play() records, never draws
        _LAST_WINDOWS.clear()
        try:
            self.scene = scene_cls()
            self.scene.construct()
        finally:
            MLWindow._schedule_mode = prev_mode
        if not _LAST_WINDOWS:
            raise RuntimeError("scene did not create an MLWindow")
        self.window = _LAST_WINDOWS[-1]
        self.timeline = self.window.build_timeline()
        self.duration = self.window._cursor

    # -- frames -------------------------------------------------------------
    def render_frame(self, t):
        """Draw frame at ``t`` into the window (no readback).  ~10 ms, O(1)."""
        self.timeline.render_at(t)

    def show_frame(self, t):
        """Alias for render_frame: the window now shows the frame at ``t``."""
        self.render_frame(t)

    def save_frame(self, t, path):
        """Draw frame at ``t`` and write it to ``path`` (adds a readback)."""
        self.render_frame(t)
        return self.window.screenshot(path)

    def export_frames(self, out_dir, times):
        """Save exactly the requested times (nothing more)."""
        os.makedirs(out_dir, exist_ok=True)
        paths = []
        for t in times:
            p = os.path.join(out_dir, f"t_{t:.3f}.png")
            self.save_frame(t, p)
            paths.append(p)
        return paths

    def close(self):
        if self.window is not None:
            self.window._defer_close = False
            self.window.close()


# windows created during the most recent FrameServer build
_LAST_WINDOWS = []


def _install_registry_capture():
    """Capture the windows a scene creates while building a FrameServer."""
    from real_time_manim.vulkan_bind import MLWindow
    if getattr(MLWindow, '_capture_hooked', False):
        return
    orig_init = MLWindow.__init__

    def _init(self, *a, **k):
        orig_init(self, *a, **k)
        _LAST_WINDOWS.append(self)

    MLWindow.__init__ = _init
    MLWindow._capture_hooked = True


_install_registry_capture()


def _resolve_scene(token):
    """token may be a demo number ('1') or 'module:Class'."""
    sys.path.insert(0, _repo_root())
    if ':' in token:
        mod_name, cls_name = token.split(':', 1)
        import importlib
        return getattr(importlib.import_module(mod_name), cls_name)
    from run import SCENES  # demo table (repo root)
    for num, desc, cls in SCENES:
        if num == token:
            return cls
    raise SystemExit(f"unknown demo number: {token}")


def main(argv=None):
    argv = list(sys.argv[1:] if argv is None else argv)
    if not argv:
        print(__doc__)
        return 1
    out_dir = "frames"
    if '--out' in argv:
        i = argv.index('--out')
        out_dir = argv[i + 1]
        del argv[i:i + 2]
    scene_token, times = argv[0], argv[1:]
    cls = _resolve_scene(scene_token)
    fs = FrameServer(cls)
    print(f"prepared: duration={fs.duration:.2f}s  (construct ran once)")
    if not times:
        print("no times given; use e.g. `... 1 0 1.5 3.0`")
        fs.close()
        return 0
    for spec in times:
        t = float(spec)
        p = os.path.join(out_dir, f"t_{t:.3f}.png")
        os.makedirs(out_dir, exist_ok=True)
        fs.save_frame(t, p)
        print(f"  t={t:<6} -> {p}")
    fs.close()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
