#include "../draw_common.h"
#include "../shared_types.h"

void BuildVerticesFromLines(const LineObj *lines, int count) {
    for (int i = 0; i < count; i++) {
        if (g_vertex_count + 6 > MAX_VERTICES) break;

        const LineObj *l = &lines[i];
        float nr = l->r / 255.0f, ng = l->g / 255.0f, nb = l->b / 255.0f;

        float dx = l->x2 - l->x1;
        float dy = l->y2 - l->y1;
        float len = sqrtf(dx*dx + dy*dy);

        if (len < 0.0001f) continue;

        float thick = (float)l->width;
        float half_thick = thick * 0.5f + 0.5f;
        float nx = (-dy / len) * half_thick;
        float ny = (dx / len) * half_thick;

        float ux = dx / len;
        float uy = dy / len;
        float ex1 = l->x1 - ux * half_thick;
        float ey1 = l->y1 - uy * half_thick;
        float ex2 = l->x2 + ux * half_thick;
        float ey2 = l->y2 + uy * half_thick;

        PushVertex(ex1 + nx, ey1 + ny, nr, ng, nb, l->alpha);
        PushVertex(ex1 - nx, ey1 - ny, nr, ng, nb, l->alpha);
        PushVertex(ex2 + nx, ey2 + ny, nr, ng, nb, l->alpha);

        PushVertex(ex1 - nx, ey1 - ny, nr, ng, nb, l->alpha);
        PushVertex(ex2 - nx, ey2 - ny, nr, ng, nb, l->alpha);
        PushVertex(ex2 + nx, ey2 + ny, nr, ng, nb, l->alpha);
    }
}

#define MAX_LINE_STRIPS 4096
#define MAX_STRIP_POINTS 16384
/* Points live in one shared pool and a strip only stores its offset, so a
   strip costs ~40 bytes instead of 192 KB.  The old layout was one inline
   points[16384*2]+alphas[16384] per strip, which capped the strip list at
   512 -- and ThreeDSurfaceLab submits 1325 strips per frame (every surface
   cell strokes), so whichever mobject landed past #512 was silently dropped
   (measured: the depth-sorted ribbon flushed at #1319 and its yellow stroke
   vanished, 0 px vs CE 1928). */
#define MAX_STRIP_POOL_POINTS 2097152

typedef struct {
    int pt_start;                 /* offset into g_strip_pool */
    int num_points;
    int width;
    int r, g, b;
    int has_per_vertex_alpha;
    float alpha;
} LineStripObj;

static LineStripObj g_strips[MAX_LINE_STRIPS];
static float g_strip_pool_xy[MAX_STRIP_POOL_POINTS * 2];
static float g_strip_pool_a[MAX_STRIP_POOL_POINTS];
static int g_strip_count = 0;
static int g_strip_pool_used = 0;

__declspec(dllexport) void AddLineStrip(
    const float *points, const float *alphas, int num_points,
    int width, int r, int g, int b, float alpha)
{
    if (points == NULL) return;
    if (num_points < 2 || g_strip_count >= MAX_LINE_STRIPS) return;

    /* A strip longer than MAX_STRIP_POINTS used to be SILENTLY cut off, so the
       stroke simply stopped mid-path -- a visible break with no warning (and
       callers such as the surface-lab ribbons do exceed it).  Emit the
       overflow as extra strips instead, each starting on the previous strip's
       last point so the run stays continuous. */
    int remaining = num_points;
    int src = 0;
    while (remaining >= 2 && g_strip_count < MAX_LINE_STRIPS) {
        int take = remaining > MAX_STRIP_POINTS ? MAX_STRIP_POINTS : remaining;
        if (g_strip_pool_used + take > MAX_STRIP_POOL_POINTS) return;

        int cmd_index = g_strip_count;
        LineStripObj *s = &g_strips[cmd_index];
        s->pt_start = g_strip_pool_used;
        g_strip_pool_used += take;
        s->num_points = take;
        s->width = width;
        s->r = r; s->g = g; s->b = b;
        s->alpha = alpha;
        s->has_per_vertex_alpha = (alphas != 0);
        for (int i = 0; i < take * 2; i++) {
            g_strip_pool_xy[s->pt_start * 2 + i] = points[(src * 2) + i];
        }
        if (alphas) {
            for (int i = 0; i < take; i++) {
                g_strip_pool_a[s->pt_start + i] = alphas[src + i];
            }
        }
        g_strip_count++;
        /* Drawn at its submission position: the stroke belongs to the mobject
           that is being sent right now, not to the end of the frame. */
        DrawCmd_Push(CMD_LINE_STRIP, cmd_index);

        remaining -= take - 1;      /* the next strip restarts on the last point */
        src += take - 1;
        if (take < 2) break;
    }
}

