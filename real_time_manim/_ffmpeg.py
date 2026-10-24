"""Locating the external ``ffmpeg`` / ``ffprobe`` binaries.

ffmpeg cannot be bundled as a Python dependency, so a machine without it must
get one actionable error instead of a traceback from deep inside the frame
writer -- or, on the fast-record path where ffmpeg's stderr is captured, no
message at all (a bare ``BrokenPipeError: [Errno 32] Broken pipe``).

Call :func:`require` before shelling out; use :func:`capture` for a
``stderr=...`` handle that can be read back after the process exits.
"""
from __future__ import annotations

import shutil
import tempfile

INSTALL_HINT = (
    "macOS: brew install ffmpeg | Windows: winget install ffmpeg | "
    "Debian/Ubuntu: sudo apt install ffmpeg"
)


def require(name: str = "ffmpeg", what: str = "record video") -> str:
    """Return the binary's path, or raise with an install hint."""
    path = shutil.which(name)
    if path is None:
        raise FileNotFoundError(
            "%s is required to %s but was not found on PATH. Install it "
            "(%s) and re-run." % (name, what, INSTALL_HINT)
        )
    return path


def capture():
    """A temp file suitable as ``Popen(stderr=...)``.

    A pipe would deadlock once ffmpeg fills the OS buffer; a temp file keeps the
    log for the error message without ever blocking the encoder.
    """
    return tempfile.TemporaryFile()


def read_capture(handle, limit: int = 800) -> str:
    """The tail of a :func:`capture` handle (``""`` when it cannot be read)."""
    if handle is None:
        return ""
    try:
        handle.seek(0)
        data = handle.read()
    except (OSError, ValueError):
        return ""
    if isinstance(data, bytes):
        data = data.decode("utf-8", "replace")
    data = data.strip()
    return data[-limit:]
