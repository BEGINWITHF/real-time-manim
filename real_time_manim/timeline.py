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


def _is_wait_animation(anim):
    """True for manim's ``Wait`` AND RTM's own ``Wait``.

    RTM exports a ``Wait`` that subclasses RTM's ``Animation``, not manim's,
    so an ``isinstance(anim, manim.Wait)`` test misses it: a lone RTM
    ``Wait(0.3)`` @15fps counted the stepped ``arange`` 5 frames where manim
    writes the frozen ``int()`` 4 (BUG_REPORT L6).  ``scene.wait()`` builds a
    manim ``Wait``; ``win.play(Wait(...))`` builds this one -- both must
    resolve frozen-vs-stepped the same way.
    """
    try:
        from manim import Wait as _ManimWait
        if isinstance(anim, _ManimWait):
            return True
    except Exception:                       # pragma: no cover - manim is required
        pass
    from real_time_manim.animations.wait import Wait as _RTMWait
    return isinstance(anim, _RTMWait)


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
    step = 1.0 / fps
    anims = list(anims or [])
    frozen = False
    if len(anims) == 1:
        anim = anims[0]
        try:
            # Mirror manim's own test -- `Scene.is_current_animation_frozen_frame`
            # is `... and animations[0].is_static_wait`, i.e. plain truthiness.
            # `Scene.wait` resolves that flag from `should_update_mobjects()`, so a
            # scene *with updaters* gets False and manim STEPS the wait (measured:
            # 0.3 s -> 5 frames, ceil) while a plain scene gets True and freezes it
            # (4 frames, int).  Treating None as frozen put six updater/camera scenes
            # one frame short of CE.  `_is_wait_animation` also matches RTM's own
            # `Wait`, which is not a manim subclass (BUG_REPORT L6).
            frozen = (_is_wait_animation(anim)
                      and bool(getattr(anim, "is_static_wait", False)))
        except Exception:
            frozen = False
    if frozen:
        # manim: CairoRenderer.freeze_current_frame -> int(duration / dt)
        return max(1, int(duration / step))
    # manim: one frame per step of np.arange(0, run_time, step).  Mirror it exactly
    # rather than approximating with ceil(duration*fps): the two disagree whenever
    # float error lands on the boundary -- Blink's Succession run_time is
    # 0.6000000000000001, and 0.6000000000000001/(1/15) = 9.000000000000002 gives
    # manim 10 frames where ceil(0.6*15) gives 9.
    import numpy as np
    return max(1, len(np.arange(0.0, duration, step)))


def drive_animation_updaters(anim, dt):
    """Run one animation's OWN updater pass -- manim's ``Animation.update_mobjects``.

    ``Scene.update_to_time`` (manim 0.21) does three things per frame, in this
    order::

        for animation in self.animations:
            animation.update_mobjects(dt)   # (1) this function
            animation.interpolate(alpha)    # (2)
        self.update_mobjects(dt)            # (3) scene/mobject updaters

    RTM's timeline only ever did (2) and (3).  Step (1) is not a no-op: it walks
    ``Animation.get_all_mobjects_to_update()`` -- everything in
    ``get_all_mobjects()`` *except* ``self.mobject``, i.e. **the copies**
    ``begin()`` took (``starting_mobject``, ``target_mobject``, ``target_copy``).

    Those copies keep the updaters they were copied with, and a copy's updaters
    are the only place some animations accumulate state.  The wiki report
    ``03-动画/更新器动画/01b-更新工具与自动变化`` -- "tracepath画出的时直线" --
    is exactly this: the sample drives
    ``group.animate.shift(RIGHT*6)`` while ``group`` carries
    ``add_updater(lambda m: m.rotate(-0.3))`` and a ``TracedPath`` records
    ``circ.get_start``.  Without step (1) the two copies never rotate, so
    ``interpolate`` keeps re-deriving ``group`` from an unrotated pair and the
    scene pass' fresh ``rotate(-0.3)`` is wiped on the next frame: the traced
    point only ever sits at the single offset ``0.66*sin(-0.3)``, i.e. a
    perfectly straight horizontal line (measured: y spread 0.0000 in RTM vs
    1.3664 for manim's own loop).

    Only manim-native animations get this pass -- RTM's own classes take an
    absolute time in ``interpolate`` and write their channels themselves, and
    several of them expose a ``get_all_mobjects()`` whose entries are the real
    scene mobjects (running them here would double-drive their updaters against
    ``_drive_mobject_updaters``).
    """
    if not _is_manim_animation(anim):
        return
    updater = getattr(anim, "update_mobjects", None)
    if not callable(updater):
        return
    updater(dt)


