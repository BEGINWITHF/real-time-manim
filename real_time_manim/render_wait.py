"""A tiny "compiling formula…" popup, so a cold LaTeX/Typst first render never
looks like a freeze.

Why this exists
---------------
``MathTex`` / ``Typst`` compile **synchronously inside ``__init__``** (see
``window/mathtex.py`` and ``typst_support.py``).  A live scene creates its
``MLWindow`` before it builds its mobjects, so on a cold tex cache the window is
already on screen and then the main thread blocks for a second or two on the
compiler -- with nothing drawn yet.  To a user that is indistinguishable from a
hang.

This module shows a small always-on-top window while that compile runs:

* only when a **visible** RTM window already exists (offline ``fast_record`` /
  ``FrameServer`` run hidden and stay silent),
* only when the compile is **slow** (a cache hit finishes in ~30 ms, so a
  short delay arms the popup and a fast compile cancels it before it appears),
* with a live "已等待 N.Ns" counter and a **percentage** bar, so it is visibly
  *doing something* rather than frozen,
* telling the user the truth: this is a first render, and a warm cache is fast.

The percentage is an adaptive estimate: LaTeX and dvisvgm do not expose an
internal completion counter, so the bar advances with elapsed time versus a
rolling estimate of how long a slow compile takes.  It approaches 99% if a
compile outlives that estimate and is set to 100% only when the compile really
returns.  The slow SVG/mobject build is moved to a worker thread (pure CPU) so
the main thread can keep painting the bar instead of freezing it.

The compile itself is untouched -- this only observes how long it takes.

Language
--------
The popup text follows the **user's UI language** -- the Windows display
language (``GetUserDefaultUILanguage``, then the system UI language, then the
locale name as fallbacks); ``LC_ALL``/``LC_MESSAGES``/``LANG``/``locale``
elsewhere -- for Chinese, English, Japanese and Korean; anything else falls back
to English.  ``RTM_LANG=zh|en|ja|ko`` overrides the detection.

Toggles
-------
``RTM_WAIT_POPUP=0``      disable the popup entirely.
``RTM_WAIT_POPUP_DELAY``  seconds before it appears (default ``0.35``).
``RTM_WAIT_ICON``         override the ``.ico`` used for the popup window.
``RTM_LANG``              force the popup language (``zh`` / ``en`` / ``ja`` / ``ko``).

Without a visible window (or on a platform without a native popup),
:func:`formula_compile_wait` is a no-op.  On macOS the popup is native Cocoa:
the compile blocks the main thread, so :func:`pump_compile_wait` runs a short
AppKit run-loop slice from the LaTeX subprocess waits, the Typst future waits,
and the worker that builds the SVG mobject, keeping the percentage bar and
elapsed counter moving.
"""
from __future__ import annotations

import os
import sys
import threading
import time

__all__ = ["formula_compile_wait", "popup_is_shown", "WaitPopup",
           "pump_compile_wait", "wait_future", "popup_armed",
           "run_pumping"]

_ENABLED = os.environ.get("RTM_WAIT_POPUP", "1") != "0"
try:
    _DELAY = max(0.0, float(os.environ.get("RTM_WAIT_POPUP_DELAY", "0.35")))
except ValueError:
    _DELAY = 0.35

#: Rolling estimate of a formula's total compile time, used to turn the
#: popup's progress bar into a percentage.  LaTeX/dvisvgm do not expose their
#: internal completion, so the fraction is elapsed/expected (never stalling:
#: a compile that outlives the estimate approaches 99% until it really ends).
_EXPECTED = 1.0
_EXPECTED_MIN = 0.40
_EXPECTED_MAX = 5.0

#: Win32 class name of the popup (never translated -- tests and FindWindowW
#: look it up by this exact string).
_CLASS_NAME = "RTMRenderWait"

