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

user32 = kernel32 = gdi32 = comctl32 = None

if sys.platform == "win32":  # pragma: no cover - platform dependent
    import ctypes
    import ctypes.wintypes as wt

    user32 = ctypes.windll.user32
    kernel32 = ctypes.windll.kernel32
    gdi32 = ctypes.windll.gdi32
    comctl32 = ctypes.windll.comctl32
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
    comctl32.InitCommonControlsEx.restype = wt.BOOL
    comctl32.InitCommonControlsEx.argtypes = [ctypes.c_void_p]


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
    """The live Vulkan window handle of *this process*, or ``None``.

    Our own process first (class + pid), so several RTM windows -- e.g. two
    frame previews side by side -- never cross wires; the title lookup is only a
    last-resort fallback for a window we cannot see through EnumWindows.
    """
    if user32 is None:
        return None
    me = os.getpid()
    for cand in _top_level_windows():
        if _class_of(cand) == VIDEO_CLASS and _pid_of(cand) == me:
            return cand
    hwnd = user32.FindWindowW(VIDEO_CLASS, VIDEO_TITLE)
    if hwnd and user32.IsWindow(hwnd):
        return hwnd
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


def force_foreground(hwnd):
    """Bring ``hwnd`` to the front even when another app owns the foreground.

    Plain ``SetForegroundWindow`` is *denied* unless the caller is already the
    foreground process, so a preview opened from a terminal behind a maximized
    editor silently appears underneath it.  Flipping the window topmost,
    activating it, then dropping the topmost bit is the standard recipe that
    Windows does allow.
    """
    if user32 is None or not hwnd:
        return False
    import ctypes
    import ctypes.wintypes as wt

    user32.SetWindowPos.restype = wt.BOOL
    user32.SetWindowPos.argtypes = [wt.HWND, wt.HWND, ctypes.c_int,
                                    ctypes.c_int, ctypes.c_int, ctypes.c_int,
                                    ctypes.c_uint]
    user32.BringWindowToTop.restype = wt.BOOL
    user32.BringWindowToTop.argtypes = [wt.HWND]
    SWP_NOSIZE, SWP_NOMOVE, SWP_SHOWWINDOW = 0x0001, 0x0002, 0x0040
    flags = SWP_NOSIZE | SWP_NOMOVE | SWP_SHOWWINDOW
    user32.SetWindowPos(hwnd, ctypes.c_void_p(-1), 0, 0, 0, 0, flags)  # TOPMOST
    user32.SetForegroundWindow(hwnd)
    user32.BringWindowToTop(hwnd)
    user32.SetWindowPos(hwnd, ctypes.c_void_p(-2), 0, 0, 0, 0, flags)  # NOTOPMOST
    return True