def resolve_static_wait(scene, anims):
    """Mark a lone ``Wait`` static, the way manim's renderer does.

    ``Scene.wait`` leaves ``Wait.is_static_wait`` at ``None``; manim resolves it
    inside ``compile_animation_data`` / ``should_update_mobjects`` -- neither of
    which runs once RTM takes over ``Scene.play``, so the flag stayed ``None`` and
    both RTM and the frame counter had to guess.  manim's rule for a single Wait:

        static  <=>  not (always_update_mobjects or scene updaters or a
                          stop_condition or any mobject with a time updater)

    A static wait is a *frozen* frame, counted ``int(duration*fps)``; every other
    wait steps like an animation, counted ``ceil(duration*fps)``.  Measured: a
    plain scene's ``wait(0.3)`` = 4 frames, the same wait in a scene with updaters
    = 5 -- the difference behind six suite scenes one frame short of CE.

    Both manim's ``Wait`` (``self.wait``) and RTM's own ``Wait``
    (``win.play(Wait(...))``) are resolved; RTM's class used to fall through
    the ``isinstance`` test and stayed stepped even in a plain scene
    (BUG_REPORT L6).
    """
    if len(anims) != 1 or not _is_wait_animation(anims[0]):
        return
    wait = anims[0]
    if getattr(wait, "is_static_wait", None) is not None:
        return                                          # explicit True/False wins
    try:
        should_update = bool(
            getattr(scene, "always_update_mobjects", False)
            or getattr(scene, "updaters", None)
            or wait.stop_condition is not None
            or any(mob.has_time_based_updater()
                   for mob in scene.get_mobject_family_members())
        )
    except Exception:
        should_update = True                            # be conservative: step it
    wait.is_static_wait = not should_update

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
        # [start, end) spans whose wait CE renders with freeze_current_frame --
        # computed in finalize(); inside them render_at holds the picture
        # instead of driving updaters (see _frozen_at).
        self._frozen_windows = []

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
        # Chronological order matters: manim's begin() captures the mobject's
        # CURRENT state as that animation's start, so an entry must see every
        # earlier entry already advanced to its own start time.  Capturing all
        # the start states up front (the previous order) made a later play on
        # the same mobject start from the scene's INITIAL state instead of
        # where its predecessor finished -- visible on the staggered schedule
        # `frames.FrameServer` builds (it records every play on one timeline),
        # where every play was rendered from the initial state.
        begun = []
        for entry in sorted(self._entries, key=lambda e: e["start"]):
            for prior in begun:
                evaluate_animation(prior["anim"],
                                   entry["start"] - prior["start"])
            anim = entry["anim"]
            if _is_manim_animation(anim):
                # manim's Scene.play() gives every animation its scene before
                # begin(): introducers register their mobject and .scene is
                # stored.  manim-native classes such as AddTextWordByWord read
                # it, so the timeline path has to do the same (lazy import: this
                # module is imported by vulkan_bind).
                from real_time_manim.window.scene import _setup_anim_scene
                _setup_anim_scene(anim, self.scene)
                anim.begin()          # manim's begin() takes no time argument
            else:
                anim.begin(0.0)       # our animations take an absolute start time
            # Phase 3: a manim-native animation writes no render channels of its
            # own, so install the adapter that derives them from its state.
            from real_time_manim.render.hooks import install_hooks
            install_hooks(anim)
            begun.append(entry)
        self.duration = max(
            (e["start"] + e["run_time"] for e in self._entries), default=0.0)
        self._frozen_windows = self._compute_frozen_windows()
        self._prepared = True
        return self

    def _compute_frozen_windows(self):
        """``[start, end)`` spans whose frames CE would ``freeze_current_frame``.

        CE freezes a wait ONLY when it is the play's single animation
        (``Scene.is_current_animation_frozen_frame`` -> the lone-Wait branch of
        ``compile_animation_data``); a Wait sharing the play with other
        animations goes through ``play_internal`` and steps normally.  Plays
        never overlap in time (each starts on the previous one's cursor), so
        "no other entry overlaps this span" is the schedule-level form of
        CE's lone-Wait rule and works for both the per-play timeline and the
        whole-scene schedule ``FrameServer`` builds.

        The eps absorbs float noise at the seams: a schedule entry's start is
        a cumulative sum and can sit ~1 ulp off the frame grid, while entries
        that are truly concurrent share the same start by construction, so
        1e-9 separates the two cases by a wide margin.
        """
        eps = 1e-9
        wins = []
        for e in self._entries:
            if e["run_time"] <= 0:
                continue
            anim = e["anim"]
            if not (_is_wait_animation(anim)
                    and getattr(anim, "is_static_wait", None) is True):
                continue
            a = e["start"]
            b = a + e["run_time"]
            concurrent = any(
                other is not e
                and other["start"] < b - eps
                and a + eps < other["start"] + other["run_time"]
                for other in self._entries)
            if not concurrent:
                wins.append((a, b))
        return wins

    def _frozen_at(self, t):
        """Whether ``t`` falls inside a frozen-wait window.

        The lower bound carries eps so a wait whose (cumulatively-summed)
        start lands ~1 ulp ABOVE its own first frame still freezes that
        frame.  The upper bound is EXACT so the first frame of a contiguous
        next entry is never swallowed -- and it matches ``ce_frame_count``'s
        ``int()`` cut, which is derived from the same end value: a lone play's
        last frame is always at least one full ``dt`` below ``end``.
        """
        for a, b in self._frozen_windows:
            if t >= a - 1e-9 and t < b:
                return True
        return False

    def prepare(self, *animations):
        """Convenience: schedule every animation at ``t = 0`` and finalize."""
        for anim in animations:
            self.add(anim, 0.0)
        return self.finalize()

    def stateful_names(self):
        return [type(e["anim"]).__name__ for e in self._entries if e["stateful"]]

    def evaluate(self, t, dt=0.0, drive=True):
        """Set every animation's mobjects to their state at time ``t`` (no draw).

        ``dt`` / ``drive`` mirror manim's per-animation updater pass (see
        :func:`drive_animation_updaters`): ``drive=False`` is what a *seek*
        passes, exactly like ``_drive_mobject_updaters`` -- updaters are
        stateful, so replaying them while jumping backwards would accumulate
        history the forward walk never had.
        """
        if not self._prepared:
            raise RuntimeError("call finalize()/prepare() first")
        # Every entry must write *something* at every t, so the result stays a
        # pure function of t (skipping the unstarted ones makes the frame depend
        # on which times were rendered before it -- see tests/test_frame_access).
        #
        # Reset pass: an entry that has not started yet must restore the
        # AUTHORED state of its mobjects.  With staggered starts its captured
        # start state is the accumulator from its predecessors, and writing that
        # before they have run would jump the picture ahead (at t=0 a chained
        # second play would already show the first play's END value).  Descending
        # start order, so the earliest-starting entry of a chain writes last:
        # with nothing started, the authored state is what must stand.
        for entry in sorted(self._entries, key=lambda e: e["start"],
                            reverse=True):
            if entry["start"] > t:
                evaluate_animation(entry["anim"], -1.0)   # clamps to alpha 0
        # Apply pass: the entries that have started, earliest first, so the one
        # that started last wins -- exactly manim's play-a-sequence semantics.
        # manim runs each animation's own updater pass BEFORE interpolating it
        # (`Scene.update_to_time`), so the copies `begin()` took advance first
        # and the interpolation then derives the mobject from that fresh state.
        for entry in sorted(self._entries, key=lambda e: e["start"]):
            if entry["start"] <= t:
                if drive:
                    drive_animation_updaters(entry["anim"], dt)
                evaluate_animation(entry["anim"], t - entry["start"])

    def _frame_duration(self):
        """Nominal seconds-per-frame of the walk currently rendering ``self``.

        CE's clock advances once per *written* frame (``CairoRenderer.add_frame``
        does ``self.time += num_frames * dt``), so the very first frame of a play
        counts one ``dt`` too.  ``Timeline`` is handed times, not frame rates, so
        the rate has to be recovered the same way ``PlayMixin._run_timeline``
        picks its own: a fast record runs at its configured rate, everything else
        at the engine's one supported rate (``TARGET_FPS``).  ``render_mp4``
        passes its explicit ``fps`` as ``render_at(..., frame_dt=...)``.
        """
        win = self.window
        fps = None
        if getattr(win, "_fast_record", False):
            fps = getattr(win, "_fast_record_fps", None)
        from real_time_manim.state import TARGET_FPS
        return 1.0 / float(fps or TARGET_FPS)

    def _advance_scene_time(self, amount):
        """Advance the renderer clock ``Scene.time`` reads (manim semantics).

        ``Scene.time`` is a read-only property over ``renderer.time``
        (``CairoRenderer.time``), which CE adds to on every emitted frame and
        RTM never touched -- so ``self.time`` stayed ``0.0`` for a whole scene
        (wiki 01-场景与相机/场景/01-Scene基础).  Scenes without a renderer
        clock (stubs) fall back to their own plain ``time`` attribute.
        """
        if not amount or amount <= 0:
            return
        scene = self.scene
        renderer = getattr(scene, "renderer", None)
        if renderer is not None and isinstance(
                getattr(renderer, "time", None), (int, float)):
            renderer.time = float(renderer.time) + float(amount)
            return
        if "time" in getattr(scene, "__dict__", {}):
            scene.time = float(scene.time) + float(amount)

    def stop_conditions(self, t=None):
        """Every scheduled ``Wait.stop_condition``, optionally only those whose
        span covers ``t`` (a condition guards the wait it was built with)."""
        eps = 1e-9
        conds = []
        for e in self._entries:
            cond = getattr(e["anim"], "stop_condition", None)
            if not callable(cond):
                continue
            if t is not None and not (e["start"] - eps <= t
                                      < e["start"] + e["run_time"]):
                continue
            conds.append(cond)
        return conds

    def poll_stop_conditions(self, t):
        """Evaluate the stop conditions covering ``t`` once; True = end the wait.

        CE's renderer checks ``stop_condition`` once per frame *after* writing
        that frame (``write_frame`` then ``if stop_condition(): break``), so a
        wait ends on the frame where the condition first turns true instead of
        running its full ``run_time``.  Forward walks only: a random-access
        ``render_at`` never polls (``stop_condition`` is a stateful,
        side-effecting callable), which is why seeking still follows the full
        schedule -- wiki 01-场景与相机/场景/03-播放与等待.

        A raising condition ends the wait rather than killing the render, the
        policy ``PlayMixin._run_timeline`` already applies to the live path.
        """
        for cond in self.stop_conditions(t):
            try:
                if cond():
                    return True
            except Exception:
                return True
        return False

    def render_at(self, t, readback=False, frame_dt=None):
        """Evaluate at ``t``, draw that state, and present it.  O(1) in ``t``.

        Order matters: the renderer draws whatever is queued, so the state at
        ``t`` must be queued (``sync``) *before* the frame is drawn (``tick``).
        Drawing first presents the previous call's state, which is what made a
        readback after ``render_at(t)`` return the previous frame.

        With ``readback=True`` the frame also copies itself into the readback
        buffer before it is presented, so a following read returns exactly this
        frame (see ``MLWindow.request_readback``).

        ``frame_dt`` overrides the frame duration used for the FIRST frame's
        contribution to ``Scene.time`` (see ``_advance_scene_time``); walks that
        know their own fps -- ``render_mp4`` -- pass it, everything else uses
        the window's rate.

        Returns False when the frame could not be drawn (window closed), True
        otherwise -- see the ``tick()`` call at the end.
        """
        first = self._last_t is None
        dt = 0.0 if (first or t <= self._last_t) else t - self._last_t
        # A frozen wait (CE's freeze_current_frame) holds the picture: no
        # updater pass at all, exactly like CE's frozen branch, which renders
        # one frame and repeats it WITHOUT ever calling Scene.update_mobjects.
        # Without this gate an explicit frozen_frame=True / self.pause() in a
        # scene with updaters kept stepping them, so the "frozen" pause moved.
        # The gate even swallows the first-frame re-anchor (dt=0): CE never
        # runs an updater pass inside a frozen window either.  `_last_t` still
        # advances, so the first frame after the window steps exactly one
        # frame of dt -- CE resumes updater time right where the wait ends.
        drive = not self._frozen_at(t) and (dt > 0.0 or first)
        # The gate has to be resolved BEFORE `evaluate`: the same `drive` now
        # also runs manim's per-animation updater pass, whose copies
        # (`starting_mobject` / `target_copy`) accumulate state just like the
        # scene mobjects do -- see `timeline.drive_animation_updaters`.
        self.evaluate(t, dt=dt if drive else 0.0, drive=drive)
        if drive:
            from real_time_manim.window.scene import _drive_mobject_updaters
            _drive_mobject_updaters(self.scene, dt)
        self._last_t = t
        self.window.sync(self.scene)
        if readback:
            self.window.request_readback()
        # tick() answers False when the window is gone (WM_QUIT): the frame was
        # NOT drawn, so the caller must stop walking the schedule instead of
        # capturing a picture of nothing.
        drawn = bool(self.window.tick())
        if drawn:
            # A9 -- CE advances ``Scene.time`` once per EMITTED frame
            # (``CairoRenderer.add_frame`` -> ``self.time += num_frames * dt``),
            # while RTM produced frames itself and never touched the renderer
            # clock, so ``scene.time`` stayed 0.0 forever (wiki 01-场景与相机/
            # 场景/01-Scene基础).  Order matters: this runs AFTER ``evaluate`` /
            # the updater pass above, exactly like CE, whose updaters see the
            # time as it stood before the frame was written.  The first frame of
            # a schedule still counts one frame (``frame_dt``/``_frame_duration``)
            # because CE counts frame 0 too; a backwards or repeated ``t`` (dt 0)
            # adds nothing, just like re-writing a frame at the same instant.
            self._advance_scene_time(
                (float(frame_dt) if frame_dt else self._frame_duration())
                if first else dt)
        return drawn

    def screenshot_at(self, t, path):
        self.render_at(t, readback=True)
        return self.window.screenshot(path)

    def render_mp4(self, path, fps=60, duration=None, realtime=False):
        """Render the whole schedule forward to ``path`` (mp4) by walking ``t``
        and drawing each frame — the same ``evaluate(t)`` path that powers
        ``render_at``.  With ``realtime=True`` it paces to wall-clock (for a live
        window); otherwise it runs as fast as it can (like a fast record).

        A scheduled ``Wait.stop_condition`` is polled once per drawn frame (the
        same timing as CE's renderer and as ``PlayMixin._run_timeline``) and
        ends the walk early, so a ``wait_until``-style wait writes only the
        frames up to the one where its condition first fired.
        """
        import os
        import shutil
        import subprocess
        import tempfile
        import time

        duration = float(self.duration if duration is None else duration)
        anims = [e.get("anim") for e in getattr(self, "_entries", [])]
        n_frames = ce_frame_count(anims, duration, fps)
        frame_dt = 1.0 / float(fps)
        tmpdir = tempfile.mkdtemp(prefix="rtm_timeline_")
        # Only frames that were actually drawn may go to ffmpeg: a closed
        # window makes ``render_at`` answer False, and looping on would have
        # muxed `n_frames` pictures out of the handful that ever existed.
        from real_time_manim.window.paint_order import native_dll_is_live
        live = native_dll_is_live(self.window.dll)
        written = 0
        try:
            for k in range(n_frames):
                t = k / float(fps)
                frame_start = time.perf_counter()
                if not self.render_at(t, readback=True, frame_dt=frame_dt) and live:
                    break
                self.window.screenshot(os.path.join(tmpdir, f"f_{k:05d}.bmp"))
                written += 1
                # A condition that fires on THIS frame ends the walk now, the
                # frame that fired is still written (CE writes then checks).
                if self.poll_stop_conditions(t):
                    break
                if realtime:
                    left = (1.0 / fps) - (time.perf_counter() - frame_start)
                    if left > 0:
                        time.sleep(left)
            subprocess.run(
                ["ffmpeg", "-y", "-loglevel", "error",
                 "-framerate", str(fps),
                 "-i", os.path.join(tmpdir, "f_%05d.bmp"),
                 "-frames:v", str(written),
                 "-c:v", "libx264", "-pix_fmt", "yuv420p", path],
                check=True)
        finally:
            shutil.rmtree(tmpdir, ignore_errors=True)
        return path
