"""On-demand frame rendering: prepare a scene once, then render ANY frame.

Highest priority for RTM: "get whichever frame you want, immediately".

Preparing a scene costs one ``construct()`` pass (records the whole timeline
without drawing); after that every frame is O(1) -- just draw it at time ``t``.

    from real_time_manim.frames import FrameServer
    from scenes.demo_scene import DemoCreate

    fs = FrameServer(DemoCreate)        # build + record the timeline ONCE
    fs.show_frame(1.5)                  # draw t=1.5 in the window (~10 ms)
    fs.save_frame(1.5, "f.png")         # draw + readback + write (PNG)
    fs.close()

Saving many frames without blocking
-----------------------------------
GPU readback must stay on the main thread (one swapchain, not thread-safe), but
the *encode + disk write* is CPU/IO and is pipelined onto a thread pool:

    main thread: render(t) -> ReadbackFramebuffer into RAM   (fast, serial)
                     |  hand the pixel buffer to a worker (bounded queue)
    worker pool: PNG-encode + write to disk                  (parallel)

so the main thread never waits on the disk.  ``flush()`` joins the workers.

CLI (renders ONLY the frames you ask for):

    python -m real_time_manim.frames 1 0 1.5 3.0 --out frames/
"""
import ctypes
import os
import sys
import threading
from concurrent.futures import ThreadPoolExecutor


def _repo_root():
    return os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


class FrameServer:
    """A prepared scene whose every frame can be produced on demand."""

    def __init__(self, scene_cls, width=1920, height=1080,
                 max_workers=4, max_pending=32):
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
        self._bind_raw_readback()
        self.timeline = self.window.build_timeline()
        self.duration = self.window._cursor

        # background encode/write pipeline (bounded to cap memory)
        self._pool = ThreadPoolExecutor(max_workers=max_workers)
        self._slots = threading.Semaphore(max_pending)
        self._futures = []

    # -- raw readback -------------------------------------------------------
    def _bind_raw_readback(self):
        self.window.dll.SaveScreenshotRaw.restype = ctypes.c_int
        self.window.dll.SaveScreenshotRaw.argtypes = [
            ctypes.POINTER(ctypes.c_ubyte), ctypes.POINTER(ctypes.c_int)]

    def _read_pixels(self):
        """Read the window's current framebuffer into RAM (BGR). Main thread."""
        w, h = self.window.win_w, self.window.win_h
        row_bytes = ((w * 3 + 3) & ~3)
        size = row_bytes * h
        buf = (ctypes.c_ubyte * size)()
        out_size = ctypes.c_int(size)
        ok = self.window.dll.SaveScreenshotRaw(buf, ctypes.byref(out_size))
        if not ok:
            raise RuntimeError("SaveScreenshotRaw failed (no frame present?)")
        return bytes(buf), w, h, row_bytes

    # -- frames -------------------------------------------------------------
    def render_frame(self, t):
        """Draw frame at ``t`` into the window.  ~10 ms, O(1) in t."""
        self.timeline.render_at(t)

    def show_frame(self, t):
        self.render_frame(t)

    def grab(self, t):
        """Render ``t`` and read the pixels into RAM.  Returns (bytes,w,h,rb)."""
        self.render_frame(t)
        return self._read_pixels()

    def save_frame(self, t, path, quality=6):
        """Render ``t``, read it back, encode PNG and write it (synchronous)."""
        pixels, w, h, rb = self.grab(t)
        _write_png(path, pixels, w, h, rb, quality)
        return path

    def save_frame_async(self, t, path, quality=6):
        """Render ``t`` on the main thread; encode+write on a worker thread.

        The main thread never blocks on the disk, so saving many frames does not
        stall rendering.  Call ``flush()`` to wait for completion.
        """
        pixels, w, h, rb = self.grab(t)
        self._slots.acquire()                    # backpressure: cap pending writes
        fut = self._pool.submit(_write_png, path, pixels, w, h, rb, quality)
        self._futures.append(fut)

        def _release(_f):
            self._slots.release()
        fut.add_done_callback(_release)
        return fut

    def export_frames(self, out_dir, times, async_=True):
        os.makedirs(out_dir, exist_ok=True)
        paths = []
        for i, t in enumerate(times):
            p = os.path.join(out_dir, f"f_{i:05d}_t{t:.3f}.png")
            if async_:
                self.save_frame_async(t, p)
            else:
                self.save_frame(t, p)
            paths.append(p)
        if async_:
            self.flush()
        return paths

    def flush(self):
        for fut in self._futures:
            fut.result()
        self._futures.clear()

    def close(self):
        try:
            self.flush()
        finally:
            self._pool.shutdown(wait=True)
            if self.window is not None:
                self.window._defer_close = False
                self.window.close()


def _write_png(path, pixels, w, h, row_bytes, quality):
    from PIL import Image
    img = Image.frombytes("RGB", (w, h), pixels, "raw", "BGR", row_bytes, 1)
    img.save(path, format="PNG", compress_level=quality)
    return path


# windows created during the most recent FrameServer build
_LAST_WINDOWS = []


def _install_registry_capture():
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
    async_ = True
    if '--out' in argv:
        i = argv.index('--out')
        out_dir = argv[i + 1]
        del argv[i:i + 2]
    if '--sync' in argv:
        async_ = False
        argv.remove('--sync')
    scene_token, times = argv[0], argv[1:]
    cls = _resolve_scene(scene_token)
    fs = FrameServer(cls)
    print(f"prepared: duration={fs.duration:.2f}s  (construct ran once)")
    if not times:
        print("no times given; use e.g. `... 1 0 1.5 3.0`")
        fs.close()
        return 0
    os.makedirs(out_dir, exist_ok=True)
    for spec in times:
        t = float(spec)
        p = os.path.join(out_dir, f"t_{t:.3f}.png")
        if async_:
            fs.save_frame_async(t, p)
        else:
            fs.save_frame(t, p)
        print(f"  t={t:<6} -> {p}")
    fs.close()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
