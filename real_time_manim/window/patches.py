"""Monkey patches applied to manim itself when RTM is imported.

Kept apart from the renderer: importing this module changes upstream
behaviour, so it must stay obvious which upstream entry points RTM
rewires and why.

Every patch below is additive and guarded: when none of the new paths is
taken the behaviour is exactly what it was before the patch was installed.
"""

import logging
import time as _time
import warnings as _warnings

from manim import ChangingDecimal as _OrigChangingDecimal
from manim import ChangeDecimalToValue as _OrigChangeDecimalToValue
_OrigChangingDecimal.check_validity_of_input = lambda self, dm: None
_OrigChangeDecimalToValue.check_validity_of_input = lambda self, dm: None

_logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# prepare_animation: let manim's machinery accept RTM's own animations (A24)
# ---------------------------------------------------------------------------
#
# RTM's animations do not subclass manim's Animation, so the original
# ``prepare_animation`` rejected them ("TypeError: Object Wait(None) cannot be
# converted to an animation") whenever they crossed into a manim class -- most
# visibly ``manim.Succession(rtm_Wait(0.4), ...)``.  Worse, the patched copy
# below was only installed on two of the four modules that import the function
# BY NAME; ``manim.animation.composition`` (and ``manim.scene.scene``) still
# held the original, so the TypeError survived the first fix attempt.
#
# The children are then driven with manim conventions -- ``begin()`` with no
# argument and ``interpolate(alpha)`` with alpha in 0..1 -- while RTM's
# animations read elapsed *seconds*.  ``_RtmAnimationAdapter`` bridges the two
# semantics: ``begin()`` stamps a wall-clock origin (which also keeps RTM's
# own wrapper detectors -- ``ChangeSpeed`` -- happy) and ``interpolate(alpha)``
# replays the child at ``origin + alpha * run_time``.
import manim.animation.animation as _aa
import manim.animation.composition as _comp
import manim.animation.speedmodifier as _sm
import manim.scene.scene as _scene_mod
from manim.animation.animation import Animation as _MAnimAnimation
from manim.animation.animation import prepare_animation as _orig_prepare_animation
from manim.utils.rate_functions import linear as _linear
from real_time_manim.animations.base import Animation as _OurAnimation


