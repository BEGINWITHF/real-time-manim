# ruff: noqa: F403, F405 -- manim-style star imports (from .common import *)
"""Demo scenes: LaTeX and number showcases -- the full symbol table, Fourier
epicycles, the Lorenz butterfly and a progressive Write.

Split out of the original single-file ``demo_scene.py``; the class
bodies are unchanged.  Re-exported by ``examples.scenes``.
"""
from .common import *  # noqa: F401,F403
from .common import _title  # noqa: F401

__all__ = [
    "DemoLatexWithoutLatex", "DemoFourierTransform", "DemoLorenzButterfly",
    "DemoWriteLatex"
]


class DemoLatexWithoutLatex(Scene):
    def construct(self):
        render = MLWindow(1920, 1080)
        render.scene = self
        render.play(Wait(2.0))
        _title(render, "All LaTeX commands")

        FS = 28

        def sym(s):
            return MathTex(s, font_size=FS)

        def vg(*strings):
            return VGroup(*[sym(t) for t in strings]).arrange(RIGHT, buff=0.3)

        def stacked(*rows):
            return VGroup(*rows).arrange(DOWN, buff=0.35)

        _R = chr(92)
        _ra = _R + "rangle"
        _rf = _R + "rfloor"
        _rc = _R + "rceil"
        _ri = _R + "right"
        _rar = _R + "rightarrow"
        _rrp = _R + "rightleftharpoons"

        # Each pair: (group_A, group_B) where each symbol is its own MathTex
        # TransformMatchingTex will morph symbol-by-symbol

        pairs = []
        W = max  # width placeholder — ignore

        # 1. Greek lowercase → uppercase
        greek_low = ["\\alpha","\\beta","\\gamma","\\delta","\\epsilon","\\zeta","\\eta","\\theta"]
        greek_low2 = ["\\iota","\\kappa","\\lambda","\\mu","\\nu","\\xi","\\pi","\\rho"]
        greek_low3 = ["\\sigma","\\tau","\\upsilon","\\phi","\\chi","\\psi","\\omega",
                      "\\varepsilon"]
        greek_up = ["\\Gamma","\\Delta","\\Theta","\\Lambda","\\Xi","\\Pi","\\Sigma",
                    "\\Upsilon"]
        greek_up2 = ["\\Phi","\\Psi","\\Omega","\\aleph","\\beth","\\daleth","\\gimel",
                     "\\digamma"]
        g1 = stacked(vg(*greek_low), vg(*greek_low2), vg(*greek_low3))
        g2 = stacked(vg(*greek_up), vg(*greek_up2)).move_to(g1)
        pairs.append((g1, g2))

        # 2. Structures: frac→sqrt→overbrace→binom→int
        s1 = stacked(
            vg(r"\frac{a}{b}", r"\sqrt{x}", r"\sqrt[n]{x}"),
            vg(r"\overline{AB}", r"\underline{CD}"),
            vg(r"\overrightarrow{EF}", r"\hat{x}", r"\tilde{y}"),
        )
        s2 = stacked(
            vg(r"\overbrace{a+b+c}", r"\underbrace{x+y+z}"),
            vg(r"\frac{\partial f}{\partial x}", r"\frac{d}{dx}"),
            vg(r"\binom{n}{k}", r"\int_a^b f(x)\,dx"),
        ).move_to(s1)
        pairs.append((s1, s2))

        # 3. Delimiters
        d1 = stacked(
            vg("|x|", r"\Vert x\Vert", "\\langle x" + _ra),
            vg("\\{x\\}", "\\lfloor x" + _rf, "\\lceil x" + _rc),
            vg(r"\backslash", r"\uparrow", r"\downarrow"),
        )
        d2 = stacked(
            vg("\\left(\\frac{a}{b}" + _ri + ")", "\\left[\\frac{a}{b}" + _ri + "]"),
            vg("\\left\\{\\frac{a}{b}" + _ri + "\\}", "\\left|\\frac{a}{b}" + _ri + "|"),
            vg(r"\Uparrow", r"\Downarrow", r"\Updownarrow"),
        ).move_to(d1)
        pairs.append((d1, d2))

        # 4. Large operators
        o1 = stacked(
            vg(r"\sum_{i=1}^n i", r"\prod_{i=1}^n i"),
            vg(r"\int_0^\infty", r"\oint", r"\iint", r"\iiint"),
            vg(r"\bigcap", r"\bigcup", r"\bigsqcup", r"\bigvee", r"\bigwedge"),
        )
        o2 = stacked(
            vg(r"\coprod", r"\biguplus", r"\bigoplus", r"\bigotimes", r"\bigodot"),
            vg(r"\sum\nolimits_{i=1}^n", r"\int\nolimits_0^1"),
            vg(r"\displaystyle\sum_{i=1}^\infty \frac{1}{i^2} = \frac{\pi^2}{6}"),
        ).move_to(o1)
        pairs.append((o1, o2))

        # 5. Functions
        f1 = stacked(
            vg(r"\sin x", r"\cos x", r"\tan x"),
            vg(r"\arcsin x", r"\arccos x", r"\arctan x"),
            vg(r"\sinh x", r"\cosh x", r"\tanh x"),
        )
        f2 = stacked(
            vg(r"\lim_{x\to 0}\frac{\sin x}{x}=1", r"\limsup", r"\liminf"),
            vg(r"\log x", r"\ln x", r"\lg x", r"\exp x"),
            vg(r"\max", r"\min", r"\sup", r"\inf", r"\gcd", r"\det", r"\dim", r"\ker",
               r"\arg", r"\deg", r"\Pr"),
        ).move_to(f1)
        pairs.append((f1, f2))

        # 6. Binary ops → relations
        b1 = stacked(
            vg(r"\pm", r"\mp", r"\times", r"\div", r"\ast", r"\star", r"\cdot"),
            vg(r"\circ", r"\bullet", r"\oplus", r"\ominus", r"\otimes", r"\odot"),
            vg(r"\cap", r"\cup", r"\sqcap", r"\sqcup", r"\wedge", r"\vee"),
        )
        b2 = stacked(
            vg(r"\leq", r"\geq", r"\ll", r"\gg", r"\equiv", r"\sim", r"\simeq"),
            vg(r"\approx", r"\cong", r"\neq", r"\doteq", r"\propto", r"\prec", r"\succ"),
            vg(r"\subset", r"\supset", r"\subseteq", r"\supseteq", r"\in", r"\ni", r"\notin"),
        ).move_to(b1)
        pairs.append((b1, b2))

        # 7. More relations → negations
        r1 = stacked(
            vg(r"\mid", r"\parallel", r"\nmid", r"\nparallel", r"\perp", r"\bowtie", r"\Join"),
            vg(r"\vdash", r"\dashv", r"\models", r"\Vdash", r"\vDash", r"\Vvdash"),
            vg(r"\lll", r"\ggg", r"\preceq", r"\succeq", r"\precsim", r"\succsim"),
        )
        r2 = stacked(
            vg(r"\nsim", r"\ncong", r"\nleq", r"\ngeq", r"\nprec", r"\nsucc", r"\nsupseteq"),
            vg(r"\lneqq", r"\gneqq", r"\lnsim", r"\gnsim", r"\lvertneqq", r"\gvertneqq"),
            vg(r"\ntriangleleft", r"\ntriangleright", r"\nVDash", r"\nvDash", r"\nvdash"),
        ).move_to(r1)
        pairs.append((r1, r2))

        # 8. Arrows
        a1 = stacked(
            vg("\\leftarrow" + _rar, "\\leftrightarrow"),
            vg(r"\Leftarrow", r"\Rightarrow", r"\Leftrightarrow"),
            vg(r"\longleftarrow", r"\longrightarrow", r"\longleftrightarrow"),
        )
        a2 = stacked(
            vg(r"\mapsto", r"\longmapsto", r"\hookrightarrow", r"\hookleftarrow"),
            vg(r"\uparrow", r"\downarrow", r"\updownarrow", r"\Uparrow", r"\Downarrow", r"\Updownarrow"),
            vg("\\nLeftarrow", "\\nRightarrow", "\\nLeftrightarrow" + _rrp),
        ).move_to(a1)
        pairs.append((a1, a2))

        # 9. Misc symbols
        m1 = stacked(
            vg(r"\infty", r"\forall", r"\exists", r"\nexists", r"\emptyset", r"\varnothing"),
            vg(r"\nabla", r"\partial", r"\eth", r"\angle", r"\measuredangle"),
            vg(r"\triangle", r"\triangledown", r"\vartriangle", r"\lozenge", r"\blacklozenge"),
        )
        m2 = stacked(
            vg(r"\cdots", r"\vdots", r"\ddots", r"\ldots", r"\prime", r"\sharp", r"\flat"),
            vg(r"\natural", r"\surd", r"\hbar", r"\ell", r"\wp", r"\imath", r"\jmath"),
            vg(r"\clubsuit", r"\diamondsuit", r"\heartsuit", r"\spadesuit", r"\bigstar"),
        ).move_to(m1)
        pairs.append((m1, m2))

        # 10. More misc → blackboard
        mm1 = stacked(
            vg(r"\Game", r"\Finv", r"\Bbbk", r"\circledS", r"\complement"),
            vg(r"\blacksquare", r"\square", r"\blacktriangle", r"\blacktriangledown"),
            vg(r"\Re", r"\Im", r"\mho", r"\hslash", r"\backprime"),
        )
        mm2 = stacked(
            vg(r"\mathbb{R}", r"\mathbb{C}", r"\mathbb{N}", r"\mathbb{Z}", r"\mathbb{Q}"),
            vg(r"\mathcal{A}", r"\mathcal{B}", r"\mathcal{C}", r"\mathcal{D}", r"\mathcal{E}"),
            vg(r"\mathfrak{A}", r"\mathfrak{B}", r"\mathfrak{C}", r"\mathfrak{D}", r"\mathfrak{E}"),
        ).move_to(mm1)
        pairs.append((mm1, mm2))

        # 11. Accents
        ac1 = stacked(
            vg(r"\hat{x}", r"\tilde{x}", r"\bar{x}", r"\vec{x}", r"\dot{x}", r"\ddot{x}"),
            vg(r"\acute{x}", r"\grave{x}", r"\check{x}", r"\breve{x}"),
        )
        ac2 = stacked(
            vg(r"\widehat{abc}", r"\widetilde{abc}", r"\overline{abc}"),
            vg(r"\Hat{x}", r"\Tilde{x}", r"\Bar{x}", r"\Vec{x}", r"\Dot{x}", r"\Ddot{x}"),
            vg(r"\Acute{x}", r"\Grave{x}", r"\Check{x}", r"\Breve{x}", r"\underrightarrow{abc}"),
        ).move_to(ac1)
        pairs.append((ac1, ac2))

        # 12. Arrays + matrices
        arr1 = stacked(
            vg(r"\begin{array}{cc} a & b \\ c & d \end{array}"),
            vg(r"\begin{array}{|c|c|} x & y \\ z & w \end{array}"),
        )
        arr2 = stacked(
            vg(r"\begin{pmatrix} a & b \\ c & d \end{pmatrix}"),
            vg(r"\begin{bmatrix} x & y \\ z & w \end{bmatrix}"),
        ).move_to(arr1)
        pairs.append((arr1, arr2))

        # 13. Fonts
        ft1 = stacked(
            vg(r"\mathbf{A}", r"\mathbf{B}", r"\mathbf{C}"),
            vg(r"\mathsf{A}", r"\mathsf{B}", r"\mathsf{C}"),
        )
        ft2 = stacked(
            vg(r"\textbf{ABC}", r"\textit{ABC}", r"\texttt{ABC}"),
            vg(r"\underline{ABC}", r"\overline{ABC}"),
        ).move_to(ft1)
        pairs.append((ft1, ft2))

        center = ORIGIN + UP * 0.3
        for sa, sb in pairs:
            sa.move_to(center)
            sb.move_to(center)

        page_names = [
            "1/13 Greek & Hebrew", "2/13 Structures", "3/13 Delimiters",
            "4/13 Large operators", "5/13 Functions", "6/13 Binary ops → Relations",
            "7/13 Relations → Negations", "8/13 Arrows", "9/13 Misc symbols",
            "10/13 Misc → Blackboard", "11/13 Accents", "12/13 Arrays & matrices",
            "13/13 Fonts",
        ]
        page_label = Text(page_names[0], font_size=20, fill_color=GREY).to_edge(DOWN, buff=0.3)
        self.add(page_label)

        self.add(pairs[0][0])
        render.play(Wait(0.5))

        for i, ((sa, sb), (na, _)) in enumerate(zip(pairs, pairs[1:] + pairs[:1])):
            next_label = Text(page_names[(i + 1) % 13], font_size=20, fill_color=GREY).to_edge(DOWN, buff=0.3)
            render.play(TransformMatchingTex(sa, sb, run_time=0.8))
            render.play(Wait(0.1))
            render.play(TransformMatchingTex(sb, na, run_time=0.8))
            self.remove(page_label)
            self.add(next_label)
            page_label = next_label
            render.play(Wait(0.1))

        render.play(Wait(1.5))
        render.close()


