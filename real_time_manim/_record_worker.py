# -*- coding: utf-8 -*-
"""One worker of a *frame-parallel* fast record (spawned by ``record.py``).

Frames of a time-addressable scene are independent, so a range of them can be
rendered by its own process with its own window, and the resulting segments are
concatenated afterwards.  The parent decides the frame count and every worker
derives its own range from ``(n_frames, jobs, index)`` -- the same pure function
on every process.

    python -m real_time_manim._record_worker <kind> <target> <qual> \\
        <index> <jobs> <n_frames> <out.mp4> <fps>

``kind``/``target``/``qual`` identify the scene class (see ``resolve_scene``);
the parent passes its ``sys.path`` through ``RTM_RECORD_SYSPATH`` (and
``PYTHONPATH``, so ``-m`` resolves at all) so repo-local modules and page
scripts still import.
"""
import contextlib
import json
import os
import shutil
import subprocess
import sys


def frame_block(n_frames, jobs, index):
    """Contiguous ``[start, end)`` for worker ``index`` (pure, order-preserving).

    The blocks partition ``range(n_frames)`` exactly, in worker order, with the
    first ``n_frames % jobs`` blocks one frame longer -- so concatenating the
    segments in index order reproduces the whole sequence.
    """
    jobs = max(1, int(jobs))
    index = min(max(0, int(index)), jobs - 1)
    base, extra = divmod(int(n_frames), jobs)
    start = index * base + min(index, extra)
    return start, start + base + (1 if index < extra else 0)


def resolve_scene(kind, target, qual):
    """A scene handle from the parent -> the class.

    ``kind="module"`` imports ``target`` by name; ``kind="file"`` loads a script
    by path, which is how a scene defined in a directly-run
    ``python my_scene.py`` is reached (its ``__module__`` is ``"__main__"`` and
    cannot be imported by name).  ``qual`` is the dotted class name inside it.
    """
    import importlib
    import importlib.util

    if kind == "file":
        spec = importlib.util.spec_from_file_location("_rtm_user_scene", target)
        if spec is None or spec.loader is None:
            raise ImportError("cannot load scene script %r" % target)
        obj = importlib.util.module_from_spec(spec)
        sys.modules["_rtm_user_scene"] = obj
        spec.loader.exec_module(obj)
    else:
        obj = importlib.import_module(target)
    for part in qual.split("."):
        if part:
            obj = getattr(obj, part)
    return obj


def segment_ffmpeg(width, height, fps, pix_fmt, out_path, threads=None):
    """Encode one worker's raw frame pipe with the shared settings."""
    from real_time_manim.window.recording import fast_pipe_ffmpeg_args

    return fast_pipe_ffmpeg_args(width, height, fps, pix_fmt, out_path,
                                 threads=threads)


def _private_media_dir(out_path):
    """Point manim's caches at a folder only this worker uses.

    Manim's ``Text`` / ``Tex`` SVG pipeline is *not* concurrency-safe: the cached
    SVG is parsed through a temporary file written next to it and unlinked right
    after (``SVGMobject.generate_mobject``), so two workers handling the same
    text corrupt each other with a partial parse or a "file is in use" unlink.
    A per-worker media dir removes the sharing entirely.
    """
    import real_time_manim                      # installs the bundled manim
    from manim import config

    path = out_path + ".media"
    os.makedirs(path, exist_ok=True)
    config.media_dir = path
    return path


def _dump_sounds(out_path):
    """Persist ``add_sound`` cues so the parent can mux the joined file."""
    from real_time_manim import audio_track

    if not audio_track.has_sounds():
        return
    data = {
        "sounds": [list(entry) for entry in audio_track._sounds],
        "kwargs": [dict(entry) for entry in audio_track._sound_kwargs],
    }
    with open(out_path + ".sounds.json", "w", encoding="utf-8") as fh:
        json.dump(data, fh)


def main(argv=None):
    argv = list(sys.argv[1:] if argv is None else argv)
    kind, target, qual, index, jobs, n_frames, out_path, fps = (
        argv[0], argv[1], argv[2], int(argv[3]), int(argv[4]), int(argv[5]),
        argv[6], int(argv[7]))
    os.environ["RTM_IN_WORKER"] = "1"              # belt and braces: no re-split
    extra = os.environ.get("RTM_RECORD_SYSPATH")
    if extra:
        for path in json.loads(extra):
            if path and path not in sys.path:
                sys.path.insert(0, path)

    from real_time_manim import frames

    media_dir = _private_media_dir(out_path)
    try:
        scene_cls = resolve_scene(kind, target, qual)
        # The parent already ran this construct on screen: keep the workers quiet
        # so a split record prints the scene as often as a single pass does.
        with open(os.devnull, "w") as devnull, contextlib.redirect_stdout(devnull):
            server = frames.FrameServer(scene_cls)
        try:
            if index == 0:
                # The parent muxes the concatenated file once all workers are
                # done; every worker hears the same cues, so one report is
                # enough.
                _dump_sounds(out_path)
            start, end = frame_block(n_frames, jobs, index)
            if end <= start:                    # more workers than frames
                return 0
            width, height = server.frame_size
            fmt = server.readback_format
            from real_time_manim.window.recording import encoder_threads
            proc = subprocess.Popen(
                segment_ffmpeg(width, height, fps, fmt, out_path,
                               threads=encoder_threads(jobs)),
                stdin=subprocess.PIPE, stderr=subprocess.DEVNULL)
            dt = 1.0 / fps
            with proc.stdin as pipe:
                for k in range(start, end):
                    pipe.write(server.grab_pixels(k * dt))
            return proc.wait()
        finally:
            server.close()
    finally:
        shutil.rmtree(media_dir, ignore_errors=True)


if __name__ == "__main__":
    raise SystemExit(main())
