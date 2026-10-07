#ifndef DRAW_COMMON_H
#define DRAW_COMMON_H

#include "vulkan_core.h"
#include <math.h>

extern float g_vertices[];
extern uint32_t g_vertex_count;
extern VkExtent2D g_swapchain_ext;

/* The bezier *fill* emits vertices proportional to the filled **area**, so the
 * budget has to be a per-frame vertex count, not a shape count: at 1080p a
 * single Surface scene needs > 2 M vertices.  The old Windows value (1 048 576)
 * overran at ~1.3 M px, and `PushVertex` drops silently on overflow -- measured
 * on ThreeDSurfacePlot: lit pixels 71 068 at 854x480 (correct) but only 147 396
 * at 1920x1080 against CE's 355 469, i.e. the fills were being discarded from
 * the point the cap was hit (which also reads as "the lighting comes and goes"
 * and "only half of the shape").  Windows now matches the other platforms. */
#define MAX_VERTICES 4194304

static inline void ToNDC(float px, float py, float *nx, float *ny) {
    *nx = (px / (float)g_swapchain_ext.width) * 2.0f - 1.0f;
    *ny = (py / (float)g_swapchain_ext.height) * 2.0f - 1.0f;
}

static inline int PushVertex(float px, float py, float r, float g, float b, float a) {
    if (g_vertex_count >= MAX_VERTICES) return 0;

    float nx, ny;
    ToNDC(px, py, &nx, &ny);

    uint32_t idx = g_vertex_count * 6;
    g_vertices[idx + 0] = nx;
    g_vertices[idx + 1] = ny;
    g_vertices[idx + 2] = r;
    g_vertices[idx + 3] = g;
    g_vertices[idx + 4] = b;
    g_vertices[idx + 5] = a;

    g_vertex_count++;
    return 1;
}

/* Draw order.  Render_DrawScene replays the command list, so every primitive
 * has to get an entry in it -- in the order it was submitted, which is
 * manim's own order (a mobject's fill, then its stroke, then the next
 * mobject).  The bezier fill and the line-strip stroke used to be flushed
 * AFTER the whole list (vulkan_draw.c:89-90), so every stroke landed on top
 * of every fill and every earlier fill landed on top of a later shape: a
 * Sphere's quad borders showed through its own fill (read as "the surface
 * fill is see-through"), an earlier mobject's outline painted over a later
 * mobject's body, and a bezier fill covered a later rect/circle/text.
 * Values 0..9 live in vulkan_render.h. */
#define CMD_BEZIER 10
#define CMD_LINE_STRIP 11

/* Implemented by platform.c / platform_mac.m, which own the command list. */
void DrawCmd_Push(int type, int index);

#endif
