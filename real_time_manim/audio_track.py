"""Sound support for real-time-manim (plan Phase 6).

manim's `Scene.add_sound` hands the clip to the renderer's file writer, which RTM
never runs -- RTM pipes raw frames straight to ffmpeg, and that command has no
audio input at all (grep for `audio`/`add_sound` in the package used to find
nothing).  So a recorded scene silently lost its sound.

What this does instead:

* `install_add_sound_hook(scene)` (called from `record.scene_lifecycle`, before
  `construct`) records every `add_sound(sound_file, time_offset, gain)` together
  with the playhead at that moment.  manim derives the placement from
  `scene.time`, which RTM never advances, so the playhead comes from the bound
  window's `_cursor` (the recorded timeline length so far) instead.
* After the scene has run, `apply_sounds(files)` overlays the clips onto silence
  (pydub), then muxes the track into each produced MP4 with a second ffmpeg pass
  (`-c:v copy`, so the video is not re-encoded).  It is also where the run's
  subcaptions (`play(..., subcaption=...)`, collected on the window because RTM
  has no file writer) are written out as `.srt` next to the first output video.
"""

from __future__ import annotations

import os
import subprocess

_sounds = []            # list of (abs_path, start_seconds, gain_or_None)
_sound_kwargs = []      # parallel list: extra add_sound kwargs per entry

#: The ``Scene.add_sound`` keywords RTM's mix chain actually implements.
#:
#: manim's ``Scene.add_sound(**kwargs)`` forwards them to
#: ``SceneFileWriter.add_audio_segment``, whose only keyword is
#: ``gain_to_background`` -- a dB adjustment applied to the background track
#: while the clip plays, i.e. pydub's ``gain_during_overlay``.  Anything else
#: manim would reject anyway, so RTM names it and drops it (a warning) instead
#: of swallowing it in silence (gap A33).
SUPPORTED_ADD_SOUND_KWARGS = ("gain_to_background",)


def _scene_window(scene):
    """The MLWindow bound to `scene`, if one exists (for the playhead)."""
    try:
        from real_time_manim.window import MLWindow
    except Exception:                                    # pragma: no cover
        return None
    for win in reversed(getattr(MLWindow, "_registry", ()) or ()):
        if getattr(win, "scene", None) is scene:
            return win
    return None


def install_add_sound_hook(scene) -> None:
    """Record `scene.add_sound` calls instead of letting them fall on the floor."""
    if getattr(scene, "_rtm_sound_hook", False):
        return
    original = scene.add_sound

    def add_sound(sound_file, time_offset=0, gain=None, **kwargs):
        # Split the keywords RTM's mix can act on from the ones it cannot;
        # the latter are named in a warning rather than silently discarded
        # (gap A33).  manim's own writer only supports `gain_to_background`
        # anyway (SceneFileWriter.add_audio_segment).
        supported = {}
        unsupported = []
        for key, value in kwargs.items():
            if key in SUPPORTED_ADD_SOUND_KWARGS:
                supported[key] = value
            else:
                unsupported.append(str(key))
        if unsupported:
            listed = ", ".join(sorted(repr(k) for k in unsupported))
            message = (
                f"[RTM] Scene.add_sound(): unsupported parameter(s) {listed} "
                "ignored -- RTM 不支持该参数: the RTM audio mix supports only "
                "sound_file, time_offset, gain"
                + (f", {', '.join(SUPPORTED_ADD_SOUND_KWARGS)}"
                   if SUPPORTED_ADD_SOUND_KWARGS else "")
                + "."
            )
            try:                                          # encoding-safe print
                from real_time_manim.window.play import print_warning
                print_warning(message)
            except Exception:                             # pragma: no cover
                print(message)
        win = _scene_window(scene)
        playhead = float(getattr(win, "_cursor", 0.0) or 0.0)
        try:
            _sound_kwargs.append(dict(supported))
            _sounds.append((os.path.abspath(sound_file),
                            playhead + float(time_offset or 0.0), gain))
        except Exception:
            # Keep the two lists in step if the second append ever failed.
            if len(_sound_kwargs) > len(_sounds):
                _sound_kwargs.pop()
        try:
            # Forward only what manim itself accepts: an unsupported keyword
            # reaching the file writer raises TypeError, which used to be
            # swallowed here -- silently, for ever.
            return original(sound_file, time_offset=time_offset, gain=gain,
                            **supported)
        except Exception:
            # manim's file writer is not running under RTM -- our own track
            # replaces it, so a failure here is expected and harmless.
            return None

    scene.add_sound = add_sound
    scene._rtm_sound_hook = True


