# This might not cause a bug or issue, check for other place first --TT Noted
from real_time_manim.animations.write import Write
from real_time_manim.animations.base import (Animation, release_hidden_channels,
                                             resolve_mobject)
from real_time_manim.rate_functions import _linear


class Unwrite(Write):
    def __init__(self, mobject=None, rate_func=_linear, reverse=True, run_time=1.0, **kwargs):
        mobject = resolve_mobject(mobject, kwargs, "Unwrite")
        self._unwrite_reverse = reverse
        # An eraser is a remover in CE (``Write.__init__`` sets
        # ``remover=reverse`` and ``Unwrite`` passes its own ``reverse``, whose
        # default is True).  RTM forwarded ``reverse=False`` to ``Write``, so
        # the eraser never left the scene -- a transparent root accumulating
        # behind every ``Unwrite``.
        kwargs.setdefault("remover", True)
        super().__init__(mobject, rate_func=rate_func, reverse=False, run_time=run_time, **kwargs)

    def begin(self, t):
        super(Write, self).begin(t)

    def _apply_two_phase(self, alpha):
        mob = self.mobject
        has_subs = hasattr(mob, 'submobjects') and mob.submobjects
        if has_subs:
            num_subs = len(mob.submobjects)
            letter_alphas = {}
            for i in range(num_subs):
                if self._unwrite_reverse:
                    idx = num_subs - 1 - i
                else:
                    idx = i
                sub_alpha = self.get_sub_alpha(alpha, idx, num_subs)
                letter_alphas[i] = self.rate_func(1.0 - sub_alpha)
            mob._letter_alphas = letter_alphas
        else:
            mob._vulkan_progress = self.rate_func(1.0 - alpha)

    def finish(self):
        Animation.finish(self)
        mob = self.mobject
        if hasattr(mob, 'submobjects') and mob.submobjects:
            mob._letter_alphas = {i: 0.0 for i in range(len(mob.submobjects))}
        else:
            mob._vulkan_progress = 0.0
        # ...then release it again.  The parked value is what the last drawn
        # frame ends on (finish() runs after it), but a renderer-only channel
        # must not outlive the animation: CE restores the whole path in
        # `ShowPartial.clean_up_from_scene`, so re-adding or re-animating the
        # same Text later shows it whole.  Leaving `_letter_alphas = {0: 0.0}`
        # made every later `Write(txt)`/`add(txt)` blank.
        release_hidden_channels(mob)
