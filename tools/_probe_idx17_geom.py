# -*- coding: utf-8 -*-
"""Where does the area band actually sit in the video? (idx 17 geometry check)"""
import os
import sys

import numpy as np

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if REPO not in sys.path:
    sys.path.insert(0, REPO)

from tools.issues_baseline import entries, twin  # noqa: E402
from tools.wiki_diff import decode  # noqa: E402

rtm = [p for p, d in entries() if "area.mp4" in p and "riemann" not in p][0]
ce = twin(rtm)
a = decode(rtm)
b = decode(ce)
f = 220
row = 594
rtm_row = a[f, row]
ce_row = b[f, row]
flat = np.array([65, 116, 95])
inside_rtm = np.nonzero(np.abs(rtm_row.astype(int) - flat).max(axis=1) < 12)[0]
print("row", row, "RTM flat-colour extent x:", inside_rtm.min(), inside_rtm.max())
# where does CE start/stop being non-black on that row?
nonblack = np.nonzero(ce_row.astype(int).max(axis=1) > 12)[0]
print("CE non-black extent:", nonblack.min(), nonblack.max())
print("CE colours at x =", [int(x) for x in
                            (660, 768, 960, 1056, 1160, 1264, 1344)])
for x in (660, 768, 960, 1056, 1160, 1264, 1344, 1420):
    print("  x=%4d RTM %s CE %s" % (x, tuple(int(v) for v in rtm_row[x]),
                                    tuple(int(v) for v in ce_row[x])))
# vertical extent of the band at x=960
col_rtm = a[f, :, 960]
inside = np.nonzero(np.abs(col_rtm.astype(int) - flat).max(axis=1) < 12)[0]
print("RTM flat colour extent y at x=960:", inside.min(), inside.max())
