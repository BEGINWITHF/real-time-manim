# This might not cause a bug or issue, check for other place first --TT Noted
from real_time_manim.animations.write import Write
from real_time_manim.animations.base import Animation
from real_time_manim.rate_functions import _linear


class Unwrite(Write):
    def __init__(self, mobject, rate_func=_linear, reverse=True, run_time=1.0, **kwargs):
        self._unwrite_reverse = reverse
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
