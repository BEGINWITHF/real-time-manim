# -*- coding: utf-8 -*-
"""Interactive any-frame preview: a still window + a native input bar.

Nothing plays when it opens.  Type a frame, press Enter, and the window shows
that frame -- no pre-render, no replay: ``Timeline.render_at`` is O(1) in ``t``
(see the 2.0 time-addressable design notes), so a seek costs ~10 ms no matter
where it lands.

    python -m real_time_manim.preview my_scene:Hello           # module:Class
    python -m real_time_manim.preview my_scene:Hello --at 120
    python -m real_time_manim.preview my_scene:Hello --no-bar  # terminal input

A bare number (``1``) selects an entry from the development tree's demo
table; that table is not part of the installed package.

One-off cost
------------
Preparing the scene runs ``construct()`` **once**, with scheduling on: ``play``
records what each animation does instead of drawing it (``FrameServer``), which
is what makes every later seek O(1).  No frame is rendered ahead of time -- the
first picture you see is only drawn when the window appears.

Caveat: a seek replays **animation** state, not accumulated *updater* state, so
a scene whose mobjects are only driven by custom updaters / ``TracedPath`` is
exact when you step forward and approximate when you jump backwards.  Making
those time-replayable is P3 in the 2.0 time-addressable design notes.

Input bar
---------
On Windows and macOS the bar is native -- no GUI toolkit needed.  It comes in
two flavours (``controls=``):

``"input"`` (default)
    a text field + *Jump* / *Save PNG* / *Quit*.
``"slider"``
    a draggable progress bar (scrubber) + *Save PNG* / *Quit*.

The current frame always shows in the bar window's title.  Accepted input:

    123 / 123f   frame 123            (frame numbers are the default unit)
    1.5 / 1.5s   time 1.5 s
    +1 / -10     step N frames from the current one
    s            save the current frame as PNG (into --out)
    p            play forward from here (any input stops it)
    ?            help
    q            quit

On Windows the bar is Win32 and lives in a bar window docked under the video.
On macOS it is Cocoa through the same bundled dylib: a separate native window
docked under the video as well, kept clear of an auto-hiding Dock.  Other
platforms (or ``--no-bar``) read the same input from the terminal, so the mode
works without a GUI toolkit.
"""
from __future__ import annotations

import argparse
import collections
import ctypes
import os
import queue
import re
import sys
import threading
import time

from real_time_manim.frames import FrameServer
from real_time_manim.window import win32
from real_time_manim.window.win32 import force_foreground

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


CONTROL_ALIASES = {
    "input": "input", "box": "input", "text": "input", "edit": "input",
    "slider": "slider", "bar": "slider", "progress": "slider",
    "progressbar": "slider", "scrub": "slider",
}


def normalize_controls(value):
    """Map whatever the caller called it to ``"input"`` or ``"slider"``.

    ``"slider"`` is the draggable scrubber (a progress bar you can drag);
    everything else means the text field.
    """
    key = str(value or "input").strip().lower().replace("_", "").replace("-", "")
    if key not in CONTROL_ALIASES:
        raise ValueError("controls must be 'input' or 'slider', got %r"
                         % (value,))
    return CONTROL_ALIASES[key]