#: Popup strings.  ``line2`` takes the elapsed seconds as ``{e}``.
_STRINGS = {
    "zh": {
        "title": "RTM · 正在编译公式",
        "line1": "正在编译 LaTeX / Typst 公式，请稍候…",
        "line2": "已等待 {e:.1f}s —— 不是卡住；有缓存（tex cache）后会快很多。",
    },
    "en": {
        "title": "RTM · Compiling formula",
        "line1": "Compiling the LaTeX / Typst formula, please wait…",
        "line2": "Waiting {e:.1f}s — not frozen; a warm tex cache makes this much faster.",
    },
    "ja": {
        "title": "RTM · 数式をコンパイル中",
        "line1": "LaTeX / Typst の数式をコンパイルしています。しばらくお待ちください…",
        "line2": "待機中 {e:.1f}s — フリーズではありません。キャッシュ（tex cache）があれば速くなります。",
    },
    "ko": {
        "title": "RTM · 수식 컴파일 중",
        "line1": "LaTeX / Typst 수식을 컴파일하는 중입니다. 잠시만 기다려 주세요…",
        "line2": "대기 중 {e:.1f}s — 멈춘 것이 아닙니다. tex 캐시가 있으면 훨씬 빨라집니다.",
    },
}

#: Primary Win32 language IDs -> our codes.
_WIN_LANGID = {0x04: "zh", 0x09: "en", 0x11: "ja", 0x12: "ko"}
_LANGS = ("zh", "en", "ja", "ko")


def _match_lang(text: str):
    """Pick the first supported code that ``text`` starts with (e.g. 'zh-CN')."""
    low = (text or "").strip().lower()
    for code in _LANGS:
        if low.startswith(code):
            return code
    return None


def _detect_language() -> str:
    """The popup language: system UI language, or ``RTM_LANG`` when set."""
    forced = _match_lang(os.environ.get("RTM_LANG", ""))
    if forced:
        return forced
    if sys.platform == "win32":
        # The current user's UI language first -- the Windows display language,
        # which is what an app should localise to -- then the OS/system UI
        # language (e.g. an English UI on a Chinese install still lands on en,
        # but a French UI on a Chinese install falls back to zh), then the
        # user/system locale name ("zh-CN") as a last Windows-side fallback.
        import ctypes
        k = ctypes.windll.kernel32
        for fn in ("GetUserDefaultUILanguage", "GetSystemDefaultUILanguage"):
            try:
                f = getattr(k, fn)
                f.restype = ctypes.c_ushort
                code = _WIN_LANGID.get(int(f()) & 0x3FF)
                if code:
                    return code
            except Exception:
                pass
        for fn in ("GetUserDefaultLocaleName", "GetSystemDefaultLocaleName"):
            try:
                f = getattr(k, fn)
                f.restype = ctypes.c_int
                f.argtypes = [ctypes.c_wchar_p, ctypes.c_int]
                buf = ctypes.create_unicode_buffer(85)
                if f(buf, 85):
                    code = _match_lang(buf.value)
                    if code:
                        return code
            except Exception:
                pass
    for var in ("LC_ALL", "LC_MESSAGES", "LANG"):
        code = _match_lang(os.environ.get(var, ""))
        if code:
            return code
    try:
        import locale
        code = _match_lang(locale.getlocale()[0] or "")
        if code:
            return code
    except Exception:
        pass
    return "en"


_LANG = _detect_language()
_S = _STRINGS.get(_LANG, _STRINGS["en"])


def _t(key: str) -> str:
    return _S.get(key, _STRINGS["en"].get(key, ""))

# Re-entrancy guard: MathTex's LaTeX path can nest inside a wrapper (MathTex ->
# Tex), and the Typst path builds MathTypst internally.  Only the outermost
# ``with`` may show a popup.
_local = threading.local()


def _depth() -> int:
    return getattr(_local, "depth", 0)


def _icon_path() -> str:
    override = os.environ.get("RTM_WAIT_ICON")
    here = os.path.dirname(os.path.abspath(__file__))
    for name in (override, "wait.ico", "logo.ico"):
        if not name:
            continue
        path = name if os.path.isabs(name) else os.path.join(here, name)
        if os.path.exists(path):
            return path
    return ""


def _visible_window():
    """The newest RTM window a human can see, or ``None``."""
    try:
        from real_time_manim.window import MLWindow
        reg = list(getattr(MLWindow, "_registry", ()))
    except Exception:
        return None
    for window in reversed(reg):
        if getattr(window, "hidden", False):
            continue
        if getattr(window, "dll", None) is not None:
            return window
    return None


# ---------------------------------------------------------------------------
# public context manager
# ---------------------------------------------------------------------------

