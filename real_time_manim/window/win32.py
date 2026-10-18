"""The few Win32 calls RTM needs from Python.

Two jobs only:

* find our own Vulkan window -- the DLL creates it with the fixed class
  ``ManimVulkanClass`` / title ``Real Time Manim`` and never exports the handle
  (``window/recording.py`` has always relied on the title), and
* read its screen rectangle, so a widget can be docked underneath it.

Importing this module is safe everywhere: off Windows ``user32`` stays ``None``
and every helper returns ``None``.
"""
from __future__ import annotations

import os
import sys

VIDEO_TITLE = "Real Time Manim"
VIDEO_CLASS = "ManimVulkanClass"

user32 = kernel32 = gdi32 = None

if sys.platform == "win32":  # pragma: no cover - platform dependent
    import ctypes
    import ctypes.wintypes as wt

    user32 = ctypes.windll.user32
    kernel32 = ctypes.windll.kernel32
    gdi32 = ctypes.windll.gdi32
    user32.FindWindowW.restype = wt.HWND
    user32.FindWindowW.argtypes = [wt.LPCWSTR, wt.LPCWSTR]
    user32.IsWindow.restype = wt.BOOL
    user32.IsWindow.argtypes = [wt.HWND]
    user32.GetWindowRect.restype = wt.BOOL
    user32.GetWindowRect.argtypes = [wt.HWND, ctypes.POINTER(wt.RECT)]
    user32.GetClientRect.restype = wt.BOOL
    user32.GetClientRect.argtypes = [wt.HWND, ctypes.POINTER(wt.RECT)]
    kernel32.GetModuleHandleW.restype = wt.HMODULE
    kernel32.GetModuleHandleW.argtypes = [wt.LPCWSTR]
    gdi32.GetStockObject.restype = wt.HGDIOBJ
    gdi32.GetStockObject.argtypes = [ctypes.c_int]


def _top_level_windows():  # pragma: no cover - platform dependent
    import ctypes
    import ctypes.wintypes as wt

    found = []
    EnumProc = ctypes.WINFUNCTYPE(wt.BOOL, wt.HWND, wt.LPARAM)

    def _cb(hwnd, _lparam):
        found.append(hwnd)
        return True

    user32.EnumWindows(EnumProc(_cb), 0)
    return found


def _class_of(hwnd):  # pragma: no cover - platform dependent
    import ctypes

    buf = ctypes.create_unicode_buffer(256)
    user32.GetClassNameW(hwnd, buf, 256)
    return buf.value


def _pid_of(hwnd):  # pragma: no cover - platform dependent
    import ctypes
    import ctypes.wintypes as wt

    pid = wt.DWORD(0)
    user32.GetWindowThreadProcessId(hwnd, ctypes.byref(pid))
    return int(pid.value)


def find_video_hwnd():
    """The live Vulkan window handle, or ``None``.

    Matches class+title first, then falls back to "any top-level window of this
    process with our window class" -- the title is ours, but a shell or a
    localization hook could rename it.
    """
    if user32 is None:
        return None
    hwnd = user32.FindWindowW(VIDEO_CLASS, VIDEO_TITLE)
    if hwnd and user32.IsWindow(hwnd):
        return hwnd
    me = os.getpid()
    for cand in _top_level_windows():
        if _class_of(cand) == VIDEO_CLASS and _pid_of(cand) == me:
            return cand
    return None


def window_rect(hwnd):
    """``(left, top, right, bottom)`` of the whole window, or ``None``."""
    if user32 is None or not hwnd:
        return None
    import ctypes
    import ctypes.wintypes as wt

    rc = wt.RECT()
    if not user32.GetWindowRect(hwnd, ctypes.byref(rc)):
        return None
    return int(rc.left), int(rc.top), int(rc.right), int(rc.bottom)


def client_rect_on_screen(hwnd):
    """``(x, y, w, h)`` of the client area in screen pixels, or ``None``."""
    if user32 is None or not hwnd:
        return None
    import ctypes
    import ctypes.wintypes as wt

    rc = wt.RECT()
    if not user32.GetClientRect(hwnd, ctypes.byref(rc)):
        return None
    pt = wt.POINT(0, 0)
    user32.ClientToScreen(hwnd, ctypes.byref(pt))
    return int(pt.x), int(pt.y), int(rc.right - rc.left), int(rc.bottom - rc.top)
