from manim import Group, VGroup
from real_time_manim.animations.transform_matching_abstract_base import TransformMatchingAbstractBase


class TransformMatchingTex(TransformMatchingAbstractBase):
    @staticmethod
    def get_mobject_parts(mobject):
        """Recursively extract MathTexPart leaf submobjects.

        For Groups/VGroups, recurse into each direct child.  MathTex
        instances (which now carry tex_strings after the vulkan_bind
        monkeypatch) yield their MathTexPart submobjects directly.
        Individual MathTexPart objects (which carry tex_string) are
        returned as-is — never recursed into their Text children."""
        # MathTex (now VGroup via class reassignment): has tex_strings list
        # Must check BEFORE tex_string, because MathTex also has tex_string
        if hasattr(mobject, 'tex_strings'):
            return list(mobject.submobjects)
        # MathTexPart: has its own tex_string but no tex_strings — return it directly
        if hasattr(mobject, 'tex_string'):
            return [mobject]
        if isinstance(mobject, (Group, VGroup)):
            parts = []
            for s in mobject.submobjects:
                parts.extend(TransformMatchingTex.get_mobject_parts(s))
            return parts
        # Fallback: any leftover mobject with children
        if hasattr(mobject, 'submobjects') and mobject.submobjects:
            return list(mobject.submobjects)
        return [mobject]

    @staticmethod
    def get_mobject_key(mobject):
        """Return the tex_string that identifies a MathTexPart for matching."""
        return getattr(mobject, 'tex_string',
                       getattr(mobject, '_tex_string',
                               str(id(mobject))))