class DemoFourierTransform(Scene):
    """Epicycles tracing a heart via Fourier series — 20 harmonics."""

    def construct(self):
        render = MLWindow(1920, 1080)
        render.scene = self
        render.play(Wait(2.0))
        _title(render, "Fourier Transform — Epicycles")

        # ── 1. Heart path DFT ─────────────────────────────────────
        N = 256
        t = np.linspace(0, 2 * np.pi, N, endpoint=False)
        x = 16 * np.sin(t) ** 3
        y = 13 * np.cos(t) - 5 * np.cos(2 * t) - 2 * np.cos(3 * t) - np.cos(4 * t)
        pts = (x + 1j * y) / 22  # scale to ~2-unit span

        coeffs = np.fft.fft(pts) / N
        order = np.argsort(-np.abs(coeffs))
        coeffs, freqs = coeffs[order], order - N // 2

        K = 20
        coeffs, freqs = coeffs[:K], freqs[:K]
        span = float(np.sum(np.abs(coeffs))) * 2.2
        coeffs = (coeffs / span) * 3.5  # normalize visual span

        # ── 2. Build epicycle components ──────────────────────────
        colors = color_gradient([BLUE_E, PURPLE_E, RED_E, ORANGE, YELLOW], K)
        circles, arms = [], []
        for i in range(K):
            c = Circle(radius=0.08, color=colors[i], stroke_width=1.0)
            c.set_fill(colors[i], opacity=0.08)
            circles.append(c)
            arms.append(Line(ORIGIN, RIGHT * 0.1, color=colors[i], stroke_width=1.5))

        pen = Dot(radius=0.06, color=WHITE)
        trace = TracedPath(pen.get_center, stroke_color=YELLOW, stroke_width=2.5)

        epi = VGroup(*circles, *arms, pen)
        self.add(epi, trace)

        # ── 3. Updater ────────────────────────────────────────────
        start_t = time.time()
        period = 8.0

        def updater(g, dt):
            elapsed = time.time() - start_t
            pos = np.array([0.0, 0.0, 0.0])
            for i in range(K):
                mag = float(np.abs(coeffs[i]))
                phi = (2 * np.pi * float(freqs[i]) * elapsed / period
                       + float(np.angle(coeffs[i])))
                tip = pos + np.array([mag * np.cos(phi), mag * np.sin(phi), 0.0])
                circles[i].move_to(pos)
                arms[i].set_points_as_corners([pos, tip])
                pos = tip
            pen.move_to(pos)

        epi.add_updater(updater)

        # ── 4. Animate ────────────────────────────────────────────
        render.play(Wait(period + 1))
        epi.clear_updaters()
        render.play(Wait(1.0))
        render.close()


