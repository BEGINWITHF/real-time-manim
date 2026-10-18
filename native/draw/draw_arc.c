#include <math.h>
#include "../draw_common.h"

void BuildVerticesFromArcs(const ArcObj* arcs, int count) {
    for (int i = 0; i < count; i++) {
        const ArcObj* a = &arcs[i];
        // Segments for the swept fraction of a turn, sized for the on-screen
        // radius (see curve_segments) so a zoomed arc stays smooth.
        float turns = fabsf(a->angle) / (2.0f * 3.14159265f);
        const int segs = curve_segments(a->radius, turns);
        float nr = a->r / 255.0f, ng = a->g / 255.0f, nb = a->b / 255.0f;
        float sw = a->stroke_width;

        if (g_vertex_count + segs * 6 > MAX_VERTICES) break;

        for (int j = 0; j < segs; j++) {
            float t1 = (float)j / segs;
            float t2 = (float)(j + 1) / segs;
            float ang1 = a->start_angle + a->angle * t1;
            float ang2 = a->start_angle + a->angle * t2;

            float cx1 = a->x + cosf(ang1) * a->radius;
            float cy1 = a->y + sinf(ang1) * a->radius;
            float cx2 = a->x + cosf(ang2) * a->radius;
            float cy2 = a->y + sinf(ang2) * a->radius;

            float ddx = cx2 - cx1;
            float ddy = cy2 - cy1;
            float dlen = sqrtf(ddx * ddx + ddy * ddy);
            if (dlen < 0.0001f) continue;

            float hw = sw * 0.5f;
            float pnx = (-ddy / dlen) * hw;
            float pny = (ddx / dlen) * hw;

            PushVertex(cx1 + pnx, cy1 + pny, nr, ng, nb, a->alpha);
            PushVertex(cx1 - pnx, cy1 - pny, nr, ng, nb, a->alpha);
            PushVertex(cx2 + pnx, cy2 + pny, nr, ng, nb, a->alpha);

            PushVertex(cx1 - pnx, cy1 - pny, nr, ng, nb, a->alpha);
            PushVertex(cx2 - pnx, cy2 - pny, nr, ng, nb, a->alpha);
            PushVertex(cx2 + pnx, cy2 + pny, nr, ng, nb, a->alpha);
        }
    }
}
