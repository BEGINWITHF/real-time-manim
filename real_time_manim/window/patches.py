"""Monkey patches applied to manim itself when RTM is imported.

Kept apart from the renderer: importing this module changes upstream
behaviour, so it must stay obvious which upstream entry points RTM
rewires and why."""



from manim import ChangingDecimal as _OrigChangingDecimal
from manim import ChangeDecimalToValue as _OrigChangeDecimalToValue
_OrigChangingDecimal.check_validity_of_input = lambda self, dm: None
_OrigChangeDecimalToValue.check_validity_of_input = lambda self, dm: None

from manim.animation.animation import prepare_animation as _orig_prepare_animation
from real_time_manim.animations.base import Animation as _OurAnimation
def _patched_prepare_animation(anim):
    if isinstance(anim, _OurAnimation):
        return anim
    return _orig_prepare_animation(anim)
import manim.animation.speedmodifier as _sm
_sm.prepare_animation = _patched_prepare_animation
import manim.animation.animation as _aa
_aa.prepare_animation = _patched_prepare_animation

# Broadcast should emanate from the broadcast mobject's own position by
# default (focal_point = mobject.get_center()), so the glow follows the
# object instead of staying at manim's default ORIGIN.
import manim.animation.specialized as _spec
_orig_broadcast_init = _spec.Broadcast.__init__
def _patched_broadcast_init(self, mobject, focal_point=None, **kwargs):
    if focal_point is None:
        focal_point = mobject.get_center()
    _orig_broadcast_init(self, mobject, focal_point=focal_point, **kwargs)
_spec.Broadcast.__init__ = _patched_broadcast_init

# ── MathTex: keep manim's \special{dvisvgm:raw} group tags ──────────────────
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
