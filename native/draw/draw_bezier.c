#include "../draw_common.h"
#include "../shared_types.h"
#include <math.h>

#define MAX_BEZIER_PATHS 8192
#define MAX_BEZIER_SEGMENTS 1024
/* Samples per cubic.  This used to be a fixed 64, which is the same class of
   bug the primitives had (draw_circle.c and friends): the count decides the
   on-screen sagitta, so a fixed one gets coarser the bigger the curve is drawn
   -- 64 is ~7x finer than the old 36-gon (a circle is 4 cubics = 256 chords),
   which is why it held up much further, but it still has a ceiling (an
   on-screen curvature radius of ~13000 px, i.e. roughly 100x zoom, reaches
   1 px).  Worse, it also spent 64 samples on a nearly straight segment: a glyph
   box or an axis-aligned run needs two.

   The rule below picks the count from the segment's own flatness, the same
   quantity `_small_path_chords` uses on the Python side: a cubic lies inside the
   hull of its control points, so if they sit within `d` px of the chord the
   n-sample polyline deviates from the curve by about 3d/(4n^2).  Solving that
   for `BEZIER_FLATNESS_PX` gives the count, so the shape drawn is smooth to a
   quarter of a pixel at ANY size, and a flat segment costs 8 samples. */
#define BEZIER_SAMPLE_MIN 8
#define BEZIER_SAMPLE_MAX 256
#define BEZIER_FLATNESS_PX 0.25f
/* Segments live in one shared pool and a path only stores its offset, so a
   path costs ~1 KB instead of 32 KB.  The old layout was one inline
   CubicSeg[1024] per path, which capped the path list at 512 -- and a
   glyph-per-path Text scene makes ~870 AddBezierPath calls per frame, so the
   tail of every long text block was silently dropped (measured:
   ConfigFileRoundtrip drew only its top ~12 of 19 lines, lit 10236 vs CE
   20135, d(last) -3.05). */
#define MAX_BEZIER_SEG_POOL 393216

typedef struct {
    float px[4];
    float py[4];
} CubicSeg;

typedef struct {
    int seg_start;                 /* offset into g_seg_pool */
    int num_segs;
    int sr, sg, sb;
    float stroke_width;
    int fr, fg, fb;
    int fr2, fg2, fb2;             /* second fill stop (linear gradient) */
    float gx1, gy1, gx2, gy2;      /* the gradient axis, in screen pixels */
    float fill_opacity;
    float progress;
    int show_stroke;
    int show_fill;
    int sub_count;
    int sub_seg_start[128];
    int sub_winding[128];
    float alpha;
} BezierPathObj;

static BezierPathObj bezier_paths[MAX_BEZIER_PATHS];
static CubicSeg g_seg_pool[MAX_BEZIER_SEG_POOL];
static int bezier_path_count = 0;
static int g_seg_pool_used = 0;
static float g_fill_pts[MAX_BEZIER_SEGMENTS * BEZIER_SAMPLE_MAX + 1][2];

#define BP_SEG(bp, i) (g_seg_pool[(bp)->seg_start + (i)])

