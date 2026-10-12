#include "../draw_common.h"

void BuildVerticesFromRects(const Rect *rects, int count) {
    for (int i = 0; i < count; i++) {
        const Rect *r = &rects[i];

        float nr = r->r / 255.0f, ng = r->g / 255.0f, nb = r->b / 255.0f;
        float bn = r->border_r / 255.0f, bg = r->border_g / 255.0f, bb = r->border_b / 255.0f;

        float hw = r->hw, hh = r->hh;
        float cos_a = cosf(r->rot), sin_a = sinf(r->rot);

        float corners[4][2] = {{hw,-hh},{-hw,-hh},{-hw,hh},{hw,hh}};
        float rot_c[4][2];

        for (int j = 0; j < 4; j++) {
            rot_c[j][0] = r->x + corners[j][0]*cos_a - corners[j][1]*sin_a;
            rot_c[j][1] = r->y + corners[j][0]*sin_a + corners[j][1]*cos_a;
        }

        float sp = r->stroke_progress;
        if (sp > 1.0f) sp = 1.0f;
        if (sp < 0.0f) sp = 0.0f;

        float edge_lens[4];
        float perimeter = 0.0f;
        for (int j = 0; j < 4; j++) {
            int j2 = (j + 1) % 4;
            float dx = rot_c[j2][0] - rot_c[j][0];
            float dy = rot_c[j2][1] - rot_c[j][1];
            edge_lens[j] = sqrtf(dx*dx + dy*dy);
            perimeter += edge_lens[j];
        }

        float drawn = perimeter * sp;

        /* Fill: triangle fan from stroke start (rot_c[0]), following border path.

           Whether there IS a fill is answered by the ALPHA, not by the colour:
           a fill may legitimately be pure black (`config.background_color`
           defaults to black, so a swatch filled with it is r=g=b=0).  Reading
           `r|g|b != 0` silently dropped every black-filled Rectangle and let
           whatever sat behind it show through -- the same defect and the same
           measurement that `draw_polygon.c`'s fill test was already fixed for
           (see the note there: "silently dropped every black-filled shape").
           The border below is a separate decision and still keys off
           `border_width`. */
        if (r->alpha > 0.0001f) {
            float start_x = rot_c[0][0];
            float start_y = rot_c[0][1];
            float cum = 0.0f;

            for (int j = 0; j < 4; j++) {
                if (cum >= drawn) break;
                int j2 = (j + 1) % 4;
                float el = edge_lens[j];
                float x0 = rot_c[j][0], y0 = rot_c[j][1];
                float x1, y1;

                if (cum + el <= drawn) {
                    x1 = rot_c[j2][0];
                    y1 = rot_c[j2][1];
                    cum += el;
                } else {
                    float frac = (drawn - cum) / el;
                    x1 = x0 + (rot_c[j2][0] - x0) * frac;
                    y1 = y0 + (rot_c[j2][1] - y0) * frac;
                    cum = drawn;
                }

                if (g_vertex_count + 3 > MAX_VERTICES) break;
                PushVertex(start_x, start_y, nr, ng, nb, r->alpha);
                PushVertex(x0, y0, nr, ng, nb, r->alpha);
                PushVertex(x1, y1, nr, ng, nb, r->alpha);
            }
        }

        /* Border: progressive line segments */
        if (r->border_width > 0.0f && sp > 0.0f) {
            float cum = 0.0f;
            for (int j = 0; j < 4; j++) {
                if (cum >= drawn) break;
                int j2 = (j + 1) % 4;
                float el = edge_lens[j];
                float x0 = rot_c[j][0], y0 = rot_c[j][1];
                float ex, ey;

                if (cum + el <= drawn) {
                    ex = rot_c[j2][0];
                    ey = rot_c[j2][1];
                    cum += el;
                } else {
                    float frac = (drawn - cum) / el;
                    ex = x0 + (rot_c[j2][0] - x0) * frac;
                    ey = y0 + (rot_c[j2][1] - y0) * frac;
                    cum = drawn;
                }

                float dx = ex - x0, dy = ey - y0;
                float len = sqrtf(dx*dx + dy*dy);
                if (len < 0.001f) continue;
                float hw2 = r->border_width * 0.5f;
                float nx = (-dy / len) * hw2;
                float ny = (dx / len) * hw2;

                if (g_vertex_count + 6 > MAX_VERTICES) break;
                PushVertex(x0 + nx, y0 + ny, bn, bg, bb, r->alpha);
                PushVertex(x0 - nx, y0 - ny, bn, bg, bb, r->alpha);
                PushVertex(ex + nx, ey + ny, bn, bg, bb, r->alpha);
                PushVertex(x0 - nx, y0 - ny, bn, bg, bb, r->alpha);
                PushVertex(ex - nx, ey - ny, bn, bg, bb, r->alpha);
                PushVertex(ex + nx, ey + ny, bn, bg, bb, r->alpha);
            }
        }
    }
}
