"""Run tools/wiki_sweep.py and write the table to a UTF-8 file.

PowerShell's `>` mangles native-stdout UTF-8 (it decodes with the console
codepage and re-encodes UTF-16), which corrupts the Chinese wiki paths.  The
sweep itself is the same `tools/wiki_sweep.py`; this wrapper only owns the file.
"""
import contextlib
import io
import sys

REPO = r"C:\Users\begin\Desktop\real-time-manim"
OUT = r"C:\Users\begin\AppData\Local\Temp\opencode\sweep.txt"
sys.path.insert(0, REPO)

import tools.wiki_sweep as ws  # noqa: E402

sys.argv = ["wiki_sweep.py", "--jobs", "1", "--scale", "320x180"] + sys.argv[1:]
buf = io.StringIO()
try:
    with contextlib.redirect_stdout(buf):
        ws.main()
finally:
    with open(OUT, "w", encoding="utf-8") as fh:
        fh.write(buf.getvalue())
print("written", OUT, len(buf.getvalue()), "bytes")