__declspec(dllexport) void AddBezierPath(
    const float *points, int num_points,
    int sr, int sg, int sb, float stroke_width,
    int fr, int fg, int fb, float fill_opacity,
    float progress, int show_stroke, int show_fill, float alpha,
    int fr2, int fg2, int fb2,
    float gx1, float gy1, float gx2, float gy2)
{
    if (bezier_path_count >= MAX_BEZIER_PATHS) return;
    if (num_points < 8) return;

    int num_segs = num_points / 4;
    if (num_segs > MAX_BEZIER_SEGMENTS) num_segs = MAX_BEZIER_SEGMENTS;
    if (g_seg_pool_used + num_segs > MAX_BEZIER_SEG_POOL) return;

    int cmd_index = bezier_path_count;
    BezierPathObj *bp = &bezier_paths[cmd_index];
    bp->seg_start = g_seg_pool_used;
    g_seg_pool_used += num_segs;
    bp->num_segs = num_segs;
    bp->sr = sr; bp->sg = sg; bp->sb = sb;
    bp->stroke_width = stroke_width;
    bp->fr = fr; bp->fg = fg; bp->fb = fb;
    bp->fr2 = fr2; bp->fg2 = fg2; bp->fb2 = fb2;
    bp->gx1 = gx1; bp->gy1 = gy1; bp->gx2 = gx2; bp->gy2 = gy2;
    bp->fill_opacity = fill_opacity;
    bp->progress = progress;
    bp->show_stroke = show_stroke;
    bp->show_fill = show_fill;
    bp->alpha = alpha;

    for (int i = 0; i < num_segs; i++) {
        int off = i * 4 * 3;
        for (int j = 0; j < 4; j++) {
            BP_SEG(bp, i).px[j] = points[off + j * 3 + 0];
            BP_SEG(bp, i).py[j] = points[off + j * 3 + 1];
        }
    }

    bp->sub_count = 1;
    bp->sub_seg_start[0] = 0;
    for (int si = 0; si < num_segs - 1; si++) {
        float dx = BP_SEG(bp, si).px[3] - BP_SEG(bp, si + 1).px[0];
        float dy = BP_SEG(bp, si).py[3] - BP_SEG(bp, si + 1).py[0];
        if (dx * dx + dy * dy > 40.0f) {
            if (bp->sub_count < 128) {
                bp->sub_seg_start[bp->sub_count++] = si + 1;
            }
        }
    }
    for (int s = 0; s < bp->sub_count; s++) {
        int start = bp->sub_seg_start[s];
        int end = (s < bp->sub_count - 1) ? bp->sub_seg_start[s + 1] : num_segs;
        float area = 0;
        for (int si = start; si < end; si++) {
            float x0 = BP_SEG(bp, si).px[0], y0 = BP_SEG(bp, si).py[0];
            float x3 = BP_SEG(bp, si).px[3], y3 = BP_SEG(bp, si).py[3];
            area += (x0 * y3 - x3 * y0);
        }
        bp->sub_winding[s] = (area >= 0) ? 1 : -1;
    }
    bezier_path_count++;
    /* Keep this path at its submission position instead of in a trailing
       flush, so the next mobject's fill can cover it. */
    DrawCmd_Push(CMD_BEZIER, cmd_index);
}

/* How far the control points sit from the chord p0->p3, in pixels: the
   "flatness" that `bezier_samples` turns into a sample count. */
static float bezier_flatness(const CubicSeg *s) {
    float dx = s->px[3] - s->px[0], dy = s->py[3] - s->py[0];
    float len = sqrtf(dx * dx + dy * dy);
    float d1, d2;
    if (len < 1e-6f) {
        /* A segment with coincident endpoints: measure from p0 instead. */
        float ox = s->px[1] - s->px[0], oy = s->py[1] - s->py[0];
        d1 = sqrtf(ox * ox + oy * oy);
        ox = s->px[2] - s->px[0];
        oy = s->py[2] - s->py[0];
        d2 = sqrtf(ox * ox + oy * oy);
    } else {
        d1 = fabsf(dx * (s->py[0] - s->py[1]) - (s->px[0] - s->px[1]) * dy) / len;
        d2 = fabsf(dx * (s->py[0] - s->py[2]) - (s->px[0] - s->px[2]) * dy) / len;
    }
    return d1 > d2 ? d1 : d2;
}

/* Samples to draw one cubic with, so the polyline stays within
   `BEZIER_FLATNESS_PX` of the curve (see the note at BEZIER_SAMPLE_MIN). */
static int bezier_samples(const CubicSeg *s) {
    float d = bezier_flatness(s);
    int n = (int)ceilf(sqrtf(3.0f * d / (4.0f * BEZIER_FLATNESS_PX)));
    if (n < BEZIER_SAMPLE_MIN) n = BEZIER_SAMPLE_MIN;
    if (n > BEZIER_SAMPLE_MAX) n = BEZIER_SAMPLE_MAX;
    return n;
}

