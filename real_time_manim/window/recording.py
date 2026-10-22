"""Screenshots and video capture.

Pixels come from the Vulkan swapchain readback (`screenshot`, the fast-record
pipe and the live `start_record` worker); the BMP headers below are what the
fallback path parses when a DLL has no raw readback export."""

import ctypes
import os
import sys
import time
import shutil
import subprocess
import tempfile


class BITMAPINFOHEADER(ctypes.Structure):
    _pack_ = 1
    _fields_ = [
        ("biSize", ctypes.c_uint32),
        ("biWidth", ctypes.c_long),
        ("biHeight", ctypes.c_long),
        ("biPlanes", ctypes.c_uint16),
        ("biBitCount", ctypes.c_uint16),
        ("biCompression", ctypes.c_uint32),
        ("biSizeImage", ctypes.c_uint32),
        ("biXPelsPerMeter", ctypes.c_long),
        ("biYPelsPerMeter", ctypes.c_long),
        ("biClrUsed", ctypes.c_uint32),
        ("biClrImportant", ctypes.c_uint32),
    ]

class BITMAPFILEHEADER(ctypes.Structure):
    _pack_ = 1
    _fields_ = [
        ("bfType", ctypes.c_uint16),
        ("bfSize", ctypes.c_uint32),
        ("bfReserved1", ctypes.c_uint16),
        ("bfReserved2", ctypes.c_uint16),
        ("bfOffBits", ctypes.c_uint32),
    ]


def fast_pipe_ffmpeg_args(width, height, fps, pix_fmt, out_path, threads=None):
    """The ffmpeg argv that encodes a raw frame pipe (fast record, single piped).

    Shared by the live ``enable_fast_record`` pipe and the frame-parallel
    workers (``real_time_manim._record_worker``) so both halves of a split
    record produce frames with identical encoder settings -- otherwise the
    concatenated segments would not match the single-pass output.

    ``threads`` caps the *encoder's* thread pool.  x264 defaults to ~1.5x the
    core count, and several workers each doing that oversubscribes the machine:
    4 concurrent workers measured 17.3 ms/frame with their encoders against
    8.0 ms/frame with exactly the same loops and no encoder.  A single-process
    record leaves it None, so its command -- and its bitstream -- is unchanged.

    ``-vf scale=out_range=pc`` / ``-color_range pc`` keep the frames full-range:
    the default limited-range conversion scales Y by 219/255 and swscale
    truncates where manim's own encoder rounds, which decoded flat #808080 one
    level low and, through the chroma round trip, shifted flat scenes by
    (-4,-2,-5) RGB -- just outside tolerance.
    """
    args = [
        "ffmpeg", "-y",
        "-f", "rawvideo", "-pixel_format", pix_fmt,
        "-video_size", "%dx%d" % (width, height),
        "-framerate", str(fps),
        "-i", "-",
        "-c:v", "libx264", "-pix_fmt", "yuv420p",
        "-vf", "scale=out_range=pc",
        "-color_range", "pc",
        "-crf", "18", "-preset", "fast",
    ]
    if threads is not None:
        args += ["-threads", str(int(threads))]
    args.append(out_path)
    return args


