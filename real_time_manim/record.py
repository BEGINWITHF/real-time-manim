"""One-call recording helpers for real-time-manim.

Running a Scene that opens an :class:`~real_time_manim.vulkan_bind.MLWindow`
normally requires you to start/stop the recorder yourself.  These helpers wrap
that plumbing so a caller just says::

    from real_time_manim.record import fast_record_scene, record_scene

    fast_record_scene(MyScene, "preview.mp4", fps=60, hidden=True)
    record_scene(MyScene, "final.mp4", fps=60)

Both accept a Scene *subclass*, a Scene *instance*, or any no-arg callable; any
:class:`MLWindow` the scene opens is auto-recorded and its encode is flushed on
close.  The two map onto the engine's two built-in recorders:

* ``fast_record_scene`` — **offline** record via Vulkan framebuffer readback
  streamed straight to ffmpeg (optionally with a hidden window).  This is the
  path used by the batch ``run_all.py`` renderer; fastest, no visible window.
* ``record_scene`` — **real-time** record against a live window using a
  background frame-capture thread (``start_record``/``stop_record``), the path
  used by the interactive ``run.py``.

Each function takes rich keyword arguments so the capture/encode step is
customisable (fps, window visibility, count-only probe, BMP segment mode,
overwrite policy, verbosity).  A scene that opens several windows yields one
file per window (``out.mp4``, ``out_part2.mp4``, ...).  Every helper returns a
small dict describing the files it produced so scripts can act on the result.
"""
from __future__ import annotations

import os
from typing import Any, Callable, Dict, List, Optional, Union


def _default_out_path() -> str:
    """Where output lands when the caller passes no ``out_path``.

    Prefers the user's ``~/Downloads`` folder (created if missing), falling back
    to the current directory if that cannot be determined.
    """
    d = os.path.join(os.path.expanduser("~"), "Downloads")
    try:
        os.makedirs(d, exist_ok=True)
        return os.path.join(d, "output.mp4")
    except OSError:
        return os.path.join(os.getcwd(), "output.mp4")


# --------------------------------------------------------------------------
# scene normalisation
# --------------------------------------------------------------------------

def _as_runner(scene: Union[type, Any, Callable[[], None]]) -> Callable[[], None]:
    """Turn a Scene subclass / Scene instance / callable into a no-arg runner.

    Scenes in real-time-manim drive themselves via ``construct()`` and close
    their own :class:`MLWindow`, so the runner is just: create (if needed) and
    call ``construct()``.
    """
    if isinstance(scene, type):
        if not hasattr(scene, "construct"):
            raise TypeError(
                "scene looks like a class but has no construct(); pass a Scene "
                "subclass, a Scene instance, or a no-arg callable."
            )
        return lambda: scene().construct()
    if hasattr(scene, "construct"):
        return scene.construct
    if callable(scene):
        return scene
    raise TypeError(
        "scene must be a Scene subclass, a Scene instance, or a no-arg callable."
    )


def _window_out(out_path: str, index: int) -> str:
    """Per-window output path; first window uses ``out_path``, later ones get
    a ``_partN`` suffix so a scene opening several windows never clobbers."""
    if index == 0:
        return out_path
    root, ext = os.path.splitext(out_path)
    return f"{root}_part{index + 1}{ext}"


def _guard_overwrite(out_path: str, overwrite: bool, count_only: bool = False) -> None:
    """Raise if the target exists and overwrite is False (count-only probes
    write no file, so they are exempt)."""
    if not overwrite and not count_only and os.path.exists(out_path):
        raise FileExistsError(
            f"target already exists: {out_path} (pass overwrite=True to replace it)"
        )


def _produced_files(out_path: str) -> List[str]:
    """Existing files matching the out_path / its ``_partN`` siblings."""
    if os.path.exists(out_path):
        return [out_path]
    root, ext = os.path.splitext(out_path)
    hits = sorted(
        p for p in os.listdir(os.path.dirname(out_path) or ".") if p.startswith(os.path.basename(root))
    ) if os.path.isdir(os.path.dirname(out_path) or ".") else []
    return [os.path.join(os.path.dirname(out_path) or ".", p) for p in hits]


# --------------------------------------------------------------------------
# shared patcher
# --------------------------------------------------------------------------

class _AutoRecord:
    """Patch MLWindow so every window a scene opens is auto-recorded.

    Wraps ``MLWindow.__init__`` / ``MLWindow.close`` for the duration of a run.
    ``on_init(window, out_path)`` is called right after the real window is built
    (so the recorder can attach before any frame is played); ``on_close(window)``
    is called before the real ``close`` (which shuts Vulkan down), giving the
    recorder a chance to flush/encode.  Used as a context manager so the patch
    is always restored, even if the scene raises.
    """

    def __init__(self, out_path: str,
                 on_init: Callable[[Any, str], None],
                 on_close: Callable[[Any], None],
                 verbose: bool = True):
        import real_time_manim.vulkan_bind as vb
        self._vb = vb
        self._out_path = out_path
        self._on_init = on_init
        self._on_close = on_close
        self.verbose = verbose
        self._orig_init = vb.MLWindow.__init__
        self._orig_close = vb.MLWindow.close
        self._n_windows = 0
        self.windows: List[str] = []  # output path assigned to each opened window

    def __enter__(self) -> "_AutoRecord":
        vb = self._vb
        st = self

        def patched_init(self_, *a, **k):
            st._orig_init(self_, *a, **k)
            out = _window_out(st._out_path, st._n_windows)
            st._n_windows += 1
            st.windows.append(out)
            st._on_init(self_, out)
            if st.verbose:
                print(f"[record] window #{st._n_windows} -> {out}")

        def patched_close(self_):
            st._on_close(self_)
            st._orig_close(self_)

        vb.MLWindow.__init__ = patched_init
        vb.MLWindow.close = patched_close
        return self

    def __exit__(self, exc_type, exc, tb) -> bool:
        self._vb.MLWindow.__init__ = self._orig_init
        self._vb.MLWindow.close = self._orig_close
        return False  # never swallow exceptions