void ResetLineStrips(void) {
    g_strip_count = 0;
    g_strip_pool_used = 0;
}

/* Unit direction of the strip's (i0 -> i1) segment; 0 if it is degenerate. */
static int StripDir(int base, int i0, int i1, float *ux, float *uy) {
    float dx = g_strip_pool_xy[(base + i1) * 2] - g_strip_pool_xy[(base + i0) * 2];
    float dy = g_strip_pool_xy[(base + i1) * 2 + 1] - g_strip_pool_xy[(base + i0) * 2 + 1];
    float len = sqrtf(dx * dx + dy * dy);
    if (len < 0.0001f) return 0;
    *ux = dx / len;
    *uy = dy / len;
    return 1;
}

/* The two corners that BOTH quads meeting at (px,py) have to end on.

   Cutting each quad with its own perpendicular end cap (the old behaviour)
   misses a wedge on the outside of every turn -- base ~ half_w * turn_angle,
   about 1 px all round a stroked 48-gon, rasterised as dark ticks across the
   border -- and covers a matching wedge twice on the inside, which composites
   brighter while alpha < 1.  Cutting both quads along ONE line makes them
   tile exactly; for that line to reach the outer mitre point (and the inner
   one on the far side) it must pass through the joint along n_in + n_out,
   the bisector of the two caps.  Both neighbours call this with the joint's
   own (in,out) directions, so they compute bit-identical corners and share
   an edge with no crack.

   Open strip ends pass their direction twice: n + n is that segment's own
   normal, i.e. the plain perpendicular cap drawn before.  A direction
   flagged missing (zero-length neighbour) is filled from the surviving side. */
static void JointCutCorners(
    float px, float py,
    int have_in, float inx, float iny,
    int have_out, float outx, float outy,
    float half_w,
    float *ax, float *ay, float *bx, float *by)
{
    if (!have_in && !have_out) {
        inx = 1.0f; iny = 0.0f;
        outx = 1.0f; outy = 0.0f;
    } else if (!have_in) {
        inx = outx; iny = outy;
    } else if (!have_out) {
        outx = inx; outy = iny;
    }

    float cx = -iny - outy;         /* n_in + n_out, the cut's direction */
    float cy = inx + outx;
    float cl = sqrtf(cx * cx + cy * cy);
    if (cl < 0.5f) {
        /* Turn past ~151 deg: the mitre would reach beyond 4 half widths
           (and at exactly 180 deg the normals cancel).  Share a plain cap
           line instead; only such near-fold-back joints keep a notch. */
        cx = -iny;
        cy = inx;
        cl = 1.0f;
    }
    cx /= cl;
    cy /= cl;

    /* Intersect the cut line (px,py) + t*(cx,cy) with the incoming
       segment's offset lines (px,py) +- half_w*n + s*(inx,iny); crossing
       with the direction (n cross in == -1) gives t * (cx cross in) == -+
       half_w. */
    float denom = cx * iny - cy * inx;
    if (denom > -1e-4f && denom < 1e-4f) {
        /* unreachable: |denom| = cos(turn/2) >= 0.25 by the guard above */
        *ax = px - iny * half_w;
        *ay = py + inx * half_w;
        *bx = px + iny * half_w;
        *by = py - inx * half_w;
        return;
    }
    float tp = -half_w / denom;     /* on the +normal side */
    float tm = half_w / denom;
    *ax = px + tp * cx;
    *ay = py + tp * cy;
    *bx = px + tm * cx;
    *by = py + tm * cy;
}

