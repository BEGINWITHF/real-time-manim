#include <math.h>
#include "../draw_common.h"

void BuildVerticesFromCircles(const Circle *circles, int count) {
    for (int i = 0; i < count; i++) {
        const Circle *c = &circles[i];
        // One full turn, tessellated for its on-screen radius (see
        // curve_segments): 36 at the default zoom, more as the camera zooms in.
        const int segs = curve_segments(c->radius, 1.0f);
        const float step = -2.0f * 3.14159265f / (float)segs;

        float nr = c->r / 255.0f, ng = c->g / 255.0f, nb = c->b / 255.0f;
        float bn = c->border_r / 255.0f, bg = c->border_g / 255.0f, bb = c->border_b / 255.0f;

        float fill_radius = c->radius - c->border_width;
        if (fill_radius < 0.0f) fill_radius = 0.0f;

        if (fill_radius > 0.0f && c->stroke_progress > 0.0f) {
            int fill_segs = (int)(segs * c->stroke_progress);
            if (fill_segs > segs) fill_segs = segs;
            if (fill_segs < 1) fill_segs = 1;

            if (g_vertex_count + (fill_segs * 3) > MAX_VERTICES) break;

            float start_x = c->x + fill_radius;
            float start_y = c->y;

            for (int j = 0; j < fill_segs; j++) {
                float a1 = step * (float)j;
                float a2 = step * (float)(j + 1);

                float x1 = c->x + cosf(a1) * fill_radius;
                float y1 = c->y + sinf(a1) * fill_radius;
                float x2 = c->x + cosf(a2) * fill_radius;
                float y2 = c->y + sinf(a2) * fill_radius;

                PushVertex(start_x, start_y, nr, ng, nb, c->alpha);
                PushVertex(x1, y1, nr, ng, nb, c->alpha);
                PushVertex(x2, y2, nr, ng, nb, c->alpha);
            }
        }

        if (c->border_width > 0.0f && c->radius > 0.0f && c->stroke_progress > 0.0f) {
            int draw_segs = (int)(segs * c->stroke_progress);
            if (draw_segs > segs) draw_segs = segs;
            if (draw_segs < 1) draw_segs = 1;

            if (g_vertex_count + (draw_segs * 6) > MAX_VERTICES) break;

            float inner_r = fill_radius;
            float outer_r = c->radius;

            for (int j = 0; j < draw_segs; j++) {
                float a1 = step * (float)j;
                float a2 = step * (float)(j + 1);

                PushVertex(c->x + cosf(a1) * inner_r, c->y + sinf(a1) * inner_r, bn, bg, bb, c->alpha);
                PushVertex(c->x + cosf(a1) * outer_r, c->y + sinf(a1) * outer_r, bn, bg, bb, c->alpha);
                PushVertex(c->x + cosf(a2) * inner_r, c->y + sinf(a2) * inner_r, bn, bg, bb, c->alpha);

                PushVertex(c->x + cosf(a1) * outer_r, c->y + sinf(a1) * outer_r, bn, bg, bb, c->alpha);
                PushVertex(c->x + cosf(a2) * outer_r, c->y + sinf(a2) * outer_r, bn, bg, bb, c->alpha);
                PushVertex(c->x + cosf(a2) * inner_r, c->y + sinf(a2) * inner_r, bn, bg, bb, c->alpha);
            }
        }
    }
}