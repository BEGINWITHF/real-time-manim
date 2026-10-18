# -*- coding: utf-8 -*-
"""Interactive any-frame preview: a still window + a native input bar.

Nothing plays when it opens.  Type a frame, press Enter, and the window shows
that frame -- no pre-render, no replay: ``Timeline.render_at`` is O(1) in ``t``
(``docs/2.0.0-time-addressable.md``), so a seek costs ~10 ms no matter where it
lands.

    python -m real_time_manim.preview 1                  # demo #1 from run.py
    python -m real_time_manim.preview examples.scenes:DemoCreate --at 120
    python -m real_time_manim.preview 1 --no-bar         # type in the terminal

One-off cost
------------
Preparing the scene runs ``construct()`` **once**, with scheduling on: ``play``
records what each animation does instead of drawing it (``FrameServer``), which
is what makes every later seek O(1).  No frame is rendered ahead of time -- the
first picture you see is only drawn when the window appears.

Caveat: a seek replays **animation** state, not accumulated *updater* state, so
a scene whose mobjects are only driven by custom updaters / ``TracedPath`` is
exact when you step forward and approximate when you jump backwards.  Making
those time-replayable is P3 in ``docs/2.0.0-time-addressable.md``.

Input bar
---------
On Windows the bar is a small native window docked right below the video
window: a text field, *Jump* / *Save PNG* / *Quit* buttons, and the current
frame in its title bar.  Accepted input:

    123 / 123f   frame 123            (frame numbers are the default unit)
    1.5 / 1.5s   time 1.5 s
    +1 / -10     step N frames from the current one
    s            save the current frame as PNG (into --out)
    p            play forward from here (any input stops it)
    ?            help
    q            quit

Everywhere else (or with ``--no-bar``) the same input is read from the terminal,
so the mode works without a GUI toolkit.
"""
from __future__ import annotations

import argparse
import collections
import os
import queue
import sys
import threading
import time

from real_time_manim.frames import FrameServer
from real_time_manim.window import win32

Command = collections.namedtuple("Command", "kind value")

HELP = (
    "123 (frame) | 1.5s (time) | +10 -1 (step) | s (save PNG) | "
    "p (play from here) | ? (help) | q (quit)"
)


# ---------------------------------------------------------------------------
# input parsing + layout (pure -- unit tested)
# ---------------------------------------------------------------------------

def clamp_frame(frame, n_frames):
    """``n_frames`` counts renderable frames, so the range is 0 .. n-1."""
    return max(0, min(max(1, int(n_frames)) - 1, int(frame)))


def time_of_frame(frame, fps):
    return float(frame) / float(fps)


def frame_of_time(t, fps):
    return int(round(float(t) * float(fps)))


def _round_half_up(value):
    """Round half away from zero -- ``round()`` is banker's (0.5 -> 0)."""
    value = float(value)
    return int(value + 0.5) if value >= 0 else -int(-value + 0.5)


def parse_spec(text, fps, current_frame, n_frames):
    """Turn one line of input into a :class:`Command`.

    A bare integer is a **frame** (the default unit here); a bare float is a
    **time in seconds**; ``f``/``s`` suffixes force either.  Seeks are clamped
    to the scene, so ``+99`` on the last frame is harmless.
    """
    raw = (text or "").strip()
    if not raw:
        return Command("noop", None)
    low = raw.lower()
    if low in ("q", "quit", "exit"):
        return Command("quit", None)
    if low in ("s", "save"):
        return Command("save", None)
    if low in ("p", "play"):
        return Command("play", None)
    if low in ("?", "h", "help"):
        return Command("help", None)

    if raw[0] in "+-" and len(raw) > 1:
        try:
            step = float(raw)          # keeps the sign: "+1" == +1, "-10" == -10
        except ValueError:
            return Command("error", "expected a step like +1 or -10: %r" % raw)
        return Command("seek", clamp_frame(current_frame + _round_half_up(step),
                                           n_frames))

    unit = raw[-1].lower()
    core = raw[:-1] if unit in ("f", "s") else raw
    try:
        value = float(core)
    except ValueError:
        return Command("error", "cannot read %r -- try 120, 2.5s, +1, s, q"
                       % raw)

    if unit == "f":
        frame = _round_half_up(value)
    elif unit == "s":
        frame = frame_of_time(value, fps)
    elif core.lstrip("+-").isdigit():
        frame = int(value)                  # bare integer -> frame number
    else:
        frame = frame_of_time(value, fps)   # bare float -> seconds
    return Command("seek", clamp_frame(frame, n_frames))