class _RtmAnimationAdapter(_MAnimAnimation):
    """Let one manim composite class drive one RTM animation.

    Thin manim-``Animation`` shell around an RTM animation:

    * ``begin()`` / ``interpolate(alpha)`` / ``finish()`` translate manim's
      alpha semantics into RTM's time semantics (``t = origin + alpha *
      run_time``, origin = the wall-clock stamp ``begin()`` recorded -- the
      same convention RTM's own ``AnimationGroup`` uses to tell a manim
      wrapper's alpha from elapsed seconds);
    * ``is_introducer()`` reports ``True`` so manim's group building does not
      PRE-add the child's mobject to the scene at play start -- the mobject is
      presented in ``_setup_scene`` when the child's slot actually begins,
      which is what keeps a nested ``FadeIn``/``Add`` hidden until its turn;
    * ``_setup_scene`` / ``clean_up_from_scene`` / ``update_mobjects`` /
      ``set_rate_func`` forward to the wrapped animation when it implements
      them (RTM's base class does not).
    """

    def __init__(self, inner):
        self._rtm_inner = inner
        mob = getattr(inner, "mobject", None)
        super().__init__(
            mob,
            lag_ratio=float(getattr(inner, "lag_ratio", 0.0) or 0.0),
            run_time=float(getattr(inner, "run_time", 0.0) or 0.0),
            rate_func=getattr(inner, "rate_func", None) or _linear,
            reverse_rate_function=bool(
                getattr(inner, "reverse_rate_function", False)),
            name=getattr(inner, "name", None),
            remover=bool(getattr(inner, "remover", False)),
            introducer=True,
            suspend_mobject_updating=False,
        )
        # manim replaces a None mobject with an empty Mobject(); keep the
        # child's real one (may be None, e.g. Wait) for scene bookkeeping.
        self._rtm_real_mobject = mob
        self._rtm_t0 = None

    # -- manim-facing surface ----------------------------------------------

    def is_introducer(self):
        # See the class docstring: the child presents its own mobject when
        # its slot begins, so it must not be pre-added by group building.
        return True

    def begin(self):
        inner = self._rtm_inner
        begin = getattr(inner, "begin", None)
        if callable(begin):
            try:
                begin()
            except TypeError:
                # subclass with a required start-time argument
                begin(_time.time())
        origin = getattr(inner, "start_time", None)
        self._rtm_t0 = float(origin) if origin else _time.time()

    def interpolate(self, alpha):
        inner = self._rtm_inner
        run_time = float(getattr(inner, "run_time", 0.0) or 0.0)
        a = 0.0 if alpha < 0.0 else (1.0 if alpha > 1.0 else float(alpha))
        t0 = self._rtm_t0
        if t0 is None:
            # interpolate before begin (manim's begin() normally calls
            # interpolate(0)): establish the origin now.
            t0 = self._rtm_t0 = _time.time()
        inner.interpolate(t0 + a * run_time)

    def finish(self):
        try:
            self.interpolate(1.0)
        finally:
            finish = getattr(self._rtm_inner, "finish", None)
            if callable(finish):
                finish()

    def update_mobjects(self, dt):
        update = getattr(self._rtm_inner, "update_mobjects", None)
        if callable(update):
            update(dt)

    def set_rate_func(self, rate_func):
        # ChangeSpeed sets its speed profile on the wrapped animation; RTM's
        # animations apply ``rate_func`` themselves inside interpolate.
        self.rate_func = rate_func
        inner = self._rtm_inner
        setter = getattr(inner, "set_rate_func", None)
        if callable(setter):
            setter(rate_func)
        else:
            try:
                inner.rate_func = rate_func
            except Exception:               # pragma: no cover - defensive
                pass

    def _rtm_carried_mobjects(self):
        inner = self._rtm_inner
        mobs = []
        mob = getattr(inner, "mobject", None)
        if mob is not None:
            mobs.append(mob)
        for extra in getattr(inner, "mobjects", None) or ():
            if extra is not None and all(extra is not m for m in mobs):
                mobs.append(extra)
        cursor = getattr(inner, "cursor", None)
        if cursor is not None and all(cursor is not m for m in mobs):
            mobs.append(cursor)
        return mobs

    def _setup_scene(self, scene):
        if scene is None:
            return
        setup = getattr(self._rtm_inner, "_setup_scene", None)
        if callable(setup):
            setup(scene)
            return
        # RTM's own play presents every animated mobject; mirror that rule so
        # a nested RTM animation inside a manim composite registers its
        # mobjects when its slot activates.
        try:
            present = scene.get_mobject_family_members()
        except Exception:                    # pragma: no cover - stub scenes
            present = list(getattr(scene, "mobjects", None) or ())
        for mob in self._rtm_carried_mobjects():
            if mob not in present:
                try:
                    scene.add(mob)
                except Exception:            # pragma: no cover - stub scenes
                    pass

    def clean_up_from_scene(self, scene):
        inner = self._rtm_inner
        clean = getattr(inner, "clean_up_from_scene", None)
        if callable(clean):
            clean(scene)
        if self.remover and self._rtm_real_mobject is not None:
            try:
                scene.remove(self._rtm_real_mobject)
            except (ValueError, AttributeError):   # not in the scene
                pass

    @property
    def animations(self):
        # Lets render hooks recurse into the wrapped composite's children.
        return getattr(self._rtm_inner, "animations", None)

    def get_all_mobjects(self):
        getter = getattr(self._rtm_inner, "get_all_mobjects", None)
        if callable(getter):
            try:
                return list(getter())
            except Exception:                # pragma: no cover - defensive
                pass
        out = []
        for mob in (self._rtm_real_mobject, self.mobject):
            if mob is not None and all(mob is not m for m in out):
                out.append(mob)
        return out


def _patched_prepare_animation(anim):
    if isinstance(anim, _OurAnimation):
        return _RtmAnimationAdapter(anim)
    return _orig_prepare_animation(anim)