void BuildVerticesFromLineStripAt(int si) {
    LineStripObj *s = &g_strips[si];
    int n = s->num_points;
    if (n < 2) return;
    int base = s->pt_start;

    float nr = s->r / 255.0f, ng = s->g / 255.0f, nb = s->b / 255.0f;
    float thick = (float)s->width;
    float half_w = thick * 0.5f + 0.5f;

    /* A strip whose last point comes back to its first is a closed outline:
       its seam is then a joint like any other, while the two open ends of a
       partial stroke keep their perpendicular caps. */
    int closed = 0;
    float seam_x = 0.0f, seam_y = 0.0f;
    if (n >= 3) {
        seam_x = g_strip_pool_xy[base * 2];
        seam_y = g_strip_pool_xy[base * 2 + 1];
        float ddx = seam_x - g_strip_pool_xy[(base + n - 1) * 2];
        float ddy = seam_y - g_strip_pool_xy[(base + n - 1) * 2 + 1];
        closed = (ddx > -1e-3f && ddx < 1e-3f && ddy > -1e-3f && ddy < 1e-3f);
    }

    for (int i = 0; i < n - 1; i++) {
        if (g_vertex_count + 6 > MAX_VERTICES) break;

        float x0 = g_strip_pool_xy[(base + i) * 2];
        float y0 = g_strip_pool_xy[(base + i) * 2 + 1];
        float x1 = g_strip_pool_xy[(base + i + 1) * 2];
        float y1 = g_strip_pool_xy[(base + i + 1) * 2 + 1];

        float dx = x1 - x0;
        float dy = y1 - y0;
        float len = sqrtf(dx * dx + dy * dy);
        if (len < 0.0001f) continue;

        float ux = dx / len;
        float uy = dy / len;

        float a0 = s->has_per_vertex_alpha ? g_strip_pool_a[base + i] : s->alpha;
        float a1 = s->has_per_vertex_alpha ? g_strip_pool_a[base + i + 1] : s->alpha;

        /* Start cap.  Both neighbours fetch a joint's directions through the
           same StripDir calls, so their corners are bit-identical. */
        float jx = x0, jy = y0;
        float inx = ux, iny = uy, outx = ux, outy = uy;
        int have_in = 1, have_out = 1;
        if (i > 0) {
            have_in = StripDir(base, i - 1, i, &inx, &iny);
            have_out = StripDir(base, i, i + 1, &outx, &outy);
        } else if (closed) {
            jx = seam_x; jy = seam_y;
            have_in = StripDir(base, n - 2, n - 1, &inx, &iny);
            have_out = StripDir(base, 0, 1, &outx, &outy);
        }
        float sxa, sya, sxb, syb;
        JointCutCorners(jx, jy, have_in, inx, iny, have_out, outx, outy,
                        half_w, &sxa, &sya, &sxb, &syb);

        /* End cap. */
        jx = x1; jy = y1;
        inx = ux; iny = uy; outx = ux; outy = uy;
        have_in = 1; have_out = 1;
        if (i < n - 2) {
            have_in = StripDir(base, i, i + 1, &inx, &iny);
            have_out = StripDir(base, i + 1, i + 2, &outx, &outy);
        } else if (closed) {
            jx = seam_x; jy = seam_y;
            have_in = StripDir(base, n - 2, n - 1, &inx, &iny);
            have_out = StripDir(base, 0, 1, &outx, &outy);
        }
        float exa, eya, exb, eyb;
        JointCutCorners(jx, jy, have_in, inx, iny, have_out, outx, outy,
                        half_w, &exa, &eya, &exb, &eyb);

        /* A segment shorter than its two mitre cuts would bow-tie (the cut
           corners cross past each other); keep the plain caps there rather
           than emit a self-crossing quad. */
        if ((exa - sxa) * ux + (eya - sya) * uy <= 0.0f ||
            (exb - sxb) * ux + (eyb - syb) * uy <= 0.0f) {
            float nx = -uy * half_w;
            float ny = ux * half_w;
            sxa = x0 + nx; sya = y0 + ny;
            sxb = x0 - nx; syb = y0 - ny;
            exa = x1 + nx; eya = y1 + ny;
            exb = x1 - nx; eyb = y1 - ny;
        }

        PushVertex(sxa, sya, nr, ng, nb, a0);
        PushVertex(sxb, syb, nr, ng, nb, a0);
        PushVertex(exa, eya, nr, ng, nb, a1);

        PushVertex(sxb, syb, nr, ng, nb, a0);
        PushVertex(exb, eyb, nr, ng, nb, a1);
        PushVertex(exa, eya, nr, ng, nb, a1);
    }
}

void BuildVerticesFromLineStrips(void) {
    for (int si = 0; si < g_strip_count; si++) {
        BuildVerticesFromLineStripAt(si);
    }
    g_strip_count = 0;
    g_strip_pool_used = 0;
}
