"""Mobjects representing raster images."""

from __future__ import annotations

__all__ = ["AbstractImageMobject", "ImageMobject", "ImageMobjectFromCamera"]

import pathlib
from typing import TYPE_CHECKING, Any

import numpy as np
from PIL import Image
from PIL.Image import Resampling

from manim.mobject.geometry.shape_matchers import SurroundingRectangle

from ... import config
from ...camera.moving_camera import MovingCamera
from ...constants import *
from ...mobject.mobject import Mobject
from ...utils.bezier import interpolate
from ...utils.color import (
    WHITE,
    YELLOW_C,
    ManimColor,
    ParsableManimColor,
    color_to_int_rgb,
)
from ...utils.images import change_to_rgba_array, get_full_raster_image_path

__all__ = ["ImageMobject", "ImageMobjectFromCamera"]

if TYPE_CHECKING:
    from typing import Self

    import numpy.typing as npt

    from manim.typing import PixelArray, StrPath

    from ...camera.moving_camera import MovingCamera


class AbstractImageMobject(Mobject):
    """
    Automatically filters out black pixels

    Parameters
    ----------
    scale_to_resolution
        At this resolution the image is placed pixel by pixel onto the screen, so it
        will look the sharpest and best.
        This is a custom parameter of ImageMobject so that rendering a scene with
        e.g. the ``--quality low`` or ``--quality medium`` flag for faster rendering
        won't effect the position of the image on the screen.
    """

    def __init__(
        self,
        scale_to_resolution: int,
        pixel_array_dtype: str = "uint8",
        resampling_algorithm: Resampling = Resampling.BICUBIC,
        **kwargs: Any,
    ) -> None:
        self.pixel_array_dtype = pixel_array_dtype
        self.scale_to_resolution = scale_to_resolution
        self.set_resampling_algorithm(resampling_algorithm)
        super().__init__(**kwargs)

    def get_pixel_array(self) -> PixelArray:
        raise NotImplementedError()

    def mark_texture_dirty(self) -> Self:
        """Invalidate RTM's cached texture for this image.

        ``send_image`` caches the opaque RGB buffer, its digest and its ctypes
        copy between frames, keyed by these revision counters.  manim's own
        mutators (``set_color``/``set_opacity``/``interpolate_color``) bump
        them; raw writes into ``pixel_array`` should call this once, and
        ``ImageMobjectFromCamera.get_pixel_array`` bumps it because the camera
        array changes behind the same object.
        """
        self._rtm_tex_rev = int(getattr(self, "_rtm_tex_rev", 0) or 0) + 1
        self._rtm_alpha_rev = int(getattr(self, "_rtm_alpha_rev", 0) or 0) + 1
        return self

    def set_color(
        self,
        color: ParsableManimColor = YELLOW_C,
        alpha: Any = None,
        family: bool = True,
    ) -> Self:
        # Likely to be implemented in subclasses, but no obligation
        raise NotImplementedError()

    def set_resampling_algorithm(self, resampling_algorithm: int) -> Self:
        """
        Sets the interpolation method for upscaling the image. By default the image is
        interpolated using bicubic algorithm. This method lets you change it.
        Interpolation is done internally using Pillow, and the function besides the
        string constants describing the algorithm accepts the Pillow integer constants.

        Parameters
        ----------
        resampling_algorithm
            An integer constant described in the Pillow library,
            or one from the RESAMPLING_ALGORITHMS global dictionary,
            under the following keys:

            * 'bicubic' or 'cubic'
            * 'nearest' or 'none'
            * 'box'
            * 'bilinear' or 'linear'
            * 'hamming'
            * 'lanczos' or 'antialias'
        """
        if resampling_algorithm not in RESAMPLING_ALGORITHMS.values():
            raise ValueError(
                "resampling_algorithm has to be an int, one of the values defined in "
                "RESAMPLING_ALGORITHMS or a Pillow resampling filter constant. "
                "Available algorithms: 'bicubic' (or 'cubic'), 'nearest' (or 'none'), "
                "'bilinear' (or 'linear').",
            )

        self.resampling_algorithm = resampling_algorithm
        return self

    def reset_points(self) -> Self:
        """Sets :attr:`points` to be the four image corners."""
        self.points = np.array(
            [
                UP + LEFT,
                UP + RIGHT,
                DOWN + LEFT,
                DOWN + RIGHT,
            ],
        )
        self.center()
        h, w = self.get_pixel_array().shape[:2]
        if self.scale_to_resolution:
            height = h / self.scale_to_resolution * config["frame_height"]
        else:
            height = 3  # this is the case for ImageMobjectFromCamera
        self.stretch_to_fit_height(height)
        self.stretch_to_fit_width(height * w / h)
        return self