def encoder_threads(jobs, cpus=None):
    """Threads to give EACH worker's encoder when ``jobs`` of them run at once.

    The workers are CPU-bound while rendering, so the encoders must not take the
    whole machine: one core per worker is left for the frame loop and the rest
    are shared out.  A single worker (the default path) gets None -- x264's own
    auto setting -- so its output is untouched.
    """
    jobs = max(1, int(jobs))
    if jobs < 2:
        return None
    cpus = int(cpus if cpus is not None else (os.cpu_count() or 4))
    return max(1, min(8, (cpus - jobs) // jobs))


class RecordingMixin:

    def screenshot(self, path):
        # The native side opens the file through the ANSI C runtime, so the
        # path has to arrive in the system codepage.  UTF-8 bytes came back as
        # mojibake ("cn_name_中文.bmp" landed as "cn_name_涓枃.bmp") and a
        # non-ASCII directory failed outright (SaveScreenshot returned 0, so
        # fast-record's segment/BMP mode silently wrote zero frames).
        if isinstance(path, str):
            if sys.platform == "win32":
                try:
                    path_bytes = path.encode('mbcs')
                except UnicodeEncodeError:
                    path_bytes = path.encode('utf-8')
            else:
                path_bytes = path.encode('utf-8')
        else:
            path_bytes = path
        return self.dll.SaveScreenshot(path_bytes)

    def request_readback(self):
        """Arm the next drawn frame to copy itself for readback.

        Must be called *before* the tick that draws the frame you want.  A
        presented swapchain image is owned by the presentation engine, so
        copying it afterwards returns undefined pixels; the engine copies the
        frame while it still owns it instead.

        The DLL answers with the ring slot the pixels will land in (newer
        builds); it is remembered as ``_readback_slot`` so a deferred reader
        (``_capture_screenshot_to_pipe``) can pick them up later without
        waiting for the GPU.
        """
        fn = getattr(self.dll, 'Vulkan_RequestReadback', None)
        if fn is not None:
            self._readback_slot = int(fn())


    def enable_fast_record(self, path, fps=60, segment=None, hidden=True, count_only=False):
        """Enable fast offline recording.

        Args:
            path: Output path (MP4 file for pipe mode, directory for BMP mode)
            fps: Frame rate
            segment: (start_frame, end_frame) for multi-segment BMP mode,
                     None for single-process pipe mode
            hidden: Hide the Vulkan window
            count_only: Only count frames — no capture, no GPU rendering
        """
        self._fast_record = True
        self._fast_record_path = os.path.abspath(path) if path else ""
        if int(fps) != self.SUPPORTED_FPS:
            print(f"[rtm] forcing {self.SUPPORTED_FPS} fps: RTM supports high "
                  f"quality only (asked for {fps})")
            fps = self.SUPPORTED_FPS
        self._fast_record_fps = fps
        self._fast_record_segment = segment
        self._fast_record_frame_idx = 0
        self._fast_record_count_only = count_only
        # Deferred-readback state (see _fast_capture_via_slots): the ring slot
        # whose pixels are still to be written out.
        self._fast_slot_pending = None
        self._fast_raw_buf = None
        self._readback_slot = None
        w, h = self.win_w, self.win_h

        # Hide window for faster rendering (no compositing)
        if hidden and sys.platform == "win32":
            # `as _wintypes`: a bare `import ctypes.wintypes` would bind the
            # local name ``ctypes`` for this whole function and shadow the
            # module import above on platforms that skip this branch.
            import ctypes.wintypes as _wintypes  # noqa: F401
            user32 = ctypes.windll.user32
            hwnd = user32.FindWindowW(None, "Real Time Manim")
            if hwnd:
                user32.ShowWindow(hwnd, 0)  # SW_HIDE

        if count_only:
            self._fast_record_pipe_mode = False
        elif segment is not None:
            # BMP mode: each frame saved via SaveScreenshot (no pipe overhead)
            os.makedirs(self._fast_record_path, exist_ok=True)
            self._fast_record_pipe_mode = False
            print(f"[FastRecord] BMP mode {segment} → {path}/")
        else:
            # Pipe mode: SaveScreenshot → parse BMP → pipe BGR to ffmpeg
            self._fast_record_pipe_mode = True
            self._fast_w = w
            self._fast_h = h
            self._fast_row_size = w * 3
            self._fast_row_padded = ((w * 3 + 3) // 4) * 4
            # Newer DLLs hand back the raw BGRA framebuffer with no per-pixel
            # conversion (`SaveScreenshotRawBGRA`); ffmpeg eats bgra directly and
            # drops the alpha, so the per-pixel BGRA->BGR loop disappears.  The
            # BMP route stays as the fallback for a DLL without that export (and
            # for macOS).  The bare `raw_bgra` alias is what
            # tools/check_bindings.py can see, hence the explicit argtypes.
            raw_bgra = getattr(self.dll, "SaveScreenshotRawBGRA", None)
            if raw_bgra is not None:
                raw_bgra.restype = ctypes.c_int
                raw_bgra.argtypes = [
                    ctypes.POINTER(ctypes.c_ubyte), ctypes.c_int,
                    ctypes.POINTER(ctypes.c_int)]
            self._fast_raw_bgra = raw_bgra
            # And the ring-slot reader, which lets the record loop read frame k
            # only after frame k+1 was submitted -- hiding the GPU fence wait
            # (~2 ms of an ~8 ms frame).  Same bare-alias form as above.
            slot_bgra = getattr(self.dll, "SaveScreenshotSlotBGRA", None)
            if slot_bgra is not None:
                slot_bgra.restype = ctypes.c_int
                slot_bgra.argtypes = [
                    ctypes.c_int, ctypes.POINTER(ctypes.c_ubyte),
                    ctypes.c_int, ctypes.POINTER(ctypes.c_int)]
            self._fast_slot_bgra = slot_bgra
            pix_fmt = "bgra" if self._fast_raw_bgra else "bgr24"
            ffmpeg_cmd = fast_pipe_ffmpeg_args(w, h, fps, pix_fmt,
                                               self._fast_record_path)
            self._ffmpeg = subprocess.Popen(
                ffmpeg_cmd, stdin=subprocess.PIPE, stderr=subprocess.DEVNULL)
            self._fast_tmp_bmp = os.path.join(tempfile.gettempdir(),
                f"manim_fast_{os.getpid()}_{id(self)}.bmp")
            # A record must not be paced by the display (see _set_unpaced).
            self._set_unpaced(True)
            print(f"[FastRecord] Pipe: {w}x{h} @ {fps} fps ({pix_fmt}) → {path}")

    def _set_unpaced(self, unpaced):
        """Let (or stop) the window present without waiting for the display.

        Called with True while a record is running and for any hidden window: a
        record must never be capped by the refresh rate (measured: an *empty*
        scene spent 6.9 ms of an 8.3 ms frame waiting on the display).  A visible
        window goes back to vsync so live playback stays tear-free and paced.
        """
        unpaced_fn = getattr(self.dll, "Vulkan_SetUnpaced", None)
        if unpaced_fn is not None:
            unpaced_fn.restype = None
            unpaced_fn.argtypes = [ctypes.c_int]
            unpaced_fn(1 if unpaced else 0)

    def set_visible(self, visible=True):
        """Show or hide the window after it was created.

        Used to build a window hidden (offline frame export / fast record) and
        only reveal it when a human is meant to watch (FrameServer.show_frame).
        """
        visible = bool(visible)
        fn = getattr(self.dll, 'Vulkan_SetWindowVisible', None)
        if fn is not None:
            fn(1 if visible else 0)
        elif sys.platform == "win32":
            # Older DLL without the export: hide/show by window title.
            user32 = ctypes.windll.user32
            hwnd = user32.FindWindowW(None, "Real Time Manim")
            if hwnd:
                user32.ShowWindow(hwnd, 5 if visible else 0)  # SW_SHOW / SW_HIDE
        self.hidden = not visible
        # A hidden window has nothing to pace for, a visible one does.
        self._set_unpaced(not visible)

    def close(self):
        if getattr(self, '_defer_close', False):
            return                    # keep the window alive for on-demand frames
        self._unregister()
        self.dll.Vulkan_Shutdown()

    def _unregister(self):
        """Drop this window from the class registry.

        Every constructed MLWindow registers itself there; without this a process
        that opens many windows (batch runs, harnesses) keeps them all alive.
        Pure bookkeeping -- safe to call in any state, no GPU involved.
        """
        reg = type(self)._registry
        while self in reg:
            reg.remove(self)

    def _capture_screenshot_to_pipe(self):
        """Copy the frame the recorder just drew into ffmpeg's stdin.

        Three routes, all ending in tightly packed rows at ``self._fast_w``:

        * ``SaveScreenshotSlotBGRA`` (newest DLL): one frame behind, so the GPU
          fence wait disappears -- see :meth:`_fast_capture_via_slots`.
        * ``SaveScreenshotRawBGRA`` (newer DLL): the raw framebuffer, one memcpy
          right after the draw, piped verbatim as ``bgra``.
        * ``SaveScreenshot`` (fallback): a BMP on disk, read back and de-padded
          into ``bgr24``.
        """
        if getattr(self, '_fast_slot_bgra', None) is not None:
            return self._fast_capture_via_slots()
        if self._fast_raw_bgra is not None:
            return self._capture_raw_bgra_to_pipe()
        return self._capture_bmp_to_pipe()

    def _fast_capture_via_slots(self):
        """Queue this frame and write out the previous one.

        Reading a frame right after drawing it blocks the CPU on the GPU fence
        (measured ~2 ms of an ~8 ms 1080p frame).  Doing the *next* frame's work
        first -- evaluate, upload, submit -- leaves the GPU that long to finish,
        so by the time the slot is read the wait is over.  The staging buffer
        carries two slots precisely so the newer frame's copy cannot land on
        pixels nobody has read yet (native/platform.c: SS_SLOTS).
        """
        prev = self._fast_slot_pending
        if prev is not None:
            self._fast_write_slot(prev)
        slot = getattr(self, '_readback_slot', None)
        self._fast_slot_pending = slot if (slot is not None and slot >= 0) else None

    def _fast_write_slot(self, slot):
        """Encode one buffered frame from the readback ring (see the DLL)."""
        w, h = self._fast_w, self._fast_h
        need = w * h * 4
        buf = self._fast_raw_buf
        if buf is None or len(buf) < need:
            buf = (ctypes.c_ubyte * need)()
            self._fast_raw_buf = buf
        out_size = ctypes.c_int(need)
        if not self._fast_slot_bgra(slot, buf, need, ctypes.byref(out_size)):
            # That slot holds no completed copy: the frame that would have
            # serviced it was skipped (resize / window gone).  Dropping it keeps
            # the stream's rows consistent with -video_size.
            return
        if out_size.value != need:
            return
        self._ffmpeg.stdin.write(memoryview(buf)[:need])

    def _fast_drain_slot(self):
        """Write the last buffered frame (nothing follows it to hide behind)."""
        prev = getattr(self, '_fast_slot_pending', None)
        if prev is not None:
            self._fast_write_slot(prev)
            self._fast_slot_pending = None

    def _capture_raw_bgra_to_pipe(self):
        w, h = self._fast_w, self._fast_h
        need = w * h * 4
        buf = getattr(self, '_fast_raw_buf', None)
        if buf is None or len(buf) < need:
            buf = (ctypes.c_ubyte * need)()
            self._fast_raw_buf = buf
        out_size = ctypes.c_int(need)
        if not self._fast_raw_bgra(buf, need, ctypes.byref(out_size)):
            return                      # no frame present yet (or size changed)
        # A window resized mid-record would change the row layout under ffmpeg's
        # fixed -video_size: drop the frame instead of shearing the rest.
        if out_size.value != need:
            return
        self._ffmpeg.stdin.write(memoryview(buf)[:need])

    def _capture_bmp_to_pipe(self):
        """SaveScreenshot → parse BMP → pipe tightly packed BGR to ffmpeg.

        BMP rows are padded to a 4-byte boundary ((w*3 + 3) & ~3 == 2564 bytes
        at 854 px wide), but ffmpeg's ``bgr24`` with ``-video_size w x h`` expects
        tightly packed rows.  Piping the payload verbatim therefore lands every
        row 2 bytes late, which shears the picture horizontally by ~0.67 px per
        row -- a vertical line comes out as a diagonal.  The padding has to be
        stripped here (this is what _fast_row_padded exists for).
        """
        tmp = self._fast_tmp_bmp
        self.dll.SaveScreenshot(tmp.encode('utf-8'))
        with open(tmp, 'rb') as f:
            f.seek(54)
            data = f.read()

        row_size = self._fast_row_size                 # w * 3, what ffmpeg wants
        padded = self._fast_row_padded                 # what the BMP carries

        # ffmpeg's -video_size is fixed for the whole stream, so a BMP whose
        # size changed under us (the window was resized mid-record) cannot be
        # fed in: every following row would land at the wrong offset and shear
        # the picture for the rest of the video.  Drop the frame instead.
        # The dimensions live in the 54-byte header we seeked past, so re-read
        # it rather than trusting a cached value.
        with open(tmp, 'rb') as f:
            hdr = f.read(54)
        bmp_w = int.from_bytes(hdr[18:22], 'little', signed=True)
        bmp_h = abs(int.from_bytes(hdr[22:26], 'little', signed=True))
        if bmp_w != self._fast_w or bmp_h != self._fast_h:
            return
        if padded == row_size:
            self._ffmpeg.stdin.write(data)
            return

        height = self._fast_h
        try:
            import numpy as np
            rows = np.frombuffer(data, dtype=np.uint8, count=padded * height)
            self._ffmpeg.stdin.write(rows.reshape(height, padded)[:, :row_size].tobytes())
        except Exception:                              # numpy unavailable
            out = bytearray(row_size * height)
            for y in range(height):
                src = y * padded
                out[y * row_size:(y + 1) * row_size] = data[src:src + row_size]
            self._ffmpeg.stdin.write(bytes(out))

    def _finish_fast_record(self):
        """Finish recording: close ffmpeg pipe or report BMP count."""
        if not self._fast_record:
            return
        if getattr(self, '_fast_record_count_only', False):
            print(f"[FastRecord] Count: {self._fast_record_frame_idx} frames")
        elif getattr(self, '_fast_record_pipe_mode', False):
            try:
                self._fast_drain_slot()          # the frame nobody follows
                self._ffmpeg.stdin.close()
                self._ffmpeg.wait()
                sz = os.path.getsize(self._fast_record_path) / 1024
                print(f"[FastRecord] Saved: {self._fast_record_path} "
                      f"({self._fast_record_frame_idx} frames, {sz:.0f} KB)")
            except Exception as e:
                print(f"[FastRecord] ffmpeg failed: {e}")
            try:
                os.unlink(self._fast_tmp_bmp)
            except Exception:
                pass
        else:
            bmps = [f for f in os.listdir(self._fast_record_path) if f.endswith('.bmp')]
            print(f"[FastRecord] BMP: {len(bmps)} frames in {self._fast_record_path}")
        self._fast_record = False
        # Back to what the window's visibility wants: hidden stays unpaced,
        # a window someone is watching goes back to vsync (see _set_unpaced).
        self._set_unpaced(bool(getattr(self, 'hidden', True)))

    def start_record(self, path="output.mp4", fps=60):
        if self._recording:
            return
        self._record_path = os.path.abspath(path)
        if int(fps) != self.SUPPORTED_FPS:
            print(f"[rtm] forcing {self.SUPPORTED_FPS} fps: RTM supports high "
                  f"quality only (asked for {fps})")
            fps = self.SUPPORTED_FPS
        self._record_fps = fps
        self._record_dir = tempfile.mkdtemp(prefix="manim_record_")
        self._record_frame_idx = 0
        self._recording = True
        self._record_start_time = time.time()
        import threading
        self._record_stop_event = threading.Event()
        self._record_thread = threading.Thread(target=self._record_worker, daemon=True)
        self._record_thread.start()
        print(f"[Record] Recording to {self._record_path} at {fps} fps")

    def _record_worker(self):
        # Captures the Vulkan framebuffer directly via SaveScreenshot (real
        # readback), NOT the composited screen. This is immune to window
        # occlusion/scaling that would corrupt a screen-based capture.
        # On macOS SaveScreenshot is two-phase (arm → next frame copies),
        # so only advance the frame index when a BMP was actually written —
        # gaps in the file sequence would otherwise truncate ffmpeg's input.
        interval = 1.0 / self._record_fps
        next_slot = time.time()
        while not self._record_stop_event.is_set():
            try:
                path = os.path.join(self._record_dir, f"frame_{self._record_frame_idx:06d}.bmp")
                if self.screenshot(path):
                    self._record_frame_idx += 1
                    # pace writes at the nominal fps; poll aggressively
                    # between the arm and read phases (two-phase readback)
                    next_slot += interval
                    wait = next_slot - time.time()
                    if wait > 0:
                        self._record_stop_event.wait(wait)
                    continue
            except Exception:
                pass
            # arm cycle: retry shortly — each capture needs one arm + one read
            self._record_stop_event.wait(0.004)
        self._record_thread = None

    def stop_record(self):
        if not self._recording:
            return
        self._record_stop_event.set()
        self._recording = False
        if self._record_thread:
            self._record_thread.join(timeout=2.0)
            self._record_thread = None
        frame_dir = self._record_dir
        output = self._record_path
        total = self._record_frame_idx
        duration = time.time() - getattr(self, '_record_start_time', time.time())
        # Use actual capture fps as input framerate so video duration
        # matches wall-clock scene time — avoids speed-up from slow GDI.
        fps = max(total / duration, 1.0) if duration > 0 else float(self._record_fps)
        print(f"[Record] Captured {total} frames in {duration:.1f}s "
              f"({fps:.1f} fps), encoding to {output} ...")
        if total == 0:
            print("[Record] No frames captured, aborting.")
            if os.path.isdir(frame_dir):
                shutil.rmtree(frame_dir, ignore_errors=True)
            return

        pattern = os.path.join(frame_dir, "frame_%06d.bmp")
        cmd = [
            "ffmpeg", "-y",
            "-framerate", str(fps),
            "-i", pattern,
            "-r", "60",
            "-c:v", "libx264",
            "-pix_fmt", "yuv420p",
            "-vf", "scale=trunc(iw/2)*2:trunc(ih/2)*2",
            "-crf", "18",
            "-preset", "fast",
            output,
        ]
        try:
            subprocess.run(cmd, check=True, capture_output=True)
            print(f"[Record] Saved: {output}")
        except FileNotFoundError:
            print("[Record] ffmpeg not found. Install ffmpeg and add it to PATH.")
            print(f"[Record] Frames are in: {frame_dir}")
            return
        except subprocess.CalledProcessError as e:
            print(f"[Record] ffmpeg failed: {e.stderr.decode(errors='replace')}")
            print(f"[Record] Frames are in: {frame_dir}")
            return
        if os.path.isdir(frame_dir):
            shutil.rmtree(frame_dir, ignore_errors=True)


    def _capture_frame(self):
        pass