def bar_geometry(win_rect, bar_height, gap=4):
    """``(x, y, w, h)`` for a bar docked under ``win_rect`` (l, t, r, b)."""
    left, _top, right, bottom = win_rect
    return (int(left), int(bottom) + int(gap),
            max(360, int(right) - int(left)), int(bar_height))


# ---------------------------------------------------------------------------
# terminal input (fallback: no GUI toolkit needed)
# ---------------------------------------------------------------------------

class TerminalInput:
    """Reads lines from stdin on a thread and hands them to ``on_line``."""

    def __init__(self, on_line, prompt="frame> "):
        self._on_line = on_line
        self._prompt = prompt
        self._alive = True
        self._thread = threading.Thread(target=self._run, name="rtm-preview-stdin",
                                        daemon=True)

    def start(self):
        self._thread.start()

    def stop(self):
        self._alive = False

    def _run(self):
        while self._alive:
            try:
                line = input(self._prompt)
            except (EOFError, KeyboardInterrupt):
                self._on_line("q")
                return
            if not self._alive:
                return
            self._on_line(line)


# ---------------------------------------------------------------------------
# the native input bar (Win32, ctypes -- no extra dependency)
# ---------------------------------------------------------------------------

if sys.platform == "win32":  # pragma: no cover - platform dependent
    import ctypes
    import ctypes.wintypes as wt

    _LRESULT = ctypes.c_ssize_t
    _WPARAM = ctypes.c_size_t
    _LPARAM = ctypes.c_ssize_t
    _WNDPROC = ctypes.WINFUNCTYPE(_LRESULT, wt.HWND, ctypes.c_uint,
                                  _WPARAM, _LPARAM)

    class _WNDCLASSEXW(ctypes.Structure):
        _fields_ = [
            ("cbSize", ctypes.c_uint), ("style", ctypes.c_uint),
            ("lpfnWndProc", _WNDPROC), ("cbClsExtra", ctypes.c_int),
            ("cbWndExtra", ctypes.c_int), ("hInstance", wt.HINSTANCE),
            ("hIcon", wt.HICON), ("hCursor", wt.HANDLE),
            ("hbrBackground", wt.HBRUSH), ("lpszMenuName", wt.LPCWSTR),
            ("lpszClassName", wt.LPCWSTR), ("hIconSm", wt.HICON),
        ]

    class _MSG(ctypes.Structure):
        _fields_ = [
            ("hwnd", wt.HWND), ("message", ctypes.c_uint),
            ("wParam", _WPARAM), ("lParam", _LPARAM),
            ("time", ctypes.c_uint), ("pt", wt.POINT),
        ]

    _u = win32.user32
    _k = win32.kernel32
    _g = win32.gdi32
    for _fn, _res, _args in (
            ("CreateWindowExW", wt.HWND,
             [ctypes.c_uint, wt.LPCWSTR, wt.LPCWSTR, ctypes.c_uint,
              ctypes.c_int, ctypes.c_int, ctypes.c_int, ctypes.c_int,
              wt.HWND, wt.HMENU, wt.HINSTANCE, ctypes.c_void_p]),
            ("DefWindowProcW", _LRESULT,
             [wt.HWND, ctypes.c_uint, _WPARAM, _LPARAM]),
            ("DestroyWindow", wt.BOOL, [wt.HWND]),
            ("MoveWindow", wt.BOOL,
             [wt.HWND, ctypes.c_int, ctypes.c_int, ctypes.c_int, ctypes.c_int,
              wt.BOOL]),
            ("SetWindowTextW", wt.BOOL, [wt.HWND, wt.LPCWSTR]),
            ("GetWindowTextW", ctypes.c_int,
             [wt.HWND, wt.LPWSTR, ctypes.c_int]),
            ("SendMessageW", _LRESULT,
             [wt.HWND, ctypes.c_uint, _WPARAM, _LPARAM]),
            ("PostMessageW", wt.BOOL,
             [wt.HWND, ctypes.c_uint, _WPARAM, _LPARAM]),
            ("SetFocus", wt.HWND, [wt.HWND]),
            ("SetForegroundWindow", wt.BOOL, [wt.HWND]),
            ("RegisterClassExW", wt.ATOM, [ctypes.POINTER(_WNDCLASSEXW)]),
            ("UnregisterClassW", wt.BOOL, [wt.LPCWSTR, wt.HINSTANCE]),
            ("LoadCursorW", wt.HANDLE, [wt.HINSTANCE, wt.LPCWSTR]),
            ("GetDpiForWindow", ctypes.c_uint, [wt.HWND]),
            ("PeekMessageW", wt.BOOL,
             [ctypes.POINTER(_MSG), wt.HWND, ctypes.c_uint, ctypes.c_uint,
              ctypes.c_uint]),
            ("TranslateMessage", wt.BOOL, [ctypes.POINTER(_MSG)]),
            ("DispatchMessageW", _LRESULT, [ctypes.POINTER(_MSG)])):
        _f = getattr(_u, _fn, None)
        if _f is not None:
            _f.restype = _res
            _f.argtypes = _args

    _WS_POPUP, _WS_CAPTION, _WS_SYSMENU = 0x80000000, 0x00C00000, 0x00080000
    _WS_CHILD, _WS_VISIBLE, _WS_TABSTOP = 0x40000000, 0x10000000, 0x00010000
    _ES_AUTOHSCROLL = 0x0080
    _BS_DEFPUSHBUTTON = 0x0001
    _WM_CLOSE, _WM_DESTROY, _WM_COMMAND, _WM_SETFOCUS = 0x0010, 0x0002, 0x0111, 0x0007
    _WM_SETFONT = 0x0030
    _DEFAULT_GUI_FONT = 17
    _LTGRAY_BRUSH = 1        # GetStockObject: WHITE 0, LTGRAY 1, GRAY 2, BLACK 4
    _IDC_ARROW = 32512
    _ID_EDIT, _ID_GO, _ID_SAVE, _ID_QUIT = 1001, 1002, 1003, 1004
    _PROC_REFS = []          # keep the WNDPROC alive for Windows
    _BARS = {}               # hwnd -> Win32Bar
    _CLASS_REGISTERED = False

    def _bar_wnd_proc(hwnd, msg, wparam, lparam):
        bar = _BARS.get(hwnd)
        if bar is not None:
            reply = bar._on_message(hwnd, msg, wparam, lparam)
            if reply is not None:
                return reply
        return _u.DefWindowProcW(hwnd, msg, wparam, lparam)

    _bar_wnd_proc_ptr = _WNDPROC(_bar_wnd_proc)
    _PROC_REFS.append(_bar_wnd_proc_ptr)


