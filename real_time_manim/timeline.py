"""Time-addressable evaluation for real-time-manim (2.0.0 pre-work).

The default ``MLWindow.play`` pipeline advances animations by wall-clock time and
mutates mobjects in place, so reaching frame N requires replaying 0..N — you
cannot jump to an arbitrary frame.

For animations whose ``interpolate`` recomputes the mobject state from the
start/target copies captured at ``begin`` (i.e. a pure function of alpha), the
state at any time ``t`` depends only on ``t``.  ``Timeline`` exploits that:

    tl = Timeline(window, scene)
    tl.add(FadeIn(sq), start=0.0)
    tl.add(Transform(sq, circle), start=1.0)
    tl.finalize()
    tl.render_at(1.5)          # instant — no replay

A whole scene is just a schedule of animations on one global time axis, so
``render_at(t)`` gives any frame of the whole scene, enabling scrubbing / seek.

This module is additive: it does not touch ``play`` yet.  The plan is to migrate
the legacy pipeline onto this model (see ``docs/2.0.0-time-addressable.md``).

Known limitations (tracked for later phases):
- stateful animations (rotation accumulation, updaters, ``TracedPath`` histories,
  speed modifiers) are not pure; they are flagged and, in ``strict`` mode,
  rejected.
"""


#: Animation class names that are known to accumulate state across frames and
#: therefore cannot (yet) be evaluated as a pure function of time.
STATEFUL_ANIMATIONS = frozenset({
    "Rotate", "Rotating", "Rotation",
    "AnimationGroup", "Succession", "LaggedStart", "LaggedStartMap",
    "SpiralIn", "Blink", "FadeTransform", "FadeTransformPieces",
    "TransformMatchingAbstractBase", "TransformMatchingShapes",
    "TransformMatchingTex", "SpeedModifier", "ChangeSpeed",
})


def is_animation_stateful(anim):
    """Best-effort check for animations that are not pure functions of alpha."""
    for cls in type(anim).__mro__:
        if cls.__name__ in STATEFUL_ANIMATIONS:
            return True
    # animations carrying their own updaters accumulate frame-to-frame state
    if getattr(anim, "updaters", None):
        return True
    return False


def _is_manim_animation(anim):
    return type(anim).__module__.startswith("manim")


def evaluate_animation(anim, t):
    """Set ``anim``'s mobjects to their state at elapsed time ``t`` (seconds).

    Our animations take an absolute time and derive ``alpha`` from
    ``start_time``; manim's own animations take ``alpha`` directly.  In both
    cases ``start_time`` is pinned to ``0`` so ``t`` is elapsed-since-prepare.
    ``t`` is clamped to ``[0, run_time]``, so evaluating before an animation
    starts yields its start state and after it ends its final state.
    """
    run_time = float(getattr(anim, "run_time", 1.0) or 1.0)
    local = 0.0 if t < 0 else (run_time if t > run_time else t)
    alpha = 0.0 if run_time <= 0 else local / run_time
    if _is_manim_animation(anim):
        if hasattr(anim, "start_time"):
            anim.start_time = 0.0
        # manim rate-functions live inside interpolate(); pass raw alpha.
        anim.interpolate(alpha)
    else:
        if hasattr(anim, "start_time"):
            anim.start_time = 0.0
        anim.interpolate(local)


class Timeline:
    """A schedule of animations on one time axis that can render any frame
    instantly (``render_at``) or forward (``render_mp4``)."""

    def __init__(self, window, scene, strict=False):
        self.window = window
        self.scene = scene
        self.strict = strict
        self._entries = []          # {anim, start, run_time, stateful}
        self._prepared = False
        self.duration = 0.0

    def add(self, anim, start=0.0):
        """Schedule ``anim`` to begin at global time ``start`` (seconds)."""
        if self._prepared:
            raise RuntimeError("cannot add to a finalized Timeline")
        stateful = is_animation_stateful(anim)
        if stateful and self.strict:
            raise ValueError(
                f"{type(anim).__name__} is stateful and cannot be evaluated "
                f"as a pure function of time yet")
        self._entries.append({
            "anim": anim,
            "start": float(start),
            "run_time": float(getattr(anim, "run_time", 1.0) or 1.0),
            "stateful": stateful,
        })
        return self

    def finalize(self):
        """Capture each animation's pristine start state (calls ``begin``).

        Must be called once, after the scene already contains the animated
        mobjects (and any hidden targets), mirroring the setup ``play`` does.
        """
        if self._prepared:
            raise RuntimeError("Timeline already finalized")
        for entry in self._entries:
            anim = entry["anim"]
            if _is_manim_animation(anim):
                anim.begin()          # manim's begin() takes no time argument
            else:
                anim.begin(0.0)       # our animations take an absolute start time
        self.duration = max(
            (e["start"] + e["run_time"] for e in self._entries), default=0.0)
        self._prepared = True
        return self

    def prepare(self, *animations):
        """Convenience: schedule every animation at ``t = 0`` and finalize."""
        for anim in animations:
            self.add(anim, 0.0)
        return self.finalize()

    def stateful_names(self):
        return [type(e["anim"]).__name__ for e in self._entries if e["stateful"]]

    def evaluate(self, t):
        """Set every animation's mobjects to their state at time ``t`` (no draw)."""
        if not self._prepared:
            raise RuntimeError("call finalize()/prepare() first")
        for entry in self._entries:
            evaluate_animation(entry["anim"], t - entry["start"])

    def render_at(self, t):
        """Evaluate at ``t`` and draw one frame into the window.  O(1) in ``t``."""
        self.evaluate(t)
        self.window.tick()
        self.window.sync(self.scene)

    def screenshot_at(self, t, path):
        self.render_at(t)
        return self.window.screenshot(path)

    def render_mp4(self, path, fps=60, duration=None, realtime=False):
        """Render the whole schedule forward to ``path`` (mp4) by walking ``t``
        and drawing each frame — the same ``evaluate(t)`` path that powers
        ``render_at``.  With ``realtime=True`` it paces to wall-clock (for a live
        window); otherwise it runs as fast as it can (like a fast record)."""
        import os
        import shutil
        import subprocess
        import tempfile
        import time

        duration = float(self.duration if duration is None else duration)
        n_frames = int(round(duration * fps)) + 1
        tmpdir = tempfile.mkdtemp(prefix="rtm_timeline_")
        try:
            for k in range(n_frames):
                t = k / float(fps)
                frame_start = time.perf_counter()
                self.render_at(t)
                self.window.screenshot(os.path.join(tmpdir, f"f_{k:05d}.bmp"))
                if realtime:
                    left = (1.0 / fps) - (time.perf_counter() - frame_start)
                    if left > 0:
                        time.sleep(left)
            subprocess.run(
                ["ffmpeg", "-y", "-loglevel", "error",
                 "-framerate", str(fps),
                 "-i", os.path.join(tmpdir, "f_%05d.bmp"),
                 "-frames:v", str(n_frames),
                 "-c:v", "libx264", "-pix_fmt", "yuv420p", path],
                check=True)
        finally:
            shutil.rmtree(tmpdir, ignore_errors=True)
        return path
