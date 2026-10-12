"""The play loop, the timeline renderer and the legacy manim play path."""

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


class PlayMixin:

    def tick(self):
        self.frame_count += 1
        result = self.dll.Vulkan_Tick()
        if result == 0:
            return False
        self.win_w = (result >> 16) & 0xFFFF
        self.win_h = result & 0xFFFF
        return True

    def _extract_add_mobjects(self, anim):
        mobjects = []
        if isinstance(anim, Add):
            mobjects.extend(anim.mobjects)
        elif isinstance(anim, Succession):
            for sub in anim.animations:
                mobjects.extend(self._extract_add_mobjects(sub))
        elif isinstance(anim, AnimationGroup):
            for sub in anim.animations:
                mobjects.extend(self._extract_add_mobjects(sub))
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
            set_anim_opacity(mob, 1.0)
            if mob not in self.scene.mobjects:
                self.scene.mobjects.append(mob)
                appended = True

        curr_mobjects = self.scene.get_mobject_family_members()
        for a in real_anims:
            m = getattr(a, "mobject", None)
            if m is not None and m not in curr_mobjects:
                self.scene.mobjects.append(m)
                curr_mobjects += m.get_family()
                appended = True
            for mob in (getattr(a, "mobjects", None) or []):
                if mob not in curr_mobjects:
                    self.scene.mobjects.append(mob)
                    curr_mobjects += mob.get_family()
                    appended = True
            cur = getattr(a, "cursor", None)
            if cur is not None and cur not in curr_mobjects:
                self.scene.mobjects.append(cur)
                curr_mobjects += cur.get_family()
                appended = True

        return appended

    def play(self, *animations, **kwargs):
        """Timeline-driven playback (2.0.0).

        Animations are scheduled on one Timeline and every frame is produced by
        evaluating that schedule at time ``t`` -- the same O(1) ``render_at``
        path that powers seeking.  The legacy fork-aware pipeline is preserved
        as :meth:`_play_legacy` for reference during the migration.
        """
        if not self.scene:
            return

        if type(self)._schedule_mode:
            self._schedule_play(animations, kwargs)
            return

        from real_time_manim.timeline import Timeline
        from manim.mobject.mobject import _AnimationBuilder

        # resolve .animate builders
        resolved = []
        for anim in animations:
            if isinstance(anim, _AnimationBuilder):
                anim.anim_args['suspend_mobject_updating'] = False
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

        appended = self._ensure_animated_present(real_anims, add_mobs)

        # CE's Scene.add drags foreground_mobjects back to the front on every
        # add; these appends bypass Scene.add, so re-apply that rule here.
        if appended:
            foreground_to_front(self.scene)

        tl = Timeline(self, self.scene)
        for a in real_anims:
            tl.add(a, 0.0)
        tl.finalize()

        self._run_timeline(tl, real_anims)

    def _run_timeline(self, tl, anims=None):
        """Walk a finalized Timeline forward, drawing and capturing each frame.

        The frame count comes from ``timeline.ce_frame_count`` so a recording has
        exactly as many frames as manim would emit for the same play -- ceil for an
        animation, truncation for a wait.  Rounding both to nearest drifted by a
        frame per segment.
        """
        from real_time_manim.timeline import (
            _is_manim_animation,
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
        _drive_mobject_updaters(self.scene, 0.0)

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
                anim.anim_args['suspend_mobject_updating'] = False
                resolved.append(anim.build())
            else:
                resolved.append(anim)
        animations = tuple(resolved)

        add_mobs = []
        for anim in animations:
            add_mobs.extend(self._extract_add_mobjects(anim))
        real = [a for a in animations if not isinstance(a, Add)]

        if 'run_time' in kwargs:
            for a in real:
                a.run_time = kwargs['run_time']
        if 'rate_func' in kwargs:
            for a in real:
                a.rate_func = kwargs['rate_func']

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
        self._cursor += duration

    def build_timeline(self):
        """Turn the recorded schedule into a Timeline (begin() once)."""
        from real_time_manim.timeline import Timeline
        tl = Timeline(self, self.scene)
        for start, anim in self._sched:
            tl.add(anim, start)
        tl.finalize()
        return tl

    def _play_legacy(self, *animations, **kwargs):
        if not self.scene:
            return

        self._skip_mob_ids = set()

        screenshot_at = kwargs.get('screenshot_at', None)

        resolved = []
        for anim in animations:
            from manim.mobject.mobject import _AnimationBuilder
            if isinstance(anim, _AnimationBuilder):
                anim.anim_args['suspend_mobject_updating'] = False
                built = anim.build()
                resolved.append(built)
            elif isinstance(anim, AnimationGroup):
                sub_resolved = []
                for sub in anim.animations:
                    if isinstance(sub, _AnimationBuilder):
                        sub.anim_args['suspend_mobject_updating'] = False
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
                            set_anim_opacity(sub.mobject, 0.0)
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
                    for upd in tm.get_updaters():
                        upd(tm)
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

