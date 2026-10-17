from real_time_manim.animations.base import Animation, set_anim_opacity, get_anim_opacity
from real_time_manim.rate_functions import _linear

# ``begin()`` with no argument stamps ``time.time()`` (seconds since 1970), so
# a start_time this large means "wall clock", not "seconds into the play".
_WALL_CLOCK_MIN = 1.0e6
import time
import numpy as np
from manim.mobject.mobject import _AnimationBuilder
from real_time_manim.animations.wait import Wait
from real_time_manim.animations.fade_in import FadeIn
from real_time_manim.animations.fade_out import FadeOut
from real_time_manim.animations.transform import Transform


class AnimationGroup(Animation):
    def __init__(self, *animations, group=None, run_time=None, lag_ratio=0.0,
                 synchronize_with_wall_clock=False, **kwargs):
        """Compose several animations into one (manim CE semantics).

        Extra keyword-only parameters the shared ``**kwargs`` used to swallow
        silently (wiki ``03-动画/组合编排/01-AnimationGroup与错峰``):

        * ``run_time`` -- total duration; ``None`` (the default) keeps the
          automatically-computed end of the child schedule, a number stretches
          or compresses the WHOLE child schedule onto it (``init_run_time``:
          run_time overrides ``max_end_time``, children are driven against
          ``max_end_time`` scaled by the group's rate function).
        * ``group`` -- an explicit container; manim sets ``self.mobject`` to
          it and answers ``get_all_mobjects()`` with its contents.
        * ``synchronize_with_wall_clock`` -- rejected explicitly when true:
          RTM's timeline is frame-driven (TARGET_FPS) and must stay a pure
          function of time for rendering/seeking, so there is no wall-clock
          path to honour it with.
        """
        from manim.mobject.mobject import _AnimationBuilder
        if synchronize_with_wall_clock:
            raise ValueError(
                "AnimationGroup(synchronize_with_wall_clock=True) is not "
                "supported: real-time-manim drives its timeline frame by "
                "frame (TARGET_FPS/FRAME_DURATION) so every frame is a pure, "
                "seekable function of time -- coupling an animation to the "
                "wall clock would break rendering, seeking and recording. "
                "Drop the argument; live pacing is owned by the window loop. "
                "RTM 按帧驱动时间轴，无墙钟同步路径，该参数被显式拒绝。"
            )
        resolved = []
        for a in animations:
            if isinstance(a, _AnimationBuilder):
                resolved.append(a.build())
            else:
                resolved.append(a)
        self.animations = resolved
        self.lag_ratio = lag_ratio
        # manim's schedule (composition.py build_animations_with_timings):
        # start[0] = 0, start[i+1] = start[i] + run_time[i] * lag_ratio.
        # Accumulate naively, left to right, exactly as np.add.accumulate
        # does on CE's side: builtin ``sum`` on CPython >= 3.12 is
        # compensated and lands a whole frame the other side of an arange
        # boundary (wiki 组合编排/assets: 294 vs 295 frames, A30).
        start = 0.0
        for a in self.animations:
            a._group_start = start
            start = start + a.run_time * lag_ratio
        total_runs = [a._group_start + a.run_time for a in self.animations]
        total = max(total_runs) if total_runs else 0
        # The children's OWN span, in seconds, kept apart from ``run_time``.
        # manim's ``AnimationGroup`` normalises with ``rate_func(alpha) *
        # self.max_end_time`` -- ``max_end_time`` is the end of the last child,
        # computed once from the children's run_times, and its comment says so
        # explicitly: "if the run_time of AnimationGroup has been set to
        # something other than its default, these times might not correspond to
        # actual times ... Instead they'd be a rescaled version. But that's
        # okay!"  RTM used ``self.run_time`` there instead, so a play-level
        # ``run_time=`` override (which ``Scene.play``/``MLWindow.play`` apply
        # to the GROUP only) silently re-scaled the children's clock against
        # themselves: ``FadeTransformPieces`` -- two 1.0 s children, group
        # ``run_time`` then set to 1.5 s -- finished its crossfade at
        # ``smooth(t/1.5)*1.5 == 1.0``, i.e. t = 0.87 s, and the remaining
        # 0.63 s of the play froze.  Measured on the wiki
        # ``03-动画/变换/05-淡出淡入式变换``: RTM steps 0.000 for frames 376..392
        # while CE is still stepping 0.40..0.52.
        self._children_span = total
        # manim's AnimationGroup defaults to rate_func=linear; the shared
        # Animation base defaults to smooth, which would ease the whole group
        # *on top of* every child's own easing -- a staggered FadeIn group then
        # runs off CE's clock (measured: first child at 0.06 where CE has 0.5).
        kwargs.setdefault('rate_func', _linear)
        # ``lag_ratio`` must reach the base too: it stores the attribute after
        # this method would otherwise have set it (a default of 0.0 used to
        # clobber the stagger that the schedule above had already baked in).
        super().__init__(
            run_time=total if run_time is None else run_time,
            lag_ratio=lag_ratio, **kwargs)
        if group is not None:
            # manim does ``super().__init__(self.group, ...)``: the explicit
            # container becomes the animation's mobject, so CE's
            # ``add_mobjects_from_animations`` (and RTM's
            # ``_ensure_animated_present``) registers it with the scene, and
            # ``get_all_mobjects()`` answers with its contents.
            self.group = group
            self.mobject = group
        self._begun = set()

    def begin(self, t=None):
        if t is None:
            import time as _time
            t = _time.time()
        super().begin(t)
        self._begun = set()

    def interpolate(self, t):
        """Step every child to its state at time ``t``.

        Three callers, three conventions, and this class has to tell them
        apart itself:

        * the timeline passes **elapsed seconds** with ``start_time`` pinned to
          0 (``timeline.evaluate_animation``);
        * the live path passes a **wall-clock stamp**, as ``begin()`` records;
        * a manim wrapper passes manim's **normalised alpha** while our own
          ``start_time`` is still whatever ``begin()`` defaulted to --
          ``ChangeSpeed.interpolate`` does exactly
          ``self.anim.interpolate(alpha)``, and scene 59 wraps a group that
          way.

        Children are then stepped in absolute time -- RTM's animations read
        ``(t - start_time) / run_time`` themselves, so handing them a
        normalised alpha against a wall-clock
        ``start_time`` clamped to 0 for every animation that does not opt into
        ``_use_alpha`` -- ``AnimationGroup(Create(...))`` drew nothing at all.

        The old ``t < 100`` test conflated the first and the third case, so
        the timeline's *seconds* were read as an alpha: a 2.5 s group ran its
        whole schedule inside 1.0 s and the rest of the play was frozen.
        """
        total = float(self.run_time or 0.0)
        # A wall-clock origin can only be outrun by a wrapper's alpha (0..1);
        # a time, by contrast, is never below the origin it is measured from.
        from_wrapper = self.start_time > _WALL_CLOCK_MIN and t < self.start_time
        raw = t if from_wrapper else (
            (t - self.start_time) / total if total > 0 else 0.0)
        # Normalise against the RUN_TIME but map onto the CHILDREN'S span, so a
        # play-level run_time override stretches (or shortens) the whole child
        # schedule instead of cutting it short -- manim's `max_end_time`.
        # Falls back to `run_time` for a group built before the attribute
        # existed (pickled/copied instances).
        span = float(getattr(self, "_children_span", 0.0) or 0.0) or total
        group_time = (self.rate_func(max(0.0, min(1.0, raw))) * span
                      if total > 0 else 0.0)
        origin = self.start_time

        for i, a in enumerate(self.animations):
            a_start = getattr(a, '_group_start', 0.0)
            if group_time < a_start:
                continue
            is_manim = type(a).__module__.startswith('manim')
            if i not in self._begun:
                if is_manim:
                    a.begin()                       # manim's takes no time
                else:
                    a.begin(origin + a_start)
                    # Whatever an earlier grouping set is now wrong: RTM
                    # children are driven in absolute time, not handed a
                    # normalised alpha.
                    a._use_alpha = False
                self._begun.add(i)
            if is_manim:
                sub_alpha = (group_time - a_start) / a.run_time if a.run_time > 0 else 1.0
                a.interpolate(max(0.0, min(1.0, sub_alpha)))
            else:
                # past a_end this clamps to the child's final state
                a.interpolate(origin + group_time)

    @property
    def mobjects(self):
        """Every mobject the (possibly nested) children carry.

        ``PlayMixin._ensure_animated_present`` mirrors manim's
        ``Scene.add_mobjects_from_animations`` by reading each animation's
        ``.mobject`` / ``.mobjects`` and adding whatever is not in the scene
        family yet -- RTM paints the SCENE tree only, so a carrier that never
        enters the tree is never drawn.  A bare RTM group exposed neither
        attribute (manim's group exposes ``.mobject`` = its container), so the
        walker had to recurse into ``.animations`` itself and it stops at ONE
        level: the reported page-swap
        ``AnimationGroup(FadeOut(old), FadeIn(new1, new2))`` presented nothing
        until that child pass was added (A22), and a NESTED group or a group
        inside a ``Succession`` still slips through it -- the same "FadeIn
        载体未进场景" failure one level deeper.

        Enumerating the carriers here, recursively and de-duplicated, lets any
        walker reach them at any depth; for the direct case it yields exactly
        what the child pass already adds, so nothing changes there.
        """
        out = []
        seen = set()

        def visit(anim):
            if anim is None:
                return
            m = getattr(anim, "mobject", None)
            if m is not None and id(m) not in seen:
                seen.add(id(m))
                out.append(m)
            for mob in (getattr(anim, "mobjects", None) or []):
                if mob is not None and id(mob) not in seen:
                    seen.add(id(mob))
                    out.append(mob)
            for sub in (getattr(anim, "animations", None) or []):
                visit(sub)

        for child in (getattr(self, "animations", None) or []):
            visit(child)
        return out

    def _setup_scene(self, scene):
        """Hand the scene to every child, the way manim's group does.

        manim's ``AnimationGroup._setup_scene`` recurses so each introducer
        child can ``scene.add`` its mobject before ``begin`` -- that is the
        hook CE relies on to put a ``FadeIn`` target into the scene.  RTM's
        group had no such method at all, so any caller following manim's
        convention (``Scene.begin_animations``,
        ``window.scene._setup_anim_scene``) registered nothing for a group.
        Children without their own hook (RTM's own classes) get the same
        treatment inline: add whatever they carry if it is not in the scene
        family yet -- the same membership rule as CE and as the play-side
        walker.
        """
        if scene is None:
            return
        try:
            family = list(scene.get_mobject_family_members())
        except Exception:
            family = []
        for child in (getattr(self, "animations", None) or []):
            setup = getattr(child, "_setup_scene", None)
            if callable(setup):
                try:
                    setup(scene)
                except Exception:
                    pass
                continue
            carriers = (getattr(child, "mobjects", None)
                        or [getattr(child, "mobject", None)])
            for mob in carriers:
                if mob is None:
                    continue
                try:
                    if mob in family:
                        continue
                    scene.add(mob)
                    family += mob.get_family()
                except Exception:
                    continue

    def finish(self):
        super().finish()
        for a in self.animations:
            a.finish()

    def clean_up_from_scene(self, scene):
        """Recurse into each child's clean-up, the way manim's group does.

        manim's ``AnimationGroup.clean_up_from_scene`` is

            self._on_finish(scene)
            for anim in self.animations:
                anim.clean_up_from_scene(scene)

        RTM's base ``Animation.clean_up_from_scene`` is a no-op ``pass``, and
        ``AnimationGroup`` used to inherit it -- so NONE of a group's children
        ever cleaned up after it finished.  That is the reported
        ``FadeTransformPieces`` residual: ``_present_detached_animated`` walks
        into the group and adds every piece's ``_ghost`` (a copy of a target
        submobject) to the scene so the crossfade can paint, and only each
        piece's own ``clean_up_from_scene`` removes it again.  With the group
        swallowing that call, the ghosts stayed on screen after the play -- a
        leftover "copy of the target" that a later ``FadeOut`` could not touch.

        Recursing restores CE parity for every grouped animation (a lone
        ``FadeTransform`` already defined its own ``clean_up_from_scene``, which
        is why only the grouped ``...Pieces`` form was affected).
        """
        for a in self.animations:
            clean = getattr(a, "clean_up_from_scene", None)
            if callable(clean):
                clean(scene)

    def get_all_mobjects(self):
        group = getattr(self, "group", None)
        if group is not None:
            # manim: ``return list(self.group)`` -- an explicit container is
            # the answer, exactly as CE's AnimationGroup behaves when
            # ``group=`` was passed.
            return list(group)
        mobs = []
        for a in self.animations:
            mobs.extend(a.get_all_mobjects())
        return mobs

    def get_all_families_zipped(self):
        families = []
        for a in self.animations:
            families.extend(a.get_all_families_zipped())
        return families
