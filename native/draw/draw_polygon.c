#include <math.h>
#include "../draw_common.h"

void BuildVerticesFromPolygons(const PolygonObj* polygons, int count) {
    for (int i = 0; i < count; i++) {
        const PolygonObj* p = &polygons[i];
        int n = p->vert_count;
        if (n < 3) continue;

        float fill_r = p->r / 255.0f, fill_g = p->g / 255.0f, fill_b = p->b / 255.0f;
        float br = p->border_r / 255.0f, bg = p->border_g / 255.0f, bb = p->border_b / 255.0f;

        float sp = p->stroke_progress;
        if (sp > 1.0f) sp = 1.0f;
        if (sp < 0.0f) sp = 0.0f;

        float edge_lens[64];
        float perimeter = 0.0f;
        for (int j = 0; j < n; j++) {
            int j2 = (j + 1) % n;
            float dx = p->verts[j2 * 2] - p->verts[j * 2];
            float dy = p->verts[j2 * 2 + 1] - p->verts[j * 2 + 1];
            edge_lens[j] = sqrtf(dx * dx + dy * dy);
            perimeter += edge_lens[j];
        }

        float drawn = perimeter * sp;

        /* Fill: triangle fan. The fan origin depends on whether the border is
           fully drawn. A partial draw (Create animation) fans from the stroke's
           start vertex so the fill follows the border as it sweeps out. A full
           polygon (static shape, e.g. a concave Star) fans from the centroid —
           fanning a concave polygon from a boundary vertex overfills its
           notches. For convex shapes both origins cover the same area, so there
           is no visual discontinuity at the end of a Create. */
/* A fill is present whenever the caller passed fill alpha -- the fill COLOUR may
   legitimately be pure black (ConfigDrivenScene's swatch is filled with
   `config.background_color`, which defaults to black), so the colour must not
   double as "no fill".  Testing r|g|b != 0 silently dropped every black-filled
   shape and let the grey plate behind it show through (measured: same lit count
   but +2.77 mean luma in ConfigDrivenScene).  Every AddPolygon call site on the
   Python side only reaches here when the mobject really has a fill. */
        if (p->alpha > 0.0001f) {
            float fan_x, fan_y;
            if (drawn >= perimeter - 0.001f) {
                float cx = 0.0f, cy = 0.0f;
                for (int j = 0; j < n; j++) { cx += p->verts[j * 2]; cy += p->verts[j * 2 + 1]; }
                fan_x = cx / (float)n;
                fan_y = cy / (float)n;
            } else {
                fan_x = p->verts[0];
                fan_y = p->verts[1];
            }
            float cum = 0.0f;
            for (int j = 0; j < n; j++) {
                int j2 = (j + 1) % n;
                float el = edge_lens[j];
                if (cum >= drawn) break;

                float x0 = p->verts[j * 2], y0 = p->verts[j * 2 + 1];
                float x1, y1;

                if (cum + el <= drawn) {
                    x1 = p->verts[j2 * 2];
                    y1 = p->verts[j2 * 2 + 1];
                    cum += el;
                } else {
                    float frac = (drawn - cum) / el;
                    x1 = x0 + (p->verts[j2 * 2] - x0) * frac;
                    y1 = y0 + (p->verts[j2 * 2 + 1] - y0) * frac;
                    cum = drawn;
                }

                if (g_vertex_count + 3 > MAX_VERTICES) break;
                PushVertex(fan_x, fan_y, fill_r, fill_g, fill_b, p->alpha);
                PushVertex(x0, y0, fill_r, fill_g, fill_b, p->alpha);
                PushVertex(x1, y1, fill_r, fill_g, fill_b, p->alpha);
            }
        }

        /* Border: progressive line segments */
        if (p->border_width > 0.0f) {
            float cum = 0.0f;
            for (int j = 0; j < n; j++) {
                if (cum >= drawn) break;
                int j2 = (j + 1) % n;
                float el = edge_lens[j];

                float x0 = p->verts[j * 2], y0 = p->verts[j * 2 + 1];
                float ex, ey;

                if (cum + el <= drawn) {
                    ex = p->verts[j2 * 2];
                    ey = p->verts[j2 * 2 + 1];
                    cum += el;
                } else {
                    float frac = (drawn - cum) / el;
                    ex = x0 + (p->verts[j2 * 2] - x0) * frac;
                    ey = y0 + (p->verts[j2 * 2 + 1] - y0) * frac;
                    cum = drawn;
                }

                float dx = ex - x0, dy = ey - y0;
                float len = sqrtf(dx * dx + dy * dy);
                if (len < 0.0001f) continue;
                float hw = p->border_width * 0.5f;
                float nx = (-dy / len) * hw;
                float ny = (dx / len) * hw;

                if (g_vertex_count + 6 > MAX_VERTICES) break;
                PushVertex(x0 + nx, y0 + ny, br, bg, bb, p->alpha);
                PushVertex(x0 - nx, y0 - ny, br, bg, bb, p->alpha);
                PushVertex(ex + nx, ey + ny, br, bg, bb, p->alpha);

                PushVertex(x0 - nx, y0 - ny, br, bg, bb, p->alpha);
                PushVertex(ex - nx, ey - ny, br, bg, bb, p->alpha);
                PushVertex(ex + nx, ey + ny, br, bg, bb, p->alpha);
            }
        }
    }
}
