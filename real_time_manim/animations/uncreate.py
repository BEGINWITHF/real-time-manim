# This might not cause a bug or issue, check for other place first --TT Noted
from real_time_manim.animations.create import Create
from real_time_manim.animations.base import release_hidden_channels, resolve_mobject


class Uncreate(Create):
    """Like ``Create`` but in reverse -- manim CE parity.

    manim CE (``manim/animation/creation.py``)::

        class Uncreate(Create):
            def __init__(self, mobject, reverse_rate_function=True,
                         remover=True, **kwargs):
                super().__init__(mobject,
                                 reverse_rate_function=reverse_rate_function,
                                 introducer=False, remover=remover, **kwargs)

    i.e. CE reverses through ``reverse_rate_function`` and leaves ``rate_func``
    at ``Animation``'s default **smooth**, so the effective progress is
    ``smooth(1 - t)``.  RTM used to pass ``rate_func=lambda t: 1 - t`` instead:
    numerically a *linear* unwind, which is visibly different from CE's eased
    one and -- because ``Create.interpolate`` applies ``rate_func`` AFTER the
    reverse -- could not be expressed by ``reverse_rate_function`` at all.

    ``Create.interpolate`` computes ``alpha = rate_func(1 - alpha)`` when
    ``reverse_rate_function`` is set, which is exactly CE's
    ``Animation.get_sub_alpha`` (``self.rate_func(1 - (value - lower))``), so
    delegating to the base class reproduces CE's curve rather than approximating
    it.  Callers that pass an explicit ``rate_func`` keep it (CE forwards
    ``**kwargs`` the same way); the reversal stays on by default and can be
    switched off with ``reverse_rate_function=False``.
    """

    def __init__(self, mobject=None, run_time=1.0, lag_ratio=1.0, remover=True,
                 rate_func=None, reverse_rate_function=True, **kwargs):
        mobject = resolve_mobject(mobject, kwargs, "Uncreate")
        # ``rate_func=None`` falls through to Animation's default ``_smooth`` --
        # the same curve CE's Uncreate ends up with.
        super().__init__(mobject, run_time=run_time, lag_ratio=lag_ratio,
                         remover=remover, rate_func=rate_func,
                         reverse_rate_function=reverse_rate_function, **kwargs)

    def finish(self):
        # A remover must not leave the mobject in "erased" render state: CE
        # restores the whole path in `ShowPartial.clean_up_from_scene`, so a
        # mobject shown again later comes back whole.  RTM's channel stayed at
        # `_vulkan_progress = 0.0`, and every later draw of the same mobject
        # submitted nothing (see base.release_hidden_channels).
        super().finish()
        release_hidden_channels(self.mobject)