class DemoLorenzButterfly(Scene):
    """Lorenz attractor — 5 particles, rotating view, dissipating trails."""

    def construct(self):
        render = MLWindow(1920, 1080)
        render.scene = self
        render.play(Wait(2.0))
        _title(render, "Lorenz Attractor")

        # ── Lorenz params ──────────────────────────────────────────
        sigma, rho, beta = 10.0, 28.0, 8 / 3
        dt, N = 0.0015, 40000
        num_parts = 5
        run_time = 20.0

        # ── Seeds (butterfly effect!) ──────────────────────────────
        base = np.array([-8.0, 8.0, 27.0])
        rng = np.random.RandomState(42)
        seeds = [base + rng.normal(0, 0.25, 3) for _ in range(num_parts)]

        # ── Pre-compute trajectories ───────────────────────────────
        all_3d = []
        for start in seeds:
            path = [start.copy()]
            p = start.copy()
            for _ in range(N - 1):
                dx = sigma * (p[1] - p[0])
                dy = p[0] * (rho - p[2]) - p[1]
                dz = p[0] * p[1] - beta * p[2]
                p = p + np.array([dx, dy, dz]) * dt
                path.append(p.copy())
            all_3d.append(np.array(path))

        # ── Color palette ──────────────────────────────────────────
        colors = [BLUE_D, TEAL_D, PURPLE_D, MAROON_D, GOLD_D]

        # ── Dots, glows & trails ───────────────────────────────────
        dots, glows, traces = [], [], []
        for i in range(num_parts):
            d = Dot(radius=0.05, color=colors[i])
            g = Circle(radius=0.18, color=colors[i],
                       fill_opacity=0.06, stroke_width=0)
            t = TracedPath(d.get_center, stroke_color=colors[i],
                           stroke_width=1.6, dissipating_time=4.0)
            dots.append(d)
            glows.append(g)
            traces.append(t)
            self.add(d, g, t)

        # ── Updaters ───────────────────────────────────────────────
        start_t = time.time()

        for i in range(num_parts):
            _traj = all_3d[i]
            _glow = glows[i]

            def updater(d, _i=i):
                elapsed = time.time() - start_t
                frac = min(elapsed / run_time, 1.0)
                ang = frac * np.pi * 2
                fidx = frac * (N - 1)
                lo = int(fidx)
                hi = min(lo + 1, N - 1)
                t = fidx - lo
                p = _traj[lo] * (1 - t) + _traj[hi] * t
                c, s = np.cos(ang), np.sin(ang)
                rx = p[0] * c - p[1] * s
                ry = p[0] * s + p[1] * c
                sx = rx * 0.11
                sy = (ry * 0.3 + p[2] * 0.8) * 0.09
                pos = np.array([sx, sy, 0.0])
                d.move_to(pos)
                _glow.move_to(pos)

            dots[i].add_updater(updater)

        # ── Animate ────────────────────────────────────────────────
        render.play(Wait(run_time + 1))
        for d in dots:
            d.clear_updaters()
        render.play(Wait(1.0))
        render.close()


class DemoWriteLatex(Scene):
    """Write on LaTeX mobjects — exercises the progressive glyph reveal.

    Previously Write on a MathTex popped the whole equation in fully filled
    (the container fill was set, but the actual fill lives on the nested SVG
    glyph leaves).  This scene verifies the outline-then-fill reveal works.
    """

    def construct(self):
        render = MLWindow(1920, 1080)
        render.scene = self
        render.play(Wait(2.0))
        _title(render, "Write on LaTeX")

        # Single-part equation (one MathTexPart, several glyph leaves)
        eq1 = MathTex("x^2 + y^2", font_size=56).shift(UP * 1.5)
        render.play(Write(eq1, run_time=0.8))
        render.play(Wait(1.0))

        # Multi-part equation — Write staggers across the parts
        eq2 = MathTex(r"\frac{a}{b} + \sqrt{c}", font_size=56).shift(DOWN * 1.5)
        render.play(Write(eq2, run_time=0.8))
        render.play(Wait(1.5))
        render.close()
