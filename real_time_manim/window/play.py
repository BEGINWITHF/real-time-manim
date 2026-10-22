"""The play loop, the timeline renderer and the legacy manim play path."""

import datetime
import os
import time
import numpy as np
from manim import (
    Text, VGroup, Group, OUT
)
from manim.animation.transform import Transform as _ManimTransform
from manim.animation.transform import FadeTransform as _ManimFadeTransform

from real_time_manim.animations import (
    Create, DrawBorderThenFill, Write, Succession, Wait, Add, AnimationGroup, Indicate,
    FadeIn, FadeOut, FadeTransform, Rotating, Rotate,
    Transform, TransformMatchingAbstractBase, GrowArrow, ShowPassingFlash, set_anim_opacity, set_anim_rotation, get_anim_rotation,
    clear_anim_rotation_delta,
    TARGET_FPS, FRAME_DURATION,
)
from real_time_manim.window.paint_order import (
    foreground_to_front,
    native_dll_is_live,
    release_flash_window,
    release_split,
)
from real_time_manim.window.scene import _drive_mobject_updaters, _setup_anim_scene


# ---------------------------------------------------------------------------
# play-level keywords (A34)
# ---------------------------------------------------------------------------

#: The play-level keywords RTM's ``win.play`` actually implements.
#:
#: manim's ``Scene.play`` forwards ``**kwargs`` to
#: ``Scene.compile_animations``, which ``setattr``\ s them onto every
#: animation -- ``win.play(anim, lag_ratio=.5)`` therefore *does* something in
#: CE.  RTM only mirrors ``run_time`` / ``rate_func``, and every other keyword
#: used to vanish without a word.  ``_warn_unsupported_play_kwargs`` now names
#: what it dropped instead of pretending it never arrived.
#:
#: The ``path_*`` family is in here because RTM *does* honour it: manim's
#: ``Scene.compile_animations`` ends with a ``setattr(animation, k, v)`` loop
#: over every play kwarg, and ``LinearTransformationScene.apply_matrix`` and
#: friends push the arc they computed through ``play(...)`` instead of the
#: animation constructor (``vector_space_scene.py:1212-1217``).  They are
#: applied by :func:`_forward_path_kwargs` below.
PATH_PLAY_KWARGS = ("path_arc", "path_arc_axis", "path_arc_centers",
                    "path_func")

SUPPORTED_PLAY_KWARGS = ("run_time", "rate_func") + PATH_PLAY_KWARGS


def _forward_path_kwarg(anim, name, value):
    """Put one play-level ``path_*`` kwarg on ``anim`` the way its class reads it.

    Two ``Transform`` implementations are in play and they store the arc
    differently:

    * manim's own (what ``ApplyPointwiseFunction`` / ``Transform`` /
      ``LinearTransformationScene`` build): ``path_arc`` is a *property* whose
      setter rebuilds ``path_func`` and ``path_func`` is a property with a
      setter -- a plain ``setattr`` is exactly what CE relies on
      (``Scene.compile_animations``).
    * RTM's own (``real_time_manim.animations.transform``): the values live in
      ``_path_arc`` / ``_path_arc_axis`` / ``_path_arc_centers`` / ``_path_func``
      and the public ``path_func`` is a read-only property derived lazily from
      them, so the public name would be inert.

    Anything without either shape (``FadeIn`` ...) takes the plain attribute,
    which is inert -- identical to CE.
    """
    descriptor = getattr(type(anim), name, None)
    if isinstance(descriptor, property):
        if descriptor.fset is not None:
            setattr(anim, name, value)          # manim's Transform: rebuilds path_func
        else:
            setattr(anim, "_" + name, value)    # RTM's read-only path_func property
        return
    if hasattr(anim, "_" + name):
        setattr(anim, "_" + name, value)        # RTM's own Transform keeps it private
        return
    setattr(anim, name, value)


def _forward_path_kwargs(anims, kwargs):
    """Apply every ``path_*`` play kwarg to ``anims`` (manim parity)."""
    for name in PATH_PLAY_KWARGS:
        if name not in kwargs:
            continue
        value = kwargs[name]
        for anim in anims:
            try:
                _forward_path_kwarg(anim, name, value)
            except Exception:                   # pragma: no cover - defensive
                pass


def print_warning(text):
    """Print an RTM warning, surviving a stdout that cannot encode it.

    The messages carry a Chinese hint (matching the wiki's wording), and a
    redirected stdout on Windows may be cp1252/cp936 -- a bare ``print`` would
    then raise ``UnicodeEncodeError`` out of the middle of a play.  Fall back
    to an ASCII rendering of the same message instead.
    """
    try:
        print(text)
    except UnicodeEncodeError:                          # pragma: no cover
        print(text.encode("ascii", "backslashreplace").decode("ascii"))


def _warn_unsupported_play_kwargs(kwargs, known=SUPPORTED_PLAY_KWARGS,
                                  method="win.play"):
    """Print a warning naming the play-level keywords RTM ignored (gap A34).

    Nothing is applied -- RTM has never implemented play-level keywords beyond
    ``run_time`` / ``rate_func``, and silently ``setattr``-ing arbitrary names
    onto animations would be a behaviour change.  The warning only makes the
    drop visible so a ``lag_ratio=`` written at play level is not mistaken for
    a working parameter.
    """
    unknown = sorted(str(k) for k in (kwargs or {}) if k not in known)
    if not unknown:
        return
    listed = ", ".join(f"{k!r}" for k in unknown)
    print_warning(
        f"[RTM] {method}(): unsupported keyword(s) {listed} ignored "
        "-- RTM 不支持该参数: only "
        f"{', '.join(SUPPORTED_PLAY_KWARGS)} are honoured at play level; "
        "pass the rest to the animation constructor instead "
        "(e.g. Create(sq, lag_ratio=...))."
    )


# ---------------------------------------------------------------------------
# subcaptions (A6)
# ---------------------------------------------------------------------------
#
# manim writes ``play(..., subcaption=...)`` through its file writer
# (``Scene.add_subcaption`` -> ``file_writer.subcaptions`` -> ``finish()``
# writes the ``.srt``).  RTM never runs a file writer, so the entries went
# nowhere: the three parameters were not even accepted by ``win.play`` and
# landed in ``**kwargs``, where they were dropped.
#
# RTM therefore collects them in memory -- a flat per-run store in this module,
# mirrored onto the window that played them -- and exports the result with
# :func:`export_srt`.  The window mirror alone would not do: ``close()``
# unregisters the window, and a recording closes it BEFORE ``record._run``
# reaches the export step.  The clock is the window's ``_cursor`` -- the
# recorded-timeline position audio_track uses for ``Scene.add_sound`` --
# because manim's own clock, ``Scene.time``, never advances under RTM.

_SUBCAPTION_ATTR = "_rtm_subcaptions"

# The authoritative store: a flat list of the cues collected this run.
#
# It lives here rather than ONLY on the window because ``MLWindow.close()``
# unregisters the window from ``MLWindow._registry`` -- and a recording closes
# its window BEFORE ``record._run`` gets to the export step, so a registry walk
# would find nothing to write.  Each cue is additionally mirrored onto the
# window that played it (a per-window view, useful for inspection and for
# exporting a single window's cues explicitly).
_SUBCAPTIONS = []


def _subcaption_store(window, create=False):
    """The live per-window mirror of subcaption entries."""
    store = getattr(window, _SUBCAPTION_ATTR, None)
    if store is None:
        if not create:
            return []
        store = []
        try:
            setattr(window, _SUBCAPTION_ATTR, store)
        except Exception:
            return []
    return store


def record_subcaption(window, content, start, duration):
    """Remember one subcaption (in memory) for the current run.

    ``start`` / ``duration`` are seconds on the recorded timeline; ``window`` is
    the window that played the cue (its per-window mirror keeps a copy).  The
    return value is the stored ``{"content", "start", "duration"}`` dict.
    """
    entry = {
        "content": str(content),
        "start": float(start),
        "duration": max(float(duration), 0.0),
    }
    _SUBCAPTIONS.append(entry)
    if window is not None:
        _subcaption_store(window, create=True).append(entry)
    return entry


def _all_windows():
    """Every window still registered (``close()`` unregisters it)."""
    try:
        from real_time_manim.window import MLWindow
    except Exception:                                  # pragma: no cover
        return []
    return list(getattr(MLWindow, "_registry", ()) or ())


def collect_subcaptions(windows=None):
    """All collected subcaptions, sorted by start time.

    ``windows=None`` returns the run's flat store -- what the record-end export
    wants, since the recorder only knows output paths and the windows are
    already closed by then.  Passing ``windows=[...]`` collects from those
    windows' per-window mirrors instead.
    """
    entries = []
    if windows is None:
        entries.extend(_SUBCAPTIONS)
    else:
        for window in windows:
            entries.extend(_subcaption_store(window))
    return sorted(entries, key=lambda e: (e["start"], e["duration"]))


