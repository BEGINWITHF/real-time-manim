"""Public entry point of the renderer.

`vulkan_bind` is the name users import -- ``from real_time_manim.vulkan_bind
import MLWindow, Create, Wait`` is what the README and the PyPI page show --
so the module stays.  It now only re-exports what the implementation moved
into the ``real_time_manim.window`` subpackage:

    window/patches.py     monkey patches RTM installs on manim
    window/mathtex.py     native MathTex layout + its patches
    window/scene.py       scene / updater drivers
    window/paint_order.py the paint queue and every depth / z-index rule
    window/{core,paint,play,recording}.py   the MLWindow mixins

Importing this module still applies every monkey patch, in the same order as
before the split.
"""

# ruff: noqa: F401  -- this module is a re-export surface.

# The manim primitives and RTM's animation classes have always been part of
# this module's namespace; keep re-exporting them so old imports keep working.
from manim import (
    Square, Circle, Line, Rectangle, Polygon, Polygram,
    Arrow, Dot, DashedLine,
    Arc, Ellipse, Point, Text, VGroup, Group, VMobject, OUT, ORIGIN, WHITE
)
from manim.animation.transform import Transform as _ManimTransform
from manim.animation.transform import FadeTransform as _ManimFadeTransform
from manim.mobject.types.image_mobject import AbstractImageMobject
from manim.mobject.types.point_cloud_mobject import PMobject

from real_time_manim.rate_functions import (
    _smooth, _linear, _rush_into, _rush_from,
    _there_and_back, _slow_into, _double_smooth,
    _wiggle, _lingering, _exponential_decay,
    _squish_rate_func, _sigmoid,
)
from real_time_manim.animations import (
    Animation, Create, Uncreate, DrawBorderThenFill, Write, Unwrite,
    ShowIncreasingSubsets, SpiralIn,
    Blink, TypeWithCursor, UntypeWithCursor,
    Succession, Wait, Add, AnimationGroup, MoveToTarget, Indicate,
    FadeIn, FadeOut, FadeTransform, FadeTransformPieces,
    Rotating, Rotate,
    Transform, ReplacementTransform,
    TransformMatchingAbstractBase, TransformMatchingShapes, TransformMatchingTex,
    GrowFromCenter, GrowArrow, GrowFromEdge, GrowFromPoint, SpinInFromNothing,
    ApplyWave, Circumscribe, ShowPassingFlash, Homotopy, MoveAlongPath,
    set_anim_opacity, get_anim_opacity,
    set_anim_rotation, get_anim_rotation,
    set_anim_rotation_delta, get_anim_rotation_delta, clear_anim_rotation_delta,
    TARGET_FPS, FRAME_DURATION,
    TextDecimalNumber,
)
from real_time_manim.render.util import (
    manim_to_screen, rotate_point, get_fill_rgb, get_stroke_rgb, get_stroke_w,
)
from real_time_manim.render.shapes import ShapeMixin
from real_time_manim.render.text import TextMixin

from real_time_manim.window import MLWindow

from real_time_manim.window.patches import (
    _OrigChangeDecimalToValue,
    _OrigChangingDecimal,
    _OurAnimation,
    _aa,
    _orig_broadcast_init,
    _orig_prepare_animation,
    _patched_broadcast_init,
    _patched_prepare_animation,
    _sm,
    _spec,
)
from real_time_manim.window.mathtex import (
    MathTexPart,
    _LATEX_UNICODE,
    _NORMAL_PART_BUFF,
    _OrigMathTex,
    _OrigMathTexInit,
    _SCRIPT_SCALE,
    _SCRIPT_X_TIGHTEN,
    _SUB_TRANS,
    _SUPER_TRANS,
    _USE_NATIVE_MATHTEX,
    _build_math_part,
    _consume_script_content,
    _convert_visible_math_text,
    _layout_math_parts,
    _make_script_token,
    _make_text_token,
    _mathtex_init_dispatch,
    _native_mathtex_init,
    _patched_break_up_by_substrings,
    _position_script_token,
    _tokenize_math_text,
)
from real_time_manim.window.recording import BITMAPFILEHEADER, BITMAPINFOHEADER
from real_time_manim.window.scene import (
    _RASTER_TOKEN,
    _drive_mobject_updaters,
    _raster_debug,
    _run_mobject_updaters,
    _setup_anim_scene,
)
from real_time_manim.window.paint_order import (
    NATIVE_MAX_POLYGON_VERTS,
    _PaintQueue,
    container_subs,
    depth_key,
    depth_order,
    family_index,
    foreground_mobjects_of,
    foreground_to_front,
    lend_grow,
    native_dll_is_live,
    release_flash_window,
    release_grow,
    release_split,
    scan_z_index,
    split_mixed_depth,
    split_mixed_z,
    unit_z_index,
)
