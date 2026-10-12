"""Screenshots and video capture.

Also carries the BMP headers written by `screenshot_printwindow`."""

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


class RecordingMixin:

    def screenshot(self, path):
        path_bytes = path.encode('utf-8') if isinstance(path, str) else path
        return self.dll.SaveScreenshot(path_bytes)

    def request_readback(self):
        """Arm the next drawn frame to copy itself for readback.

        Must be called *before* the tick that draws the frame you want.  A
        presented swapchain image is owned by the presentation engine, so
        copying it afterwards returns undefined pixels; the engine copies the
        frame while it still owns it instead.
        """
        fn = getattr(self.dll, 'Vulkan_RequestReadback', None)
        if fn is not None:
            fn()

    def screenshot_printwindow(self, path):
        if sys.platform != "win32":
            # macOS: no GDI — the swapchain framebuffer readback is the
            # reliable capture path (TCC-free, immune to occlusion).
            return bool(self.screenshot(path))
        import ctypes.wintypes as wt
        user32 = ctypes.windll.user32
        gdi32 = ctypes.windll.gdi32
        hwnd = user32.FindWindowW(None, "Real Time Manim")
        if not hwnd:
            hwnd = self.hwnd
            if not hwnd:
                return False

        # Client area dimensions
        rc = wt.RECT()
        user32.GetClientRect(hwnd, ctypes.byref(rc))
        w, h = rc.right - rc.left, rc.bottom - rc.top

        # Client area screen position
        pt = wt.POINT(0, 0)
        user32.ClientToScreen(hwnd, ctypes.byref(pt))
        x, y = pt.x, pt.y

        # Capture from screen at client area position
        hdc_screen = user32.GetDC(None)
        hdc_mem = gdi32.CreateCompatibleDC(hdc_screen)
        hbitmap = gdi32.CreateCompatibleBitmap(hdc_screen, w, h)
        gdi32.SelectObject(hdc_mem, hbitmap)
        gdi32.BitBlt(hdc_mem, 0, 0, w, h, hdc_screen, x, y, 0x00CC0020)  # SRCCOPY

        bi = BITMAPINFOHEADER()
        bi.biSize = ctypes.sizeof(BITMAPINFOHEADER)
        bi.biWidth = w
        bi.biHeight = -h
        bi.biPlanes = 1
        bi.biBitCount = 24
        bi.biCompression = 0
        row_bytes = ((w * 3 + 3) & ~3)
        buf = (ctypes.c_ubyte * (row_bytes * h))()
        gdi32.GetDIBits(hdc_mem, hbitmap, 0, h, buf, ctypes.byref(bi), 0)
        bfh = BITMAPFILEHEADER()
        bfh.bfType = 0x4D42
        bfh.bfOffBits = ctypes.sizeof(BITMAPFILEHEADER) + ctypes.sizeof(BITMAPINFOHEADER)
        bfh.bfSize = bfh.bfOffBits + row_bytes * h
        path_b = path.encode('utf-8') if isinstance(path, str) else path
        hdr_buf = ctypes.string_at(ctypes.addressof(bfh), ctypes.sizeof(bfh)) + \
                  ctypes.string_at(ctypes.addressof(bi), ctypes.sizeof(bi))
        with open(path_b, 'wb') as f:
            f.write(hdr_buf)
            f.write(ctypes.string_at(ctypes.addressof(buf), len(buf)))
        gdi32.DeleteObject(hbitmap)
        gdi32.DeleteDC(hdc_mem)
        user32.ReleaseDC(None, hdc_screen)
        return True

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
        w, h = self.win_w, self.win_h

        # Hide window for faster rendering (no compositing)
        if hidden and sys.platform == "win32":
            import ctypes.wintypes
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
            ffmpeg_cmd = [
                "ffmpeg", "-y",
                "-f", "rawvideo", "-pixel_format", "bgr24",
                "-video_size", f"{w}x{h}",
                "-framerate", str(fps),
                "-i", "-",
                "-c:v", "libx264", "-pix_fmt", "yuv420p",
                # Keep the frames full-range: the default limited-range
                # conversion scales Y by 219/255 and the CLI's swscale truncates
                # where manim's own encoder rounds, so a flat #808080 rendered
                # correctly (verified from the DLL's own readback) decoded one
                # level low -- and the chroma round trip amplified that into a
                # (-4,-2,-5) RGB offset that pushed the flat scenes just outside
                # tolerance.
                "-vf", "scale=out_range=pc",
                "-color_range", "pc",
                "-crf", "18", "-preset", "fast",
                self._fast_record_path,
            ]
            self._ffmpeg = subprocess.Popen(
                ffmpeg_cmd, stdin=subprocess.PIPE, stderr=subprocess.DEVNULL)
            self._fast_tmp_bmp = os.path.join(tempfile.gettempdir(),
                f"manim_fast_{os.getpid()}_{id(self)}.bmp")
            print(f"[FastRecord] Pipe: {w}x{h} @ {fps} fps → {path}")

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

    def _get_screen_bbox(self):
        if sys.platform != "win32":
            return None
        import ctypes.wintypes as wt
        user32 = ctypes.windll.user32
        hwnd = user32.FindWindowW(None, "Real Time Manim")
        if not hwnd:
            return None
        rc = wt.RECT()
        user32.GetClientRect(hwnd, ctypes.byref(rc))
        pt = wt.POINT(0, 0)
        user32.ClientToScreen(hwnd, ctypes.byref(pt))
        return (pt.x, pt.y, pt.x + rc.right, pt.y + rc.bottom)

    def _capture_frame(self):
        pass