def parse_position(value):
    """``"X,Y"`` -> ``(x, y)``; ``None``/``""`` -> ``None``.

    Used to place the video window, so several previews do not land on top of
    each other (the native window is created with ``CW_USEDEFAULT``, which
    Windows does not cascade for a WS_OVERLAPPEDWINDOW created per process).

    Lenient about the spelling on purpose: shells love to rewrite
    ``100,80`` -- PowerShell hands over ``(100, 80)`` -- so the two numbers are
    just regex-extracted from whatever form arrived.
    """
    if value is None:
        return None
    if isinstance(value, (tuple, list)):
        if len(value) != 2:
            raise ValueError("position must be two numbers, got %r" % (value,))
        return (int(value[0]), int(value[1]))
    text = str(value).strip()
    if not text:
        return None
    nums = re.findall(r"-?\d+(?:\.\d+)?", text)
    if len(nums) != 2:
        raise ValueError("position must look like '100,200', got %r" % (value,))
    return (int(float(nums[0])), int(float(nums[1])))


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
            ("ShowWindow", wt.BOOL, [wt.HWND, ctypes.c_int]),
            ("UpdateWindow", wt.BOOL, [wt.HWND]),
            ("IsWindowVisible", wt.BOOL, [wt.HWND]),
            ("RegisterClassExW", wt.ATOM, [ctypes.POINTER(_WNDCLASSEXW)]),
            ("UnregisterClassW", wt.BOOL, [wt.LPCWSTR, wt.HINSTANCE]),
            ("LoadCursorW", wt.HANDLE, [wt.HINSTANCE, wt.LPCWSTR]),
            ("SetWindowLongPtrW", ctypes.c_void_p,
             [wt.HWND, ctypes.c_int, ctypes.c_void_p]),
            ("CallWindowProcW", _LRESULT,
             [ctypes.c_void_p, wt.HWND, ctypes.c_uint, _WPARAM, _LPARAM]),
            ("LoadImageW", wt.HANDLE,
             [wt.HINSTANCE, wt.LPCWSTR, ctypes.c_uint,
              ctypes.c_int, ctypes.c_int, ctypes.c_uint]),
            ("GetDpiForWindow", ctypes.c_uint, [wt.HWND]),
            ("AdjustWindowRectEx", wt.BOOL,
             [ctypes.POINTER(wt.RECT), ctypes.c_uint, wt.BOOL, ctypes.c_uint]),
            ("GetDpiForSystem", ctypes.c_uint, []),
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
    _WS_VISIBLE = 0x10000000
    _WS_CHILD, _WS_TABSTOP = 0x40000000, 0x00010000
    _ES_AUTOHSCROLL = 0x0080
    _BS_DEFPUSHBUTTON = 0x0001
    _SW_SHOW = 5
    _WM_CLOSE, _WM_DESTROY, _WM_COMMAND, _WM_SETFOCUS = 0x0010, 0x0002, 0x0111, 0x0007
    _WM_HSCROLL = 0x0114
    _WM_LBUTTONDOWN = 0x0201
    _GWLP_WNDPROC = -4
    _WM_SETFONT = 0x0030
    _DEFAULT_GUI_FONT = 17
    _LTGRAY_BRUSH = 1        # GetStockObject: WHITE 0, LTGRAY 1, GRAY 2, BLACK 4
    _IDC_ARROW = 32512
    _ICC_BAR_CLASSES = 0x0004
    _TBM_GETPOS, _TBM_SETPOS, _TBM_SETRANGE = 0x0400, 0x0405, 0x0406
    _TBM_SETTICFREQ = 0x0414
    _TRACKBAR_CLASS = "msctls_trackbar32"
    _TBS_AUTOTICKS, _TBS_TOOLTIPS = 0x0001, 0x0100
    _ID_EDIT, _ID_GO, _ID_SAVE, _ID_QUIT, _ID_SLIDER = 1001, 1002, 1003, 1004, 1005
    _PROC_REFS = []          # keep the WNDPROC alive for Windows
    _BARS = {}               # hwnd -> Win32Bar
    _CLASS_REGISTERED = False

    class _INITCOMMONCONTROLSEX(ctypes.Structure):
        _fields_ = [("dwSize", wt.DWORD), ("dwICC", wt.DWORD)]

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
    """The small docked window under the video.

    Two looks, picked by ``controls``:

    ``"input"`` (default)
        ``[ frame ] [Jump] [Save PNG] [Quit]`` -- type a frame number.

    ``"slider"``
        ``[========|===== ] [Save PNG] [Quit]`` -- drag the trackbar to scrub
        (a "progress bar" you can drag); the current frame is in the title bar
        either way.

    Everything (create, message loop, destroy) happens on one worker thread; the
    main thread only enqueues, so no rendering ever runs here.
    """

    CLASS_NAME = "RTMPreviewBar"

    def __init__(self, submit, save, quit_, seek=None, controls="input",
                 n_frames=1, title="RTM frame preview"):
        self._submit, self._save, self._quit = submit, save, quit_
        self._seek = seek
        self.controls = normalize_controls(controls)
        self._n_frames = max(1, int(n_frames))
        self._title = title
        self._hwnd = None
        self._edit = None
        self._slider = None
        self._alive = True
        self._ready = threading.Event()
        self._caption = ""
        self._position = None          # frame the slider should show
        self._video = None
        self._thread = None
        self._client_h = 0
        self._outer_h = 0

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

    def set_position(self, frame):
        """Thread-safe: move the scrubber to ``frame`` (slider mode)."""
        self._position = int(frame)

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
            # The trackbar lives in the common-controls DLL (comctl32, not
            # user32 -- and it is what registers "msctls_trackbar32").
            if win32.comctl32 is not None:
                icc = _INITCOMMONCONTROLSEX(
                    ctypes.sizeof(_INITCOMMONCONTROLSEX), _ICC_BAR_CLASSES)
                try:
                    win32.comctl32.InitCommonControlsEx(ctypes.byref(icc))
                except Exception:
                    pass
            wc = _WNDCLASSEXW()
            wc.cbSize = ctypes.sizeof(_WNDCLASSEXW)
            wc.style = 0
            wc.lpfnWndProc = _bar_wnd_proc_ptr
            wc.hInstance = hinst
            wc.hCursor = _u.LoadCursorW(None, wt.LPCWSTR(_IDC_ARROW))
            wc.hbrBackground = _g.GetStockObject(_LTGRAY_BRUSH)
            wc.lpszClassName = self.CLASS_NAME
            # Same icon as the main window: the control bar is a separate
            # window class, so without this it shows the default Python icon.
            _icon = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                                 "logo.ico")
            if getattr(_u, "LoadImageW", None) is not None and os.path.exists(_icon):
                _LR_LOADFROMFILE, _LR_DEFAULTSIZE = 0x10, 0x40
                _IMAGE_ICON = 1
                try:
                    wc.hIcon = _u.LoadImageW(
                        None, wt.LPCWSTR(_icon), _IMAGE_ICON, 0, 0,
                        _LR_LOADFROMFILE | _LR_DEFAULTSIZE)
                    wc.hIconSm = wc.hIcon
                except Exception:
                    pass
            _u.RegisterClassExW(ctypes.byref(wc))
            _CLASS_REGISTERED = True

        scale = self._dpi_scale()
        style = _WS_POPUP | _WS_CAPTION | _WS_SYSMENU
        # `MoveWindow` takes the OUTER size, so size for the client area we
        # actually want and let Windows add its caption -- sizing the outer box
        # to 34 px left ~19 px of client area and the widgets were invisible.
        self._client_h = int(36 * scale)
        rect = wt.RECT(0, 0, int(900 * scale), self._client_h)
        _u.AdjustWindowRectEx(ctypes.byref(rect), style, False, 0)
        outer_w = int(rect.right - rect.left)
        self._outer_h = int(rect.bottom - rect.top)

        self._hwnd = _u.CreateWindowExW(
            0, self.CLASS_NAME, self._title,
            style | _WS_VISIBLE,          # without this the window stays hidden
            0, 0, outer_w, self._outer_h,
            None, None, hinst, None)
        if not self._hwnd:
            return
        _BARS[self._hwnd] = self

        font = _g.GetStockObject(_DEFAULT_GUI_FONT)
        btn_w = int(80 * scale)          # Jump / Quit
        save_w = int(104 * scale)        # "Save PNG" must not ellipsize
        pad = int(6 * scale)
        ctl_h = self._client_h - 2 * pad
        y = pad
        controls = []
        if self.controls == "slider":
            x = pad
            w = outer_w - save_w - btn_w - 3 * pad
            self._slider = _u.CreateWindowExW(
                0, _TRACKBAR_CLASS, "",
                _WS_CHILD | _WS_VISIBLE | _WS_TABSTOP | _TBS_AUTOTICKS |
                _TBS_TOOLTIPS, x, y, w, ctl_h, self._hwnd, _ID_SLIDER, hinst,
                None)
            _u.SendMessageW(self._slider, _TBM_SETRANGE, 1,
                            (self._n_frames - 1) << 16 | 0)
            _u.SendMessageW(self._slider, _TBM_SETTICFREQ,
                            max(1, self._n_frames // 10), 0)
            _u.SendMessageW(self._slider, _TBM_SETPOS, 1, 0)
            # click-to-seek: remember the width and subclass the control
            self._slider_w = w
            self._slider_proc_obj = _WNDPROC(self._slider_proc)
            self._slider_old_proc = _u.SetWindowLongPtrW(
                self._slider, _GWLP_WNDPROC,
                ctypes.cast(self._slider_proc_obj, ctypes.c_void_p))
            controls.append(self._slider)
            x += w + pad
            buttons = (("Save PNG", _ID_SAVE, 0, save_w),
                       ("Quit", _ID_QUIT, 0, btn_w))
        else:
            x = pad
            w = outer_w - 2 * btn_w - save_w - 4 * pad
            self._edit = _u.CreateWindowExW(
                0, "EDIT", "", _WS_CHILD | _WS_VISIBLE | _WS_TABSTOP |
                _ES_AUTOHSCROLL, x, y, w, ctl_h, self._hwnd, _ID_EDIT, hinst,
                None)
            controls.append(self._edit)
            x += w + pad
            buttons = (("Jump", _ID_GO, _BS_DEFPUSHBUTTON, btn_w),
                       ("Save PNG", _ID_SAVE, 0, save_w),
                       ("Quit", _ID_QUIT, 0, btn_w))
        for label, cid, bstyle, bw in buttons:
            controls.append(_u.CreateWindowExW(
                0, "BUTTON", label, _WS_CHILD | _WS_VISIBLE | _WS_TABSTOP |
                bstyle, x, y, bw, ctl_h, self._hwnd, cid, hinst, None))
            x += bw + int(2 * scale)
        for ctl in controls:
            if ctl:
                _u.SendMessageW(ctl, _WM_SETFONT, int(font or 0), 1)

        self._dock()
        # Belt and braces: WS_VISIBLE at creation plus an explicit show, so the
        # bar is really on screen (`MoveWindow` never reveals a hidden window --
        # which is how the first version ended up invisible while every
        # GetWindowText/GetWindowRect probe still answered happily).
        _u.ShowWindow(self._hwnd, _SW_SHOW)
        _u.UpdateWindow(self._hwnd)
        force_foreground(self._hwnd)
        if self._edit:
            _u.SetFocus(self._edit)
        elif self._slider:
            _u.SetFocus(self._slider)

    def _dpi_scale(self):
        dpi = 96
        for probe in (lambda: _u.GetDpiForWindow(self._hwnd),
                      lambda: _u.GetDpiForSystem()):
            try:
                value = int(probe())
            except Exception:
                continue
            if value:
                dpi = value
                break
        return max(1.0, dpi / 96.0)

    def _dock(self):
        # Our OWN video window first: a second preview in another process would
        # otherwise make both bars stack under whichever window is found first.
        hw = self._video
        if not (hw and _u.IsWindow(hw)):
            hw = win32.find_video_hwnd()
        rect = win32.window_rect(hw)
        if not rect or not self._hwnd:
            return
        x, y, w, h = bar_geometry(rect, self._outer_h)
        _u.MoveWindow(self._hwnd, x, y, w, h, True)

    def _loop(self):
        msg = _MSG()
        last_dock = 0.0
        applied = None
        applied_pos = None
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
            if self._position is not None and self._position != applied_pos:
                applied_pos = self._position
                _u.SendMessageW(self._slider, _TBM_SETPOS, 1, applied_pos)
            time.sleep(0.01)

    def _slider_proc(self, hwnd, msg, wparam, lparam):
        """Exact seek on a channel click (the stock control only pages)."""
        if msg == _WM_LBUTTONDOWN:
            try:
                x = ctypes.c_short(lparam & 0xFFFF).value
                margin = int(6 * self._dpi_scale())
                span = max(1, self._slider_w - 2 * margin)
                frac = (x - margin) / span
                pos = int(round((self._n_frames - 1)
                                * min(1.0, max(0.0, frac))))
                _u.SendMessageW(hwnd, _TBM_SETPOS, 1, pos)
                # TB_THUMBTRACK = 5: the bar seeks straight to this frame
                _u.SendMessageW(self._hwnd, _WM_HSCROLL,
                                (pos << 16) | 5, hwnd)
            except Exception:
                pass
        return _u.CallWindowProcW(self._slider_old_proc, hwnd, msg,
                                  wparam, lparam)

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
        elif msg == _WM_HSCROLL and self._slider and self._seek:
            # The user dragged / clicked the scrubber: seek straight there.
            pos = int(_u.SendMessageW(self._slider, _TBM_GETPOS, 0, 0))
            self._seek(pos)
            return 0
        elif msg == _WM_CLOSE:
            self._alive = False
            _u.DestroyWindow(hwnd)
            return 0
        elif msg == _WM_DESTROY:
            self._alive = False
            return 0
        elif msg == _WM_SETFOCUS and (self._edit or self._slider):
            _u.SetFocus(self._edit or self._slider)
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
# the native input bar (Cocoa, through the same dylib -- no extra dependency)
# ---------------------------------------------------------------------------

_MAC_BAR_NONE = 0
_MAC_BAR_SUBMIT = 1
_MAC_BAR_SAVE = 2
_MAC_BAR_QUIT = 3
_MAC_BAR_SEEK = 4


class MacBar:
    """The Cocoa control bar docked below the preview window (macOS).

    It mirrors :class:`Win32Bar` exactly -- same ``controls`` looks, same
    widgets, same callbacks::

    ``"input"`` (default)
        ``[ frame ] [Jump] [Save PNG] [Quit]`` -- type a frame number.

    ``"slider"``
        ``[========|===== ] [Save PNG] [Quit]`` -- drag the scrubber.

    Like Win32Bar it is a window of its own, docked just below the video
    window.  The difference in threading follows: AppKit only runs on the main
    thread, which is also where ``FramePreview._loop`` already is, so the
    native side queues clicks/keystrokes and :meth:`poll` turns them into the
    same ``("text"|"seek"|"save"|"quit", payload)`` items Win32Bar pushes into
    the preview queue.  There is no bar thread and no Python callback from
    inside AppKit.
    """

    def __init__(self, submit, save, quit_, seek=None, controls="input",
                 n_frames=1, title="RTM frame preview", dll=None):
        self._submit, self._save, self._quit = submit, save, quit_
        self._seek = seek
        self.controls = normalize_controls(controls)
        self._n_frames = max(1, int(n_frames))
        self._title = title
        self._dll = dll
        self._started = False
        self._caption = None
        self._position = None
        self._create = self._poll = None
        self._set_caption = self._set_position = self._destroy = None

    # -- lifecycle ----------------------------------------------------------
    def _bind(self):
        dll = self._dll
        if dll is None:
            return False
        try:
            create = dll.Vulkan_CreatePreviewBar
            poll = dll.Vulkan_PollPreviewBar
            caption = dll.Vulkan_SetPreviewBarCaption
            position = dll.Vulkan_SetPreviewBarPosition
            destroy = dll.Vulkan_DestroyPreviewBar
        except AttributeError:      # older dylib -> terminal fallback
            return False
        create.restype = ctypes.c_int
        create.argtypes = [ctypes.c_int, ctypes.c_int, ctypes.c_char_p]
        poll.restype = ctypes.c_int
        poll.argtypes = [ctypes.POINTER(ctypes.c_int), ctypes.c_char_p,
                         ctypes.c_int]
        caption.restype = None
        caption.argtypes = [ctypes.c_char_p]
        position.restype = None
        position.argtypes = [ctypes.c_int]
        destroy.restype = None
        destroy.argtypes = []
        self._create, self._poll = create, poll
        self._set_caption, self._set_position = caption, position
        self._destroy = destroy
        return True

    def start(self, video_window=None, timeout=5.0):
        """Create the bar on the current (main) thread.  False -> fall back."""
        (video_window, timeout)        # parity with Win32Bar.start's signature
        if not self._bind():
            return False
        mode = 1 if self.controls == "slider" else 0
        if not self._create(self._n_frames, mode, self._title.encode("utf-8")):
            return False
        self._started = True
        return True

    def stop(self):
        if self._started:
            self._destroy()
            self._started = False
        self._caption = None
        self._position = None

    # -- feedback (main thread) --------------------------------------------
    def set_caption(self, text):
        """Set the title-bar text (the window's own loop used to do this)."""
        if not self._started:
            return
        text = str(text)
        if text != self._caption:
            self._caption = text
            self._set_caption(text.encode("utf-8"))

    def set_position(self, frame):
        """Move the scrubber without emitting a seek event (slider mode)."""
        if not self._started or self.controls != "slider":
            return
        frame = int(frame)
        if frame != self._position:
            self._position = frame
            self._set_position(frame)

    # -- events -------------------------------------------------------------
    def poll(self):
        """Drain the native event queue into preview-queue items.

        Returns at most the events that arrived since the last call; callers
        put them on ``FramePreview._queue`` so ``_dispatch`` stays the single
        place that acts on input.
        """
        if not self._started:
            return []
        events = []
        value = ctypes.c_int(0)
        buf = ctypes.create_string_buffer(256)
        while True:
            kind = self._poll(ctypes.byref(value), buf, len(buf))
            if kind == _MAC_BAR_NONE:
                break
            if kind == _MAC_BAR_SUBMIT:
                events.append(("text", buf.value.decode("utf-8", "replace")))
            elif kind == _MAC_BAR_SAVE:
                events.append(("save", None))
            elif kind == _MAC_BAR_QUIT:
                events.append(("quit", None))
            elif kind == _MAC_BAR_SEEK:
                events.append(("seek", int(value.value)))
            # Unknown codes are ignored: forward compatibility.
        return events


def _bar_class():
    """The native input bar for this platform, or ``None`` (terminal only)."""
    if sys.platform == "win32":
        return Win32Bar
    if sys.platform == "darwin":
        return MacBar
    return None


def _reserve_bar_space(window, enabled=True):
    """Reserve room below the video for the macOS bar before it is revealed.

    The native window is revealed before the bar exists, so the platform layer
    cannot see it yet.  On a display whose visible frame is exactly the video's
    aspect ratio, the bar would otherwise land against the screen edge, where
    an auto-hidden Dock intercepts its clicks.  A dylib without the export is
    simply left alone.
    """
    reserve = getattr(getattr(window, "dll", None),
                      "Vulkan_SetPreviewBarReserve", None)
    if reserve is None:
        return False
    reserve.restype = None
    reserve.argtypes = [ctypes.c_int]
    reserve(1 if enabled else 0)
    return True


# ---------------------------------------------------------------------------
# the preview itself
# ---------------------------------------------------------------------------

class FramePreview:
    """A still window plus an input bar; every seek is a single O(1) draw."""

    def __init__(self, scene_cls, fps=60, out_dir="frames", use_bar=True,
                 width=None, height=None, verbose=True, controls="input",
                 position=None):
        self.fps = int(fps)
        self.out_dir = out_dir
        self.verbose = verbose
        self.controls = normalize_controls(controls)
        self.position = parse_position(position)
        self._queue = queue.Queue()
        self.use_bar = bool(use_bar) and _bar_class() is not None
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
        # Frame indices follow the play-by-play grid (`Timeline.frame_times`),
        # so frame N is the same picture a recording writes at N -- a frozen
        # wait's int() frames included.
        self._times = self.server.frame_times(self.fps)
        self.n_frames = max(1, len(self._times))
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
        frame = clamp_frame(frame, self.n_frames)
        times = getattr(self, "_times", None)
        if times and frame < len(times):
            return float(times[frame])
        return time_of_frame(frame, self.fps)

    def frame_of(self, t):
        return clamp_frame(frame_of_time(t, self.fps), self.n_frames)

    def run(self, start_frame=0):
        """Show the window on ``start_frame``, then serve the input bar."""
        self.running = True
        try:
            if _bar_class() is MacBar:
                _reserve_bar_space(self.window, enabled=self.use_bar)
            self._seek(start_frame)
            self.server.show_frame(self.time_of(self.current))  # reveal it
            self._log("prepared in %.2fs (construct ran once, nothing rendered); "
                      "%d frames / %.2fs" % (self.prepare_seconds,
                                             self.n_frames, self.duration))
            if self.position:
                self._place(self.position)
            # A terminal behind a maximized editor cannot hand us the
            # foreground, so the window would open *under* it: claim it.
            force_foreground(self.window.hwnd)
            submit, save, quit_ = self._input_callbacks()
            if self.use_bar:
                bar_cls = _bar_class()
                kwargs = {}
                if bar_cls is MacBar:
                    kwargs["dll"] = self.window.dll
                self._bar = bar_cls(
                    submit, save, quit_,
                    seek=lambda frame: self._queue.put_nowait(("seek", frame)),
                    controls=self.controls, n_frames=self.n_frames, **kwargs)
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

    def _place(self, position):
        """Move the video window (the docked bar follows within 0.2 s)."""
        from real_time_manim.window import win32

        hwnd = self.window.hwnd
        rect = win32.window_rect(hwnd)
        if not rect:
            return
        left, top, right, bottom = rect
        win32.user32.MoveWindow(hwnd, int(position[0]), int(position[1]),
                                right - left, bottom - top, True)

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
    def _pump_bar(self):
        """Move native bar events into the queue.

        Win32Bar pushes from its own thread; MacBar queues in AppKit and has to
        be polled here, on the main thread.  Either way ``_dispatch`` is the
        only code that touches the timeline.
        """
        bar = self._bar
        poll = getattr(bar, "poll", None) if bar is not None else None
        if poll is None:
            return
        for kind, payload in poll():
            self._queue.put_nowait((kind, payload))

    def _loop(self):
        while self.running:
            self._pump_bar()
            try:
                kind, payload = self._queue.get(timeout=0.02)
            except queue.Empty:
                # Keep the OS window alive: this pumps its messages, redraws the
                # last submitted frame and handles resize.  It returns False once
                # the user closed the window.
                if not self.window.tick():
                    break
                self._pump_bar()
                continue
            self._dispatch(kind, payload)

    def _dispatch(self, kind, payload):
        """Act on one queued item.

        A scrubber drag queues one ``seek`` per pixel, so a burst of seeks is
        collapsed to the newest before drawing -- and anything else that was
        queued behind them (a save, a typed line, quit) is still run, in order.
        """
        if kind == "quit":
            self.running = False
        elif kind == "save":
            self._save()
        elif kind == "text":
            self._handle(parse_spec(payload, self.fps, self.current,
                                    self.n_frames))
        elif kind == "seek":
            deferred = []
            frame = payload
            while True:
                try:
                    k2, p2 = self._queue.get_nowait()
                except queue.Empty:
                    break
                if k2 == "seek":
                    frame = p2
                else:
                    deferred.append((k2, p2))
            self._seek(frame)
            self._status()
            for k2, p2 in deferred:
                self._dispatch(k2, p2)

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
            self._pump_bar()
            try:
                kind, payload = self._queue.get_nowait()
            except queue.Empty:
                pass
            else:
                self._playing = False
                self._dispatch(kind, payload)
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
            self._bar.set_position(self.current)      # slider mode
        elif self.verbose:
            # No bar (--no-bar, or a platform without one): terminal feedback.
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
    ap.add_argument("scene", help="'module:Class' (a demo number needs the "
                               "development-only demo table)")
    ap.add_argument("--fps", type=int, default=60, help="frame numbering rate")
    ap.add_argument("--at", type=int, default=0, help="first frame to show")
    ap.add_argument("--out", default="frames", help="where 's' writes PNGs")
    ap.add_argument("--controls", default="input", metavar="{input,slider}",
                    help="docked bar: 'input' = type a frame (default), "
                         "'slider' = drag a progress bar to scrub")
    ap.add_argument("--pos", default=None, metavar="X,Y",
                    help="place the window (keeps several previews apart)")
    ap.add_argument("--no-bar", action="store_true",
                    help="type in the terminal instead of the docked bar")
    ap.add_argument("--quiet", action="store_true")
    args = ap.parse_args(argv if argv is not None else sys.argv[1:])

    cls = _resolve_scene(args.scene)
    try:
        controls = normalize_controls(args.controls)
        position = parse_position(args.pos)
    except ValueError as exc:
        raise SystemExit("error: %s" % exc)
    preview = FramePreview(cls, fps=args.fps, out_dir=args.out,
                           use_bar=not args.no_bar, controls=controls,
                           position=position, verbose=not args.quiet)
    return preview.run(start_frame=args.at)


if __name__ == "__main__":
    raise SystemExit(main())
