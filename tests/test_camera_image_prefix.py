"""An ImageMobjectFromCamera must see the scene as drawn so far.

Report R10-5 (batch item 2): "ImagesAndSvg 有东西少了" -- three shapes are
missing from RTM's frame.

`ImageMobjectFromCamera.get_pixel_array()` returns `scene.camera.pixel_array`
**live** (`manim/mobject/types/image_mobject.py:336`).  manim's renderer walks
`camera.capture_mobjects(list(scene.mobjects))` in list order, so when it
reaches the image the array already holds the background plus everything
drawn *before* it -- the image becomes a copy of the scene so far.  That is
exactly what CE's video shows: three blobs whose bboxes map back onto the
swatch / badge / quad through `from_camera`'s box (recorded in
logs/prerig_batch10.md).

RTM draws vectors on the GPU and never writes that array
(`vulkan_bind.py::_rasterise_custom_camera` explicitly exempts a plain
`Camera`), so `send_image` uploaded the cleared background: black, invisible,
2172 px of CE content missing.

The fix: before sending a root whose `get_pixel_array()` *is* the camera's
array, reset the camera and rasterise the roots that precede it -- the prefix
CE had already drawn at that point.

Pure Python: a plain manim Camera + a stub DLL, no GPU, no ffmpeg, no DTW.
"""
import os
import sys

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if REPO not in sys.path:
    sys.path.insert(0, REPO)

import numpy as np
import pytest

try:
    import real_time_manim.vulkan_bind as vb
    from manim import (
        LEFT,
        RIGHT,
        WHITE,
        Circle,
        ImageMobjectFromCamera,
        Scene,
        Square,
    )
except Exception as e:  # pragma: no cover - import guard
    pytest.skip("manim/RTM unavailable: %s" % e, allow_module_level=True)


class _Recorder(object):
    """Stands in for the native DLL and keeps every submitted call."""

    def __init__(self):
        self.calls = []

    def __getattr__(self, name):
        def _call(*args, **kwargs):
            self.calls.append((name, args))
            return 0
        return _call


def _build_scene():
    """[bright square] [ImageMobjectFromCamera] [bright circle]."""
    scene = Scene()
    scene.add(Square(side_length=2, fill_color=WHITE, fill_opacity=1,
                     stroke_width=0).move_to(4 * LEFT))
    scene.add(ImageMobjectFromCamera(scene.camera))
    scene.add(Circle(radius=1, fill_color=WHITE, fill_opacity=1,
                     stroke_width=0).move_to(4 * RIGHT))
    return scene


def _sync(scene):
    window = vb.MLWindow(854, 480)
    rec = _Recorder()
    real_dll = window.dll
    window.dll = rec
    try:
        window.sync(scene)
    finally:
        window.dll = real_dll
        window.close()
    return rec


def _camera_px(scene, manim_x, manim_y):
    """Pixel-array coordinates of a manim-space point."""
    arr = np.asarray(scene.camera.pixel_array)
    h, w = arr.shape[0], arr.shape[1]
    return int(round(w / 2 + manim_x * h / 8.0)), int(round(h / 2 - manim_y * h / 8.0))


def _bright(arr, x, y, thresh=200):
    return int(np.max(arr[y, x, :3])) >= thresh


def test_preceding_mobject_reaches_the_camera_array():
    """Red before the fix: the array was still the cleared background."""
    scene = _build_scene()
    _sync(scene)
    arr = np.asarray(scene.camera.pixel_array)
    x, y = _camera_px(scene, -4, 0)
    assert _bright(arr, x, y), (
        "the Square that is drawn BEFORE the ImageMobjectFromCamera never "
        "reached camera.pixel_array at (%d, %d): max RGB %d.  "
        "ImageMobjectFromCamera.get_pixel_array() reads that array live, so "
        "CE's copy of the scene-so-far cannot appear" % (x, y, int(arr[y, x, :3].max()))
    )


def test_only_preceding_mobjects_are_captured():
    """Red before the fix: nothing at all was captured (square absent)."""
    scene = _build_scene()
    _sync(scene)
    arr = np.asarray(scene.camera.pixel_array)
    sx, sy = _camera_px(scene, -4, 0)
    cx, cy = _camera_px(scene, 4, 0)
    assert _bright(arr, sx, sy), (
        "prefix missing: the Square preceding the camera image is not in "
        "camera.pixel_array (max RGB %d at (%d, %d))"
        % (int(arr[sy, sx, :3].max()), sx, sy)
    )
    assert not _bright(arr, cx, cy), (
        "the Circle that comes AFTER the camera image leaked into the capture "
        "-- CE reaches that array only at the image's own position in the "
        "family walk (max RGB %d at (%d, %d))" % (int(arr[cy, cx, :3].max()), cx, cy)
    )


def test_uploaded_texture_contains_the_prefix():
    """Red before the fix: the uploaded bytes were pure background."""
    scene = _build_scene()
    rec = _sync(scene)
    quads = [args for name, args in rec.calls if name == "AddImageQuad"]
    assert quads, "send_image never submitted the camera image at all"
    arr = np.asarray(scene.camera.pixel_array)
    h, w = arr.shape[0], arr.shape[1]
    cam_quads = [a for a in quads if int(a[3]) == w and int(a[4]) == h]
    assert cam_quads, (
        "no %dx%d texture was uploaded (submitted sizes: %r)"
        % (w, h, [(int(a[3]), int(a[4])) for a in quads])
    )
    payload = np.frombuffer(bytes(cam_quads[-1][2]), dtype=np.uint8)
    payload = payload.reshape(h, w, 4)
    sx, sy = _camera_px(scene, -4, 0)
    assert int(payload[sy, sx, :3].max()) >= 200, (
        "the camera image's texture is blank at the Square's position "
        "(max RGB %d) -- the array it reads was never written"
        % int(payload[sy, sx, :3].max())
    )
