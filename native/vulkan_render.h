#ifndef VULKAN_RENDER_H
#define VULKAN_RENDER_H

#ifdef _WIN32
#include <windows.h>
#define VK_USE_PLATFORM_WIN32_KHR
#else
#define VK_USE_PLATFORM_METAL_EXT
#endif
#include <vulkan/vulkan.h>
#include "shared_types.h"

#ifdef _WIN32
void Render_Init(HWND hwnd, int width, int height, HINSTANCE hinst);
#else
void Render_Init(void *metal_layer, int width, int height);
void Mac_GetDrawableSize(int *w, int *h);
void Mac_CreateReadbackBuffer(uint32_t w, uint32_t h);
#endif

int Render_IsReady(void);

#define CMD_RECT 0
#define CMD_CIRCLE 1
#define CMD_LINE 2
#define CMD_ELLIPSE 3
#define CMD_POLYGON 4
#define CMD_DASHED_LINE 5
#define CMD_ARC 6
#define CMD_POINT 7
#define CMD_TEXT 8
#define CMD_IMAGE 9

typedef struct {
    int type;
    int index;
} DrawCmd;

void Render_DrawScene(const Rect* rects, int rect_count,
                      const Circle* circles, int circle_count,
                      const LineObj* lines, int line_count,
                      const EllipseObj* ellipses, int ellipse_count,
                      const PolygonObj* polygons, int polygon_count,
                      const DashedLineObj* dashed_lines, int dashed_line_count,
                      const ArcObj* arcs, int arc_count,
                      const PointObj* points, int point_count,
                      const TextObj* texts, int text_count,
                      const DrawCmd* cmds, int cmd_count);

void Render_Cleanup(void);

#endif