def clear_subcaptions(windows=None):
    """Drop collected subcaptions (fresh recording run).

    ``windows=None`` clears the flat store plus every registered window's
    mirror; an explicit ``windows`` list clears only those mirrors.
    """
    if windows is None:
        _SUBCAPTIONS.clear()
        windows = _all_windows()
    for window in windows:
        store = _subcaption_store(window)
        if store:
            store.clear()


def _format_srt_time(seconds):
    """``HH:MM:SS,mmm`` -- the SRT timestamp format."""
    if seconds < 0:
        seconds = 0.0
    total_ms = int(round(seconds * 1000))
    hours, rem = divmod(total_ms, 3_600_000)
    minutes, rem = divmod(rem, 60_000)
    secs, ms = divmod(rem, 1000)
    return f"{hours:02d}:{minutes:02d}:{secs:02d},{ms:03d}"


def compose_srt(entries):
    """Compose ``.srt`` text from ``{"content", "start", "duration"}`` dicts.

    Uses manim's own ``srt`` library when importable, so the bytes match what
    ``SceneFileWriter.write_subcaption_file`` would have produced; a small
    hand-rolled formatter covers the (unlikely) case where it is missing.
    """
    ordered = sorted(entries, key=lambda e: (float(e["start"]),
                                             float(e["duration"])))
    try:
        import srt
    except Exception:                                  # pragma: no cover
        srt = None
    if srt is not None:
        try:
            subtitles = [
                srt.Subtitle(
                    index=i,
                    content=str(e["content"]),
                    start=datetime.timedelta(seconds=float(e["start"])),
                    end=datetime.timedelta(seconds=float(e["start"])
                                            + float(e["duration"])),
                )
                for i, e in enumerate(ordered, start=1)
            ]
            return srt.compose(subtitles)
        except Exception:                              # pragma: no cover
            pass
    # Fallback formatter (SRT is three lines plus a blank line per cue).
    blocks = []
    for i, e in enumerate(ordered, start=1):
        start = float(e["start"])
        end = start + float(e["duration"])
        blocks.append(
            f"{i}\n{_format_srt_time(start)} --> {_format_srt_time(end)}\n"
            f"{e['content']}\n"
        )
    return "\n".join(blocks)


def export_srt(path, entries=None, windows=None, verbose=False):
    """Write the collected subcaptions to ``path`` as ``.srt``.

    Returns the path written, or ``None`` when there is nothing to write (no
    file is created then -- an empty ``.srt`` would only clutter the output
    directory).

    ``entries`` overrides the collection; ``windows=None`` collects the run's
    flat store (see :func:`collect_subcaptions`), which outlives the windows
    themselves -- ``MLWindow.close()`` unregisters them, and a recording closes
    its window before this runs.

    Record end: ``record._run`` calls ``audio_track.apply_sounds(files)`` at
    the end of *every* recording run, and that function calls this one -- so a
    recorded scene that used ``play(..., subcaption=...)`` gets its ``.srt``
    next to the MP4 automatically, without ``record.py`` (owned by another
    session) having to change.
    """
    if entries is None:
        entries = collect_subcaptions(windows)
    entries = sorted(entries, key=lambda e: (float(e["start"]),
                                             float(e["duration"])))
    if not entries:
        return None
    text = compose_srt(entries)
    with open(path, "w", encoding="utf-8", newline="\n") as fh:
        fh.write(text)
    if verbose:
        print(f"[srt] wrote {len(entries)} subcaption(s) -> {path}")
    return str(path)


