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
    """True for manim's own animations *and* user subclasses of them.

    Matching on the module name missed ``class MyFade(FadeIn)`` -- defined in the
    user's own module -- which then got RTM's ``begin(t)`` signature and raised
    "begin() takes 1 positional argument but 2 were given".  Identity is what
    matters, and RTM's own base class does not inherit manim's Animation.
    """
    try:
        from manim.animation.animation import Animation as _ManimAnimation
    except Exception:                       # pragma: no cover - manim is required
        return type(anim).__module__.startswith("manim")
    if isinstance(anim, _ManimAnimation):
        return True
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


def ce_frame_count(anims, duration, fps):
    """How many frames manim itself emits for one play of ``anims``.

    An animation is stepped with ``np.arange(0, run_time, 1/fps)`` -- one frame per
    step, at times ``0, dt, 2dt, ...`` -- while a wait is a *frozen* frame counted
    as ``int(duration / dt)`` (``CairoRenderer.freeze_current_frame``).  Rounding
    both to nearest instead drifts by a frame per segment, which is what put 47 of
    114 suite scenes 1-4 frames away from CE.

    The epsilon keeps an exact multiple of dt (e.g. run_time 0.6666.. = 10/15) at
    ``n`` rather than ``n + 1``, matching ``arange``'s exclusive end.
    """
    import math
    try:
        fps = float(fps) or 30.0
        duration = float(duration)
    except (TypeError, ValueError):
        return 1
    anims = list(anims or [])
    frozen = len(anims) == 1 and bool(getattr(anims[0], "is_static_wait", False))
    if frozen:
        return max(1, int(duration * fps))
    return max(1, int(math.ceil(duration * fps - 1e-9)))

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
        self._last_t = None        # last rendered time, for updater dt re-anchoring

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
                # manim's Scene.play() gives every animation its scene before
                # begin(): introducers register their mobject and .scene is
                # stored.  manim-native classes such as AddTextWordByWord read
                # it, so the timeline path has to do the same (lazy import: this
                # module is imported by vulkan_bind).
                from real_time_manim.vulkan_bind import _setup_anim_scene
                _setup_anim_scene(anim, self.scene)
                anim.begin()          # manim's begin() takes no time argument
            else:
                anim.begin(0.0)       # our animations take an absolute start time
            # Phase 3: a manim-native animation writes no render channels of its
            # own, so install the adapter that derives them from its state.
            from real_time_manim.render_hooks import install_hooks
            install_hooks(anim)
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

    def render_at(self, t, readback=False):
        """Evaluate at ``t``, draw that state, and present it.  O(1) in ``t``.

        Order matters: the renderer draws whatever is queued, so the state at
        ``t`` must be queued (``sync``) *before* the frame is drawn (``tick``).
        Drawing first presents the previous call's state, which is what made a
        readback after ``render_at(t)`` return the previous frame.

        With ``readback=True`` the frame also copies itself into the readback
        buffer before it is presented, so a following read returns exactly this
        frame (see ``MLWindow.request_readback``).
        """
        self.evaluate(t)
        # Mobject updaters are stateful, so they accumulate only while the
        # timeline moves forward; a seek (first frame, same t, or backwards)
        # re-anchors with dt=0 instead of replaying history.  The animation
        # state itself stays a pure function of t, so random access is intact.
        dt = 0.0 if (self._last_t is None or t <= self._last_t) else t - self._last_t
        if dt > 0.0:
            from real_time_manim.vulkan_bind import _drive_mobject_updaters
            _drive_mobject_updaters(self.scene, dt)
        self._last_t = t
        self.window.sync(self.scene)
        if readback:
            self.window.request_readback()
        self.window.tick()

    def screenshot_at(self, t, path):
        self.render_at(t, readback=True)
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
        anims = [e.get("anim") for e in getattr(self, "_entries", [])]
        n_frames = ce_frame_count(anims, duration, fps)
        tmpdir = tempfile.mkdtemp(prefix="rtm_timeline_")
        try:
            for k in range(n_frames):
                t = k / float(fps)
                frame_start = time.perf_counter()
                self.render_at(t, readback=True)
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
