"""Construction and per-frame synchronisation of the render window.

Owns the DLL binding, the camera publish path and `sync`, the entry
point that walks the scene once per frame."""

import ctypes
import hashlib
import os
import sys
from typing import TYPE_CHECKING

import numpy as np

from real_time_manim.window.paint_order import (
    _PaintQueue,
    depth_key,
    family_index,
    foreground_mobjects_of,
    scan_z_index,
)
from real_time_manim.window.scene import _RASTER_TOKEN, _raster_debug

if TYPE_CHECKING:
    from manim import Scene


class CoreMixin:
    # This renderer supports exactly ONE output format: 1920x1080 at 60 fps.
    # Anything smaller is refused rather than silently accepted, because a small
    # window hides resolution-bound defects completely -- the native per-frame
    # vertex cap is only reached past ~1.3 M px, so a Surface scene that lost 60%
    # of its fills at 1080p looked perfect at 480p for months.
    SUPPORTED_WIDTH = 1920
    SUPPORTED_HEIGHT = 1080
    SUPPORTED_FPS = 60
    # When True, play() records a timeline instead of rendering (see play()).
    _schedule_mode = False
    # Windows created while this is True are built hidden (never shown), so
    # offline work -- frame export, fast record, batch rendering -- does not pop
    # windows onto the desktop.  Set it around a scene run, then restore.
    _hidden_default = False
    # Every constructed window is registered here (used by frames.FrameServer
    # to grab the window a scene created for itself).
    _registry = []


    def __init__(self, w=SUPPORTED_WIDTH, h=SUPPORTED_HEIGHT, hidden=None):
        # NB: a bare class-level name is NOT in scope inside a method body
        # (class namespaces are not enclosing scopes) -- these must be `self.`.
        if (int(w), int(h)) != (self.SUPPORTED_WIDTH, self.SUPPORTED_HEIGHT):
            print(f"[rtm] forcing {self.SUPPORTED_WIDTH}x{self.SUPPORTED_HEIGHT}: "
                  f"RTM supports high quality only (asked for {int(w)}x{int(h)})")
            w, h = self.SUPPORTED_WIDTH, self.SUPPORTED_HEIGHT
        if hidden is None:
            hidden = bool(getattr(type(self), '_hidden_default', False))
        self.hidden = bool(hidden)
        self.win_w = w
        self.win_h = h
        self.frame_count = 0
        self.scene: Scene | None = None
        self._active_anims = []
        # Schedule mode (2.0.0): when the class flag _schedule_mode is True,
        # play() records animations on a global timeline instead of rendering,
        # so any frame can later be produced on demand via build_timeline().
        self._sched = []          # list of (start_seconds, animation)
        self._cursor = 0.0        # current end of the recorded timeline
        self._defer_close = bool(getattr(type(self), '_schedule_mode', False))
        type(self)._registry.append(self)
        self._recording = False
        self._record_dir = None
        self._record_frame_idx = 0
        self._record_path = None
        self._record_fps = 60

        # Fast offline record — renders at full speed via simulated time
        self._fast_record = False
        self._fast_record_path = None
        self._fast_record_fps = 60
        self._fast_record_sim_time = 0.0
        self._fast_record_frame_idx = 0
        self._fast_record_segment = None  # (start_frame, end_frame) or None for all

        # `core.py` lives one level below the package, so the package root --
        # where the bundled DLL and (from a source checkout) ../dist live --
        # is two directories up.
        base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        # Search order: bundled lib (pip-installed package) → dev repo release → dev repo debug
        if sys.platform == "darwin":
            candidates = [
                os.path.join(base_dir, "vulkan_core.dylib"),
                os.path.normpath(os.path.join(base_dir, "..", "dist", "release", "vulkan_core.dylib")),
                os.path.normpath(os.path.join(base_dir, "..", "dist", "debug", "vulkan_core.dylib")),
            ]
            lib_kind = "vulkan_core.dylib"
            build_hint = "native/build_mac.sh (requires Vulkan SDK + MoltenVK)"
        elif sys.platform == "win32":
            candidates = [
                os.path.join(base_dir, "vulkan_core.dll"),
                os.path.normpath(os.path.join(base_dir, "..", "dist", "release", "vulkan_core.dll")),
                os.path.normpath(os.path.join(base_dir, "..", "dist", "debug", "vulkan_core.dll")),
            ]
            lib_kind = "vulkan_core.dll"
            build_hint = "native/build.ps1 (requires Vulkan SDK + MinGW-w64)"
        else:
            # Falling into the Windows branch used to report "vulkan_core.dll
            # not found" on Linux, which sent the reader looking for a file
            # that does not exist for their platform at all.
            raise RuntimeError(
                "real-time-manim ships native Vulkan backends for Windows and "
                "macOS only; %r is not supported. Run on Windows or macOS, or "
                "build a native backend for this platform and place it next "
                "to real_time_manim/." % sys.platform
            )
        dll_path = next((p for p in candidates if os.path.exists(p)), None)
        if dll_path is None:
            raise FileNotFoundError(
                f"{lib_kind} not found. If running from source, build it with {build_hint}."
            )

        self.dll = ctypes.CDLL(dll_path)

        self.dll.Vulkan_Init.restype = ctypes.c_int
        self.dll.Vulkan_Init.argtypes = [ctypes.c_int, ctypes.c_int]
        self.dll.Vulkan_Tick.restype = ctypes.c_int
        self.dll.Vulkan_Tick.argtypes = []
        self.dll.Vulkan_Shutdown.restype = None
        self.dll.Vulkan_Shutdown.argtypes = []
        self.dll.ClearShapes.restype = None
        self.dll.ClearShapes.argtypes = []

        self.dll.AddRect.restype = None
        self.dll.AddRect.argtypes = [
            ctypes.c_float, ctypes.c_float, ctypes.c_float,
            ctypes.c_float, ctypes.c_float,
            ctypes.c_int, ctypes.c_int, ctypes.c_int,
            ctypes.c_int, ctypes.c_int, ctypes.c_int,
            ctypes.c_float, ctypes.c_float,
            ctypes.c_float,
        ]
        self.dll.AddCircle.restype = None
        self.dll.AddCircle.argtypes = [
            ctypes.c_float, ctypes.c_float, ctypes.c_float,
            ctypes.c_int, ctypes.c_int, ctypes.c_int,
            ctypes.c_int, ctypes.c_int, ctypes.c_int,
            ctypes.c_float, ctypes.c_float,
            ctypes.c_float,
        ]
        self.dll.AddLine.restype = None
        self.dll.AddLine.argtypes = [
            ctypes.c_float, ctypes.c_float,
            ctypes.c_float, ctypes.c_float,
            ctypes.c_int, ctypes.c_int,
            ctypes.c_int, ctypes.c_int,
            ctypes.c_float,
        ]
        self.dll.AddLineStrip.restype = None
        self.dll.AddLineStrip.argtypes = [
            ctypes.POINTER(ctypes.c_float),
            ctypes.POINTER(ctypes.c_float),
            ctypes.c_int,
            ctypes.c_int, ctypes.c_int,
            ctypes.c_int, ctypes.c_int,
            ctypes.c_float,
        ]
        self.dll.AddEllipse.restype = None
        self.dll.AddEllipse.argtypes = [
            ctypes.c_float, ctypes.c_float,
            ctypes.c_float, ctypes.c_float,
            ctypes.c_int, ctypes.c_int, ctypes.c_int,
            ctypes.c_int, ctypes.c_int, ctypes.c_int,
            ctypes.c_float, ctypes.c_float,
            ctypes.c_float,
        ]
        self.dll.AddPolygon.restype = None
        self.dll.AddPolygon.argtypes = [
            ctypes.c_float, ctypes.c_float,
            ctypes.c_int, ctypes.c_int, ctypes.c_int,
            ctypes.c_int, ctypes.c_int, ctypes.c_int,
            ctypes.c_float, ctypes.c_int,
            ctypes.POINTER(ctypes.c_float),
            ctypes.c_float, ctypes.c_float,
            ctypes.c_int,
        ]
        self.dll.AddDashedLine.restype = None
        self.dll.AddDashedLine.argtypes = [
            ctypes.c_float, ctypes.c_float,
            ctypes.c_float, ctypes.c_float,
            ctypes.c_int, ctypes.c_int,
            ctypes.c_int, ctypes.c_int,
            ctypes.c_float, ctypes.c_float,
            ctypes.c_float,
        ]
        self.dll.AddPoint.restype = None
        self.dll.AddPoint.argtypes = [
            ctypes.c_float, ctypes.c_float,
            ctypes.c_int, ctypes.c_int, ctypes.c_int,
            ctypes.c_float,
            ctypes.c_float,
        ]
        self.dll.AddBezierPath.restype = None
        self.dll.AddBezierPath.argtypes = [
            ctypes.POINTER(ctypes.c_float), ctypes.c_int,
            ctypes.c_int, ctypes.c_int, ctypes.c_int, ctypes.c_float,
            ctypes.c_int, ctypes.c_int, ctypes.c_int, ctypes.c_float,
            ctypes.c_float, ctypes.c_int, ctypes.c_int,
            ctypes.c_float,
            # second fill stop + its screen-space axis (straight-alpha gradient)
            ctypes.c_int, ctypes.c_int, ctypes.c_int,
            ctypes.c_float, ctypes.c_float, ctypes.c_float, ctypes.c_float,
        ]

        self.dll.SaveScreenshot.restype = ctypes.c_int
        self.dll.SaveScreenshot.argtypes = [ctypes.c_char_p]

        # Textured quads (plan 4.4B): one stable token per mobject owning a GPU
        # texture slot, refreshed only when the pixel digest changes.
        self.dll.AddImageQuad.restype = None
        self.dll.AddImageQuad.argtypes = [
            ctypes.c_ulonglong, ctypes.c_ulonglong,
            ctypes.POINTER(ctypes.c_ubyte), ctypes.c_int, ctypes.c_int,
            ctypes.POINTER(ctypes.c_float), ctypes.c_float,
        ]

        # Frame clear colour (manim's `camera.background_color`).  Optional: a DLL
        # built before this existed simply keeps clearing to black.
        _set_background = getattr(self.dll, 'SetBackgroundColor', None)
        if _set_background is not None:
            _set_background.restype = None
            _set_background.argtypes = [ctypes.c_float, ctypes.c_float, ctypes.c_float]
        self._set_background = _set_background

        # Hidden-window init and show/hide are Windows-only exports (mac builds
        # the window through Vulkan_Init and hides it via orderOut on shutdown).
        # Bind them the way SetBackgroundColor is bound above: the call sites
        # already getattr-guard, but these bind lines must not touch a missing
        # symbol.
        _set_visible = getattr(self.dll, 'Vulkan_SetWindowVisible', None)
        if _set_visible is not None:
            _set_visible.restype = None
            _set_visible.argtypes = [ctypes.c_int]
        _init_ex = getattr(self.dll, 'Vulkan_InitEx', None)
        if _init_ex is not None:
            _init_ex.restype = ctypes.c_int
            _init_ex.argtypes = [ctypes.c_int, ctypes.c_int, ctypes.c_int]

        init_ex = _init_ex
        if self.hidden and init_ex is not None:
            # Create the window without ever showing it: offline work (frame
            # export, fast record) must not pop a window onto the desktop.
            if not init_ex(w, h, 1):
                raise RuntimeError("Vulkan_InitEx failed")
        else:
            if self.dll.Vulkan_Init(w, h) != 1:
                raise RuntimeError("Vulkan_Init failed")
            if self.hidden:
                # Older DLL without hidden creation: hide right after building.
                self.set_visible(False)

    @property
    def hwnd(self):
        """This window's Win32 handle (``None`` off Windows / before init).

        The DLL never exports the handle, so it is looked up by class+title
        (``window/win32.py``) and cached -- ``recording.py`` and the frame
        preview both need it to talk to the OS window.
        """
        from real_time_manim.window import win32

        cached = getattr(self, "_hwnd_cache", None)
        if cached and win32.user32 is not None:
            import ctypes
            if win32.user32.IsWindow(cached):
                return cached
            self._hwnd_cache = None
        found = win32.find_video_hwnd()
        self._hwnd_cache = found
        return found

    def _publish_background_color(self, scene):
        """Hand native the frame's clear colour.

        manim lets a scene override it (`self.camera.background_color`, falling
        back to `config.background_color`); the native side used to hard-code
        black, so a scene with a light background rendered on black (measured on
        the gallery logo scene: CE luma 220 vs RTM 9.5, the largest mismatch in
        the suite).

        `camera.background_opacity` is deliberately *not* applied here.  In CE it
        only rides in the frame's alpha channel: the background pixels keep the
        colour at full strength and the alpha is dropped by the opaque
        (yuv420p) video writer, so the video shows the full colour whatever the
        opacity.  Scaling the clear colour by it (the earlier behaviour) made
        RTM disagree with CE: on `01-场景与相机/相机/01-Camera-background` the
        background read RTM `(16,34,55)` vs CE `(29,57,93)` for 48 frames after
        `background_opacity = 0.6` was set.  RTM only writes opaque video, so it
        publishes the colour unscaled and stays frame-exact with CE.
        """
        setter = getattr(self, "_set_background", None)
        if setter is None:
            return
        camera = getattr(scene, "camera", None)
        colour = getattr(camera, "background_color", None)
        if colour is None:
            try:
                from manim import config as _config
                colour = _config["background_color"]
            except Exception:
                return
        try:
            if isinstance(colour, str):
                from manim.utils.color.core import ManimColor
                colour = ManimColor(colour)
            rgb = colour.to_rgb() if hasattr(colour, "to_rgb") else colour
            values = [float(v) for v in list(rgb)[:3]]
        except Exception:
            return
        if len(values) == 3:
            setter(*values)

    @staticmethod
    def _camera_needs_raster(scene, cam):
        """True for a Camera subclass that redefines how a frame is captured.

        Only *unhandled* subclasses qualify (plan 5.4): a Camera that overrides
        ``capture_mobjects``/``get_frame`` can apply arbitrary per-pixel effects that
        no vector pipeline can express, but the ones RTM already models properly --
        MovingCamera (5.1), ThreeDCamera (5.2) -- must keep the vector path, or every
        camera scene would silently become a slow full-screen rasterisation.
        """
        try:
            from manim.camera.camera import Camera as _BaseCamera
        except Exception:                              # pragma: no cover
            return False
        if type(cam) is _BaseCamera:
            return False
        handled = set()
        for module, names in (
                ("manim.camera.moving_camera", ("MovingCamera",)),
                ("manim.camera.three_d_camera", ("ThreeDCamera", "SpecialThreeDCamera")),
                ("manim.camera.mapping_camera", ("MappingCamera", "OldMultiCamera")),
        ):
            for name in names:
                try:
                    mod = __import__(module, fromlist=[name])
                    handled.add(getattr(mod, name))
                except Exception:
                    pass
        # A camera that renders *other cameras* into image mobjects composites a
        # second viewport inside its own frame (ZoomedScene's MultiCamera does
        # this in capture_mobjects, inset included).  There is no vector
        # equivalent, and it must be checked before the MovingCamera exemption
        # below -- MultiCamera *is* a MovingCamera.  The list is empty until
        # activate_zooming() runs, so un-zoomed scenes keep the vector path.
        if getattr(cam, "image_mobjects_from_cameras", None):
            return True
        if isinstance(cam, tuple(handled)) or getattr(cam, "zoomed_display", None) is not None:
            return False
        for klass in type(cam).__mro__:
            if klass is _BaseCamera:
                break
            if "capture_mobjects" in klass.__dict__ or "get_frame" in klass.__dict__:
                return True
        return False

    def _rasterise_custom_camera(self, scene):
        """Draw a custom camera's frame as one textured quad (plan 5.4).

        The scene's *own* camera does the rasterising, so whatever the subclass does
        to the pixels is included by construction.  Correct but slow: one
        rasterisation per frame, which is the accepted price of a fallback.
        Returns True when it drew the frame.
        """
        cam = getattr(scene, "camera", None)
        needs = cam is not None and self._camera_needs_raster(scene, cam)
        _raster_debug(f"camera={type(cam).__name__ if cam is not None else None} "
                      f"needs_raster={needs}")
        if not needs:
            return False
        try:
            reset = getattr(cam, "reset", None)
            if callable(reset):
                reset()                                # clear the previous frame
            # Rasterise at the window's own resolution.  manim's camera is built
            # from config.pixel_* (1920x1080 by default in this harness) while
            # the window is 854x480, so the fallback was rasterising ~5x the
            # pixels and only then downscaling: moving/zoomed scenes cost seconds
            # per frame (MovingZoomedSceneAround's 180 frames exceeded the 600 s
            # harness timeout) and a downscaled raster is blurrier than CE's own
            # 854x480 render.
            try:
                if (int(cam.pixel_width) != self.win_w
                        or int(cam.pixel_height) != self.win_h):
                    cam.reset_pixel_shape(self.win_h, self.win_w)
            except Exception:
                pass
            cam.capture_mobjects(list(scene.mobjects))
            pixels = np.asarray(cam.pixel_array, dtype=np.float32)
        except Exception as exc:
            _raster_debug(f"  capture failed: {type(exc).__name__}: {exc}")
            return False                               # fall back to the vector path
        if pixels.ndim != 3 or pixels.shape[2] < 3:
            _raster_debug(f"  unusable pixel_array: {getattr(pixels, 'shape', None)}")
            return False
        _raster_debug(f"  pixels {pixels.shape} min={float(pixels.min()):.3f} "
                      f"max={float(pixels.max()):.3f} mean={float(pixels.mean()):.3f}")

        rgb = pixels[..., :3]
        if float(rgb.max()) <= 1.0 + 1e-3:              # manim hands back 0..1 floats
            rgb = rgb * 255.0
        image = np.empty(pixels.shape[:2] + (4,), dtype=np.uint8)
        image[..., :3] = np.clip(rgb, 0, 255).astype(np.uint8)
        # The rasterised frame is already composited over the background, and
        # manim's own writer takes the RGB and ignores the alpha channel.  RTM
        # draws it as a texture blended with SRC_ALPHA, so a camera alpha below
        # 255 dimmed the whole frame (measured MovingZoomedSceneAround: every
        # white texel came back (251,253,250) instead of (255,255,255) and
        # (10,10,10) became (4,6,3), a uniform -1.9% and 220 -> 756 distinct
        # colours).  Force it opaque to match CE.
        image[..., 3] = 255

        height, width = image.shape[:2]
        data = np.ascontiguousarray(image)
        buf = (ctypes.c_ubyte * data.nbytes).from_buffer_copy(data.tobytes())
        quad = (ctypes.c_float * 8)(
            0.0, 0.0, float(self.win_w), 0.0,
            float(self.win_w), float(self.win_h), 0.0, float(self.win_h))
        key = int.from_bytes(hashlib.blake2b(data.tobytes(), digest_size=8).digest(),
                             "little")
        self.dll.AddImageQuad(_RASTER_TOKEN, key, buf, int(width), int(height), quad, 1.0)
        return True

    def sync(self, scene, angle=0.0):
        # Phase 5: publish this frame's camera viewport (None for a plain Camera,
        # so non-camera scenes keep the fixed default frame).
        from real_time_manim.camera_state import set_viewport_from_scene
        set_viewport_from_scene(scene)
        self.dll.ClearShapes()
        self._publish_background_color(scene)
        # Phase 5.4: a custom camera's frame comes back as pixels, not geometry.
        if self._rasterise_custom_camera(scene):
            return
        skip_ids = getattr(self, '_skip_mob_ids', None)
        # Also skip any root that is a descendant of another root (prevents
        # double render).  One walk of every family, not a root-pairs cross
        # product: the old form re-walked the whole tree once per (i, j) pair,
        # which is O(n^2 * family) -- a scene with a few hundred roots in
        # `scene.mobjects` spent more time here than it did drawing.
        #
        # A root always contains itself, so "some OTHER root also contains this
        # id" is exactly "the id was seen under two or more roots".  Skipping on
        # that condition removes the DESCENDANT and keeps the ancestor, which is
        # what CE's ``remove_list_redundancies`` does (it keeps the first
        # occurrence, the one inside the container).
        # CE renders ``scene.mobjects`` plus the foreground mobjects that are
        # not already there (``CairoRenderer.update_frame``), so they belong
        # at the end of the list this frame is painted from.
        roots = list(scene.mobjects) + list(foreground_mobjects_of(scene))
        # A member listed twice is painted once, at its first occurrence
        # (``remove_list_redundancies``); without this the descendant skip
        # below would find "other is r" and drop it from BOTH positions.
        unique_roots = []
        _seen_roots = set()
        for _r in roots:
            if id(_r) in _seen_roots:
                continue
            _seen_roots.add(id(_r))
            unique_roots.append(_r)
        roots = unique_roots
        del unique_roots, _seen_roots
        def _family_ids(node):
            stack = [node]
            while stack:
                cur = stack.pop()
                yield id(cur)
                stack.extend(getattr(cur, 'submobjects', []) or ())
        extra_skip = set()
        _owner = {}                 # id -> index of the first root that owns it
        _shared = set()             # ids owned by two or more roots
        for _i, _r in enumerate(roots):
            for _nid in _family_ids(_r):
                prev = _owner.get(_nid)
                if prev is None:
                    _owner[_nid] = _i
                elif prev != _i:
                    _shared.add(_nid)
        for _r in roots:
            if id(_r) in _shared:
                extra_skip.add(id(_r))
        # A root that is skipped because another root already holds it does not
        # paint where it sits in the list: CE drops that occurrence entirely
        # (``remove_list_redundancies`` keeps the first one, inside the
        # container), so the frame has to be ordered by family position instead
        # of by list position -- see ``family_index``.
        descendant_roots = set(extra_skip)
        # ``MovingCamera.frame`` is *not* special-cased here: in CE it is an
        # ordinary mobject that only shows up when the scene explicitly adds
        # it (its default frame has zero stroke/fill, so nothing is painted),
        # and an explicitly added, visible frame *is* drawn.  RTM used to skip
        # it outright, which made ``self.add(self.camera.frame)`` a no-op
        # compared with CE; only do that for frames that are not scene
        # content, i.e. never add it implicitly -- see the sync() caller.
        if skip_ids is None:
            skip_ids = extra_skip
        else:
            skip_ids |= extra_skip
        # Same-font Text roots on one visual line that need baseline alignment.
        self._row_text_ids = self._text_row_ids(scene, skip_ids)
        # manim's ThreeDCamera leaves fixed-in-frame mobjects unprojected
        # (transform_points_pre_display returns their points unchanged), so a
        # 3D scene's title/caption stays put instead of being rotated away.  RTM
        # had no such path at all: every root went through the 3D rotation and
        # the caption landed off-frame (measured: FixedInFrameMObjectTest and
        # the captions of ThreeDSurfaceLab / PolyhedraShowcase missing).
        from real_time_manim.camera_state import (
            get_viewport)
        fixed_ids = set()
        cam = getattr(scene, "camera", None)
        for fixed in getattr(cam, "fixed_in_frame_mobjects", ()) or ():
            fixed_ids.add(id(fixed))
        cam_images = self._camera_image_prefixes(cam, roots)
        # Paint order follows CE's own sort (see _PaintQueue): CE flattens the
        # whole family, stable-sorts it by ``z_index``, and -- under a
        # ThreeDCamera -- stable-sorts that by camera-space depth, so cells of
        # different roots interleave.  Both cases are walked: ``_send`` hands
        # each unit to the queue with its own depth key, its own ``z_index``
        # and its own family position, while fixed overlays and camera images
        # keep whole-mobject handling (an unrotated frame, a prefix replay).
        # A scene that uses no ``z_index`` and has no 3D camera still paints
        # its roots whole, in document order -- the pre-existing fast path.
        viewport = get_viewport()
        is_3d = viewport is not None and getattr(viewport, "rotation", None) is not None
        # ``Camera(use_z_index=False)`` turns CE's z sort off too.
        z_mode = bool(getattr(cam, "use_z_index", True)) and scan_z_index(roots)
        # A root that is also somebody's child paints inside that container, so
        # list order stops being paint order for it (see ``family_index``).
        overlap = any(id(m) in descendant_roots for m in roots)
        walk = is_3d or z_mode or overlap
        # The map costs one dict entry per family member, and it is only ever
        # needed when list order and paint order can differ -- i.e. when a root
        # is also somebody's child.  Otherwise the walk order *is* CE's family
        # order (no member is reachable from two roots), so the queue falls
        # back to the visit sequence and skips the build entirely.
        index = family_index(roots) if overlap else {}
        queue = _PaintQueue(viewport, index, z_mode)
        saved_queue = getattr(self, "_paint_queue", None)
        self._paint_queue = queue
        try:
            for idx, mob in enumerate(roots):
                if skip_ids and id(mob) in skip_ids:
                    continue
                if walk and idx not in cam_images and id(mob) not in fixed_ids:
                    self._send(mob, angle, parent_alpha=1.0)
                    continue
                queue.add(
                    depth_key(mob, viewport),
                    self._root_paint(cam, roots, idx, mob, angle, fixed_ids,
                                     cam_images),
                    mob,
                )
        finally:
            self._paint_queue = saved_queue
        queue.flush()

