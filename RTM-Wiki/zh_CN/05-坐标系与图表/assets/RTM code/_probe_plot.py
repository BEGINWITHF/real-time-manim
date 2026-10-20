# -*- coding: utf-8 -*-
"""探针：05-函数曲线 plot 样例里 bad 曲线（无 discontinuities）的几何统计。"""
import sys
import numpy as np

sys.path.insert(0, r"C:\Users\begin\Desktop\real-time-manim")
from real_time_manim import Axes, RED  # noqa: E402

ax = Axes(x_range=[-3, 3, 1], y_range=[-4, 4, 1])
f = lambda x: (x**2 - 2) / (x**2 - 4)
bad = ax.plot(f, color=RED)
pts = bad.get_points()
print("n_points:", len(pts))
print("x range:", pts[:, 0].min(), pts[:, 0].max())
print("y range:", pts[:, 1].min(), pts[:, 1].max())
print("|y|>100 count:", int(np.sum(np.abs(pts[:, 1]) > 100)))
print("has inf/nan:", bool(np.isinf(pts).any()), bool(np.isnan(pts).any()))
big = np.argsort(-np.abs(pts[:, 1]))[:8]
for i in sorted(big):
    print("  pt", i, pts[i])
# 连续大值之间是否符号翻转（会画出穿屏竖线）
ys = pts[:, 1]
flips = int(np.sum(np.sign(ys[:-1]) != np.sign(ys[1:])))
print("sign flips between consecutive pts:", flips)