class PlayMixin:

    def tick(self):
        self.frame_count += 1
        result = self.dll.Vulkan_Tick()
        if result == 0:
            return False
        self.win_w = (result >> 16) & 0xFFFF
        self.win_h = result & 0xFFFF
        return True

    def _extract_add_mobjects(self, anim, _nested=False):
        mobjects = []
        if isinstance(anim, Add):
            for mob in anim.mobjects:
                # A nested Add (inside Succession/AnimationGroup) must stay
                # hidden until its own slot runs: CE only lets the mobject
                # enter when the sub-animation begins, so forcing it visible
                # at play start would show every queued mobject at once.
                # Add.interpolate flips opacity back to 1 when the slot
                # activates; a direct top-level Add is instant, so it must
                # stay visible.
                mob._rtm_deferred_add = _nested
                if _nested:
                    set_anim_opacity(mob, 0.0)
                mobjects.append(mob)
        elif isinstance(anim, Succession):
            for sub in anim.animations:
                mobjects.extend(self._extract_add_mobjects(sub, _nested=True))
        elif isinstance(anim, AnimationGroup):
            for sub in anim.animations:
                mobjects.extend(self._extract_add_mobjects(sub, _nested=True))
        return mobjects

    def _ensure_animated_present(self, real_anims, add_mobs=()):
        """Mirror ``Scene.add_mobjects_from_animations``'s membership rule.

        A mobject already somewhere in the scene's FAMILY -- a graph vertex
        that is a submobject of its ``Graph``, a ``Text`` glyph -- must NOT be
        re-appended to the top level: ``Scene.add`` would ``restructure`` it
        out of its parent and drag it to the end, inverting the paint order
        against CE.  CE checks membership against the whole family
        (``mob not in self.get_mobject_family_members()``), so an animated
        submobject is left exactly where it is; only a genuinely-new mobject
        is appended.  This used to check only ``scene.mobjects`` (the top
        level), which promoted any animated submobject to the end and made
        ``who-is-on-top`` diverge from CE.

        Returns True if anything was appended (callers then re-apply CE's
        ``foreground_mobjects``-go-last rule, which those bypassed ``Scene.add``
        appends would otherwise skip).
        """
        appended = False

        for mob in add_mobs:
            # Deferred (nested) Adds stay hidden at registration; their own
            # Add.interpolate turns them visible when the slot activates.
            set_anim_opacity(
                mob, 0.0 if getattr(mob, "_rtm_deferred_add", False) else 1.0)
            if mob not in self.scene.mobjects:
                self.scene.mobjects.append(mob)
                appended = True

        curr_mobjects = self.scene.get_mobject_family_members()
        # Appends go through Scene.add, not a bare list append: CE's add
        # restructures first, pulling any already-top-level FAMILY member out
        # of the list before the new root goes on the end.  Without that
        # absorb, `scene.add(eq1)` + `play(FadeOut-ish anim on Group(eq1, ...))`
        # leaves eq1 top-level as well as inside the Group, so
        # clean_up_from_scene removes only the Group and eq1's parts stay in
        # the scene forever -- TransformMatchingTex's "old letters never left"
        # after every match.  The family-membership guard above already skips
        # mobjects that are merely submobjects, which is the case where CE's
        # restructure would have restructured them out of their parent; what
        # reaches the add here is genuinely new at the top level, exactly
        # where CE absorbs-and-appends too.
        for a in real_anims:
            m = getattr(a, "mobject", None)
            if m is not None and m not in curr_mobjects:
                self.scene.add(m)
                curr_mobjects += m.get_family()
                appended = True
            for mob in (getattr(a, "mobjects", None) or []):
                if mob not in curr_mobjects:
                    self.scene.add(mob)
                    curr_mobjects += mob.get_family()
                    appended = True
            cur = getattr(a, "cursor", None)
            if cur is not None and cur not in curr_mobjects:
                self.scene.add(cur)
                curr_mobjects += cur.get_family()
                appended = True
            # A grouped animation carries its mobjects on the CHILDREN, not on
            # itself (AnimationGroup has no ``.mobject``/``.mobjects``).  A
            # page-swap ``AnimationGroup(FadeOut(old), FadeIn(new1, new2))``
            # therefore presented nothing here: the fade-in targets are not
            # pre-added to the scene (FadeIn is an introducer), and with no
            # recursion the whole "换上" half never entered the scene.  Walk one
            # level into the group's children and present each child's mobjects;
            # already-present ones (the FadeOut source) are skipped by the guard.
            for child in (getattr(a, "animations", None) or []):
                cm = getattr(child, "mobject", None)
                if cm is not None and cm not in curr_mobjects:
                    self.scene.add(cm)
                    cm_family = cm.get_family()
                    curr_mobjects += cm_family
                    appended = True
                for cmob in (getattr(child, "mobjects", None) or []):
                    if cmob not in curr_mobjects:
                        self.scene.add(cmob)
                        curr_mobjects += cmob.get_family()
                        appended = True

        return appended

    def _present_detached_animated(self, real_anims):
        """Present sub-animation copies the scene tree cannot reach.

        RTM paints the SCENE tree only.  A few animations drive a copy that
        is neither in the scene nor reachable from it: the
        TransformMatching* fade-in target copy (``_fade_target_copy``) and
        FadeTransform's morph ghost (``_ghost``) -- and, nested, the ghost
        of every piece of a FadeTransformPieces.  The legacy pipeline added
        exactly these (see ``_play_legacy``); the timeline migration
        dropped them, so the copies never rendered: unmatched target parts
        stayed invisible until clean_up_from_scene popped them in, and the
        FadeTransform ghost never showed at all ("act" instead of "hat").

        Called AFTER ``Timeline.finalize()``, which is where begin() runs
        and TMA creates its target copy.  Their clean_up implementations
        already remove the presented copies again.

        Returns True if anything was appended.
        """
        appended = False
        curr_mobjects = self.scene.get_mobject_family_members()

        def visit(anim):
            nonlocal appended, curr_mobjects
            extras = []
            ghost = getattr(anim, '_ghost', None)
            if ghost is not None:
                extras.append(ghost)
            ftc = getattr(anim, '_fade_target_copy', None)
            if ftc is not None:
                extras.append(ftc)
            # The key_map branch needs no entry of its own: it builds CE's
            # FadeTransformPieces, and `visit` recurses into the group's
            # children below, so each piece's `_ghost` is presented by the
            # `_ghost` lookup above (it used to build a detached VGroup of
            # copies instead, which is what `_key_mapped_copies` was for).
            for mob in extras:
                if mob not in curr_mobjects:
                    # Scene.add, so CE's absorb + foreground-to-front apply.
                    self.scene.add(mob)
                    curr_mobjects += mob.get_family()
                    appended = True
            for sub in (getattr(anim, '_anims', None)
                        or getattr(anim, 'animations', None) or ()):
                visit(sub)

        for a in real_anims:
            visit(a)
        return appended

    def _validate_play_run_time(self, anims):
        """Validate a play's aggregate run_time the way manim's Scene.play does.

        Mirrors ``Scene.get_run_time`` -> ``Scene.validate_run_time``: the
        effective run_time of a play is the MAX across its animations.  A
        non-positive run_time raises ValueError (nothing could be rendered);
        a run_time shorter than one frame is clamped up to one frame and warns,
        so a near-zero animation still emits a frame instead of vanishing.

        The scene carries the validator (manim ``Scene`` classmethod); the
        frame rate comes from manim ``config``.  Both reads are defensive so a
        bare stub scene or a stripped config degrades to a no-op rather than
        crashing playback.
        """
        if not anims:
            return
        try:
            rts = [float(getattr(a, "run_time", 0.0) or 0.0) for a in anims]
        except (TypeError, ValueError):
            return
        if not rts:
            return
        total = max(rts)
        validate = getattr(self.scene, "validate_run_time", None)
        if not callable(validate):
            return
        try:
            validate(total, self.play, "total run_time")
        except ValueError:
            # A non-positive run_time: re-raise CE's own clear message.
            raise
        except Exception:
            return

    def _register_play_subcaption(self, content, start_cursor,
                                  duration=None, offset=0):
        """Collect one ``play(..., subcaption=...)`` cue in memory (gap A6).

        manim's ``Scene.play`` stamps the cue at "play start + subcaption_offset"
        and defaults its duration to the play's *actual* run time -- both are
        reproduced here with the window's recorded-timeline cursor as the clock
        (manim's own clock, ``Scene.time``, never advances under RTM, which is
        why calling ``Scene.add_subcaption`` directly still places every cue at
        t=0).

        Nothing is rendered or written here; :func:`export_srt` turns the store
        into an ``.srt`` (automatically at record end, see that function), from
        the flat per-run store this records into -- the per-window mirror is
        only a view, because ``close()`` unregisters the window.
        """
        if not content:
            return
        start = float(start_cursor) + float(offset or 0.0)
        if duration is None:
            # What the play really consumed: a wait_until that stopped early
            # reports its real elapsed time through the cursor.
            duration = (float(getattr(self, "_cursor", 0.0) or 0.0)
                        - float(start_cursor))
        return record_subcaption(self, content, start, duration)

    def play(self, *animations, subcaption=None, subcaption_duration=None,
             subcaption_offset=0, **kwargs):
        """Timeline-driven playback (2.0.0).

        Animations are scheduled on one Timeline and every frame is produced by
        evaluating that schedule at time ``t`` -- the same O(1) ``render_at``
        path that powers seeking.  The legacy fork-aware pipeline is preserved
        as :meth:`_play_legacy` for reference during the migration.

        ``subcaption`` / ``subcaption_duration`` / ``subcaption_offset`` are
        manim's ``Scene.play`` signature: the cue is collected in memory on this
        window (default duration = the play's run_time) and written out as
        ``.srt`` by :func:`export_srt`.  Unrecognised ``**kwargs`` print a
        warning instead of vanishing (gap A34).
        """
        if not self.scene:
            # Silently returning here produced a 0-frame / 262-byte video when
            # the user forgot ``win.scene = self``: no exception, no warning,
            # just an empty file after a full render (audit
            # ``unbound_window_fast_record``).  Fail loudly instead.
            raise RuntimeError(
                "win.play() called before the scene was bound: run "
                "`win.scene = self` inside construct(), or pass the scene "
                "explicitly; without it RTM has nothing to draw or record."
            )

        _warn_unsupported_play_kwargs(kwargs)

        # CE's ``Scene.play`` rejects a bare Mobject ("Unexpected argument X
        # passed to Scene.play()"): only animations and ``.animate`` builders are
        # accepted.  Check before schedule mode too, so FrameServer recordings
        # fail the same way instead of silently scheduling nothing.
        from manim.mobject.mobject import Mobject as _Mobject
        for _a in animations:
            if isinstance(_a, _Mobject):
                raise TypeError(
                    "Unexpected argument %s passed to MLWindow.play(): pass an "
                    "Animation or a .animate(...) builder (or Scene.add() the "
                    "mobject first)." % type(_a).__name__
                )

        # Position of this play on the recorded timeline: the clock a subcaption
        # is stamped with (recorded before anything advances it below).
        start_cursor = float(getattr(self, "_cursor", 0.0) or 0.0)

        if type(self)._schedule_mode:
            self._schedule_play(animations, kwargs)
            self._register_play_subcaption(subcaption, start_cursor,
                                           subcaption_duration,
                                           subcaption_offset)
            return

        from real_time_manim.timeline import Timeline
        from manim.mobject.mobject import _AnimationBuilder

        # resolve .animate builders
        resolved = []
        for anim in animations:
            if isinstance(anim, _AnimationBuilder):
                # CE parity: manim's `_AnimationBuilder.build()` leaves
                # `suspend_mobject_updating` at its DEFAULT, so
                # `Animation.begin()` calls `mobject.suspend_updating()` and the
                # animated mobject's own updaters are OFF for the whole play
                # (`Mobject.update` returns early) while `Scene.update_to_time`
                # still advances the copies `begin()` took.  Forcing it False
                # here made RTM apply an EXTRA `group.rotate(-0.3)` every frame
                # on top of those copies, putting the animation exactly one
                # frame AHEAD of CE (measured on the wiki
                # `03-动画/更新器动画/01b-更新工具与自动变化` TracedPath sample:
                # RTM[k] == CE[k+1], max |Δ| 0.198 scene units).  Dropping the
                # override reproduces manim's own loop to the bit
                # (|CE-RTM| max = 0.0000 over 120 frames).
                resolved.append(anim.build())
            else:
                resolved.append(anim)
        animations = tuple(resolved)

        # Add() only makes mobjects visible; it is not a timed animation.
        add_mobs = []
        for anim in animations:
            add_mobs.extend(self._extract_add_mobjects(anim))
        real_anims = [a for a in animations if not isinstance(a, Add)]

        # manim resolves a lone Wait's frozen-vs-stepping decision inside its
        # renderer, which RTM replaces -- so do it here, before the timeline is
        # built, because it decides whether the wait is counted int() or ceil().
        from real_time_manim.timeline import resolve_static_wait
        resolve_static_wait(self.scene, real_anims)

        # shared kwargs
        if 'run_time' in kwargs:
            for a in real_anims:
                a.run_time = kwargs['run_time']
        if 'rate_func' in kwargs:
            for a in real_anims:
                a.rate_func = kwargs['rate_func']
        # manim's `Scene.compile_animations` finishes with
        # ``for animation in animations: for k, v in kwargs.items(): setattr(...)``,
        # so EVERY play kwarg reaches EVERY animation.  For the `path_*` family
        # that is load-bearing: `LinearTransformationScene.apply_transposed_matrix`
        # computes the transformation's net rotation and passes it as
        # ``play(..., path_arc=...)``, and manim's `Transform.path_arc` setter
        # turns it into `path_func` -- the circular interpolation path.  RTM only
        # forwarded run_time/rate_func, so the arc was dropped and the number
        # plane interpolated in a straight line: measured on wiki
        # 01-场景与相机/专用场景 `05-线性变换场景-apply.mp4` f40 the grid line
        # that starts at y=3 sits at y=3.144 in CE (the arc lifts |y| by 4.8 %,
        # matching a direct point-level probe) but stayed at 3.000 in RTM --
        # mean|diff| 4.08 with 172 frames over 4.0.
        _forward_path_kwargs(real_anims, kwargs)

        # manim's Scene.play validates the total run_time via
        # ``Scene.get_run_time`` -> ``Scene.validate_run_time`` before it ever
        # renders: a ``run_time`` of 0 or less raises a clear ValueError, and a
        # run_time shorter than one frame is clamped up to a frame with a
        # warning.  RTM replaced ``Scene.play`` with this method and never
        # called the validator, so ``win.play(FadeIn(sq), run_time=0)`` silently
        # produced nothing instead of the friendly error CE gives (the wiki
        # ``03-播放与等待`` documents this as a missing diagnostic).
        #
        # manim's ``wait``/``pause``/``wait_until`` already self-validate before
        # delegating to ``self.play``, so only a DIRECT play() call reaches here
        # unvalidated -- validating the aggregate (max) run_time mirrors
        # ``Scene.get_run_time`` exactly.
        self._validate_play_run_time(real_anims)

        appended = self._ensure_animated_present(real_anims, add_mobs)

        # CE's Scene.add drags foreground_mobjects back to the front on every
        # add; these appends bypass Scene.add, so re-apply that rule here.
        if appended:
            foreground_to_front(self.scene)

        tl = Timeline(self, self.scene)
        for a in real_anims:
            tl.add(a, 0.0)
        tl.finalize()
        # finalize() ran begin(), which is where the sub-animations create
        # their detached copies (TMA's fade-in target copy, FadeTransform's
        # ghost).  Present them now so the paint walk can reach them.
        self._present_detached_animated(real_anims)

        elapsed = self._run_timeline(tl, real_anims)
        # `_cursor` is "the current end of the recorded timeline" and the
        # playhead audio_track uses for Scene.add_sound placement.  Schedule
        # mode advances it in _schedule_play; this timeline path used to leave
        # it at 0.0, so every mid-scene add_sound piled up at its bare
        # time_offset instead of at the moment it was called.
        #
        # Advance by the MEDIA time (frames actually written / fps), not the
        # nominal `tl.duration`: the two differ whenever a play's duration is
        # not a frame multiple (frozen waits round down, animations round up),
        # and using the nominal value made audio/subtitles drift against the
        # video by the remainder of every play.
        advance = elapsed
        if advance is None:
            advance = getattr(self, "_last_run_media_time", None)
        if advance is None:
            advance = getattr(tl, "duration", 0.0) or 0.0
        self._cursor += float(advance)

        # manim adds the subcaption AFTER the play has run, deriving its start
        # from the time the play began -- mirrored here (cursor already
        # advanced, so the default duration falls out of the delta above).
        self._register_play_subcaption(subcaption, start_cursor,
                                       subcaption_duration, subcaption_offset)

    def _run_timeline(self, tl, anims=None):
        """Walk a finalized Timeline forward, drawing and capturing each frame.

        The frame count comes from ``timeline.ce_frame_count`` so a recording has
        exactly as many frames as manim would emit for the same play -- ceil for an
        animation, truncation for a wait.  Rounding both to nearest drifted by a
        frame per segment.
        """
        from real_time_manim.timeline import (
            _is_manim_animation,
            _is_wait_animation,
            ce_frame_count,
            evaluate_animation,
        )
        # Live playback paces at the renderer's one supported rate, the same
        # `FRAME_DURATION` `_play_legacy` sleeps on.  This used to be a bare
        # `30`, so the timeline path ran a play at HALF the rate the legacy
        # path -- and half the rate the class documents ("exactly ONE output
        # format: 1920x1080 at 60 fps") -- which halved the frames a live play
        # showed and made the two paths disagree about how long a given
        # `run_time` took on screen.  Fast-record keeps its own configurable
        # rate, since that is what the encoder was told.
        fps = self._fast_record_fps if self._fast_record else TARGET_FPS
        dt = 1.0 / fps
        if anims is None:
            anims = [e.get("anim") for e in getattr(tl, "_entries", [])]
        n_frames = ce_frame_count(anims, tl.duration, fps)

        if self._fast_record:
            self._fast_record_sim_time = time.time()
            self._last_frame_time = self._fast_record_sim_time - dt

        seg = getattr(self, '_fast_record_segment', None) if self._fast_record else None
        # ``wait_until(stop_condition)``: find the condition (if any) so the
        # frame loop can end the wait as soon as it fires.  manim's renderer
        # stores ``Scene.wait``'s ``stop_condition`` on the renderer and checks
        # it after every written frame; RTM receives the very same manim ``Wait``
        # object (carrying ``.stop_condition``) through ``win.play``.  Without
        # this check a ``wait_until(cond, max_time=0.3)`` always ran its full
        # ``max_time`` even when ``cond`` was already true -- the wiki
        # ``03-播放与等待`` documents that as a missing feature.
        stop_cond = None
        for a in anims:
            cand = getattr(a, "stop_condition", None)
            if cand is not None and callable(cand):
                stop_cond = cand
                break
        # CE's frozen branch (is_current_animation_frozen_frame) renders the
        # wait via update_frame + freeze_current_frame and SKIPS
        # play_internal -- whose last act is Scene.update_mobjects(0) -- so
        # after a frozen wait CE runs no updater pass at all.  The trailing
        # dt=0 re-anchor at the end of this method therefore applies to every
        # play EXCEPT a lone frozen wait (a stop_condition wait is dynamic by
        # definition and keeps it).
        frozen_wait = (len(anims) == 1
                       and _is_wait_animation(anims[0])
                       and getattr(anims[0], "is_static_wait", None) is True)
        stop_elapsed = None
        for k in range(n_frames):
            frame_start = time.time()
            # `idx` is only meaningful while fast-recording (a stand-in window
            # has no frame counter at all), so it stays inside that branch.
            in_segment = True
            if self._fast_record:
                idx = self._fast_record_frame_idx
                # Segment rendering: only frames in [seg[0], seg[1]) are
                # CAPTURED.  `_play_legacy` has always applied this rule;
                # `_run_timeline` ignored `_fast_record_segment` outright, so a
                # segment render walked the whole schedule and wrote every frame
                # from 0 -- the ffmpeg step then encoded the full play instead of
                # the requested slice.
                #
                # The animation state still advances on the skipped frames
                # (`render_at` -> `evaluate(t)` + the updater walk), so a later
                # in-segment frame sees exactly the state it would have seen had
                # the whole schedule been drawn: that is what `_play_legacy` does
                # too -- it drives the updaters every frame and only gates the
                # draw/capture.
                if seg is not None and idx >= seg[1]:
                    break
                in_segment = seg is None or (seg[0] <= idx < seg[1])
            # Arm the readback BEFORE the draw: `SaveScreenshot` (fast-record's
            # frame capture, the live `start_record` worker, user screenshots)
            # only sees real pixels if the frame copied itself out while it
            # still owned the image -- see platform.c:663.  Without it every
            # capture silently fell back to `CopySwapchainImageToBuffer`, whose
            # content the spec leaves undefined after present (measured: stale
            # frames).  The live record worker polls `SaveScreenshot` from its
            # own thread and arms nothing, so the loop has to arm for it too.
            #
            # The kwarg is passed only when a capture really is due: a plain
            # live play needs no readback, and a stand-in timeline in the tests
            # implements the original no-argument signature.
            _want_readback = bool(self._fast_record or
                                  getattr(self, '_recording', False))
            if not (tl.render_at(k * dt, readback=True) if _want_readback
                    else tl.render_at(k * dt)):
                # tick() answered False: the window is gone, so stop instead of
                # capturing nothing.  Only a live native loader can mean that --
                # a stand-in DLL answers 0 to everything (see
                # ``native_dll_is_live``), and a stand-in window may carry no
                # loader at all.
                if native_dll_is_live(getattr(self, 'dll', None)):
                    break

            if self._fast_record:
                if in_segment:
                    if getattr(self, '_fast_record_count_only', False):
                        pass
                    elif getattr(self, '_fast_record_pipe_mode', True):
                        self._capture_screenshot_to_pipe()
                    else:
                        self.screenshot(os.path.join(
                            self._fast_record_path,
                            f"frame_{idx:06d}.bmp"))
                self._fast_record_frame_idx += 1
            else:
                self._capture_frame()
                elapsed = time.time() - frame_start
                if elapsed < dt:
                    time.sleep(dt - elapsed)

            # ``wait_until`` stop_condition: evaluate it once per frame AFTER
            # the frame is drawn, exactly like manim's renderer loop
            # (``write_frame`` then ``if stop_condition(): break``).  The wait
            # then ends on the frame where the condition first turns true
            # instead of always running its full ``max_time``.  This is
            # inherently forward-only: ``stop_condition`` is a stateful,
            # side-effecting callable, so the resolved end time is only known
            # while stepping forward (a random-access ``render_at`` into the
            # middle of the wait still follows the full-schedule timeline).
            if stop_cond is not None:
                try:
                    if stop_cond():
                        stop_elapsed = (k + 1) * dt
                        break
                except Exception:
                    # A raising condition stops the wait rather than killing the
                    # whole play mid-render; CE would propagate, but a partial
                    # clip beats losing the entire recording.
                    stop_elapsed = (k + 1) * dt
                    break

        for entry in tl._entries:
            anim = entry['anim']
            # manim's Scene.play_internal finishes before cleaning up:
            #
            #     for animation in self.animations:
            #         animation.finish()
            #         animation.clean_up_from_scene(self)
            #
            # clean_up_from_scene calls _on_finish, NOT finish(), so omitting it
            # here left every animated mobject permanently updating_suspended --
            # _drive_mobject_updaters then skipped it on every later frame, which
            # froze PolygonOnAxes for 47 frames (an always_redraw rectangle whose
            # ValueTracker kept animating but never reached the screen).  finish()
            # also applies interpolate(1), which ce_frame_count's exclusive arange
            # end never reaches on its own.
            if _is_manim_animation(anim) and hasattr(anim, "finish"):
                anim.finish()
            elif anim is not None and hasattr(anim, "interpolate"):
                # RTM's own animations take an *absolute* time, so manim's
                # finish() -> interpolate(1) does not apply to them -- but the
                # frame loop above is still an exclusive arange, so the last
                # frame lands just short of run_time.  Their final state was
                # therefore never evaluated: Create(VGroup) ended with
                # _vulkan_progress == 0.9973, and the per-submobject split
                # (``progress * num_subs - i``) amplifies that 0.27% by the
                # number of children -- the last child of a 30-element VGroup
                # drew only 92% of its outline.  Step to the exact end of the
                # segment, mirroring CE's finish().
                try:
                    evaluate_animation(
                        anim, float(getattr(anim, "run_time", 1.0) or 1.0))
                except Exception:
                    pass
                # ...and then run the class's own clean-up side effects.
                # manim's play_internal does ``animation.finish()`` for EVERY
                # animation; RTM only did it for manim-native ones, so every
                # finish-only behaviour vanished: Blink left the mobject hidden
                # for the rest of the scene (A06 missing circle),
                # TypeWithCursor/UntypeWithCursor ignored
                # ``leave_cursor_on=False``, SpinInFromNothing kept
                # ``_grow_rot`` forever and Write kept ``_write_active`` on
                # every glyph.  RTM's ``Animation.finish`` only flags the
                # animation, so calling it here is safe; the /GrowFrom*/ crash
                # that would otherwise surface is fixed in grow_from_center.py.
                finish = getattr(anim, "finish", None)
                if callable(finish):
                    try:
                        finish()
                    except Exception:
                        pass
            if hasattr(anim, 'clean_up_from_scene'):
                try:
                    anim.clean_up_from_scene(self.scene)
                except Exception:
                    pass
            # ...and drop the per-child stamps the container's split wrote, so
            # the frames of the *next* play see every child at full progress.
            release_split(getattr(anim, 'mobject', None))
            # ...and the empty path-window a finished ShowPassingFlash parked
            # at (1.0, 1.0), so a flashed mobject that re-enters a later frame
            # is drawn in full, not invisible (CE restores its full path).
            release_flash_window(getattr(anim, 'mobject', None))

        # manim's Scene.play_internal ends with
        #
        #     self.update_mobjects(0)
        #
        # -- i.e. one more updater pass *after* finish()/clean_up_from_scene().
        # finish() applies interpolate(1) only here, at the very end of play(),
        # and the scene's next play() may remove_updater first, so without this
        # pass the camera frame's update_curve updater never sees the dot at
        # alpha == 1.  Restore.begin() then captures a camera one pan-step
        # behind and the boundary snaps by ~0.18 world units (44 px @1080p)
        # before easing back over the following frames.  dt=0 only re-anchors
        # (applies the updaters once) instead of accumulating time.
        #
        # A lone frozen wait is the exception: CE's frozen branch never enters
        # play_internal, so update_mobjects(0) has nothing to come after --
        # skipping the pass keeps pause()/frozen_frame=True a true hold.
        if not frozen_wait:
            _drive_mobject_updaters(self.scene, 0.0)
        # A ``wait_until`` that stopped early reports its real elapsed time so
        # the caller advances the audio playhead by what actually played, not
        # the full ``max_time`` schedule; every other play returns None and the
        # caller keeps using the Timeline's own duration (no behavior change).
        #
        # The produced picture lasts `n_frames * dt`, not the nominal
        # `run_time`: a frozen wait writes int() frames and an animation
        # arange() frames.  `play()` advances `_cursor` by this media time so
        # `add_sound` / subtitles stay aligned with the frames on disk.
        self._last_run_media_time = (stop_elapsed if stop_elapsed is not None
                                     else n_frames * dt)
        return stop_elapsed

    def _schedule_play(self, animations, kwargs):
        """Record a play() call on the global timeline instead of rendering.

        Mobjects are still added to the scene (so everything exists for later
        evaluation) but nothing is drawn.  Later, ``build_timeline()`` turns the
        whole recording into a Timeline whose every frame can be produced on
        demand.
        """
        from manim.mobject.mobject import _AnimationBuilder

        resolved = []
        for anim in animations:
            if isinstance(anim, _AnimationBuilder):
                # Same CE-parity rule as `play()` (see the long note there):
                # manim's `suspend_mobject_updating` default is left alone, so a
                # scheduled `.animate` renders exactly like an immediate one.
                resolved.append(anim.build())
            else:
                resolved.append(anim)
        animations = tuple(resolved)

        add_mobs = []
        for anim in animations:
            add_mobs.extend(self._extract_add_mobjects(anim))
        real = [a for a in animations if not isinstance(a, Add)]

        # Same lone-Wait resolution play() applies: the schedule branch
        # returns before it, so without this a recorded pause/wait kept
        # is_static_wait=None and both Timeline's frozen windows and
        # ce_frame_count treated it as a stepped wait -- a FrameServer export
        # then drove updaters through a pause CE renders as a frozen frame.
        from real_time_manim.timeline import resolve_static_wait
        resolve_static_wait(self.scene, real)

        if 'run_time' in kwargs:
            for a in real:
                a.run_time = kwargs['run_time']
        if 'rate_func' in kwargs:
            for a in real:
                a.rate_func = kwargs['rate_func']
        # Same play-level `path_*` forwarding as the live path (see the note
        # there): the recorded schedule must carry the arc too.
        _forward_path_kwargs(real, kwargs)

        # Same ``Scene.get_run_time`` -> ``Scene.validate_run_time`` check the
        # live path applies (gap A31): schedule mode is still a ``win.play``
        # entry, so ``run_time=0`` must raise CE's ValueError here too instead
        # of quietly recording a zero-length segment.
        self._validate_play_run_time(real)

        # Same family-membership rule as Scene.add_mobjects_from_animations
        # (see _ensure_animated_present): don't promote a mobject that is
        # already somewhere in the scene's family -- checking only the
        # top-level list would re-append a submobject at the end and reorder
        # the paint relative to CE.
        self._ensure_animated_present(real, add_mobs)

        duration = max((float(getattr(a, 'run_time', 1.0) or 1.0) for a in real),
                       default=0.0)
        for a in real:
            self._sched.append((self._cursor, a))
        # Advance by what a render would actually produce (frames / fps), not
        # the nominal `run_time`: a frozen Wait counts int() frames and an
        # animation arange() frames, so a nominal cursor would put subtitle
        # durations (and the next play's start) 0.11 s apart where the video
        # has 0.10 s.  This mirrors `play()`'s `_last_run_media_time` advance,
        # so a FrameServer / parallel recording and a single-pass one produce
        # the same `.srt` and the same total duration.
        from real_time_manim.timeline import ce_frame_count
        fps = (getattr(self, "_fast_record_fps", TARGET_FPS)
               if getattr(self, "_fast_record", False) else TARGET_FPS)
        self._cursor += ce_frame_count(real, duration, fps) / float(fps or 1.0)

    def build_timeline(self):
        """Turn the recorded schedule into a Timeline (begin() once)."""
        from real_time_manim.timeline import Timeline
        tl = Timeline(self, self.scene)
        for start, anim in self._sched:
            tl.add(anim, start)
        tl.finalize()
        # Same detached-copy presentation as play(): begin() has now run,
        # so TMA's fade-in target copy and FadeTransform ghosts exist.
        self._present_detached_animated([a for _, a in self._sched])
        return tl

    def _play_legacy(self, *animations, **kwargs):
        if not self.scene:
            return

        # Same no-silent-drop rule as ``play``; this path also implements
        # ``screenshot_at``, so it is a recognised keyword here.
        _warn_unsupported_play_kwargs(
            kwargs, known=SUPPORTED_PLAY_KWARGS + ("screenshot_at",),
            method="win._play_legacy")

        self._skip_mob_ids = set()

        screenshot_at = kwargs.get('screenshot_at', None)

        resolved = []
        for anim in animations:
            from manim.mobject.mobject import _AnimationBuilder
            if isinstance(anim, _AnimationBuilder):
                # CE parity, and the same rule `play()` already applies: a
                # builder's `build()` leaves `suspend_mobject_updating` at its
                # DEFAULT (True), so `Animation.begin()` calls
                # `mobject.suspend_updating()` and the animated mobject's own
                # updaters stay OFF for the whole play -- only the copies
                # `begin()` took are advanced (manim `Animation.begin`).
                # Forcing it False here made THIS path apply an extra
                # `mobject.update(dt)` per frame on top of those copies, i.e.
                # the animation ran exactly one frame AHEAD of CE (measured on
                # the wiki `03-动画/更新器动画/01b-更新工具与自动变化` TracedPath
                # sample while `play()` still carried the same override:
                # RTM[k] == CE[k+1], max |Δ| 0.198 scene units; with the
                # default kept, |CE - RTM| max = 0.0000 over 120 frames).  The
                # legacy loop below already drives updaters through
                # `_drive_mobject_updaters`, which prunes any subtree whose
                # `updating_suspended` is set (window/scene.py
                # `_run_mobject_updaters`), and `a.finish()` -- the resume side
                # of the same contract -- resumes it again (animation.py:226),
                # so the rule holds end to end with no other change.
                built = anim.build()
                resolved.append(built)
            elif isinstance(anim, AnimationGroup):
                sub_resolved = []
                for sub in anim.animations:
                    if isinstance(sub, _AnimationBuilder):
                        # Same suspend rule as the branch above: no override.
                        built = sub.build()
                        sub_resolved.append(built)
                    else:
                        sub_resolved.append(sub)
                anim.animations = sub_resolved
                resolved.append(anim)
            else:
                resolved.append(anim)
        animations = tuple(resolved)

        add_mobs = []
        for anim in animations:
            add_mobs.extend(self._extract_add_mobjects(anim))

        all_mobjects = list(add_mobs)
        for anim in animations:
            if isinstance(anim, (Create, Write, DrawBorderThenFill, FadeIn, Rotating, Rotate, GrowArrow, Indicate, ShowPassingFlash)) and anim.mobject:
                if isinstance(anim, (Create, DrawBorderThenFill)):
                    anim.mobject._vulkan_progress = 0.0
                if anim.mobject not in all_mobjects:
                    all_mobjects.append(anim.mobject)
            elif isinstance(anim, (FadeIn, FadeOut)):
                for mob in anim.mobjects:
                    if isinstance(anim, FadeIn):
                        set_anim_opacity(mob, 0.0)
                    if mob not in all_mobjects:
                        all_mobjects.append(mob)
            elif isinstance(anim, TransformMatchingAbstractBase):
                if anim.mobject not in all_mobjects:
                    all_mobjects.append(anim.mobject)
                # Don't add target_mobject here — clean_up_from_scene handles it
                # after all transforms complete, to avoid premature rendering.
                set_anim_opacity(anim.target_mobject, 0.0)
                anim.mobject._transforming = True
                for sub_anim in getattr(anim, '_anims', []):
                    if isinstance(sub_anim, (FadeIn, FadeOut)):
                        for mob in sub_anim.mobjects:
                            if isinstance(sub_anim, FadeIn):
                                set_anim_opacity(mob, 0.0)
                            if mob not in all_mobjects:
                                all_mobjects.append(mob)
                    elif isinstance(sub_anim, (Transform, _ManimTransform)):
                        if sub_anim.mobject not in all_mobjects:
                            all_mobjects.append(sub_anim.mobject)
                        if sub_anim.target_mobject not in all_mobjects:
                            all_mobjects.append(sub_anim.target_mobject)
                        set_anim_opacity(sub_anim.target_mobject, 0.0)
            elif isinstance(anim, FadeTransform):
                if anim.mobject not in all_mobjects:
                    all_mobjects.append(anim.mobject)
                if anim.target_mobject not in all_mobjects:
                    all_mobjects.append(anim.target_mobject)
                ghost = getattr(anim, '_ghost', None)
                if ghost is not None and ghost not in all_mobjects:
                    all_mobjects.append(ghost)
                is_manim_ft = type(anim).__module__.startswith('manim')
                if is_manim_ft and hasattr(anim.mobject, 'submobjects'):
                    for sub in anim.mobject.submobjects:
                        for existing in self.scene.mobjects:
                            if sub is existing:
                                if not hasattr(self, '_skip_mob_ids'):
                                    self._skip_mob_ids = set()
                                self._skip_mob_ids.add(id(existing))
                                break
            elif isinstance(anim, (Transform, _ManimTransform)):
                if anim.mobject not in all_mobjects:
                    all_mobjects.append(anim.mobject)
                # ApplyMethod subclasses (Restore, ApplyPointwiseFunction, etc.)
                # modify the mobject's points away from the original geometric shape.
                # They need _transforming=True so the renderer uses _send_vmobject
                # (point-based bezier path) instead of the shape-specific dispatcher
                # (like _send_square) which ignores point changes.
                # Restore interpolates BACK to the original shape — the native
                # dispatcher handles it fine.
                from manim.animation.transform import ApplyMethod as _ManimApplyMethod
                if isinstance(anim, _ManimApplyMethod) and type(anim).__name__ != 'Restore':
                    anim.mobject._transforming = True
                    # ApplyMethod warps bezier handles into curves — _send_polygon
                    # (straight edges) can't represent them.  Route through
                    # _send_vmobject instead so the bezier path is preserved.
                    anim.mobject._apply_method = True
                # Manim Transform subclasses (ClockwiseTransform, CounterclockwiseTransform,
                # and plain manim Transform) modify mobject points but don't set _transforming.
                # Without _transforming=True the renderer ignores point changes and draws
                # the native shape (e.g. _send_dot instead of _send_vmobject).
                if isinstance(anim, _ManimTransform) and not isinstance(anim, Transform):
                    Transform._set_transforming(anim.mobject, True)
                # Tag FocusOn starting dot so it routes through _send_dot
                # (not the generic _send_vmobject) — renders as a proper circle
                if type(anim).__name__ == 'FocusOn':
                    anim.mobject._focus_on_dot = True
                    # Subtle-but-visible spotlight: 0.4 was too strong, 0.03
                    # invisible under the accurate UNORM swapchain.
                    anim.mobject._dot_max_opacity = 0.15
                if anim.replace_mobject_with_target_in_scene:
                    if anim.target_mobject not in all_mobjects:
                        all_mobjects.append(anim.target_mobject)
                    set_anim_opacity(anim.target_mobject, 0.0)
                if isinstance(anim, _ManimFadeTransform) and hasattr(anim.mobject, 'submobjects'):
                    for sub in anim.mobject.submobjects:
                        for existing in self.scene.mobjects:
                            if sub is existing:
                                self._skip_mob_ids.add(id(existing))
                                break
            elif isinstance(anim, Succession):
                for sub in anim.animations:
                    if isinstance(sub, (Create, Write, DrawBorderThenFill, FadeIn, Rotating, Rotate)) and sub.mobject:
                        if isinstance(sub, (Create, DrawBorderThenFill)):
                            sub.mobject._vulkan_progress = 0.0
                        if isinstance(sub, FadeIn):
                            # Same fix as the AnimationGroup branch above: RTM's
                            # FadeIn keeps only ``mobjects[0]`` as ``self.mobject``,
                            # so present every mobject it carries, not just the head.
                            for fi_mob in getattr(sub, "mobjects", None) or [sub.mobject]:
                                set_anim_opacity(fi_mob, 0.0)
                                if fi_mob not in all_mobjects:
                                    all_mobjects.append(fi_mob)
                            continue
                        if sub.mobject not in all_mobjects:
                            all_mobjects.append(sub.mobject)
                    elif isinstance(sub, (FadeIn, FadeOut)):
                        for mob in sub.mobjects:
                            if isinstance(sub, FadeIn):
                                set_anim_opacity(mob, 0.0)
                            if mob not in all_mobjects:
                                all_mobjects.append(mob)
                    elif isinstance(sub, TransformMatchingAbstractBase):
                        if sub.mobject not in all_mobjects:
                            all_mobjects.append(sub.mobject)
                        if sub.target_mobject not in all_mobjects:
                            all_mobjects.append(sub.target_mobject)
                        sub.mobject._transforming = True
                        for sub_anim in getattr(sub, '_anims', []):
                            if isinstance(sub_anim, (FadeIn, FadeOut)):
                                for mob in sub_anim.mobjects:
                                    set_anim_opacity(mob, 0.0)
                                    if mob not in all_mobjects:
                                        all_mobjects.append(mob)
                            elif isinstance(sub_anim, (Transform, _ManimTransform)):
                                if sub_anim.mobject not in all_mobjects:
                                    all_mobjects.append(sub_anim.mobject)
                                if sub_anim.target_mobject not in all_mobjects:
                                    all_mobjects.append(sub_anim.target_mobject)
                    elif isinstance(sub, FadeTransform):
                        if sub.mobject not in all_mobjects:
                            all_mobjects.append(sub.mobject)
                        if sub.target_mobject not in all_mobjects:
                            all_mobjects.append(sub.target_mobject)
                        ghost = getattr(sub, '_ghost', None)
                        if ghost is not None and ghost not in all_mobjects:
                            all_mobjects.append(ghost)
                        is_manim_ft = type(sub).__module__.startswith('manim')
                        if is_manim_ft and hasattr(sub.mobject, 'submobjects'):
                            for child in sub.mobject.submobjects:
                                for existing in self.scene.mobjects:
                                    if child is existing:
                                        self._skip_mob_ids.add(id(existing))
                                        break
            elif isinstance(anim, AnimationGroup):
                for sub in anim.animations:
                    if isinstance(sub, (Create, Write, DrawBorderThenFill, FadeIn, Rotating, Rotate, GrowArrow)) and sub.mobject:
                        if isinstance(sub, (Create, DrawBorderThenFill)):
                            sub.mobject._vulkan_progress = 0.0
                        if isinstance(sub, FadeIn):
                            # RTM's FadeIn stores only ``mobjects[0]`` as
                            # ``self.mobject`` and the rest in ``self.mobjects``
                            # (manim wraps them all in one VGroup).  A page-swap
                            # group ``AnimationGroup(FadeOut(old), FadeIn(new1,
                            # new2), lag_ratio=0)`` therefore presented only the
                            # FIRST fade-in mobject here -- the "换上" half was
                            # missing its extra mobjects.  Add every mobject the
                            # FadeIn carries, not just the head one.
                            for fi_mob in getattr(sub, "mobjects", None) or [sub.mobject]:
                                set_anim_opacity(fi_mob, 0.0)
                                if fi_mob not in all_mobjects:
                                    all_mobjects.append(fi_mob)
                            continue
                        if sub.mobject not in all_mobjects:
                            all_mobjects.append(sub.mobject)
                    elif isinstance(sub, (FadeIn, FadeOut)):
                        for mob in sub.mobjects:
                            if isinstance(sub, FadeIn):
                                set_anim_opacity(mob, 0.0)
                            if mob not in all_mobjects:
                                all_mobjects.append(mob)
                    elif isinstance(sub, Transform):
                        if sub.mobject not in all_mobjects:
                            all_mobjects.append(sub.mobject)
                        if sub.target_mobject not in all_mobjects:
                            all_mobjects.append(sub.target_mobject)
                        sub.mobject._transforming = True
                    elif isinstance(sub, FadeTransform):
                        # FadeTransform subs (e.g. per-piece FadeTransformPieces)
                        # need their target and ghost added too, otherwise the
                        # target shape never renders during the crossfade.
                        if sub.mobject not in all_mobjects:
                            all_mobjects.append(sub.mobject)
                        if sub.target_mobject not in all_mobjects:
                            all_mobjects.append(sub.target_mobject)
                        gh = getattr(sub, '_ghost', None)
                        if gh is not None and gh not in all_mobjects:
                            all_mobjects.append(gh)
                    else:
                        # Catch-all for ApplyMethod, etc. — track their mobjects
                        # so _is_descendant_of_scene can prevent double-rendering
                        if hasattr(sub, 'mobject') and sub.mobject is not None:
                            if sub.mobject not in all_mobjects:
                                all_mobjects.append(sub.mobject)
            else:
                from manim.animation.composition import AnimationGroup as _ManimAG
                if isinstance(anim, _ManimAG):
                    for sub in anim.animations:
                        if hasattr(sub, 'mobject') and sub.mobject is not None:
                            if sub.mobject not in all_mobjects:
                                all_mobjects.append(sub.mobject)
                        if hasattr(sub, 'target_mobject') and sub.target_mobject is not None:
                            if not isinstance(sub, _ManimTransform) or type(sub) is _ManimTransform:
                                if sub.target_mobject not in all_mobjects:
                                    all_mobjects.append(sub.target_mobject)

        def _is_descendant_of_scene(mob):
            """Check if mob is already somewhere in the scene mobject tree."""
            def _search(node, target):
                if node is target:
                    return True
                for sub in getattr(node, 'submobjects', []):
                    if _search(sub, target):
                        return True
                return False

            for root in self.scene.mobjects:
                if root is mob:
                    continue
                if _search(root, mob):
                    return True
            return False

        for mob in all_mobjects:
            if _is_descendant_of_scene(mob):
                self._skip_mob_ids.add(id(mob))
                continue
            if mob not in self.scene.mobjects:
                self.scene.add(mob)

        appended = False
        for anim in animations:
            if hasattr(anim, 'mobject') and anim.mobject is not None:
                if anim.mobject not in self.scene.mobjects:
                    self.scene.mobjects.append(anim.mobject)
                    appended = True
            cursor = getattr(anim, 'cursor', None)
            if cursor is not None and cursor not in self.scene.mobjects:
                self.scene.mobjects.append(cursor)
                appended = True
        if appended:
            foreground_to_front(self.scene)

        for mob in add_mobs:
            set_anim_opacity(mob, 0.0)

        for a in animations:
            if isinstance(a, Add):
                for mob in a.mobjects:
                    set_anim_opacity(mob, 1.0)

        real_anims = [a for a in animations if not isinstance(a, Add)]

        if 'run_time' in kwargs:
            shared_rt = kwargs['run_time']
            for a in real_anims:
                if isinstance(a, (Wait, Succession)):
                    continue
                a.run_time = shared_rt
        if 'rate_func' in kwargs:
            shared_rf = kwargs['rate_func']
            for a in real_anims:
                if isinstance(a, (Wait, Succession)):
                    continue
                a.rate_func = shared_rf
        # Same play-level `path_*` forwarding as the timeline path (see the note
        # there): this reference path must not disagree with the live one.
        _forward_path_kwargs(real_anims, kwargs)

        # Fast record: seed simulated time so start_time uses a consistent clock
        if self._fast_record:
            self._fast_record_sim_time = time.time()
            _frame_interval = 1.0 / self._fast_record_fps

        for a in real_anims:
            is_manim = type(a).__module__.startswith('manim')
            if is_manim:
                # don't render an invisible source. The target was set to 0.0
                # by the previous animation's target setup at line 513.
                if getattr(a, 'mobject', None) is not None:
                    set_anim_opacity(a.mobject, 1.0)
                _setup_anim_scene(a, self.scene)
                a.start_time = self._fast_record_sim_time if self._fast_record else time.time()
                a.begin()
                tm = getattr(a, 'target_mobject', None)
                if tm is not None and hasattr(tm, 'get_updaters') and tm.get_updaters():
                    # Same arity rule as `_run_mobject_updaters`
                    # (window/scene.py): updater() / updater(m) / updater(m,
                    # dt).  The bare `upd(tm)` this used to be raised
                    # TypeError for the two-argument form the moment a
                    # Transform's target copy carried one.
                    import inspect as _inspect
                    for upd in tm.get_updaters():
                        try:
                            nparams = len(_inspect.signature(upd).parameters)
                        except (TypeError, ValueError):
                            nparams = 1
                        if nparams == 0:
                            upd()
                        elif nparams == 1:
                            upd(tm)
                        else:
                            upd(tm, 0.0)
                    tc = getattr(a, 'target_copy', None)
                    if tc is not None:
                        tc.move_to(tm.get_center())
                if a.mobject is not None and a.mobject not in self.scene.mobjects:
                    self.scene.mobjects.append(a.mobject)
            else:
                a.begin(self._fast_record_sim_time if self._fast_record else time.time())

        for a in real_anims:
            if isinstance(a, TransformMatchingAbstractBase):
                # Remove the source VGroup from scene — sub-anims' Transform
                # handles rendering of individual MathTexPart children.
                # This prevents ghost copies where eq2's own submobjects
                # render at original positions while transform_source
                # renders copies at interpolated positions.
                if a.mobject in self.scene.mobjects:
                    self.scene.remove(a.mobject)
                set_anim_opacity(a.mobject, 0.0)
                for sub_anim in getattr(a, '_anims', []):
                    if isinstance(sub_anim, (Transform, _ManimTransform)):
                        if sub_anim.mobject not in self.scene.mobjects:
                            self.scene.add(sub_anim.mobject)
                        if sub_anim.target_mobject not in self.scene.mobjects:
                            self.scene.add(sub_anim.target_mobject)
                        # Hide the target VGroup — it's only a shape reference;
                        # the source mobject morphs into its shape during interpolate.
                        set_anim_opacity(sub_anim.target_mobject, 0.0)
                    elif isinstance(sub_anim, FadeOut):
                        # Add fade_source VGroup so unmatched source parts
                        # (e.g. x, y, z) render and fade progressively.
                        if sub_anim.mobject not in self.scene.mobjects:
                            self.scene.add(sub_anim.mobject)
                    elif isinstance(sub_anim, FadeIn):
                        # Add fade_target_copy so unmatched target parts
                        # fade in. Start fully transparent.
                        if sub_anim.mobject not in self.scene.mobjects:
                            self.scene.add(sub_anim.mobject)
                        set_anim_opacity(sub_anim.mobject, 0.0)

        self._active_anims = real_anims
        self._last_frame_time = time.time() - (1.0 / 30.0)

        # Fast record: align _last_frame_time with simulated clock so the
        # first frame's dt equals _frame_interval.
        if self._fast_record:
            self._last_frame_time = self._fast_record_sim_time - _frame_interval

        _orig_vgroup_rotate = {}
        _prev_vg_rotation = {}

        def _rotation_pivot(vg):
            if hasattr(vg, '_rotation_about_point'):
                return np.array(vg._rotation_about_point, dtype=float)
            # Use the first submobject's center as pivot instead of the
            # VGroup aggregate center. This prevents vertical vibration when a
            # dot on the circumference shifts the VGroup center (rolling circle).
            if hasattr(vg, 'submobjects') and len(vg.submobjects) > 0:
                return np.array(vg.submobjects[0].get_center(), dtype=float)
            return vg.get_center()

        def _maybe_clear_prev_vg_rotation(anim):
            """After interpolate() resets mobject points, clear prev-rotation
            tracking so the VGroup delta loop reapplies the FULL accumulated
            rotation, not just the increment since last frame."""
            mob = getattr(anim, 'mobject', None)
            if mob is None:
                return
            for scene_mob in self.scene.mobjects:
                if isinstance(scene_mob, (VGroup, Group)):
                    # Check if anim.mobject is this VGroup or a descendant
                    if mob is scene_mob or (
                        hasattr(scene_mob, 'family_members_with_points') and
                        mob in scene_mob.family_members_with_points()
                    ):
                        _prev_vg_rotation.pop(id(scene_mob), None)

        def _patch_vgroup(vg):
            if id(vg) in _orig_vgroup_rotate:
                return
            _orig_vgroup_rotate[id(vg)] = vg.rotate
            def _propagating_rotate(angle, axis=OUT, about_point=None, about_edge=None, **kwargs):
                alpha = _anim_alpha[0]
                effective = angle * alpha
                pivot = _rotation_pivot(vg)
                for m in vg.family_members_with_points():
                    if hasattr(m, 'points') and len(m.points) > 0:
                        c, s = np.cos(effective), np.sin(effective)
                        rot_matrix = np.array([[c, -s, 0], [s, c, 0], [0, 0, 1]])
                        m.points = (m.points - pivot) @ rot_matrix.T + pivot
                current = get_anim_rotation(vg)
                set_anim_rotation(vg, current + effective)
                return vg
            vg.rotate = _propagating_rotate

        def _unpatch_vgroup(vg):
            if id(vg) in _orig_vgroup_rotate:
                vg.rotate = _orig_vgroup_rotate.pop(id(vg))

        frame_count = 0
        # Mutable container so _patch_vgroup's closure reads the latest alpha
        _anim_alpha = [1.0]
        while True:
            if self._fast_record:
                now = self._fast_record_sim_time
                dt = _frame_interval
                self._fast_record_sim_time += _frame_interval
            else:
                frame_start = time.time()
                now = frame_start
                dt = now - self._last_frame_time

            self._last_frame_time = now
            all_done = True

            # Time-based rotation: original manim uses -0.3 rad/frame at 30fps
            # which is -9 rad/s.  current_alpha = dt * 30 gives:
            #   30fps → 1.0, 60fps → 0.5, etc.
            current_alpha = dt * 30
            _anim_alpha[0] = current_alpha

            for a in self._active_anims:
                is_manim = type(a).__module__.startswith('manim')
                if is_manim:
                    elapsed = now - a.start_time
                    alpha = elapsed / a.run_time if a.run_time > 0 else 1.0
                    alpha = max(0.0, min(1.0, alpha))
                    a.interpolate(alpha)
                    # interpolate() resets mobject points, erasing accumulated rotation.
                    # Clear _prev_vg_rotation so the delta loop reapplies the FULL rotation.
                    _maybe_clear_prev_vg_rotation(a)

                    if not getattr(a, 'finished', False) and elapsed >= a.run_time:
                        a.finish()
                        a.finished = True
                        if hasattr(a, 'clean_up_from_scene'):
                            a.clean_up_from_scene(self.scene)
                        mob = getattr(a, 'mobject', None)
                        if mob:
                            mob.resume_updating()
                            # After the animation ends, clear _transforming only when
                            # the mobject's appearance reverts to its original shape.
                            # Keep it for permanent morphs:
                            #   - ApplyMethod (WarpSquare, etc.) except Restore
                            #   - _ManimTransform without replacement (ClockwiseTransform
                            #     permanently morphs the mobject's points to the target)
                            from manim.animation.transform import ApplyMethod as _ManimApplyMethod2
                            keep = False
                            if isinstance(a, _ManimApplyMethod2):
                                keep = type(a).__name__ != 'Restore'
                            elif isinstance(a, _ManimTransform) and not getattr(a, 'replace_mobject_with_target_in_scene', False):
                                keep = True
                            if not keep:
                                Transform._set_transforming(mob, False)
                            if hasattr(mob, '_was_transforming_text'):
                                del mob._was_transforming_text
                            if hasattr(mob, '_dot_max_opacity'):
                                del mob._dot_max_opacity
                            if hasattr(mob, '_focus_on_dot'):
                                del mob._focus_on_dot
                            if hasattr(mob, '_apply_method') and not keep:
                                del mob._apply_method
                            target = getattr(a, 'target_mobject', None) or getattr(a, 'target', None)
                            if target and isinstance(mob, Text) and hasattr(mob, 'text') and hasattr(target, 'text'):
                                mob.text = target.text
                            if getattr(a, 'replace_mobject_with_target_in_scene', False):
                                set_anim_opacity(mob, 1.0)
                        if hasattr(a, 'animations'):
                            for sub in a.animations:
                                sub_mob = getattr(sub, 'mobject', None)
                                if sub_mob and hasattr(sub_mob, '_transforming'):
                                    sub_mob._transforming = False
                        if hasattr(a, '_anims'):
                            for sub in a._anims:
                                sub_mob = getattr(sub, 'mobject', None)
                                if sub_mob and hasattr(sub_mob, '_transforming'):
                                    sub_mob._transforming = False
                else:
                    a.interpolate(now)
                    if not a.finished and (now - a.start_time) >= a.run_time:
                        a.finish()
                        a.finished = True
                        if hasattr(a, 'clean_up_from_scene'):
                            a.clean_up_from_scene(self.scene)
                if not getattr(a, 'finished', False):
                    all_done = False

            # Apply rotation delta per VGroup.
            for mob in self.scene.mobjects:
                if isinstance(mob, (VGroup, Group)):
                    if getattr(mob, '_rotation_about_point', None) is not None or getattr(mob, '_rotation_3d', False):
                        # Rotation is handled by the VGroup handler in _send().
                        continue
                    vg_rot = get_anim_rotation(mob)
                    prev_rot = _prev_vg_rotation.get(id(mob), 0.0)
                    delta = vg_rot - prev_rot
                    if abs(delta) > 1e-12:
                        pivot = _rotation_pivot(mob)
                        c, s = np.cos(delta), np.sin(delta)
                        rot_matrix = np.array([[c, -s, 0], [s, c, 0], [0, 0, 1]])
                        for sub in mob.family_members_with_points():
                            if hasattr(sub, 'points') and len(sub.points) > 0:
                                sub.points = (sub.points - pivot) @ rot_matrix.T + pivot
                    _prev_vg_rotation[id(mob)] = vg_rot

            _drive_mobject_updaters(self.scene, dt, _patch_vgroup, _unpatch_vgroup)

            clear_anim_rotation_delta()

            if self._fast_record:
                seg = self._fast_record_segment
                idx = self._fast_record_frame_idx
                
                if seg is not None and idx >= seg[1]:
                    break
                
                in_segment = (seg is None) or (seg[0] <= idx < seg[1])
                if in_segment:
                    if getattr(self, '_fast_record_count_only', False):
                        pass  # count only — no GPU
                    else:
                        # Queue this frame's state first, then draw + capture it:
                        # tick() renders whatever is queued, so drawing before
                        # sync() would capture the previous frame.  The readback
                        # request must also be armed before the draw, so the
                        # frame copies itself out while it still owns the image.
                        self.sync(self.scene)
                        self.request_readback()
                        if not self.tick():
                            break
                        if getattr(self, '_fast_record_pipe_mode', True):
                            self._capture_screenshot_to_pipe()
                        else:
                            bmp = os.path.join(
                                self._fast_record_path,
                                f"frame_{idx:06d}.bmp")
                            self.screenshot(bmp)
                
                self._fast_record_frame_idx += 1
            else:
                self.sync(self.scene)
                self.request_readback()
                if not self.tick():
                    break
                self._capture_frame()

            frame_count += 1

            if screenshot_at:
                for a in self._active_anims:
                    if a in screenshot_at:
                        alpha = (now - a.start_time) / a.run_time if a.run_time > 0 else 1.0
                        alpha = max(0.0, min(1.0, alpha))
                        alpha = a.rate_func(alpha)
                        for threshold, path in screenshot_at[a]:
                            if abs(alpha - threshold) < 0.02:
                                self.screenshot(path)
                                del screenshot_at[a][screenshot_at[a].index((threshold, path))]
                                break

            if all_done:
                break

            if not self._fast_record:
                elapsed = time.time() - frame_start
                if elapsed < FRAME_DURATION:
                    time.sleep(FRAME_DURATION - elapsed)

        for a in real_anims:
            if hasattr(a, 'clean_up_from_scene'):
                a.clean_up_from_scene(self.scene)