static void sample_cubic(const CubicSeg *s, float t, float *ox, float *oy) {    float u = 1.0f - t;
    float u2 = u * u, u3 = u2 * u;
    float t2 = t * t, t3 = t2 * t;
    *ox = u3 * s->px[0] + 3.0f * u2 * t * s->px[1] + 3.0f * u * t2 * s->px[2] + t3 * s->px[3];
    *oy = u3 * s->py[0] + 3.0f * u2 * t * s->py[1] + 3.0f * u * t2 * s->py[2] + t3 * s->py[3];
}

static void tangent_cubic(const CubicSeg *s, float t, float *tx, float *ty) {
    float u = 1.0f - t;
    *tx = 3.0f * u * u * (s->px[1] - s->px[0]) +
          6.0f * u * t * (s->px[2] - s->px[1]) +
          3.0f * t * t * (s->px[3] - s->px[2]);
    *ty = 3.0f * u * u * (s->py[1] - s->py[0]) +
          6.0f * u * t * (s->py[2] - s->py[1]) +
          3.0f * t * t * (s->py[3] - s->py[2]);
}

static void tessellate_stroke(BezierPathObj *bp) {
    float nr = bp->sr / 255.0f;
    float ng = bp->sg / 255.0f;
    float nb = bp->sb / 255.0f;
    float half_w = bp->stroke_width * 0.5f + 0.5f;

    int total_segs = bp->num_segs;
    float progress = bp->progress;
    if (progress > 1.0f) progress = 1.0f;
    if (progress < 0.0f) progress = 0.0f;

    float target = progress * (float)total_segs;
    int full_segs = (int)target;
    float partial_t = target - (float)full_segs;
    if (full_segs > total_segs) full_segs = total_segs;

    float prev_x = 0, prev_y = 0, prev_nx = 0, prev_ny = 0;
    int has_prev = 0;

    int cur_sub = 0;
    float wind = (bp->sub_count > 0) ? (float)bp->sub_winding[0] : 1.0f;

    if (total_segs > 0 && full_segs >= 0) {
        const CubicSeg *s0 = &BP_SEG(bp, 0);
        float tx0, ty0;
        sample_cubic(s0, 0.0f, &prev_x, &prev_y);
        tangent_cubic(s0, 0.0f, &tx0, &ty0);
        float tlen0 = sqrtf(tx0 * tx0 + ty0 * ty0);
        if (tlen0 < 0.0001f) tlen0 = 0.0001f;
        prev_nx = (-ty0 / tlen0) * half_w * wind;
        prev_ny = (tx0 / tlen0) * half_w * wind;
        has_prev = 1;
    }

    for (int si = 0; si <= full_segs && si < total_segs; si++) {
        const CubicSeg *s = &BP_SEG(bp, si);
        int n = bezier_samples(s);
        int end_n = (si == full_segs && partial_t > 0.001f) ? (int)(partial_t * n + 0.5f) : n;
        if (end_n < 1) end_n = 1;
        int start_i = (si == 0) ? 1 : 0;

        for (int i = start_i; i <= end_n; i++) {
            float t = (float)i / (float)n;
            if (si == full_segs && partial_t > 0.001f) {
                t = (float)i / (float)n * partial_t;
            }

            float px, py, tx, ty;
            sample_cubic(s, t, &px, &py);
            tangent_cubic(s, t, &tx, &ty);

            float tlen = sqrtf(tx * tx + ty * ty);
            if (tlen < 0.0001f) tlen = 0.0001f;

            if (si > 0 && i == start_i && has_prev) {
                float dx = px - prev_x;
                float dy = py - prev_y;
                if (dx * dx + dy * dy > 1600.0f) {
                    cur_sub++;
                    if (cur_sub < bp->sub_count) {
                        wind = (float)bp->sub_winding[cur_sub];
                    }
                    prev_x = px; prev_y = py;
                    prev_nx = (-ty / tlen) * half_w * wind;
                    prev_ny = (tx / tlen) * half_w * wind;
                    has_prev = 1;
                    continue;
                }
                float cnx = (-ty / tlen) * half_w * wind;
                float cny = (tx / tlen) * half_w * wind;
                if (g_vertex_count + 3 > MAX_VERTICES) return;
                PushVertex(prev_x, prev_y, nr, ng, nb, bp->alpha);
                PushVertex(prev_x - prev_nx, prev_y - prev_ny, nr, ng, nb, bp->alpha);
                PushVertex(px - cnx, py - cny, nr, ng, nb, bp->alpha);
                prev_x = px; prev_y = py;
                prev_nx = cnx; prev_ny = cny;
                has_prev = 1;
                continue;
            }

            float nx = (-ty / tlen) * half_w * wind;
            float ny = (tx / tlen) * half_w * wind;

            if (has_prev) {
                if (g_vertex_count + 6 > MAX_VERTICES) return;
                PushVertex(prev_x, prev_y, nr, ng, nb, bp->alpha);
                PushVertex(prev_x - prev_nx, prev_y - prev_ny, nr, ng, nb, bp->alpha);
                PushVertex(px, py, nr, ng, nb, bp->alpha);

                PushVertex(prev_x - prev_nx, prev_y - prev_ny, nr, ng, nb, bp->alpha);
                PushVertex(px - nx, py - ny, nr, ng, nb, bp->alpha);
                PushVertex(px, py, nr, ng, nb, bp->alpha);
            }

            prev_x = px; prev_y = py;
            prev_nx = nx; prev_ny = ny;
            has_prev = 1;
        }
    }
}