class ImageMobject(AbstractImageMobject):
    """Displays an Image from a numpy array or a file.

    Parameters
    ----------
    scale_to_resolution
        At this resolution the image is placed pixel by pixel onto the screen, so it
        will look the sharpest and best.
        This is a custom parameter of ImageMobject so that rendering a scene with
        e.g. the ``--quality low`` or ``--quality medium`` flag for faster rendering
        won't effect the position of the image on the screen.


    Example
    -------
    .. manim:: ImageFromArray
        :save_last_frame:

        class ImageFromArray(Scene):
            def construct(self):
                image = ImageMobject(np.uint8([[0, 100, 30, 200],
                                               [255, 0, 5, 33]]))
                image.height = 7
                self.add(image)


    Changing interpolation style:

    .. manim:: ImageInterpolationEx
        :save_last_frame:

        class ImageInterpolationEx(Scene):
            def construct(self):
                img = ImageMobject(np.uint8([[63, 0, 0, 0],
                                                [0, 127, 0, 0],
                                                [0, 0, 191, 0],
                                                [0, 0, 0, 255]
                                                ]))

                img.height = 3

                group = Group()
                algorithm_texts = ["nearest", "linear", "cubic"]
                for algorithm_text in algorithm_texts:
                    algorithm = RESAMPLING_ALGORITHMS[algorithm_text]
                    img_copy = img.copy().set_resampling_algorithm(algorithm)
                    img_copy.add(Text(algorithm_text).scale(0.5).next_to(img_copy, UP))
                    group.add(img_copy)

                group.arrange()
                self.add(group)
    """

    def __init__(
        self,
        filename_or_array: StrPath | npt.NDArray,
        scale_to_resolution: int = QUALITIES[DEFAULT_QUALITY]["pixel_height"],
        invert: bool = False,
        image_mode: str = "RGBA",
        **kwargs: Any,
    ) -> None:
        self.fill_opacity: float = 1
        self.stroke_opacity: float = 1
        self.invert_image = invert
        self.image_mode = image_mode
        if isinstance(filename_or_array, (str, pathlib.PurePath)):
            path = get_full_raster_image_path(filename_or_array)
            image = Image.open(path).convert(self.image_mode)
            self.pixel_array = np.array(image)
            self.path = path
        else:
            self.pixel_array = np.array(filename_or_array)
        self.pixel_array_dtype = kwargs.get("pixel_array_dtype", "uint8")
        self.pixel_array = change_to_rgba_array(
            self.pixel_array, self.pixel_array_dtype
        )
        if self.invert_image:
            self.pixel_array[:, :, :3] = (
                np.iinfo(self.pixel_array_dtype).max - self.pixel_array[:, :, :3]
            )
        self.orig_alpha_pixel_array = self.pixel_array[:, :, 3].copy()
        # A scalar opacity for uniform-alpha images.  The alpha channel stays
        # untouched (send_image applies this as the quad's opacity), so a fade
        # costs no per-pixel write; per-pixel alpha images keep writing the
        # channel because their mask is the texture.
        self._rtm_tex_opacity = 1.0
        self._rtm_uniform_alpha = bool(
            self.orig_alpha_pixel_array.size
            and int(self.orig_alpha_pixel_array.min())
            == int(self.orig_alpha_pixel_array.max())
        )
        super().__init__(scale_to_resolution, **kwargs)

    def get_pixel_array(self) -> PixelArray:
        """A simple getter method."""
        return self.pixel_array

    def set_color(
        self,
        color: ParsableManimColor = YELLOW_C,
        alpha: Any = None,
        family: bool = True,
    ) -> Self:
        rgb = color_to_int_rgb(color)
        self.pixel_array[:, :, :3] = rgb
        if alpha is not None:
            self.pixel_array[:, :, 3] = int(255 * alpha)
            # `set_color(alpha=...)` writes the channel directly (manim's
            # semantics); drop the scalar and let set_opacity write pixels
            # again so a later fade matches CE exactly.
            self._rtm_tex_opacity = 1.0
            self._rtm_uniform_alpha = False
        for submob in self.submobjects:
            submob.set_color(color, alpha, family)
        self.color = ManimColor(color)
        self.mark_texture_dirty()
        return self

    def set_opacity(self, alpha: float) -> Self:
        """Sets the image's opacity.

        Parameters
        ----------
        alpha
            The alpha value of the object, 1 being opaque and 0 being
            transparent.

        Notes
        -----
        For a uniform-alpha image the pixel channel is left untouched: RTM's
        renderer applies this value as the quad's opacity, so a fade costs no
        per-pixel write.  An image whose alpha channel is a mask still writes
        the channel (and re-uploads it when the value changes).
        """
        if getattr(self, "_rtm_uniform_alpha", False):
            # Uniform alpha: send_image applies it as the quad opacity.  Keep
            # the alpha channel untouched so a fade costs no per-pixel write.
            # Quantise like the old uint8 write so the rendered alpha is
            # bit-identical to the channel path.
            base = 0
            if self.orig_alpha_pixel_array.size:
                base = int(self.orig_alpha_pixel_array.flat[0])
            self._rtm_tex_opacity = (
                (int(base * alpha) / float(base)) if base > 0 else 0.0
            )
        else:
            self.pixel_array[:, :, 3] = self.orig_alpha_pixel_array * alpha
            self._rtm_tex_opacity = 1.0
            self._rtm_alpha_rev = (
                int(getattr(self, "_rtm_alpha_rev", 0) or 0) + 1
            )
        self.stroke_opacity = alpha
        return self

    def fade(self, darkness: float = 0.5, family: bool = True) -> Self:
        """Sets the image's opacity using a 1 - alpha relationship.

        Parameters
        ----------
        darkness
            The alpha value of the object, 1 being transparent and 0 being
            opaque.
        family
            Whether the submobjects of the ImageMobject should be affected.
        """
        self.set_opacity(1 - darkness)
        super().fade(darkness, family)
        return self

    def interpolate_color(
        self, mobject1: Mobject, mobject2: Mobject, alpha: float
    ) -> Self:
        """Interpolates the array of pixel color values from one ImageMobject
        into an array of equal size in the target ImageMobject.

        Parameters
        ----------
        mobject1
            The ImageMobject to transform from.

        mobject2
            The ImageMobject to transform into.

        alpha
            Used to track the lerp relationship. Not opacity related.
        """
        assert isinstance(mobject1, ImageMobject)
        assert isinstance(mobject2, ImageMobject)
        assert mobject1.pixel_array.shape == mobject2.pixel_array.shape, (
            f"Mobject pixel array shapes incompatible for interpolation.\n"
            f"Mobject 1 ({mobject1}) : {mobject1.pixel_array.shape}\n"
            f"Mobject 2 ({mobject2}) : {mobject2.pixel_array.shape}"
        )
        self.fill_opacity = interpolate(
            mobject1.fill_opacity,
            mobject2.fill_opacity,
            alpha,
        )
        self.stroke_opacity = interpolate(
            mobject1.stroke_opacity,
            mobject2.stroke_opacity,
            alpha,
        )
        self._rtm_tex_opacity = interpolate(
            getattr(mobject1, "_rtm_tex_opacity", 1.0),
            getattr(mobject2, "_rtm_tex_opacity", 1.0),
            alpha,
        )
        self._rtm_uniform_alpha = (
            getattr(mobject1, "_rtm_uniform_alpha", False)
            and getattr(mobject2, "_rtm_uniform_alpha", False)
        )
        if not self._rtm_uniform_alpha:
            # A per-pixel mask already carries the fade; do not apply the
            # scalar a second time.
            self._rtm_tex_opacity = 1.0
        self.pixel_array = interpolate(
            mobject1.pixel_array,
            mobject2.pixel_array,
            alpha,
        ).astype(self.pixel_array_dtype)
        self.mark_texture_dirty()
        return self

    def get_style(self) -> dict[str, Any]:
        return {
            "fill_color": ManimColor(self.color.to_rgb()).to_hex(),
            "fill_opacity": self.fill_opacity,
        }


