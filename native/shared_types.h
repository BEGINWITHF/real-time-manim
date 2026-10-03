#ifndef SHARED_TYPES_H
#define SHARED_TYPES_H

#ifndef MAX_SHAPES
#define MAX_SHAPES 4096
#endif

#ifndef MAX_POLYGON_VERTS
#define MAX_POLYGON_VERTS 64
#endif

typedef struct {
    float x, y, hw, hh, rot;
    int r, g, b;
    int border_r, border_g, border_b;
    float border_width;
    float stroke_progress;
    float alpha;
} Rect;

typedef struct {
    float x, y, radius;
    int r, g, b;
    int border_r, border_g, border_b;
    float border_width;
    float stroke_progress;
    float alpha;
} Circle;

typedef struct {
    float x1, y1, x2, y2;
    int width, r, g, b;
    float alpha;
} LineObj;

typedef struct {
    float x, y, rx, ry;
    int r, g, b;
    int border_r, border_g, border_b;
    float border_width;
    float stroke_progress;
    float alpha;
} EllipseObj;

typedef struct {
    float x, y;
    int r, g, b;
    int border_r, border_g, border_b;
    float border_width;
    int vert_count;
    float verts[MAX_POLYGON_VERTS * 2];
    float stroke_progress;
    float alpha;
    int close_path;
} PolygonObj;

typedef struct {
    float x1, y1, x2, y2;
    int width, r, g, b;
    float dash_length;
    float gap_length;
    float alpha;
} DashedLineObj;

typedef struct {
    float x, y, radius;
    float start_angle, angle;
    int r, g, b;
    float stroke_width;
    float alpha;
} ArcObj;

typedef struct {
    float x, y;
    int r, g, b;
    float alpha;
    // Dot radius in pixels (<=0 -> default).  manim draws a PMobject point as a
    // 4 px *diameter* disc (measured), while this used to be a fixed 4 px radius,
    // i.e. four times the area.
    float radius;
} PointObj;

#ifndef MAX_IMAGE_QUADS
#define MAX_IMAGE_QUADS 64
#endif

// A textured quad submitted by the Python side (see AddImageQuad).  Corners are
// in window pixels, ordered top-left, top-right, bottom-right, bottom-left --
// the same order the texture coordinates run.  ``token`` identifies the pixel
// data so the same image is uploaded once and reused across frames.
typedef struct {
    unsigned long long token;
    float xy[8];
    float opacity;
} ImageQuad;

#ifndef MAX_TEXT_LEN
#define MAX_TEXT_LEN 512
#endif

typedef struct {
    float x, y;
    int r, g, b;
    float font_size;
    float opacity;
    char text[MAX_TEXT_LEN];
    float alpha;
} TextObj;

#endif