static float g_cross_x[4096];
static int g_cross_dir[4096];

static int g_pt_sub[ MAX_BEZIER_SEGMENTS * BEZIER_SAMPLE_MAX + 1 ];

/* --- fill helpers -------------------------------------------------------
   The scanline below used to emit TWO TRIANGLES PER COVERED PIXEL (6
   vertices each), so a fill cost 6 * area vertices.  That is affordable for
   a glyph and catastrophic for a screen-filling path: FocusOn's starting
   `Dot(radius = frame_x_radius + frame_y_radius)` (11.11 units, larger than
   the frame) covers the whole 1920x1080 stage, i.e. 2 073 600 px = 12.4 M
   vertices against MAX_VERTICES = 4.19 M.  `tessellate_fill` therefore hit
   the cap part-way down the frame and `return`ed, so the rows below the cut
   never got their span.

   Measured on wiki 03-动画/强调与提示 (02-圈注与聚焦.mp4, reported as
   "圆形uncreate方向错误，聚焦动画播放错误"): at f401 ManimCE carries the
   purple spotlight over the whole frame (row luma ~19.8 everywhere) while
   RTM matches it down to y=395 and is then PURE BLACK (row luma 0.000) to
   the bottom -- a straight horizontal cut that moves down as the disc
   shrinks (f410 reaches y=761, f430 y=604), i.e. exactly the signature of a
   per-frame vertex budget running out, not of any geometry.

   Only the FIRST and LAST pixel of a span are partially covered; every pixel
   between them has coverage exactly 1.0 and therefore the same colour and
   alpha, so they collapse into ONE quad per span.  The cost drops to
   O(rows + columns): at most 18 vertices per row instead of 6 * width, and
   the emitted pixels are bit-for-bit the ones the per-pixel loop produced
   (an interior pixel's coverage is 1.0 both ways, an edge pixel keeps its
   own partial quad). */