class _CompileWait:
    def __init__(self, label: str = ""):
        self.label = label
        self._timer = None
        self._popup = None
        self._cancelled = False
        self._lock = threading.Lock()
        # macOS: armed for the outermost compile.  The native panel is created
        # only by pump() once the compile has actually exceeded _DELAY.
        self._mac_armed = None
        self._mac_dll = None
        self._mac_shown = False
        self._mac_pump = None
        self._mac_destroy = None
        self._mac_progress = None
        self._mac_shown_at = None

    def __enter__(self):
        _local.depth = _depth() + 1
        if _depth() == 1 and _ENABLED:
            window = _visible_window()
            if window is not None:
                if sys.platform == "win32":
                    self._timer = threading.Timer(_DELAY, self._spawn)
                    self._timer.daemon = True
                    self._timer.start()
                elif (sys.platform == "darwin"
                        and threading.current_thread() is threading.main_thread()):
                    # Never arm from a worker thread: AppKit is main-thread only.
                    # (A heavy formula's SVG build runs on a worker while this
                    # main thread pumps; nested wrappers there must stay quiet.)
                    self._mac_armed = time.monotonic()
                    self._mac_dll = window.dll
                    _local.wait = self
        return self

    def _spawn(self):
        # `__exit__` may already have run (the compile finished just as the
        # timer fired); the lock makes "create the popup" and "cancel" atomic so
        # a stray popup can never be left behind.
        with self._lock:
            if self._cancelled:
                return
            popup = WaitPopup(self.label)
            self._popup = popup
        try:
            popup.start()
        except Exception:
            with self._lock:
                if self._popup is popup:
                    self._popup = None

    # -- macOS ------------------------------------------------------------
    def _expectation(self):
        return max(_EXPECTED_MIN, min(_EXPECTED_MAX, _EXPECTED))

    def pump(self):
        """Show/advance the mac popup; called from the compile's wait loop."""
        if self._mac_armed is None:
            return
        if threading.current_thread() is not threading.main_thread():
            return                       # AppKit is main-thread only
        if not self._mac_shown:
            if time.monotonic() - self._mac_armed < _DELAY:
                return
            if not self._show_mac():
                self._mac_armed = None   # old dylib: compile silently
                return
        if self._mac_progress is not None and self._mac_shown_at is not None:
            elapsed = max(0.0, time.monotonic() - self._mac_shown_at)
            x = elapsed / self._expectation()
            # Elapsed-based, but never stalls: a compile that outlives the
            # estimate keeps inching towards 99% until it actually finishes.
            pct = 100.0 * x / (x + 0.7)
            if pct > 99.0:
                pct = 99.0
            try:
                self._mac_progress(pct)
            except Exception:
                self._mac_progress = None
        if self._mac_pump is not None:
            try:
                self._mac_pump(0.01)
            except Exception:
                self._mac_pump = None

    def _show_mac(self):
        dll = self._mac_dll
        if dll is None:
            return False
        try:
            arm = dll.Vulkan_WaitPopupArm
            show = dll.Vulkan_WaitPopupShow
            pump = dll.Vulkan_WaitPopupPump
            destroy = dll.Vulkan_WaitPopupDestroy
        except AttributeError:           # dylib predates the popup
            return False
        progress = getattr(dll, "Vulkan_WaitPopupSetProgress", None)
        import ctypes
        arm.restype = None
        arm.argtypes = [ctypes.c_char_p] * 4
        show.restype = None
        show.argtypes = []
        pump.restype = None
        pump.argtypes = [ctypes.c_double]
        destroy.restype = None
        destroy.argtypes = []
        if progress is not None:
            progress.restype = None
            progress.argtypes = [ctypes.c_double]

        snippet = self.label
        if len(snippet) > 70:
            snippet = snippet[:67] + "..."
        line2 = _t("line2").replace("{e:.1f}", "%0.1f").replace("{e}", "%0.1f")
        try:
            arm(_t("title").encode("utf-8"),
                _t("line1").encode("utf-8"),
                line2.encode("utf-8"),
                snippet.encode("utf-8"))
            show()
        except Exception:
            return False
        self._mac_pump = pump
        self._mac_progress = progress
        self._mac_destroy = destroy
        self._mac_shown_at = time.monotonic()
        self._mac_shown = True
        return True

    def __exit__(self, *exc):
        _local.depth = max(0, _depth() - 1)
        if getattr(_local, "wait", None) is self:
            _local.wait = None
        with self._lock:
            self._cancelled = True
            if self._timer is not None:
                self._timer.cancel()
                self._timer = None
            popup, self._popup = self._popup, None
        if popup is not None:
            popup.stop()
        main = threading.current_thread() is threading.main_thread()
        if self._mac_shown and self._mac_armed is not None and main:
            actual = time.monotonic() - self._mac_armed
            if 0.0 < actual < 60.0:
                global _EXPECTED
                _EXPECTED = 0.8 * _EXPECTED + 0.2 * actual
            # Show a completed bar for a moment instead of tearing it down at
            # 97%: the compile *did* finish, so 100% is the honest value.
            if self._mac_progress is not None and self._mac_pump is not None:
                try:
                    self._mac_progress(100.0)
                    self._mac_pump(0.04)
                except Exception:
                    pass
        if (self._mac_destroy is not None and main):
            try:
                self._mac_destroy()
            except Exception:
                pass
        self._mac_destroy = None
        self._mac_pump = None
        self._mac_progress = None
        self._mac_shown = False
        self._mac_shown_at = None
        self._mac_armed = None
        return False


