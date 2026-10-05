#include <math.h>
#include "../draw_common.h"

void BuildVerticesFromPoints(const PointObj* points, int count) {
    const int segs = 12;
    const float default_radius = 2.0f;
    float step = 2.0f * 3.14159265f / (float)segs;

    for (int i = 0; i < count; i++) {
        const PointObj* p = &points[i];
        float nr = p->r / 255.0f, ng = p->g / 255.0f, nb = p->b / 255.0f;
        float radius = p->radius > 0.0f ? p->radius : default_radius;

        if (g_vertex_count + segs * 3 > MAX_VERTICES) break;

        for (int j = 0; j < segs; j++) {
            float a1 = step * (float)j;
            float a2 = step * (float)(j + 1);

            PushVertex(p->x, p->y, nr, ng, nb, p->alpha);
            PushVertex(p->x + cosf(a1) * radius, p->y + sinf(a1) * radius, nr, ng, nb, p->alpha);
            PushVertex(p->x + cosf(a2) * radius, p->y + sinf(a2) * radius, nr, ng, nb, p->alpha);
        }
    }
}