class Win32Bar:  # pragma: no cover - needs a Windows desktop
    """The small docked window: ``[ frame ] [Enter] [Save PNG] [Quit]``.

    Everything (create, message loop, destroy) happens on one worker thread; the
    main thread only enqueues the typed text, so no rendering ever runs here.
    """

    CLASS_NAME = "RTMPreviewBar"

    def __init__(self, submit, save, quit_, title="RTM frame preview"):
        self._submit, self._save, self._quit = submit, save, quit_
        self._title = title
        self._hwnd = None
        self._edit = None
        self._alive = True
        self._ready = threading.Event()
        self._caption = ""
        self._video = None
        self._thread = None

    # -- lifecycle ----------------------------------------------------------
    def start(self, video_hwnd, timeout=5.0):
        self._video = video_hwnd
        self._thread = threading.Thread(target=self._run, name="rtm-preview-bar",
                                        daemon=True)
        self._thread.start()
        self._ready.wait(timeout)
        return self._hwnd is not None

    def stop(self):
        if self._hwnd:
            _u.PostMessageW(self._hwnd, _WM_CLOSE, 0, 0)
        self._alive = False

    def set_caption(self, text):
        """Thread-safe: the bar's own loop applies it."""
        self._caption = str(text)

    # -- worker thread ------------------------------------------------------
    def _run(self):
        try:
            self._create()
        finally:
            self._ready.set()
        if self._hwnd:
            self._loop()
        _BARS.pop(self._hwnd, None)

    def _create(self):
        global _CLASS_REGISTERED
        hinst = _k.GetModuleHandleW(None)
        if not _CLASS_REGISTERED:
            wc = _WNDCLASSEXW()
            wc.cbSize = ctypes.sizeof(_WNDCLASSEXW)
            wc.style = 0
            wc.lpfnWndProc = _bar_wnd_proc_ptr
            wc.hInstance = hinst
            wc.hCursor = _u.LoadCursorW(None, wt.LPCWSTR(_IDC_ARROW))
            wc.hbrBackground = _g.GetStockObject(_LTGRAY_BRUSH)
            wc.lpszClassName = self.CLASS_NAME
            _u.RegisterClassExW(ctypes.byref(wc))
            _CLASS_REGISTERED = True

        scale = self._dpi_scale()
        self._height = int(38 * scale)
        btn_w = int(78 * scale)

        self._hwnd = _u.CreateWindowExW(
            0, self.CLASS_NAME, self._title,
            _WS_POPUP | _WS_CAPTION | _WS_SYSMENU,
            0, 0, int(900 * scale), self._height,
            None, None, hinst, None)
        if not self._hwnd:
            return
        _BARS[self._hwnd] = self

        font = _g.GetStockObject(_DEFAULT_GUI_FONT)
        pad = int(6 * scale)
        edit_w = max(int(120 * scale), int(520 * scale) - 3 * btn_w - 4 * pad)
        x = pad
        self._edit = _u.CreateWindowExW(
            0, "EDIT", "", _WS_CHILD | _WS_VISIBLE | _WS_TABSTOP |
            _ES_AUTOHSCROLL, x, int(8 * scale), edit_w, self._height - 2 * int(8 * scale),
            self._hwnd, _ID_EDIT, hinst, None)
        x += edit_w + pad
        for i, (label, cid, style) in enumerate((
                ("Jump", _ID_GO, _BS_DEFPUSHBUTTON),
                ("Save PNG", _ID_SAVE, 0),
                ("Quit", _ID_QUIT, 0))):
            _u.CreateWindowExW(
                0, "BUTTON", label, _WS_CHILD | _WS_VISIBLE | _WS_TABSTOP |
                style, x, int(6 * scale), btn_w, self._height - 2 * int(6 * scale),
                self._hwnd, cid, hinst, None)
            x += btn_w + int(2 * scale)
        for ctl in (self._edit,):
            if ctl:
                _u.SendMessageW(ctl, _WM_SETFONT, int(font or 0), 1)

        self._dock()
        _u.SetForegroundWindow(self._hwnd)
        if self._edit:
            _u.SetFocus(self._edit)

    def _dpi_scale(self):
        dpi = 96
        try:
            if self._hwnd:
                dpi = int(_u.GetDpiForWindow(self._hwnd)) or 96
        except Exception:
            pass
        return max(1.0, dpi / 96.0)

    def _dock(self):
        hw = win32.find_video_hwnd() or self._video
        rect = win32.window_rect(hw)
        if not rect or not self._hwnd:
            return
        x, y, w, h = bar_geometry(rect, self._height)
        _u.MoveWindow(self._hwnd, x, y, w, h, True)

    def _loop(self):
        msg = _MSG()
        last_dock = 0.0
        applied = None
        while self._alive:
            if _u.PeekMessageW(ctypes.byref(msg), None, 0, 0, 1):
                _u.TranslateMessage(ctypes.byref(msg))
                _u.DispatchMessageW(ctypes.byref(msg))
                continue
            now = time.perf_counter()
            if now - last_dock > 0.2:
                last_dock = now
                self._dock()
            if self._caption != applied:
                applied = self._caption
                _u.SetWindowTextW(self._hwnd, applied)
            time.sleep(0.01)

    # -- window messages ----------------------------------------------------
    def _on_message(self, hwnd, msg, wparam, lparam):
        if msg == _WM_COMMAND:
            cid = int(wparam) & 0xFFFF
            if cid == _ID_GO:
                self._pressed(self._submit)
                return 0
            if cid == _ID_SAVE:
                self._pressed(self._save)
                return 0
            if cid == _ID_QUIT:
                self._pressed(self._quit)
                return 0
        elif msg == _WM_CLOSE:
            self._alive = False
            _u.DestroyWindow(hwnd)
            return 0
        elif msg == _WM_DESTROY:
            self._alive = False
            return 0
        elif msg == _WM_SETFOCUS and self._edit:
            _u.SetFocus(self._edit)
            return 0
        return None

    def _pressed(self, action):
        text = self._text()
        if action is self._submit:
            action(text)
        else:
            action()
        if self._edit:
            _u.SetWindowTextW(self._edit, "")

    def _text(self):
        if not self._edit:
            return ""
        buf = ctypes.create_unicode_buffer(256)
        _u.GetWindowTextW(self._edit, buf, 256)
        return buf.value


