#include <math.h>
#include "../draw_common.h"

void BuildVerticesFromDashedLines(const DashedLineObj* lines, int count) {
    for (int i = 0; i < count; i++) {
        const DashedLineObj* l = &lines[i];
        float dx = l->x2 - l->x1;
        float dy = l->y2 - l->y1;
        float length = sqrtf(dx * dx + dy * dy);
        if (length < 0.0001f) continue;

        float nr = l->r / 255.0f, ng = l->g / 255.0f, nb = l->b / 255.0f;
        float nx = dx / length;
        float ny = dy / length;
        float pos = 0.0f;
        int drawing = 1;

        while (pos < length) {
            float seg_len = drawing ? l->dash_length : l->gap_length;
            /* Backstop for the AddDashedLine guard: a zero/negative (or NaN)
               segment length would leave `pos` unchanged and loop forever. */
            if (!(seg_len > 0.0f)) break;
            float end_pos = pos + seg_len;
            if (end_pos > length) end_pos = length;

            if (drawing) {
                float x1 = l->x1 + nx * pos;
                float y1 = l->y1 + ny * pos;
                float x2 = l->x1 + nx * end_pos;
                float y2 = l->y1 + ny * end_pos;

                float ddx = x2 - x1;
                float ddy = y2 - y1;
                float dlen = sqrtf(ddx * ddx + ddy * ddy);
                if (dlen > 0.0001f) {
                    float hw = l->width * 0.5f;
                    float pnx = (-ddy / dlen) * hw;
                    float pny = (ddx / dlen) * hw;

                    if (g_vertex_count + 6 <= MAX_VERTICES) {
                        PushVertex(x1 + pnx, y1 + pny, nr, ng, nb, l->alpha);
                        PushVertex(x1 - pnx, y1 - pny, nr, ng, nb, l->alpha);
                        PushVertex(x2 + pnx, y2 + pny, nr, ng, nb, l->alpha);

                        PushVertex(x1 - pnx, y1 - pny, nr, ng, nb, l->alpha);
                        PushVertex(x2 - pnx, y2 - pny, nr, ng, nb, l->alpha);
                        PushVertex(x2 + pnx, y2 + pny, nr, ng, nb, l->alpha);
                    }
                }
            }

            pos = end_pos;
            drawing = !drawing;
        }
    }
}
