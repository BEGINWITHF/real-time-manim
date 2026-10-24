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
  path used by a batch renderer; fastest, no visible window.
* ``record_scene`` — **real-time** record against a live window
  (``start_record``/``stop_record``): each frame the play loop presents is
  captured on the render thread and piped to ffmpeg, so the file has exactly
  as many frames as the scene draws.  This is the path used by interactive
  playback.

Each function takes rich keyword arguments so the capture/encode step is
customisable (fps, window visibility, count-only probe, BMP segment mode,
overwrite policy, verbosity).  A scene that opens several windows yields one
file per window (``out.mp4``, ``out_part2.mp4``, ...).  Every helper returns a
small dict describing the files it produced so scripts can act on the result.
"""
from __future__ import annotations

import json
import os
import shutil
import subprocess
import sys
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

def scene_lifecycle(scene) -> None:
    """Run a scene the way Manim does: ``setup()``, ``construct()``, ``tear_down()``.

    Manim's own ``Scene.render()`` calls ``setup()`` before ``construct()`` and
    ``tear_down()`` at the end; RTM used to call ``construct()`` alone, so
    everything a scene prepares in ``setup()`` was missing --
    ``LinearTransformationScene`` (``moving_vectors``), ``ZoomedScene``
    (``zoomed_display``), ``MovingCameraScene`` (``camera.frame``) and any user
    ``setup()`` hook -- and *nothing* ever ran the ``tear_down()`` finish hook
    (wiki 01-场景与相机/场景/01-Scene基础: "全仓库没有任何地方调
    ``tear_down()``").

    ``tear_down()`` now runs exactly once per scene, in a ``finally`` so a
    scene that raises inside ``construct()`` still gets its finish hook (the
    exception keeps propagating -- RTM only guarantees the hook runs).  Only
    the user hook is called: ``Scene.tear_down`` is a no-op in manim 0.21 and
    the file-writer teardown lives elsewhere (``renderer.scene_finished`` /
    ``file_writer``), which RTM deliberately does not drive -- calling it here
    would double-close encode jobs RTM never opened.
    """
    # Phase 6: capture Scene.add_sound so the recorder can mux a real track
    from real_time_manim import audio_track
    audio_track.install_add_sound_hook(scene)
    scene.setup()
    try:
        scene.construct()
    finally:
        # Duck-typed scenes (any object with construct()) may lack the hook.
        tear_down = getattr(scene, "tear_down", None)
        if callable(tear_down):
            tear_down()


def _as_runner(scene: Union[type, Any, Callable[[], None]]) -> Callable[[], None]:
    """Turn a Scene subclass / Scene instance / callable into a no-arg runner.

    Scenes in real-time-manim drive themselves via ``construct()`` and close
    their own :class:`MLWindow`, so the runner is just: create (if needed) and
    run the scene's lifecycle.
    """
    if isinstance(scene, type):
        if not hasattr(scene, "construct"):
            raise TypeError(
                "scene looks like a class but has no construct(); pass a Scene "
                "subclass, a Scene instance, or a no-arg callable."
            )
        return lambda: scene_lifecycle(scene())
    if hasattr(scene, "construct"):
        return lambda: scene_lifecycle(scene)
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


def _validate_out_path(out_path: str, *, segment=None,
                       count_only: bool = False) -> None:
    """Refuse destinations that cannot produce a video, before the scene runs.

    A missing extension and a directory both used to reach ffmpeg, which exits
    immediately; because the fast-record pipe captures ffmpeg's stderr, the
    caller only saw ``BrokenPipeError: [Errno 32] Broken pipe`` from the first
    frame write.
    """
    if count_only or segment is not None:
        return                       # count-only writes nothing; BMP mode uses a dir
    from real_time_manim.window.recording import check_pipe_destination
    check_pipe_destination(out_path)


def _require_ffmpeg(what: str) -> None:
    """Fail with an actionable message when ffmpeg is not installed."""
    from real_time_manim._ffmpeg import require
    require("ffmpeg", what)


def _remove_incomplete(path: str) -> None:
    """Delete a header-only file left by a failed record (best effort)."""
    try:
        if os.path.isfile(path) and os.path.getsize(path) < 1024:
            os.remove(path)
    except OSError:
        pass


# --------------------------------------------------------------------------
# frame-parallel fast record
# --------------------------------------------------------------------------

class _NotParallelizable(RuntimeError):
    """The scene cannot be handed to worker processes: record it in one pass."""


def _planned_jobs(jobs) -> int:
    """How many worker processes to use for a pipe-mode fast record.

    ``"auto"`` picks ``min(4, cpus - 1)``; an int is taken as-is, and 1 (or less)
    means the classic single-pass route.  ``None`` never reaches a worker split
    (see ``_parallel_plan``): it is the default single pass.
    """
    if jobs is None or jobs == "auto":
        return max(1, min(4, (os.cpu_count() or 2) - 1))
    return max(1, int(jobs))


# ``jobs="auto"`` splits only from this many frames on.  Every worker pays its
# own interpreter + Vulkan device + construct() startup (~0.5-1 s each,
# measured) while the frame cost only divides by the worker count, so a naive
# model crosses over at roughly 245 frames of 1080p60 (4 s of video) on this
# 16-core machine.  Measured end to end the crossing moves around a lot with
# machine state -- splitting a 15 s scene has been as good as 2x and as bad as
# nothing -- so the threshold is deliberately conservative: below it one pass is
# faster *and* starts sooner, and above it splitting at least cannot lose.
_AUTO_MIN_FRAMES = 240


def _has_main_guard(path: str) -> bool:
    """True when ``path`` keeps its demo behind ``if __name__ == "__main__"``.

    A by-path import executes the script's module body, so without the guard the
    demo would re-run inside every worker (recursing back into
    ``fast_record_scene``).  Such a scene is recorded in one pass instead.
    """
    import ast
    try:
        with open(path, encoding="utf-8") as fh:
            tree = ast.parse(fh.read(), filename=path)
    except Exception:
        return False
    for node in tree.body:
        if not isinstance(node, ast.If):
            continue
        test = node.test
        if (isinstance(test, ast.Compare) and isinstance(test.left, ast.Name)
                and test.left.id == "__name__" and len(test.comparators) == 1):
            value = test.comparators[0]
            if isinstance(value, ast.Constant) and value.value == "__main__":
                return True
    return False


def _scene_token(scene) -> Dict[str, str]:
    """A ``{kind, target, qual}`` handle the workers can re-import.

    ``kind`` is ``"module"`` (``target`` is an importable module name) or
    ``"file"`` (``target`` is a script path -- how a directly-run
    ``python my_scene.py`` is reached).  Anything that cannot be re-imported in
    another process (an instance, a lambda, a class defined inside a function, a
    REPL) raises :class:`_NotParallelizable` so the caller records in one pass.
    """
    if not isinstance(scene, type):
        raise _NotParallelizable("only a Scene class can be split across processes")
    qual = getattr(scene, "__qualname__", "") or ""
    if not qual or "<locals>" in qual:
        raise _NotParallelizable("the Scene class is not importable by name")
    module = getattr(scene, "__module__", "") or ""
    if module == "__main__":
        # A script run directly (`python my_scene.py`) has no importable name:
        # hand the worker the file so it can load it by path.
        path = getattr(sys.modules.get("__main__"), "__file__", None)
        if not path or not os.path.exists(path):
            raise _NotParallelizable("cannot locate the running script for workers")
        path = os.path.abspath(path)
        if not _has_main_guard(path):
            raise _NotParallelizable(
                "the script has no `if __name__ == \"__main__\"` guard, so it "
                "cannot be imported by the workers")
        return {"kind": "file", "target": path, "qual": qual}
    if not module:
        raise _NotParallelizable("the Scene class has no module")
    return {"kind": "module", "target": module, "qual": qual}


def _parallel_plan(scene, jobs, fps: int, hidden: bool, count_only: bool,
                   segment, verbose: bool) -> Optional[Dict[str, Any]]:
    """``{jobs, scene_ref, n_frames}`` when this record should be split, else None.

    Only the explicit forms split: ``jobs=N`` and ``jobs="auto"``.  The default
    ``jobs=None`` returns immediately -- deciding needs a probe pass that brings
    up a window and a Vulkan device just to learn the frame count (~1.4 s
    measured), which is not worth paying on the default path for scenes that
    usually turn out to be short.

    The probe prepares the scene (construct + timeline, no frame drawn) so the
    parent knows the frame count *and* that exactly one window is opened.  Its
    ``construct()`` output is deliberately left on screen: the workers then run
    the same construct with their stdout muted, so the user sees it exactly
    once, as in a single-pass record.
    """
    if jobs is None:                               # default: one pass, no probe
        return None
    if count_only or segment is not None or not hidden:
        return None
    if os.environ.get("RTM_IN_WORKER"):
        return None                                # a worker never re-splits
    want = _planned_jobs(jobs)
    if want < 2:
        return None
    auto = jobs == "auto"
    try:
        token = _scene_token(scene)
    except _NotParallelizable as exc:
        if verbose:
            print("[rtm] %s; recording in one pass" % exc)
        return None
    from real_time_manim.frames import FrameServer, _LAST_WINDOWS
    server = FrameServer(scene, hidden=True)
    try:
        # Play-by-play frame count (per-play grids, frozen waits via int()),
        # not round(duration * fps): the two disagree whenever a play's
        # duration is not a frame multiple, which made a split record write a
        # different number of frames than the single-pass one.  The fallback
        # keeps a stand-in server (tests, older wrappers) working.
        frame_times = getattr(server, "frame_times", None)
        if callable(frame_times):
            n_frames = len(frame_times(fps))
        else:
            n_frames = max(1, int(round(server.duration * fps)))
        n_windows = len(_LAST_WINDOWS)
    finally:
        server.close()
    if n_windows != 1:
        if verbose:
            print("[rtm] scene opens %d windows; recording in one pass" % n_windows)
        return None
    if auto and n_frames < _AUTO_MIN_FRAMES:
        return None                                # not long enough to pay off
    # Never spawn a worker whose block would be empty.
    return {"jobs": min(want, n_frames), "scene_ref": token, "n_frames": n_frames}


def _concat_segments(segments: List[str], out_path: str) -> None:
    """Join the workers' segments in order, without re-encoding."""
    # Guard here as well as in the caller: this is the one external process the
    # parallel path runs itself, and a missing ffmpeg must name itself.
    _require_ffmpeg("join the recorded segments into %r" % out_path)
    lst = out_path + ".concat.txt"
    with open(lst, "w", encoding="utf-8") as fh:
        for seg in segments:
            fh.write("file '%s'\n" % seg.replace("\\", "/"))
    try:
        subprocess.run(
            ["ffmpeg", "-y", "-loglevel", "error", "-f", "concat", "-safe", "0",
             "-i", lst, "-c", "copy", out_path], check=True)
    finally:
        if os.path.exists(lst):
            os.remove(lst)


def _worker_sounds(segments: List[str]):
    """The first worker's collected ``add_sound`` cues (they are identical)."""
    for seg in segments:
        side = seg + ".sounds.json"
        if not os.path.exists(side):
            continue
        try:
            with open(side, encoding="utf-8") as fh:
                data = json.load(fh)
        except Exception:
            return None
        if data.get("sounds"):
            return ([tuple(s) for s in data["sounds"]],
                    [dict(k) for k in data.get("kwargs", [])])
    return None


def _worker_subcaptions(segments: List[str]):
    """The first worker's collected subcaption cues (they are identical).

    Workers run ``construct`` in schedule mode, so ``play(subcaption=...)``
    lands in the worker's in-memory store; worker 0 persists it next to its
    segment.  Without this the parent's ``audio_track.reset()`` (below) left
    the flat store empty and no ``.srt`` was ever written for a split record.
    """
    for seg in segments:
        side = seg + ".subcaptions.json"
        if not os.path.exists(side):
            continue
        try:
            with open(side, encoding="utf-8") as fh:
                data = json.load(fh)
        except Exception:
            return None
        if data:
            return [dict(entry) for entry in data]
    return None


def _fast_record_parallel(scene, out_path: str, *, fps: int, jobs: int,
                          scene_ref: Dict[str, str], n_frames: int,
                          overwrite: bool, cleanup: bool,
                          verbose: bool) -> Dict[str, Any]:
    """Record by splitting the frame range across ``jobs`` processes.

    Frames of a time-addressable scene are independent, so worker *i* renders
    its own contiguous block into its own mp4; the segments are then
    concatenated with ``-c copy``.  Each worker pays its own ``construct()`` and
    window, so this wins when the scene is long compared with that setup cost.
    """
    import tempfile

    out_path = os.path.abspath(out_path)
    _validate_out_path(out_path)
    _require_ffmpeg("record %r" % out_path)
    os.makedirs(os.path.dirname(out_path) or ".", exist_ok=True)
    _guard_overwrite(out_path, overwrite)

    from real_time_manim import audio_track
    audio_track.reset()

    tmp_dir = tempfile.mkdtemp(prefix="rtm_frames_")
    try:
        segments = [os.path.join(tmp_dir, "seg_%03d.mp4" % i) for i in range(jobs)]
        env = dict(os.environ)
        # A worker imports the scene by name, so it needs our import path -- both
        # for `-m` to resolve real_time_manim itself (that happens before the
        # module body runs, hence PYTHONPATH) and for the scene's own module
        # (RTM_RECORD_SYSPATH, inserted by the worker before importing).
        import_path = [os.path.abspath(p) for p in sys.path
                       if p and os.path.isdir(p)]
        env["RTM_RECORD_SYSPATH"] = json.dumps(import_path)
        inherited = env.get("PYTHONPATH")
        env["PYTHONPATH"] = os.pathsep.join(
            import_path + ([inherited] if inherited else []))
        env["PYTHONIOENCODING"] = "utf-8"
        procs = []
        errs = []
        for i, seg in enumerate(segments):
            cmd = [sys.executable, "-m", "real_time_manim._record_worker",
                   scene_ref["kind"], scene_ref["target"], scene_ref["qual"],
                   str(i), str(jobs), str(n_frames), seg, str(fps)]
            err_path = os.path.join(tmp_dir, "err_%03d.log" % i)
            errs.append(err_path)
            procs.append(subprocess.Popen(
                cmd, env=env, cwd=os.getcwd(),
                stdout=subprocess.DEVNULL,      # parent already printed construct
                stderr=open(err_path, "wb")))
        codes = [p.wait() for p in procs]
        if any(codes):
            raise RuntimeError("frame worker(s) failed: exit codes %s\n%s"
                               % (codes, _tail_logs(errs, codes)))

        good = [s for s in segments
                if os.path.exists(s) and os.path.getsize(s) > 0]
        if not good:
            raise RuntimeError("no worker produced a segment")
        _concat_segments(good, out_path)

        sounds = _worker_sounds(good)
        if sounds:
            audio_track.reset()
            audio_track._sounds.extend(sounds[0])
            audio_track._sound_kwargs.extend(sounds[1])
        # Restore the cues AFTER the reset(s) above: `reset()` also empties the
        # subcaption store, so merging earlier would throw them away again.
        captions = _worker_subcaptions(good)
        if captions:
            from real_time_manim.window.play import record_subcaption
            for entry in captions:
                try:
                    record_subcaption(None, entry.get("content", ""),
                                      entry.get("start", 0.0),
                                      entry.get("duration", 0.0))
                except Exception:
                    continue
        if verbose:
            total = sum(_frame_count(s) for s in good)
            print("[FastRecord] Parallel: %d workers x %d frames -> %d frames -> %s"
                  % (jobs, n_frames, total, out_path))
    finally:
        shutil.rmtree(tmp_dir, ignore_errors=True)

    if cleanup:
        from real_time_manim.util import clear_media
        clear_media(verbose=verbose)
    muxed = audio_track.apply_sounds([out_path], verbose=verbose)
    return {
        "out_path": out_path,
        "windows": [out_path],
        "files": [out_path] if os.path.exists(out_path) else [],
        "with_audio": muxed,
    }


def _tail_logs(paths: List[str], codes: List[int], lines: int = 12) -> str:
    """The tail of each failed worker's stderr, for the error message."""
    parts = []
    for path, code in zip(paths, codes):
        if not code or not os.path.exists(path):
            continue
        try:
            with open(path, encoding="utf-8", errors="replace") as fh:
                text = fh.read().strip().splitlines()[-lines:]
        except OSError:
            text = ["<unreadable log>"]
        parts.append("--- %s (exit %d) ---\n%s"
                     % (os.path.basename(path), code, "\n".join(text)))
    return "\n".join(parts)


def _frame_count(path: str) -> int:
    """Frame count of an mp4 (ffprobe), 0 when it cannot be read."""
    try:
        out = subprocess.run(
            ["ffprobe", "-v", "error", "-select_streams", "v:0", "-count_frames",
             "-show_entries", "stream=nb_read_frames", "-of", "csv=p=0", path],
            capture_output=True, text=True, encoding="utf-8").stdout.strip()
        return int(out.splitlines()[0])
    except (OSError, ValueError, IndexError):
        return 0                        # no ffprobe / unreadable file: best effort


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
        import real_time_manim.window as vb
        self._vb = vb
        self._out_path = out_path
        self._on_init = on_init
        self._on_close = on_close
        self.verbose = verbose
        self._orig_init = vb.MLWindow.__init__
        self._orig_close = vb.MLWindow.close
        self._n_windows = 0
        self._n_closed = 0
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
            st._n_closed += 1
            try:
                st._on_close(self_)
            finally:
                # Always shut the window down, even when the encoder raises
                # (the failure is reported by the caller, not masked by a
                # leaked Vulkan device).
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
         cleanup: bool = True, hidden: Optional[bool] = None,
         expect_files: bool = True, segment=None) -> Dict[str, Any]:
    runner = _as_runner(scene)
    out_path = os.path.abspath(out_path)
    _validate_out_path(out_path, segment=segment, count_only=count_only)
    if expect_files:
        _require_ffmpeg("record %r" % out_path)
    os.makedirs(os.path.dirname(out_path) or ".", exist_ok=True)
    _guard_overwrite(out_path, overwrite, count_only)
    from real_time_manim import audio_track
    audio_track.reset()
    rec = _AutoRecord(out_path, on_init, on_close, verbose=verbose)
    # ``hidden`` decides whether the scene's windows are *created* hidden (never
    # shown, so nothing pops onto the desktop) -- not merely hidden afterwards.
    from real_time_manim.window import MLWindow
    prev_hidden = MLWindow._hidden_default
    if hidden is not None:
        MLWindow._hidden_default = bool(hidden)
    try:
        with rec:
            runner()
    finally:
        MLWindow._hidden_default = prev_hidden
    # A window that was opened but never closed never ran the encoder finish
    # hook (``_finish_fast_record`` / ``stop_record``): the ffmpeg pipe stays
    # open and the file on disk is a 48-byte header.  That used to be reported
    # as success (audit ``forget_close_fast_record``); fail with an actionable
    # message instead of handing back a broken video, and remove the stub so it
    # cannot be mistaken for a real recording later.
    if expect_files and rec._n_windows and rec._n_closed < rec._n_windows:
        for f in rec.windows:
            _remove_incomplete(f)
        raise RuntimeError(
            "recorded %d window(s) but MLWindow.close() was only called %d "
            "time(s): the encoder was never finished, so the output is "
            "incomplete (and the partial file was removed). Call win.close() "
            "at the end of construct()."
            % (rec._n_windows, rec._n_closed)
        )
    # A scene with no MLWindow draws nothing RTM can capture: it ran on
    # ManimCE's Cairo renderer (writing its own media/ output, which the
    # cleanup below removes) and used to come back as `files: []` -- success,
    # with no video and no explanation.  `self.play(...)` is not enough.
    if expect_files and rec._n_windows == 0:
        if cleanup:
            from real_time_manim.util import clear_media
            clear_media(verbose=verbose)
        raise RuntimeError(
            "the scene ran but opened no MLWindow, so nothing was recorded.\n"
            "RTM only captures frames drawn by an MLWindow. Inside "
            "construct():\n"
            "    win = MLWindow(1920, 1080)\n"
            "    win.scene = self\n"
            "    win.play(Create(mobject), run_time=1.0)\n"
            "    win.close()\n"
            "(`self.play(...)` alone runs on ManimCE's Cairo renderer, which "
            "RTM does not record.)"
        )
    # Rendering leaves transient manim media/Tex output behind; clear it for the
    # caller so they never have to remember to.  Opt out via cleanup=False.
    if cleanup:
        from real_time_manim.util import clear_media
        clear_media(verbose=verbose)
    files = [f for f in (rec.windows if rec.windows else _produced_files(out_path))
             if os.path.exists(f)]
    if segment is not None:
        # In BMP mode each ``rec.windows`` entry is a directory, so the generic
        # branch above returns the directories themselves -- not the frames
        # that were written.  Callers use ``files`` to know what is on disk.
        bmps = []
        for target in (rec.windows or [out_path]):
            if os.path.isdir(target):
                bmps.extend(sorted(
                    os.path.join(target, name)
                    for name in os.listdir(target) if name.endswith(".bmp")
                ))
        if not bmps:
            raise RuntimeError(
                "BMP segment mode wrote no frames to %r" % out_path
            )
        files = bmps
    # A 262-byte "video" is what an unbound scene leaves behind (no frame was
    # ever drawn) -- see audit ``unbound_window_fast_record``.  Anything below
    # one kilobyte cannot contain a frame.
    if expect_files:
        for f in files:
            try:
                size = os.path.getsize(f)
            except OSError:
                size = 0
            if size < 1024:
                _remove_incomplete(f)
                raise RuntimeError(
                    "recorded file looks empty/incomplete (%d bytes): %s -- "
                    "did the scene forget `win.scene = self`, or forget "
                    "win.close()? (the incomplete file was removed)"
                    % (size, f)
                )
    # Phase 6: attach the sounds the scene registered (copy the video stream).
    muxed = audio_track.apply_sounds(files, verbose=verbose)
    return {
        "out_path": out_path,
        "windows": rec.windows,
        "files": files,
        "with_audio": muxed,
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
    path).  The window is shown, and every frame the play loop presents is
    captured on the render thread and piped straight to ffmpeg -- one captured
    frame per drawn frame, so a 1.0 s ``play`` at 60 fps contributes exactly
    60 frames (no wall-clock sampling and no duplicate padding).  Encoding
    runs alongside the scene and is finished by ``stop_record``.

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
                      verbose: bool = True,
                      jobs: Union[int, str, None] = None) -> Dict[str, Any]:
    """Record a scene **offline** via fast framebuffer readback.

    Maps onto ``MLWindow.enable_fast_record`` / ``_finish_fast_record`` (the
    batch path): each frame is read straight from the Vulkan
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
    jobs:
        Worker processes for the pipe mode.  ``None`` (default) records in one
        pass -- no probe, nothing to pay for short clips.  ``"auto"`` first
        probes the scene (one extra window bring-up) and then splits only if
        that is a win: an importable single-window Scene of at least
        ``_AUTO_MIN_FRAMES`` frames, across ``min(4, cpus - 1)`` processes.  An
        int asks for that many workers, splitting when the scene allows it (the
        frame count and the single-window requirement are checked once, then the
        range is divided and the segments concatenated losslessly).  ``1`` is
        the classic single pass.  Splitting needs a Scene *class* importable in
        another process, so instances, lambdas and classes defined inside a
        function (or a script with no ``if __name__ == "__main__"`` guard)
        always fall back to one pass.  Ignored for ``count_only``, ``segment``
        and ``hidden=False``.

    Returns
    -------
    dict with ``out_path``, ``windows`` and ``files`` (see :func:`record_scene`).
    """
    plan = _parallel_plan(scene, jobs, fps, hidden, count_only, segment, verbose)
    if plan is not None:
        return _fast_record_parallel(
            scene, out_path if out_path is not None else _default_out_path(),
            fps=fps, overwrite=overwrite, cleanup=cleanup, verbose=verbose,
            **plan)

    def on_init(win: Any, out: str) -> None:
        win.enable_fast_record(out, fps=fps, hidden=hidden,
                               segment=segment, count_only=count_only)

    def on_close(win: Any) -> None:
        win._finish_fast_record()

    return _run(scene, out_path if out_path is not None else _default_out_path(),
                on_init, on_close, verbose, overwrite, count_only=count_only,
                cleanup=cleanup, hidden=hidden, segment=segment,
                expect_files=(not count_only) and segment is None)
