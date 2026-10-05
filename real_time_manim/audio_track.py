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
  (`-c:v copy`, so the video is not re-encoded).
"""

from __future__ import annotations

import os
import subprocess

_sounds = []            # list of (abs_path, start_seconds, gain_or_None)


def _scene_window(scene):
    """The MLWindow bound to `scene`, if one exists (for the playhead)."""
    try:
        from real_time_manim.vulkan_bind import MLWindow
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
        win = _scene_window(scene)
        playhead = float(getattr(win, "_cursor", 0.0) or 0.0)
        try:
            _sounds.append((os.path.abspath(sound_file),
                            playhead + float(time_offset or 0.0), gain))
        except Exception:
            pass
        try:
            return original(sound_file, time_offset=time_offset, gain=gain, **kwargs)
        except Exception:
            # manim's file writer is not running under RTM -- our own track
            # replaces it, so a failure here is expected and harmless.
            return None

    scene.add_sound = add_sound
    scene._rtm_sound_hook = True


def reset() -> None:
    _sounds.clear()


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
    for path, start, gain in _sounds:
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
        track = track.overlay(clip, position=int(max(start, 0.0) * 1000))
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


def apply_sounds(files, verbose=False):
    """Build the track from the recorded calls and mux it into every file."""
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