def reset() -> None:
    _sounds.clear()
    _sound_kwargs.clear()
    # Subcaptions are collected on windows that the registry keeps alive for
    # the life of the process, so a fresh recording run has to empty them --
    # otherwise an earlier run's cues would be exported into this run's .srt.
    # `record._run` calls reset() before it starts the scene.
    try:
        from real_time_manim.window.play import clear_subcaptions
        clear_subcaptions()
    except Exception:                                    # pragma: no cover
        pass


def sounds():
    return list(_sounds)


def has_sounds() -> bool:
    return bool(_sounds)


def _probe_duration(path):
    out = subprocess.run(["ffprobe", "-v", "error", "-show_entries",
                          "format=duration", "-of", "csv=p=0", path],
                         capture_output=True, text=True).stdout.strip()
    try:
        return float(out)
    except ValueError:
        return 0.0


def build_track(wav_path, duration=None):
    """Overlay every recorded sound onto silence -> `wav_path` (PCM wav)."""
    from pydub import AudioSegment

    if duration is None:
        duration = max((start for _, start, _ in _sounds), default=0.0) + 1.0
    track = AudioSegment.silent(duration=int(max(duration, 0.1) * 1000))
    for i, (path, start, gain) in enumerate(_sounds):
        if not os.path.exists(path):
            continue
        try:
            clip = AudioSegment.from_file(path)
        except Exception:
            continue
        if gain:
            try:
                clip = clip.apply_gain(float(gain))       # manim: gain in dB
            except Exception:
                pass
        overlay_kwargs = {}
        extra = _sound_kwargs[i] if i < len(_sound_kwargs) else None
        bg_gain = (extra or {}).get("gain_to_background")
        if bg_gain is not None:
            # manim's `gain_to_background` is pydub's `gain_during_overlay`:
            # a dB adjustment applied to the existing track while this clip
            # plays over it (SceneFileWriter.add_audio_segment).
            try:
                overlay_kwargs["gain_during_overlay"] = float(bg_gain)
            except (TypeError, ValueError):
                pass
        track = track.overlay(clip, position=int(max(start, 0.0) * 1000),
                              **overlay_kwargs)
    track.export(wav_path, format="wav")
    return wav_path


def mux_audio(mp4_path, wav_path):
    """Copy the video stream and attach `wav_path` as AAC.  Replaces the file."""
    tmp = mp4_path + ".withaudio.mp4"
    proc = subprocess.run(
        ["ffmpeg", "-y", "-loglevel", "error", "-i", mp4_path, "-i", wav_path,
         "-c:v", "copy", "-c:a", "aac", "-shortest", tmp],
        capture_output=True, text=True)
    if proc.returncode != 0 or not os.path.exists(tmp):
        return False
    os.replace(tmp, mp4_path)
    return True


def _export_subcaptions(files, verbose=False):
    """Record-end hook: write the run's subcaptions as ``.srt`` (gap A6).

    ``record._run`` calls :func:`apply_sounds` at the end of every recording
    with the files that were produced -- it is the one place that knows the
    output path without ``record.py`` (owned by another session) changing.
    The ``.srt`` lands next to the first output video, the way manim names it
    after the video file.  Returns the path written, or None (no captions, no
    files, or nothing to export).
    """
    existing = [f for f in (files or []) if os.path.exists(f)]
    if not existing:
        return None
    try:
        from real_time_manim.window.play import export_srt
    except Exception:                                    # pragma: no cover
        return None
    srt_path = os.path.splitext(existing[0])[0] + ".srt"
    try:
        return export_srt(srt_path, verbose=verbose)
    except OSError:                                      # pragma: no cover
        return None


def apply_sounds(files, verbose=False):
    """Build the track from the recorded calls and mux it into every file.

    Also exports any subcaptions the run collected (see
    :func:`_export_subcaptions`); the two are independent, so a scene with
    captions but no sound still gets its ``.srt``.
    """
    _export_subcaptions(files, verbose=verbose)
    if not _sounds or not files:
        return []
    files = [f for f in files if os.path.exists(f)]
    if not files:
        return []
    # Padding: a track that is even slightly shorter than the video makes
    # `-shortest` trim video frames (measured: 16 -> 12 frames).  Extra audio
    # tail is harmless, so always overshoot a little.
    duration = max((_probe_duration(f) for f in files), default=None)
    if duration:
        duration += 0.5
    wav = os.path.join(os.path.dirname(files[0]) or ".", "_rtm_soundtrack.wav")
    try:
        build_track(wav, duration)
        done = [f for f in files if mux_audio(f, wav)]
    finally:
        try:
            os.remove(wav)
        except OSError:
            pass
    if verbose:
        print(f"[audio] muxed {len(_sounds)} sound(s) into {len(done)} file(s)")
    return done