# TODO, add the ability to have the dimensions/orientation of this
# mobject more strongly tied to the frame of the camera it contains,
# in the case where that's a MovingCamera


class ImageMobjectFromCamera(AbstractImageMobject):
    def __init__(
        self,
        camera: MovingCamera,
        default_display_frame_config: dict[str, Any] | None = None,
        **kwargs: Any,
    ) -> None:
        self.camera = camera
        if default_display_frame_config is None:
            default_display_frame_config = {
                "stroke_width": 3,
                "stroke_color": WHITE,
                "buff": 0,
            }
        self.default_display_frame_config = default_display_frame_config
        self.pixel_array = self.camera.pixel_array
        super().__init__(scale_to_resolution=False, **kwargs)

    # TODO: Get rid of this.
    def get_pixel_array(self) -> PixelArray:
        self.pixel_array = self.camera.pixel_array
        self.mark_texture_dirty()
        return self.pixel_array

    def add_display_frame(self, **kwargs: Any) -> Self:
        config = dict(self.default_display_frame_config)
        config.update(kwargs)
        self.display_frame = SurroundingRectangle(self, **config)
        self.add(self.display_frame)
        return self

    def interpolate_color(
        self, mobject1: Mobject, mobject2: Mobject, alpha: float
    ) -> Self:
        assert isinstance(mobject1, ImageMobjectFromCamera)
        assert isinstance(mobject2, ImageMobjectFromCamera)
        assert mobject1.pixel_array.shape == mobject2.pixel_array.shape, (
            f"Mobject pixel array shapes incompatible for interpolation.\n"
            f"Mobject 1 ({mobject1}) : {mobject1.pixel_array.shape}\n"
            f"Mobject 2 ({mobject2}) : {mobject2.pixel_array.shape}"
        )
        self.pixel_array = interpolate(
            mobject1.pixel_array,
            mobject2.pixel_array,
            alpha,
        ).astype(self.pixel_array_dtype)
        self.mark_texture_dirty()
        return self
