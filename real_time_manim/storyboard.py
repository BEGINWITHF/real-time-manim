"""One-image storyboard for an RTM scene.

Reviewing a film frame-by-frame in a video player is slow, and a downscaled
video hides exactly the problems that matter (text contrast, clipping, empty
shots).  ``contact_sheet`` prepares the scene once with :class:`FrameServer`,
renders a list of timestamps at full size, and tiles them into a single
labelled PNG -- the comic page an agent (or a person) can check in one read.

    from real_time_manim import contact_sheet
    contact_sheet(MyScene, [0.5, 3, 7, 11, 16, 22, 30, 38], "frames/sheet.png")

Frame times default to 12 evenly spaced samples when ``times`` is omitted, or
8 for a short scene.  Each cell is labelled with its timestamp.  The function
returns the output path and never leaves the window open.

Design notes
------------
- The window is prepared once (~10 ms per frame afterwards), so a 12-cell sheet
  costs about as much as one still plus one scene build.
- Cells are scaled with ``cell_width``; labels use Pillow's scalable default
  font, which needs no font file.
- The sheet is for judging *sequence*: title safety, caption legibility, empty
  shots, clipped geometry.  It is not a colour reference -- use a still for
  that.
"""
from __future__ import annotations

import os
import tempfile
from typing import Iterable, Optional, Sequence

BG = (7, 11, 20)
INK = (123, 147, 166)


def _font(size: int):
    from PIL import ImageFont

    try:
        return ImageFont.load_default(size=size)
    except TypeError:                      # Pillow < 10.1
        return ImageFont.load_default()


def contact_sheet(
    scene,
    times: Optional[Iterable[float]] = None,
    out_path: str = "frames/contact_sheet.png",
    *,
    cols: int = 4,
    cell_width: int = 640,
    labels: bool = True,
    gap: int = 6,
    pad: int = 8,
    quality: int = 6,
    verbose: bool = True,
) -> str:
    """Render ``times`` and tile the frames into one labelled PNG.

    Parameters
    ----------
    scene:
        ``Scene`` subclass / instance / no-arg callable, as for
        :class:`~real_time_manim.frames.FrameServer`.
    times:
        Iterable of timestamps in **seconds**.  ``None`` -> 12 evenly spaced
        samples across the scene duration (8 when it is shorter than 20 s).
    out_path:
        Destination PNG; parent directories are created.
    cols:
        Cells per row.
    cell_width:
        Width of one cell in pixels; height follows the 16:9 frame.
    labels:
        Draw ``t=12.40 s`` above each cell.
    gap, pad:
        Pixel gaps between cells / around the sheet.
    quality:
        Passed to ``FrameServer.save_frame``.
    verbose:
        Print one line with the sheet layout.

    Returns
    -------
    str
        ``out_path``.
    """
    from PIL import Image, ImageDraw

    from real_time_manim.frames import FrameServer

    if cols < 1:
        raise ValueError("cols must be >= 1")

    os.makedirs(os.path.dirname(os.path.abspath(out_path)) or ".", exist_ok=True)
    fs = FrameServer(scene)
    try:
        duration = float(fs.duration)
        if times is None:
            n = 12 if duration >= 20.0 else 8
            ts: Sequence[float] = [duration * i / (n - 1) for i in range(n)]
        else:
            ts = [float(t) for t in times]
        if not ts:
            raise ValueError("times must not be empty")
        ts = [min(max(t, 0.0), duration) for t in ts]

        rows = (len(ts) + cols - 1) // cols
        label_h = 20 if labels else 0
        with tempfile.TemporaryDirectory() as tmp:
            cells = []
            for i, t in enumerate(ts):
                p = os.path.join(tmp, "f%03d.png" % i)
                fs.save_frame(t, p, quality=quality)
                img = Image.open(p)
                img.load()
                img = img.convert("RGB")
                if img.width != cell_width:
                    h = max(1, round(img.height * cell_width / img.width))
                    img = img.resize((cell_width, h), Image.LANCZOS)
                cells.append(img)
            cw, ch = cells[0].size

            sheet = Image.new(
                "RGB",
                (
                    pad * 2 + cols * cw + (cols - 1) * gap,
                    pad * 2 + rows * (ch + label_h) + (rows - 1) * gap,
                ),
                BG,
            )
            draw = ImageDraw.Draw(sheet)
            font = _font(14) if labels else None
            for i, (t, img) in enumerate(zip(ts, cells)):
                r, c = divmod(i, cols)
                x = pad + c * (cw + gap)
                y = pad + r * (ch + label_h + gap)
                if labels:
                    draw.text((x + 2, y + 2), "t=%.2f s" % t, fill=INK, font=font)
                sheet.paste(img, (x, y + label_h))

            sheet.save(out_path)
    finally:
        fs.close()

    if verbose:
        print(
            "[contact_sheet] %d frames, %dx%d cells -> %s"
            % (len(ts), rows, cols, out_path)
        )
    return out_path