def _run(scene, out_path: str, on_init, on_close,
         verbose: bool, overwrite: bool, count_only: bool,
         cleanup: bool = True, hidden: Optional[bool] = None) -> Dict[str, Any]:
    runner = _as_runner(scene)
    out_path = os.path.abspath(out_path)
    os.makedirs(os.path.dirname(out_path) or ".", exist_ok=True)
    _guard_overwrite(out_path, overwrite, count_only)
    rec = _AutoRecord(out_path, on_init, on_close, verbose=verbose)
    # ``hidden`` decides whether the scene's windows are *created* hidden (never
    # shown, so nothing pops onto the desktop) -- not merely hidden afterwards.
    from real_time_manim.vulkan_bind import MLWindow
    prev_hidden = MLWindow._hidden_default
    if hidden is not None:
        MLWindow._hidden_default = bool(hidden)
    try:
        with rec:
            runner()
    finally:
        MLWindow._hidden_default = prev_hidden
    # Rendering leaves transient manim media/Tex output behind; clear it for the
    # caller so they never have to remember to.  Opt out via cleanup=False.
    if cleanup:
        from real_time_manim.util import clear_media
        clear_media(verbose=verbose)
    files = rec.windows if rec.windows else _produced_files(out_path)
    return {
        "out_path": out_path,
        "windows": rec.windows,
        "files": [f for f in files if os.path.exists(f)],
    }


# --------------------------------------------------------------------------
# public API
# --------------------------------------------------------------------------

def record_scene(scene: Union[type, Any, Callable[[], None]],
                 out_path: Optional[str] = None,
                 *,
                 fps: int = 60,
                 overwrite: bool = True,
                 cleanup: bool = True,
                 verbose: bool = True) -> Dict[str, Any]:
    """Record a scene to video in **real time** against a visible window.

    This maps onto ``MLWindow.start_record`` / ``stop_record`` (the interactive
    ``run.py`` path): a background thread snapshots the live window at ``fps``
    and the frames are encoded on close.  The window itself must be shown, so
    the user sees the animation as it is captured.

    Parameters
    ----------
    scene:
        Scene subclass, Scene instance, or no-arg callable to run.
    out_path:
        Destination ``.mp4``.  Defaults to ``~/Downloads/output.mp4`` when
        omitted (a scene opening several windows appends ``_partN``).
    fps:
        Capture frame rate passed to ``start_record``.
    overwrite:
        When False, refuse to overwrite an existing ``out_path``.
    cleanup:
        Remove the transient manim ``media`` folder after recording so the
        caller does not have to (default True).  Set False to keep it.
    verbose:
        Print per-window progress lines.

    Returns
    -------
    dict with ``out_path``, ``windows`` (paths handed to each recorder) and
    ``files`` (those actually present on disk after the run).
    """
    def on_init(win: Any, out: str) -> None:
        win.start_record(out, fps=fps)

    def on_close(win: Any) -> None:
        win.stop_record()

    return _run(scene, out_path if out_path is not None else _default_out_path(),
                on_init, on_close, verbose, overwrite, count_only=False,
                cleanup=cleanup)


def fast_record_scene(scene: Union[type, Any, Callable[[], None]],
                      out_path: Optional[str] = None,
                      *,
                      fps: int = 60,
                      hidden: bool = True,
                      count_only: bool = False,
                      segment: Optional[tuple] = None,
                      overwrite: bool = True,
                      cleanup: bool = True,
                      verbose: bool = True) -> Dict[str, Any]:
    """Record a scene **offline** via fast framebuffer readback.

    Maps onto ``MLWindow.enable_fast_record`` / ``_finish_fast_record`` (the
    batch ``run_all.py`` path): each frame is read straight from the Vulkan
    buffer and streamed to ffmpeg, so no visible window is required and capture
    is the engine's fastest route.

    Parameters
    ----------
    scene:
        Scene subclass, Scene instance, or no-arg callable to run.
    out_path:
        Destination ``.mp4`` (pipe mode) or directory (``segment`` BMP mode).
        Defaults to ``~/Downloads/output.mp4`` when omitted (pipe mode).
    fps:
        Output frame rate passed to ``enable_fast_record``.
    hidden:
        Build the window hidden and never show it (default True), so an offline
        capture never pops a window onto the desktop.  Pass False to watch.
    count_only:
        Probe mode — count frames without capturing or GPU-rendering.
    segment:
        ``(start_frame, end_frame)`` to capture a frame *range* into a BMP
        directory instead of one MP4.  When set, ``out_path`` is a directory.
    overwrite:
        When False, refuse to overwrite an existing target (ignored when
        ``count_only`` since that writes nothing).
    cleanup:
        Remove the transient manim ``media`` folder after recording so the
        caller does not have to (default True).  Set False to keep it.
    verbose:
        Print per-window progress lines.

    Returns
    -------
    dict with ``out_path``, ``windows`` and ``files`` (see :func:`record_scene`).
    """
    def on_init(win: Any, out: str) -> None:
        win.enable_fast_record(out, fps=fps, hidden=hidden,
                               segment=segment, count_only=count_only)

    def on_close(win: Any) -> None:
        win._finish_fast_record()

    return _run(scene, out_path if out_path is not None else _default_out_path(),
                on_init, on_close, verbose, overwrite, count_only=count_only,
                cleanup=cleanup, hidden=hidden)
