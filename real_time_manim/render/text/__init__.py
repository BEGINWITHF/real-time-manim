"""Text rendering: glyphs and the generic bezier path sender."""

from real_time_manim.render.text.glyphs import GlyphMixin
from real_time_manim.render.text.vmobject import VMobjectMixin, _mitre_room_filter


class TextMixin(GlyphMixin, VMobjectMixin):
    """Text senders, assembled."""


__all__ = ["TextMixin", "_mitre_room_filter"]