_sm.prepare_animation = _patched_prepare_animation      # speedmodifier (ChangeSpeed)
_aa.prepare_animation = _patched_prepare_animation      # animation module itself
# These two imported the function by name before the patch above existed, so
# their module globals kept the ORIGINAL function -- the direct cause of the
# documented "manim Succession cannot hold a vulkan_bind.Wait" TypeError (A24).
_comp.prepare_animation = _patched_prepare_animation
_scene_mod.prepare_animation = _patched_prepare_animation

# A manim composite nested inside an RTM composite never gets a scene through
# manim's Scene.play (RTM's Succession/AnimationGroup drive their children
# directly), and manim's Animation defines no ``scene`` attribute at all --
# so a slot activation crashed with "… has no attribute 'scene'".  A ``None``
# default turns that crash into manim's own scene-less behaviour; the real
# scene is still stored by ``_setup_anim_scene`` wherever it is available.
if getattr(_MAnimAnimation, "scene", _MAnimAnimation) is _MAnimAnimation:
    _MAnimAnimation.scene = None

# ---------------------------------------------------------------------------
# Broadcast: RTM's default focal point is the mobject's own centre (A32)
# ---------------------------------------------------------------------------
# RTM deliberately diverges from CE here (CE defaults to ORIGIN) so the glow
# follows the object instead of staying at the screen centre.  The default is
# kept -- changing it would silently change every existing RTM render -- but
# EXPLICIT values are always respected, keyword or positional, so
# ``Broadcast(mob, focal_point=ORIGIN)`` gives CE behaviour.  (The previous
# signature `(self, mobject, focal_point=None, **kwargs)` crashed on the
# positional form ``Broadcast(mob, focal_point, n_mobs)``:
# "takes from 2 to 3 positional arguments but 4 were given".)
import manim.animation.specialized as _spec
_orig_broadcast_init = _spec.Broadcast.__init__
def _patched_broadcast_init(self, mobject, *args, **kwargs):
    if args:
        # focal_point passed positionally; None still means "RTM's default".
        if args[0] is None:
            args = (mobject.get_center(),) + args[1:]
    elif kwargs.get("focal_point", None) is None:
        kwargs["focal_point"] = mobject.get_center()
    _orig_broadcast_init(self, mobject, *args, **kwargs)
_spec.Broadcast.__init__ = _patched_broadcast_init

# ---------------------------------------------------------------------------
# manim's Add must be recognised like RTM's own Add (A24, second half)
# ---------------------------------------------------------------------------
# RTM's play pipeline registers ``Add``-mobjects through ``isinstance(anim,
# Add)`` checks against *RTM's* Add class (window/play.py: extraction,
# exclusion from the timed animation list, the legacy path).  manim's Add
# failed every one of them: ``win.play(manin.Add(x))`` even raised CE's
# "total run_time must be > 0" ValueError, because the run_time-less Add was
# still counted as a timed animation, and a nested manim Add never had its
# mobjects registered at all ("RTM only registers its own Add type into the
# scene").
#
# Re-basing manim's Add onto RTM's Add fixes every isinstance site at once
# while keeping the manim Animation base (and therefore manim's own
# ``begin``/``interpolate`` no-ops) intact.  Two small additions on top:
# ``.mobjects`` (RTM's extractor reads that list) and a begin() that flips
# the RTM opacity registry, which is how a *nested* Add's mobjects become
# visible when its slot activates.
from manim.animation.animation import Add as _MAnimAdd
from real_time_manim.animations.add import Add as _OurAdd
from real_time_manim.state import set_anim_opacity as _set_anim_opacity


def _manim_add_mobjects(anim):
    """The mobjects a manim ``Add`` carries (its original varargs)."""
    mobs = getattr(anim, "mobjects", None)
    if mobs:
        return list(mobs)
    mob = getattr(anim, "mobject", None)
    return [mob] if mob is not None else []