static int push_fill_quad2(float x0, float x1, float y0, float y1,
                           float l_r, float l_g, float l_b,
                           float r_r, float r_g, float r_b, float a) {
    if (g_vertex_count + 6 > MAX_VERTICES) return 0;
    PushVertex(x0, y0, l_r, l_g, l_b, a);
    PushVertex(x1, y0, r_r, r_g, r_b, a);
    PushVertex(x1, y1, r_r, r_g, r_b, a);
    PushVertex(x0, y0, l_r, l_g, l_b, a);
    PushVertex(x1, y1, r_r, r_g, r_b, a);
    PushVertex(x0, y1, l_r, l_g, l_b, a);
    return 1;
}

static int push_fill_quad(float x0, float x1, float y0, float y1,
                          float r, float g, float b, float a) {
    return push_fill_quad2(x0, x1, y0, y1, r, g, b, r, g, b, a);
}

/* Everything one scanline span needs to shade itself; keeps the helpers
   below at a readable parameter count. */
typedef struct {
    const BezierPathObj *bp;
    float cr, cg, cb;              /* fill colour stop 0 */
    float gr, gg, gb;              /* fill colour stop 1 (gradient) */
    float gdx, gdy, glen2;         /* gradient axis, screen pixels */
    float fill_alpha;
    int gradient;
} FillCtx;

/* One anti-aliased pixel of the span.  Returns 0 only when the per-frame
   vertex budget is spent (the caller then aborts the fill, exactly as the
   old per-pixel loop did).  A pixel that is < 5 % covered is skipped and
   still counts as "done" -- that is the original rule, unchanged. */
static int push_fill_pixel(const FillCtx *c, int px, float xl, float xr,
                           float scan_y) {
    float seg_l = (float)px;
    float seg_r = seg_l + 1.0f;
    float coverage_l = (xl > seg_l) ? xl : seg_l;
    float coverage_r = (xr < seg_r) ? xr : seg_r;
    float coverage = coverage_r - coverage_l;
    if (coverage < 0.05f) return 1;

    // Straight-alpha fill: keep the full fill colour and fold the pixel
    // coverage into the alpha.  Previously the colour was scaled by coverage
    // while alpha stayed opaque, which turned low-coverage edge pixels into a
    // dark 1px rim around glyphs (visible on any non-black background).
    float pr = c->cr, pg = c->cg, pb = c->cb;
    if (c->gradient) {
        float tt = ((seg_l + 0.5f - c->bp->gx1) * c->gdx
                    + (scan_y - c->bp->gy1) * c->gdy) / c->glen2;
        tt = tt < 0.0f ? 0.0f : (tt > 1.0f ? 1.0f : tt);
        pr = c->cr + (c->gr - c->cr) * tt;
        pg = c->cg + (c->gg - c->cg) * tt;
        pb = c->cb + (c->gb - c->cb) * tt;
    }
    return push_fill_quad(seg_l, seg_r, scan_y, scan_y + 1.0f,
                          pr, pg, pb, c->fill_alpha * coverage);
}

/* Colours of the two ends of a run of fully covered pixels.  Returns 0 when
   the interpolation parameter clamps at either end: outside [0, 1] the ramp
   is no longer affine across the run, so linear interpolation between the
   two end colours would NOT reproduce the per-pixel clamp -- the caller then
   keeps the old per-pixel emission for that run. */
static int gradient_run_colors(const BezierPathObj *bp, float xl, float xr,
                               float scan_y, float cr, float cg, float cb,
                               float *l_r, float *l_g, float *l_b,
                               float *r_r, float *r_g, float *r_b) {
    float gdx = bp->gx2 - bp->gx1;
    float gdy = bp->gy2 - bp->gy1;
    float glen2 = gdx * gdx + gdy * gdy;
    if (glen2 <= 1e-6f) return 0;
    float tl = ((xl - bp->gx1) * gdx + (scan_y - bp->gy1) * gdy) / glen2;
    float tr = ((xr - bp->gx1) * gdx + (scan_y - bp->gy1) * gdy) / glen2;
    if (tl <= 0.0f || tl >= 1.0f || tr <= 0.0f || tr >= 1.0f) return 0;
    float gr = bp->fr2 / 255.0f;
    float gg = bp->fg2 / 255.0f;
    float gb = bp->fb2 / 255.0f;
    *l_r = cr + (gr - cr) * tl;
    *l_g = cg + (gg - cg) * tl;
    *l_b = cb + (gb - cb) * tl;
    *r_r = cr + (gr - cr) * tr;
    *r_g = cg + (gg - cg) * tr;
    *r_b = cb + (gb - cb) * tr;
    return 1;
}