def formula_compile_wait(label: str = "") -> _CompileWait:
    """Wrap a formula compile; show the popup only if it turns out to be slow."""
    return _CompileWait(str(label or ""))


def popup_armed() -> bool:
    """True while this (main) thread has an armed compile popup."""
    return getattr(_local, "wait", None) is not None


def run_pumping(fn, *args, **kwargs):
    """Run a heavy, CPU-only step on a worker while the mac popup animates.

    ``SVGMobject``'s build (SVG parse + thousands of path mobjects) is the long
    part of a cold formula render and does not touch AppKit or Vulkan.  Off the
    main thread it can run while ``pump_compile_wait()`` keeps the popup's
    percentage and elapsed counter moving; without this the panel would freeze
    for the whole build.  Other platforms/threads call ``fn`` inline.
    """
    wait = getattr(_local, "wait", None)
    if (sys.platform != "darwin" or wait is None
            or threading.current_thread() is not threading.main_thread()):
        return fn(*args, **kwargs)
    box = {}

    def target():
        try:
            box["value"] = fn(*args, **kwargs)
        except BaseException as exc:          # re-raised on the main thread
            box["error"] = exc

    thread = threading.Thread(target=target, name="rtm-svg-build", daemon=True)
    thread.start()
    while thread.is_alive():
        thread.join(0.02)
        wait.pump()
    if "error" in box:
        raise box["error"]
    return box.get("value")


def pump_compile_wait() -> None:
    """Keep a slow compile's popup alive (macOS); a no-op elsewhere.

    Call this from loops that block the main thread while a formula compiles
    (the LaTeX subprocess waits and the Typst future waits).  It only does
    anything on the thread that armed the popup.
    """
    wait = getattr(_local, "wait", None)
    if wait is not None:
        wait.pump()


def wait_future(future):
    """``future.result()`` while pumping the macOS compile popup."""
    if sys.platform != "darwin":
        return future.result()
    from concurrent.futures import TimeoutError as FutureTimeout
    while True:
        try:
            return future.result(timeout=0.02)
        except FutureTimeout:
            pump_compile_wait()


def popup_is_shown() -> bool:
    """True while the popup window is actually on screen (for tests)."""
    if sys.platform == "darwin":
        wait = getattr(_local, "wait", None)
        return bool(wait is not None and getattr(wait, "_mac_shown", False))
    return any(p.alive for p in list(_POPUPS.values()))


# ---------------------------------------------------------------------------
# Win32 implementation
# ---------------------------------------------------------------------------

_POPUPS: dict = {}