# ---------------------------------------------------------------------------
# the preview itself
# ---------------------------------------------------------------------------

class FramePreview:
    """A still window plus an input bar; every seek is a single O(1) draw."""

    def __init__(self, scene_cls, fps=60, out_dir="frames", use_bar=True,
                 width=None, height=None, verbose=True):
        self.fps = int(fps)
        self.out_dir = out_dir
        self.verbose = verbose
        self._queue = queue.Queue()
        self.use_bar = bool(use_bar) and sys.platform == "win32"
        self._log = (lambda *a: print("[rtm]", *a)) if verbose else (lambda *a: None)
        self._print = print if verbose else (lambda *a: None)

        kwargs = {}
        if width:
            kwargs["width"] = int(width)
        if height:
            kwargs["height"] = int(height)
        t0 = time.perf_counter()
        self.server = FrameServer(scene_cls, hidden=True, **kwargs)
        self.prepare_seconds = time.perf_counter() - t0

        self.window = self.server.window
        self.duration = float(self.server.duration)
        self.n_frames = max(1, int(round(self.duration * self.fps)))
        self.current = 0
        self.running = False
        self.saved = []
        self._bar = None
        self._term = None
        self._playing = False

    # -- public -------------------------------------------------------------
    @property
    def last_frame(self):
        return self.n_frames - 1

    def time_of(self, frame):
        return time_of_frame(frame, self.fps)

    def frame_of(self, t):
        return clamp_frame(frame_of_time(t, self.fps), self.n_frames)

    def run(self, start_frame=0):
        """Show the window on ``start_frame``, then serve the input bar."""
        self.running = True
        try:
            self._seek(start_frame)
            self.server.show_frame(self.time_of(self.current))  # reveal it
            self._log("prepared in %.2fs (construct ran once, nothing rendered); "
                      "%d frames / %.2fs" % (self.prepare_seconds,
                                             self.n_frames, self.duration))
            submit, save, quit_ = self._input_callbacks()
            if self.use_bar:
                self._bar = Win32Bar(submit, save, quit_)
                if not self._bar.start(self.window.hwnd):
                    self._bar = None
            if self._bar is None:
                self._log(HELP)
                self._term = TerminalInput(submit)
                self._term.start()
            self._status()
            self._loop()
        finally:
            self.close()
        return 0

    def _input_callbacks(self):
        """``(submit, save, quit)`` for the input widgets.

        They *only* enqueue: rendering has to stay on the main thread (one
        swapchain, not thread-safe), so the bar's and the terminal's own threads
        must never touch the timeline.
        """
        return (lambda text: self._queue.put_nowait(("text", text)),
                lambda: self._queue.put_nowait(("save", None)),
                lambda: self._queue.put_nowait(("quit", None)))

    def close(self):
        self.running = False
        for closer in (self._bar.stop if self._bar else None,
                       self._term.stop if self._term else None):
            if closer:
                closer()
        self._bar = None
        self._term = None
        try:
            self.server.close()
        except Exception:
            pass

    # -- main loop ----------------------------------------------------------
    def _loop(self):
        while self.running:
            try:
                kind, payload = self._queue.get(timeout=0.02)
            except queue.Empty:
                # Keep the OS window alive: this pumps its messages, redraws the
                # last submitted frame and handles resize.  It returns False once
                # the user closed the window.
                if not self.window.tick():
                    break
                continue
            if kind == "quit":
                break
            if kind == "save":
                self._save()
                continue
            if kind == "text":
                self._handle(parse_spec(payload, self.fps, self.current,
                                        self.n_frames))
                continue
            if kind == "seek":
                self._seek(payload)
                self._status()

    def _handle(self, cmd):
        if cmd.kind == "quit":
            self.running = False
        elif cmd.kind == "seek":
            self._seek(cmd.value)
            self._status()
        elif cmd.kind == "save":
            self._save()
        elif cmd.kind == "play":
            self._play()
        elif cmd.kind == "help":
            self._print(HELP)
            self._status()
        elif cmd.kind == "error":
            self._print("[rtm] " + cmd.value)
            self._status(cmd.value)
        elif cmd.kind != "noop":
            self._status()

    # -- actions ------------------------------------------------------------
    def _seek(self, frame):
        frame = clamp_frame(frame, self.n_frames)
        self.server.render_frame(self.time_of(frame))
        self.current = frame
        return frame

    def _save(self):
        os.makedirs(self.out_dir, exist_ok=True)
        path = os.path.join(self.out_dir, "f_%04d.png" % self.current)
        self.server.save_frame(self.time_of(self.current), path)
        self.saved.append(path)
        self._log("saved %s" % path)
        self._status("saved %s" % os.path.basename(path))

    def _play(self):
        """Play forward from here at ``fps``; any input stops it."""
        self._playing = True
        frame = self.current
        deadline = time.perf_counter()
        while self._playing and self.running and frame < self.n_frames:
            try:
                kind, payload = self._queue.get_nowait()
            except queue.Empty:
                pass
            else:
                self._playing = False
                if kind == "quit":
                    self.running = False
                elif kind == "save":
                    self._save()
                elif kind == "text":
                    self._handle(parse_spec(payload, self.fps, self.current,
                                            self.n_frames))
                return
            if not self.server.timeline.render_at(self.time_of(frame)):
                self._playing = False
                self.running = False
                return
            self.current = frame
            if frame % 15 == 0:
                self._status()
            frame += 1
            deadline += 1.0 / self.fps
            delay = deadline - time.perf_counter()
            if delay > 0:
                time.sleep(delay)
            else:
                deadline = time.perf_counter()      # fell behind: re-anchor
        self._playing = False
        self._status("played to frame %d" % self.current)

    # -- feedback -----------------------------------------------------------
    def _status(self, message=None):
        text = "frame %d/%d   t=%.3fs" % (self.current, self.last_frame,
                                          self.time_of(self.current))
        if message:
            text = "%s   |   %s" % (message, text)
        if self._bar is not None:
            self._bar.set_caption(text)
        elif self.verbose:
            # No bar (macOS / --no-bar): the terminal is the only feedback.
            self._print("[rtm] " + text)


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------

def _resolve_scene(token):
    from real_time_manim.frames import _resolve_scene as resolve
    try:
        return resolve(token)
    except ImportError:
        raise SystemExit(
            "cannot resolve %r: run this from the repository root, or pass "
            "'module:Class'" % token)


def main(argv=None):
    ap = argparse.ArgumentParser(
        prog="python -m real_time_manim.preview",
        description="Show any frame of a scene instantly (no pre-render).")
    ap.add_argument("scene", help="demo number (from run.py) or 'module:Class'")
    ap.add_argument("--fps", type=int, default=60, help="frame numbering rate")
    ap.add_argument("--at", type=int, default=0, help="first frame to show")
    ap.add_argument("--out", default="frames", help="where 's' writes PNGs")
    ap.add_argument("--no-bar", action="store_true",
                    help="type in the terminal instead of the docked bar")
    ap.add_argument("--quiet", action="store_true")
    args = ap.parse_args(argv if argv is not None else sys.argv[1:])

    cls = _resolve_scene(args.scene)
    preview = FramePreview(cls, fps=args.fps, out_dir=args.out,
                           use_bar=not args.no_bar, verbose=not args.quiet)
    return preview.run(start_frame=args.at)


if __name__ == "__main__":
    raise SystemExit(main())