static void tessellate_fill(BezierPathObj *bp) {
    float fr = bp->fr / 255.0f;
    float fg = bp->fg / 255.0f;
    float fb = bp->fb / 255.0f;
    float fo = bp->fill_opacity;
    // Straight-alpha fill: colour stays full; opacity goes into alpha.
    // Baking opacity into the colour (cr = fr * fo) made low-opacity fills
    // (e.g. the start of a Write fill ramp) render as BLACK instead of
    // transparent — the colour approached 0 while alpha stayed ~1.
    float cr = fr, cg = fg, cb = fb;
    float fill_alpha = fo * bp->alpha;

    // Optional second fill stop.  manim shades a 3D face with TWO colours (its
    // start- and end-corner stops) and Cairo interpolates between them across
    // the path; a single flat colour caps the peak -- measured on
    // SolidPrimitives3D's Sphere, CE's bright limb reaches luma 249 while the
    // averaged single colour tops out near 195, which is what made the Surfaces
    // read flat.  The axis is in screen pixels; a degenerate axis keeps the
    // flat colour, so a caller that passes the same colour twice is unaffected.
    float gr = bp->fr2 / 255.0f;
    float gg = bp->fg2 / 255.0f;
    float gb = bp->fb2 / 255.0f;
    float gdx = bp->gx2 - bp->gx1;
    float gdy = bp->gy2 - bp->gy1;
    float glen2 = gdx * gdx + gdy * gdy;
    int gradient = (glen2 > 1e-6f);

    int total_pts = 0;

    for (int s = 0; s < bp->sub_count; s++) {
        int start = bp->sub_seg_start[s];
        int end = (s < bp->sub_count - 1) ? bp->sub_seg_start[s + 1] : bp->num_segs;

        for (int si = start; si < end; si++) {
            const CubicSeg *seg = &BP_SEG(bp, si);
            int sn = bezier_samples(seg);
            for (int i = 0; i < sn; i++) {
                float t = (float)i / (float)sn;
                sample_cubic(seg, t, &g_fill_pts[total_pts][0], &g_fill_pts[total_pts][1]);
                g_pt_sub[total_pts] = s;
                total_pts++;
                if (total_pts >= MAX_BEZIER_SEGMENTS * BEZIER_SAMPLE_MAX) goto done_sample_all;
            }
        }
    }
done_sample_all:
    if (total_pts < 3) return;

    float y_min = g_fill_pts[0][1], y_max = g_fill_pts[0][1];
    for (int i = 1; i < total_pts; i++) {
        if (g_fill_pts[i][1] < y_min) y_min = g_fill_pts[i][1];
        if (g_fill_pts[i][1] > y_max) y_max = g_fill_pts[i][1];
    }

    int y_start = (int)floorf(y_min);
    int y_end = (int)ceilf(y_max);

    /* Clamp the scan to the surface.  Rows outside it are clipped by the
       viewport anyway, so they cannot ink a pixel -- but the loop still paid a
       full `total_pts` crossing pass for every one of them, so a fill parked
       far off-screen (a Transform mid-flight, a mobject shifted well outside
       the frame) burned time proportional to its off-screen pixel bbox and
       stalled the frame.  Unclamped this ran to millions of rows; clamped it
       is at most the surface height. */
    int surf_h = (int)g_swapchain_ext.height;
    int surf_w = (int)g_swapchain_ext.width;
    if (surf_h > 0) {
        if (y_start < 0) y_start = 0;
        if (y_end > surf_h - 1) y_end = surf_h - 1;
    }

    for (int y = y_start; y <= y_end; y++) {
        float scan_y = (float)y + 0.5f;
        int n_cross = 0;

        for (int i = 0; i < total_pts && n_cross < 4096; i++) {
            int j;
            if (i + 1 < total_pts && g_pt_sub[i] == g_pt_sub[i + 1]) {
                j = i + 1;
            } else {
                int s = g_pt_sub[i];
                int sub_start_idx = 0;
                for (int k = 0; k < total_pts; k++) {
                    if (g_pt_sub[k] == s) { sub_start_idx = k; break; }
                }
                j = sub_start_idx;
            }
            float yi = g_fill_pts[i][1];
            float yj = g_fill_pts[j][1];
            float dy = yj - yi;
            if (fabsf(dy) < 0.0001f) continue;
            float ey0 = yi, ey1 = yj;
            if (ey0 > ey1) { float tmp = ey0; ey0 = ey1; ey1 = tmp; }
            if (scan_y <= ey0 || scan_y > ey1) continue;
            float t = (scan_y - yi) / dy;
            g_cross_x[n_cross] = g_fill_pts[i][0] + t * (g_fill_pts[j][0] - g_fill_pts[i][0]);
            g_cross_dir[n_cross] = (dy > 0) ? 1 : -1;
            n_cross++;
        }

        for (int a = 1; a < n_cross; a++) {
            float key_x = g_cross_x[a];
            int key_d = g_cross_dir[a];
            int b = a - 1;
            while (b >= 0 && g_cross_x[b] > key_x) {
                g_cross_x[b + 1] = g_cross_x[b];
                g_cross_dir[b + 1] = g_cross_dir[b];
                b--;
            }
            g_cross_x[b + 1] = key_x;
            g_cross_dir[b + 1] = key_d;
        }

        int inside = 0;
        for (int i = 0; i < n_cross; i++) {
            inside ^= 1;
            if (inside && i + 1 < n_cross) {
                float xl = g_cross_x[i];
                float xr = g_cross_x[i + 1];
                if (xr <= xl) continue;

                int px_start = (int)floorf(xl);
                int px_end = (int)ceilf(xr);

                /* Same clamp as the row loop, for the same reason: a span
                   entirely off-screen cannot ink anything, and the coverage
                   below is a max/min against the pixel span, so trimming the
                   loop bounds leaves every VISIBLE pixel's coverage bit-for-bit
                   identical. */
                if (surf_w > 0) {
                    if (px_start < 0) px_start = 0;
                    if (px_end > surf_w) px_end = surf_w;
                }

                FillCtx ctx;
                ctx.bp = bp;
                ctx.cr = cr; ctx.cg = cg; ctx.cb = cb;
                ctx.gr = gr; ctx.gg = gg; ctx.gb = gb;
                ctx.gdx = gdx; ctx.gdy = gdy; ctx.glen2 = glen2;
                ctx.fill_alpha = fill_alpha;
                ctx.gradient = gradient;

                /* Run of FULLY covered pixels: `p >= xl && p + 1 <= xr`, i.e.
                   p in [ceil(xl), floor(xr - 1)].  Every one of them would be
                   pushed with coverage exactly 1.0 and the same colour, so they
                   become a single quad -- this is what keeps a screen-filling
                   path inside the per-frame vertex budget (see the note above
                   `push_fill_quad`). */
                int full_start = (int)ceilf(xl);
                int full_end = (int)floorf(xr - 1.0f) + 1;
                if (full_start < px_start) full_start = px_start;
                if (full_end > px_end) full_end = px_end;
                if (full_end <= full_start) {
                    /* No interior pixel: emit every pixel of the span as its
                       own partial quad (the run collapses to nothing). */
                    full_start = px_start;
                    full_end = px_start;
                }

                for (int px = px_start; px < full_start; px++) {
                    if (!push_fill_pixel(&ctx, px, xl, xr, scan_y)) return;
                }

                if (full_end > full_start && gradient) {
                    float l_r, l_g, l_b, r_r, r_g, r_b;
                    /* pixel CENTRES of the first/last full pixel, so the two
                       end colours are exactly what the per-pixel loop would
                       have computed for them; Vulkan then interpolates
                       linearly across the quad (affine ramp) and reproduces
                       every interior pixel's colour. */
                    if (gradient_run_colors(bp,
                            (float)full_start + 0.5f,
                            (float)full_end - 0.5f,
                            scan_y, cr, cg, cb,
                            &l_r, &l_g, &l_b, &r_r, &r_g, &r_b)) {
                        if (!push_fill_quad2((float)full_start, (float)full_end,
                                             scan_y, scan_y + 1.0f,
                                             l_r, l_g, l_b, r_r, r_g, r_b,
                                             fill_alpha)) return;
                    } else {
                        /* the ramp clamps inside the run: keep the old
                           per-pixel emission for it */
                        for (int px = full_start; px < full_end; px++) {
                            if (!push_fill_pixel(&ctx, px, xl, xr, scan_y)) return;
                        }
                    }
                } else if (full_end > full_start) {
                    if (!push_fill_quad((float)full_start, (float)full_end,
                                        scan_y, scan_y + 1.0f,
                                        cr, cg, cb, fill_alpha)) return;
                }

                for (int px = full_end; px < px_end; px++) {
                    if (!push_fill_pixel(&ctx, px, xl, xr, scan_y)) return;
                }
            }
        }
    }
}