if sys.platform == "win32":  # pragma: no cover - needs a Windows desktop
    import ctypes
    import ctypes.wintypes as wt

    from real_time_manim.window import win32

    _u = win32.user32
    _k = win32.kernel32
    _g = win32.gdi32
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

    class _INITCOMMONCONTROLSEX(ctypes.Structure):
        _fields_ = [("dwSize", wt.DWORD), ("dwICC", wt.DWORD)]

    for _fn, _res, _args in (
            ("CreateWindowExW", wt.HWND,
             [ctypes.c_uint, wt.LPCWSTR, wt.LPCWSTR, ctypes.c_uint,
              ctypes.c_int, ctypes.c_int, ctypes.c_int, ctypes.c_int,
              wt.HWND, wt.HMENU, wt.HINSTANCE, ctypes.c_void_p]),
            ("DefWindowProcW", _LRESULT, [wt.HWND, ctypes.c_uint, _WPARAM, _LPARAM]),
            ("DestroyWindow", wt.BOOL, [wt.HWND]),
            ("SetWindowTextW", wt.BOOL, [wt.HWND, wt.LPCWSTR]),
            ("SendMessageW", _LRESULT, [wt.HWND, ctypes.c_uint, _WPARAM, _LPARAM]),
            ("PostMessageW", wt.BOOL, [wt.HWND, ctypes.c_uint, _WPARAM, _LPARAM]),
            ("ShowWindow", wt.BOOL, [wt.HWND, ctypes.c_int]),
            ("UpdateWindow", wt.BOOL, [wt.HWND]),
            ("RegisterClassExW", wt.ATOM, [ctypes.POINTER(_WNDCLASSEXW)]),
            ("LoadCursorW", wt.HANDLE, [wt.HINSTANCE, wt.LPCWSTR]),
            ("LoadImageW", wt.HANDLE,
             [wt.HINSTANCE, wt.LPCWSTR, ctypes.c_uint, ctypes.c_int,
              ctypes.c_int, ctypes.c_uint]),
            ("SetTimer", ctypes.c_size_t,
             [wt.HWND, ctypes.c_size_t, ctypes.c_uint, ctypes.c_void_p]),
            ("KillTimer", wt.BOOL, [wt.HWND, ctypes.c_size_t]),
            ("GetMessageW", wt.BOOL, [ctypes.POINTER(_MSG), wt.HWND,
                                      ctypes.c_uint, ctypes.c_uint]),
            ("TranslateMessage", wt.BOOL, [ctypes.POINTER(_MSG)]),
            ("DispatchMessageW", _LRESULT, [ctypes.POINTER(_MSG)]),
            ("PostQuitMessage", None, [ctypes.c_int]),
            ("AdjustWindowRectEx", wt.BOOL,
             [ctypes.POINTER(wt.RECT), ctypes.c_uint, wt.BOOL, ctypes.c_uint]),
            ("GetDpiForSystem", ctypes.c_uint, []),
            ("GetSystemMetrics", ctypes.c_int, [ctypes.c_int]),
            ("SetWindowPos", wt.BOOL,
             [wt.HWND, wt.HWND, ctypes.c_int, ctypes.c_int, ctypes.c_int,
              ctypes.c_int, ctypes.c_uint])):
        _f = getattr(_u, _fn, None)
        if _f is not None:
            _f.restype = _res
            _f.argtypes = _args

    for _fn, _res, _args in (
            ("CreateSolidBrush", wt.HBRUSH, [wt.COLORREF]),
            ("SetTextColor", wt.COLORREF, [wt.HDC, wt.COLORREF]),
            ("SetBkColor", wt.COLORREF, [wt.HDC, wt.COLORREF])):
        _f = getattr(_g, _fn, None)
        if _f is not None:
            _f.restype = _res
            _f.argtypes = _args

    #: COLORREF is 0x00BBGGRR.  A light client with dark text, forced rather
    #: than inherited, so the popup is readable whatever the system theme is.
    _BG = 0x00F2F2F2
    _FG = 0x00202020
    _bg_brush = None

    _WS_POPUP, _WS_CAPTION, _WS_SYSMENU = 0x80000000, 0x00C00000, 0x00080000
    _WS_CHILD, _WS_VISIBLE = 0x40000000, 0x10000000
    _WS_EX_TOOLWINDOW, _WS_EX_TOPMOST, _WS_EX_NOACTIVATE = 0x80, 0x08, 0x08000000
    _SS_LEFT = 0x00000000
    _PBS_MARQUEE = 0x08
    _PBM_SETMARQUEE = 0x040A
    _WM_SETICON, _ICON_SMALL, _ICON_BIG = 0x0080, 0, 1
    _WM_TIMER, _WM_CLOSE, _WM_DESTROY, _WM_SETFONT, _WM_CTLCOLORSTATIC = (
        0x0113, 0x0010, 0x0002, 0x0030, 0x0138)
    _DEFAULT_GUI_FONT = 17
    _ICC_PROGRESS_CLASS = 0x20
    _SW_SHOW = 5
    _LR_LOADFROMFILE = 0x10
    _IMAGE_ICON = 1
    _HWND_TOPMOST = -1
    _SWP_NOSIZE, _SWP_NOMOVE, _SWP_NOACTIVATE = 0x0001, 0x0002, 0x0010
    _STATIC_CLASS, _PROGRESS_CLASS = "STATIC", "msctls_progress32"

    _CLASS_REGISTERED = False
    _CLASS_LOCK = threading.Lock()

    def _wnd_proc(hwnd, msg, wparam, lparam):
        popup = _POPUPS.get(hwnd)
        if popup is not None:
            reply = popup._on_message(hwnd, msg, wparam, lparam)
            if reply is not None:
                return reply
        return _u.DefWindowProcW(hwnd, msg, wparam, lparam)

    _wnd_proc_ptr = _WNDPROC(_wnd_proc)

    def _register_class():
        global _CLASS_REGISTERED, _bg_brush
        with _CLASS_LOCK:
            if _CLASS_REGISTERED:
                return
            if _bg_brush is None:
                try:
                    _bg_brush = _g.CreateSolidBrush(_BG)
                except Exception:
                    _bg_brush = None
            if win32.comctl32 is not None:
                icc = _INITCOMMONCONTROLSEX(
                    ctypes.sizeof(_INITCOMMONCONTROLSEX), _ICC_PROGRESS_CLASS)
                try:
                    win32.comctl32.InitCommonControlsEx(ctypes.byref(icc))
                except Exception:
                    pass
            hinst = _k.GetModuleHandleW(None)
            wc = _WNDCLASSEXW()
            wc.cbSize = ctypes.sizeof(_WNDCLASSEXW)
            wc.lpfnWndProc = _wnd_proc_ptr
            wc.hInstance = hinst
            wc.hCursor = _u.LoadCursorW(None, wt.LPCWSTR(32512))  # IDC_ARROW
            wc.hbrBackground = _bg_brush or _g.GetStockObject(1)  # light client
            wc.lpszClassName = _CLASS_NAME
            icon = _icon_path()
            if getattr(_u, "LoadImageW", None) is not None and icon:
                try:
                    h = _u.LoadImageW(None, wt.LPCWSTR(icon), _IMAGE_ICON, 0, 0,
                                      _LR_LOADFROMFILE)
                    wc.hIcon = h
                    wc.hIconSm = h
                except Exception:
                    pass
            _u.RegisterClassExW(ctypes.byref(wc))
            _CLASS_REGISTERED = True

    def _dpi_scale():
        try:
            dpi = _u.GetDpiForSystem()
            return (dpi or 96) / 96.0
        except Exception:
            return 1.0

    class WaitPopup:
        """The popup itself: created, driven and destroyed on its own thread."""

        def __init__(self, label: str = ""):
            self.label = str(label)
            self._hwnd = None
            self._text = None
            self._bar = None
            self._icon = None
            self._start = time.time()
            self._ready = threading.Event()
            self._thread = threading.Thread(target=self._run, name="rtm-render-wait",
                                            daemon=True)
            self.alive = False

        # -- lifecycle ------------------------------------------------------
        def start(self, timeout=2.0):
            self._thread.start()
            self._ready.wait(timeout)
            return self._hwnd is not None

        def stop(self):
            self._ready.wait(1.0)
            hwnd = self._hwnd
            if hwnd:
                _u.PostMessageW(hwnd, _WM_CLOSE, 0, 0)
            self._thread.join(timeout=2.0)

        # -- worker ---------------------------------------------------------
        def _run(self):
            try:
                self._create()
            except Exception:
                self._hwnd = None
            finally:
                self._ready.set()
            if not self._hwnd:
                return
            _POPUPS[self._hwnd] = self
            self.alive = True
            _u.ShowWindow(self._hwnd, _SW_SHOW)
            _u.UpdateWindow(self._hwnd)
            _u.SetTimer(self._hwnd, 1, 100, None)     # drive the "已等待" counter
            msg = _MSG()
            while _u.GetMessageW(ctypes.byref(msg), None, 0, 0) > 0:
                _u.TranslateMessage(ctypes.byref(msg))
                _u.DispatchMessageW(ctypes.byref(msg))
            _POPUPS.pop(self._hwnd, None)
            self.alive = False

        def _create(self):
            _register_class()
            hinst = _k.GetModuleHandleW(None)
            scale = _dpi_scale()
            style = _WS_POPUP | _WS_CAPTION | _WS_SYSMENU
            ex_style = _WS_EX_TOOLWINDOW | _WS_EX_TOPMOST | _WS_EX_NOACTIVATE
            client_w, client_h = int(430 * scale), int(118 * scale)
            rect = wt.RECT(0, 0, client_w, client_h)
            _u.AdjustWindowRectEx(ctypes.byref(rect), style, False, ex_style)
            outer_w = int(rect.right - rect.left)
            outer_h = int(rect.bottom - rect.top)
            left, top = self._place(outer_w, outer_h)

            self._hwnd = _u.CreateWindowExW(
                ex_style, _CLASS_NAME, _t("title"),
                style, left, top, outer_w, outer_h,
                None, None, hinst, None)
            if not self._hwnd:
                return

            icon = _icon_path()
            if icon:
                h = _u.LoadImageW(None, wt.LPCWSTR(icon), _IMAGE_ICON, 0, 0,
                                  _LR_LOADFROMFILE)
                if h:
                    self._icon = h
                    _u.SendMessageW(self._hwnd, _WM_SETICON, _ICON_BIG, h)
                    _u.SendMessageW(self._hwnd, _WM_SETICON, _ICON_SMALL, h)

            pad = int(12 * scale)
            self._text = _u.CreateWindowExW(
                0, _STATIC_CLASS, self._body(0.0),
                _WS_CHILD | _WS_VISIBLE | _SS_LEFT,
                pad, pad, client_w - 2 * pad, int(62 * scale),
                self._hwnd, None, hinst, None)
            self._bar = _u.CreateWindowExW(
                0, _PROGRESS_CLASS, "",
                _WS_CHILD | _WS_VISIBLE | _PBS_MARQUEE,
                pad, client_h - int(30 * scale), client_w - 2 * pad, int(16 * scale),
                self._hwnd, None, hinst, None)
            font = _g.GetStockObject(_DEFAULT_GUI_FONT)
            for ctl in (self._text, self._bar):
                if ctl:
                    _u.SendMessageW(ctl, _WM_SETFONT, font, 1)
            if self._bar:
                _u.SendMessageW(self._bar, _PBM_SETMARQUEE, 1, 30)

        def _place(self, w, h):
            """Dock near the video window (top-right), else centre the screen."""
            try:
                vid = win32.find_video_hwnd()
                if vid:
                    r = win32.window_rect(vid)
                    if r:
                        left = min(max(r[2] - w - 24, 0), _u.GetSystemMetrics(0) - w)
                        top = max(r[1] + 24, 0)
                        return int(left), int(top)
            except Exception:
                pass
            sw, sh = _u.GetSystemMetrics(0), _u.GetSystemMetrics(1)
            return int((sw - w) / 2), int((sh - h) / 2)

        def _body(self, elapsed):
            lines = [_t("line1"), _t("line2").format(e=elapsed)]
            if self.label:
                snippet = self.label if len(self.label) <= 70 else self.label[:67] + "…"
                lines.append(snippet)
            return "\n".join(lines)

        # -- message handling ----------------------------------------------
        def _on_message(self, hwnd, msg, wparam, lparam):
            if msg == _WM_TIMER:
                if self._text:
                    elapsed = time.time() - self._start
                    _u.SetWindowTextW(self._text, self._body(elapsed))
                return 0
            if msg == _WM_CLOSE:
                if self._bar:
                    _u.KillTimer(hwnd, 1)
                _u.DestroyWindow(hwnd)
                return 0
            if msg == _WM_DESTROY:
                _u.PostQuitMessage(0)
                return 0
            if msg == _WM_CTLCOLORSTATIC:
                hdc = ctypes.c_void_p(wparam)
                _g.SetTextColor(hdc, _FG)
                _g.SetBkColor(hdc, _BG)
                return _bg_brush if _bg_brush else 0
            return None

else:  # pragma: no cover - non-Windows stub
    class WaitPopup:  # type: ignore[no-redef]
        alive = False

        def __init__(self, label: str = ""):
            self.label = label

        def start(self, timeout: float = 2.0):
            return False

        def stop(self):
            return None
