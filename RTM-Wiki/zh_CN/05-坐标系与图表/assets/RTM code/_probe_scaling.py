# -*- coding: utf-8 -*-
"""10 页 LogBase 语义探针（只算不渲）：轴范围是“真实值”还是“指数”。"""
import os
import sys
import numpy as np

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), *[".."] * 5)))
from real_time_manim import Axes, NumberLine, LogBase  # noqa: E402

ax = Axes(x_range=[0, 10, 1], y_range=[-2, 6, 1], tips=False,
          axis_config={"include_numbers": True},
          y_axis_config={"scaling": LogBase(custom_labels=True)})
print("c2p(1, 1)  =", ax.c2p(1, 1))
print("c2p(1, 100)=", ax.c2p(1, 100))
print("c2p(10, 1) =", ax.c2p(10, 1))
try:
    g = ax.plot(lambda x: x**2, x_range=[0.001, 10], use_smoothing=False)
    pts = g.get_points()
    print("graph y scene range:", pts[:, 1].min(), pts[:, 1].max())
    print("ax frame y range:", ax.c2p(0, 1)[1], ax.c2p(0, 6)[1])
except Exception as e:
    print("plot failed:", type(e).__name__, e)

nl = NumberLine(x_range=[0, 6, 1], scaling=LogBase(base=10), include_numbers=True)
print("nl n2p(0..6):", [nl.n2p(v)[0] for v in range(7)])
print("nl labels:", [l.text if hasattr(l, "text") else str(l) for l in nl.numbers] if nl.numbers else None)