if not issubclass(_MAnimAdd, _OurAdd):
    _MAnimAdd.__bases__ = (_OurAdd, _MAnimAnimation)
    # Keep manim's set_default (bound to the CALLING class, not to
    # Animation): RTM's -- MRO-earlier -- version would restore the wrong
    # __init__ on the no-argument reset path.
    _MAnimAdd.set_default = classmethod(_MAnimAnimation.set_default.__func__)

_manim_add_orig_init = _MAnimAdd.__init__
def _manim_add_init_patched(self, *mobjects, _orig=_manim_add_orig_init,
                            **kwargs):
    _orig(self, *mobjects, **kwargs)
    # manim's Add knows only the (possibly grouped) ``mobject``; RTM's play
    # reads the flat list.
    self.mobjects = list(mobjects)
_manim_add_init_patched._rtm_patched = True
if not getattr(_MAnimAdd.__init__, "_rtm_patched", False):
    _MAnimAdd.__init__ = _manim_add_init_patched

_manim_add_orig_begin = _MAnimAdd.begin
def _manim_add_begin_patched(self, _orig=_manim_add_orig_begin):
    # A nested Add's mobjects were registered hidden (``_rtm_deferred_add``);
    # its slot activating -- ``begin()`` in every driving path -- is what
    # must make them appear.  RTM's own Add does the same in interpolate().
    for mob in _manim_add_mobjects(self):
        _set_anim_opacity(mob, 1.0)
    return _orig(self)
_manim_add_begin_patched._rtm_patched = True
if not getattr(_MAnimAdd.begin, "_rtm_patched", False):
    _MAnimAdd.begin = _manim_add_begin_patched

# window/play.py cannot be edited from here, and its Add handling is reached
# only after this module has already been imported by window/__init__ -- so
# install the extraction half lazily-but-eagerly below (bottom of file).

# ---------------------------------------------------------------------------
# override_animation / use_override for RTM's own animation classes (A25)
# ---------------------------------------------------------------------------
# manim's ``Animation.__new__`` consults the mobject's override registry
# (``@override_animation``), but RTM's own Animation base never did, so
# ``vulkan_bind.FadeIn(MySquare())`` ignored a registered override and the
# ``use_override=`` keyword did nothing (wiki: "RTM 未接线重写机制").
#
# The registry lookup also falls back to the SAME-NAMED class in the other
# namespace (manim <-> real_time_manim.animations), so an override written
# against manim's FadeIn applies when the animation is played as RTM's
# FadeIn, and vice versa.  Only exact name matches qualify, so manim's
# "overrides do not apply to subclasses of the animation" rule is preserved.
import manim as _manim_pkg
import real_time_manim.animations as _rtm_animations_pkg
from manim.mobject.mobject import Mobject as _MObject


def _animation_counterpart(animation_class):
    name = getattr(animation_class, "__name__", "")
    if not name or name.startswith("_"):
        return None
    module = getattr(animation_class, "__module__", "") or ""
    if module.startswith("manim"):
        candidate = getattr(_rtm_animations_pkg, name, None)
    elif module.startswith("real_time_manim"):
        candidate = getattr(_manim_pkg, name, None)
    else:
        return None
    if isinstance(candidate, type) and candidate is not animation_class:
        return candidate
    return None


_orig_animation_override_for = _MObject.animation_override_for.__func__

def _patched_animation_override_for(cls, animation_class,
                                    _orig=_orig_animation_override_for):
    func = _orig(cls, animation_class)
    if func is not None:
        return func
    counterpart = _animation_counterpart(animation_class)
    if counterpart is not None:
        return _orig(cls, counterpart)
    return None

_patch_marker = getattr(
    _orig_animation_override_for, "_rtm_counterpart_patch", False)
if not _patch_marker:
    _patched_animation_override_for._rtm_counterpart_patch = True
    _patched_animation_override_for._rtm_orig = _orig_animation_override_for
    _MObject.animation_override_for = classmethod(
        _patched_animation_override_for)

_object_new = object.__new__

def _rtm_animation_new(cls, mobject=None, *args, use_override=True, **kwargs):
    if use_override and isinstance(mobject, _MObject):
        try:
            func = mobject.animation_override_for(cls)
        except Exception:                    # pragma: no cover - defensive
            func = None
        if func is not None:
            _logger.debug(
                "The %s animation has been overridden for %s mobjects.",
                cls.__name__, type(mobject).__name__)
            return func(mobject, *args, **kwargs)
    return _object_new(cls)

