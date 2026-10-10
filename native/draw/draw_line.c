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
    if (num_points < 2 || g_strip_count >= MAX_LINE_STRIPS) return;
    if (num_points > MAX_STRIP_POINTS) num_points = MAX_STRIP_POINTS;
    if (g_strip_pool_used + num_points > MAX_STRIP_POOL_POINTS) return;

    int cmd_index = g_strip_count;
    LineStripObj *s = &g_strips[cmd_index];
    s->pt_start = g_strip_pool_used;
    g_strip_pool_used += num_points;
    s->num_points = num_points;
    s->width = width;
    s->r = r; s->g = g; s->b = b;
    s->alpha = alpha;
    s->has_per_vertex_alpha = (alphas != 0);
    for (int i = 0; i < num_points * 2; i++) {
        g_strip_pool_xy[s->pt_start * 2 + i] = points[i];
    }
    if (alphas) {
        for (int i = 0; i < num_points; i++) {
            g_strip_pool_a[s->pt_start + i] = alphas[i];
        }
    }
    g_strip_count++;
    /* Drawn at its submission position: the stroke belongs to the mobject
       that is being sent right now, not to the end of the frame. */
    DrawCmd_Push(CMD_LINE_STRIP, cmd_index);
}

void ResetLineStrips(void) {
    g_strip_count = 0;
    g_strip_pool_used = 0;
}

void BuildVerticesFromLineStripAt(int si) {
    LineStripObj *s = &g_strips[si];
    int n = s->num_points;
    if (n < 2) return;
    int base = s->pt_start;

    float nr = s->r / 255.0f, ng = s->g / 255.0f, nb = s->b / 255.0f;
    float thick = (float)s->width;
    float half_w = thick * 0.5f + 0.5f;

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

        float nx = (-dy / len) * half_w;
        float ny = (dx / len) * half_w;

        float a0 = s->has_per_vertex_alpha ? g_strip_pool_a[base + i] : s->alpha;
        float a1 = s->has_per_vertex_alpha ? g_strip_pool_a[base + i + 1] : s->alpha;

        PushVertex(x0 + nx, y0 + ny, nr, ng, nb, a0);
        PushVertex(x0 - nx, y0 - ny, nr, ng, nb, a0);
        PushVertex(x1 + nx, y1 + ny, nr, ng, nb, a1);

        PushVertex(x0 - nx, y0 - ny, nr, ng, nb, a0);
        PushVertex(x1 - nx, y1 - ny, nr, ng, nb, a1);
        PushVertex(x1 + nx, y1 + ny, nr, ng, nb, a1);
    }
}

void BuildVerticesFromLineStrips(void) {
    for (int si = 0; si < g_strip_count; si++) {
        BuildVerticesFromLineStripAt(si);
    }
    g_strip_count = 0;
    g_strip_pool_used = 0;
}