void BuildVerticesFromBezierPathAt(int i) {
    BezierPathObj *bp = &bezier_paths[i];
    if (bp->show_fill && bp->fill_opacity > 0.001f) {
        tessellate_fill(bp);
    }
    if (bp->show_stroke && bp->stroke_width > 0.001f) {
        tessellate_stroke(bp);
    }
}

/* Called once the frame's command list has been replayed: paths that were
   dropped (queue full) are discarded rather than drawn a frame late. */
void ResetBezierPaths(void) {
    bezier_path_count = 0;
    g_seg_pool_used = 0;
}

/* Replays every path submitted since the last reset (fill then stroke).
   Exported so the headless probe below can drive it directly. */
__declspec(dllexport) void BuildVerticesFromBezierPaths(void) {
    for (int i = 0; i < bezier_path_count; i++) {
        BuildVerticesFromBezierPathAt(i);
    }
    ResetBezierPaths();
}

/* --- headless regression probe -----------------------------------------
   The renderer reaches the tessellator only through Render_DrawScene with a
   live swapchain; nothing outside the DLL can see how many vertices a fill
   produced, yet "did the fill finish?" is exactly what
   wiki 03-动画/强调与提示 ("圆形uncreate方向错误，聚焦动画播放错误") was
   broken by.  These four entry points let a pytest drive
   AddBezierPath -> tessellate -> inspect on a machine with no GPU, no
   window and no image: it sets the surface size, resets the per-frame
   budget, runs the fill and reads the vertices back (NDC, as PushVertex
   stored them).  They do not touch the Vulkan renderer at all. */
__declspec(dllexport) unsigned int RtmTest_VertexCount(void) {
    return g_vertex_count;
}

__declspec(dllexport) int RtmTest_ReadVertex(int index, float *out6) {
    if (index < 0 || (uint32_t)index >= g_vertex_count || out6 == NULL) return 0;
    const float *v = &g_vertices[(uint32_t)index * 6];
    for (int k = 0; k < 6; k++) out6[k] = v[k];
    return 1;
}

__declspec(dllexport) void RtmTest_ResetFrame(void) {
    g_vertex_count = 0;
    ResetBezierPaths();
}

__declspec(dllexport) void RtmTest_SetSurfaceSize(unsigned int w, unsigned int h) {
    g_swapchain_ext.width = w;
    g_swapchain_ext.height = h;
}