if not getattr(_OurAnimation, "_rtm_override_dispatch", False):
    _rtm_animation_new._rtm_override_dispatch = True
    _OurAnimation.__new__ = _rtm_animation_new

# ---------------------------------------------------------------------------
# turn_animation_into_updater / cycle_animation with RTM animations (A26)
# ---------------------------------------------------------------------------
# manim's helper calls ``begin()`` (no argument), ``get_run_time()``,
# ``update_mobjects(dt)`` and drives ``interpolate(alpha)`` -- all manim
# conventions RTM's animations do not implement ("'Create' object has no
# attribute 'get_run_time'" on the first frame).  The patched copy keeps
# manim's own loop for manim animations and bridges RTM's with
# ``t = origin + alpha * run_time``.
import manim.animation.updaters.mobject_update_utils as _mu

_orig_turn_animation_into_updater = _mu.turn_animation_into_updater

def _call_update_mobjects(animation, dt):
    update = getattr(animation, "update_mobjects", None)
    if callable(update):
        update(dt)


def _patched_turn_animation_into_updater(animation, cycle=False, delay=0,
                                         _orig=_orig_turn_animation_into_updater,
                                         **kwargs):
    if not isinstance(animation, _OurAnimation):
        return _orig(animation, cycle=cycle, delay=delay, **kwargs)

    mobject = getattr(animation, "mobject", None)
    if mobject is None:
        # Mirror manim: a Wait has an empty Mobject to carry the updater.
        from manim.mobject.mobject import Mobject as _M
        mobject = _M()
    animation.suspend_mobject_updating = False
    begin = getattr(animation, "begin", None)
    if callable(begin):
        try:
            begin()
        except TypeError:
            begin(_time.time())
    origin = float(getattr(animation, "start_time", None) or _time.time())
    animation.total_time = -float(delay)

    def _update(m, dt):
        if animation.total_time >= 0:
            # read the run_time every tick, like manim's get_run_time()
            run_time = float(getattr(animation, "run_time", 0.0) or 0.0)
            if run_time <= 0:
                # instantly snap to final state once, then remove updater
                animation.interpolate(origin)
                _call_update_mobjects(animation, dt)
                animation.finish()
                m.remove_updater(_update)
                animation.total_time += dt
                return
            ratio = animation.total_time / run_time
            if cycle:
                alpha = ratio % 1.0
            else:
                alpha = 0.0 if ratio < 0.0 else (1.0 if ratio > 1.0 else ratio)
                if alpha >= 1.0:
                    # manim's finish() would interpolate(1); RTM's only marks
                    # the animation finished, so force the final state here.
                    animation.interpolate(origin + run_time)
                    _call_update_mobjects(animation, dt)
                    animation.finish()
                    m.remove_updater(_update)
                    animation.total_time += dt
                    return
            animation.interpolate(origin + alpha * run_time)
            _call_update_mobjects(animation, dt)
        animation.total_time += dt

    mobject.add_updater(_update)
    return mobject


_mu.turn_animation_into_updater = _patched_turn_animation_into_updater
if (hasattr(_manim_pkg, "turn_animation_into_updater")
        and _manim_pkg.turn_animation_into_updater is not _patched_turn_animation_into_updater):
    _manim_pkg.turn_animation_into_updater = _patched_turn_animation_into_updater

# ---------------------------------------------------------------------------
# .animate(lag_ratio=...) must not be swallowed silently (A27)
# ---------------------------------------------------------------------------
# manim's ``_AnimationBuilder.build()`` ``setattr``-s every ``.animate(...)``
# keyword onto the built animation, so nothing RTM-side drops ``lag_ratio=``:
# for a mobject WITH submobjects manim's own ``Animation.interpolate_mobject``
# staggers them per family and RTM renders that geometry (CE-identical).  For
# a mobject WITHOUT submobjects the keyword is inert -- in CE too -- and RTM
# now says so instead of silently accepting it.
from manim.mobject.mobject import _AnimationBuilder as _AnimBuilder

_orig_builder_build = _AnimBuilder.build

def _patched_builder_build(self, _orig=_orig_builder_build):
    anim = _orig(self)
    try:
        lag_ratio = float(self.anim_args.get("lag_ratio", 0.0) or 0.0)
    except Exception:                        # pragma: no cover - defensive
        lag_ratio = 0.0
    if lag_ratio and not getattr(self.mobject, "submobjects", None):
        _warnings.warn(
            "RTM: .animate(lag_ratio=%.2f) has no effect on %s -- it has no "
            "submobjects to stagger (ManimCE behaves the same). Use "
            "AnimationGroup / LaggedStart for staggered group animation."
            % (lag_ratio, type(self.mobject).__name__),
            UserWarning,
            stacklevel=2)
    return anim

_patched_builder_build._rtm_patched = True
if not getattr(_orig_builder_build, "_rtm_patched", False):
    _AnimBuilder.build = _patched_builder_build

# ---------------------------------------------------------------------------
# Add extraction in window/play.py: walk manim's Add/composites too (A24)
# ---------------------------------------------------------------------------
# ``PlayMixin._extract_add_mobjects`` recognises only RTM's Add and RTM's
# composites; a manim ``Succession(Add(a), Wait(1), Add(b, run_time=0.5))``
# therefore never registered its mobjects.  The wrapper below takes the same
# road RTM's own classes take (deferred = hidden until the slot activates)
# and delegates everything else -- RTM types included -- to the original.
try:
    from real_time_manim.window.play import PlayMixin as _PlayMixin

    _orig_extract_add_mobjects = _PlayMixin._extract_add_mobjects

    def _extract_add_mobjects_patched(self, anim, _nested=False):
        if isinstance(anim, _MAnimAdd):
            mobjects = []
            for mob in _manim_add_mobjects(anim):
                # Same contract as the original: a nested Add stays hidden
                # until its slot runs (its begin() flips the registry back),
                # a top-level one is instant.
                mob._rtm_deferred_add = _nested
                if _nested:
                    _set_anim_opacity(mob, 0.0)
                mobjects.append(mob)
            return mobjects
        if isinstance(anim, _comp.AnimationGroup):
            # AnimationGroup covers Succession/LaggedStart; their children are
            # "nested" exactly like RTM composite children are.
            mobjects = []
            for sub in anim.animations:
                mobjects.extend(
                    _extract_add_mobjects_patched(self, sub, _nested=True))
            return mobjects
        return _orig_extract_add_mobjects(self, anim, _nested)

    _extract_add_mobjects_patched._rtm_patched = True
    if not getattr(_orig_extract_add_mobjects, "_rtm_patched", False):
        _PlayMixin._extract_add_mobjects = _extract_add_mobjects_patched
except Exception as exc:                     # pragma: no cover - never block
    _logger.warning("RTM: could not patch PlayMixin._extract_add_mobjects: %s",
                    exc)

# ---------------------------------------------------------------------------
# MathTex: keep manim's \special{dvisvgm:raw} group tags ──────────────────
# manim wraps each tex_string in \special{dvisvgm:raw <g id='uniqueNNN'>} so that
# dvisvgm emits a named SVG group per tex_string, and MathTex then hands every
# group to its own MathTexPart.  That mapping is *exact*: it knows how many glyphs
# a string produced (spaces, `\\` line breaks, `fi`/`ffl` ligatures and LaTeX
# commands all disagree with a character count).
#
# These tags used to be stripped and the glyphs split by position instead, which
# mis-assigns glyphs whenever the per-string character weights do not match the
# per-string glyph counts.  BulletedList is the visible case: of
# "changelog entries\\" / "caching fixes\\" / ... the weights 19/15/14/18 over
# 53 glyphs put the first boundary at 15 instead of 16, so the trailing "s" of
# "entries" landed in the next part -- its dot was then placed left of that "s"
# and the first bullet wrapped onto its own line.  So the original joining is
# left alone and only the splitting below is patched.
