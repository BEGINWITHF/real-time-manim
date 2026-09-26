#include "platform.h"
#include "vulkan_render.h"
#include "vulkan_core.h"
#include "shared_types.h"
#include <stdio.h>
#include <string.h>
#include <windows.h>

static Rect g_rects[MAX_SHAPES];
static int g_rect_count = 0;
static Circle g_circles[MAX_SHAPES];
static int g_circle_count = 0;
static LineObj g_lines[MAX_SHAPES];
static int g_line_count = 0;
static EllipseObj g_ellipses[MAX_SHAPES];
static int g_ellipse_count = 0;
static PolygonObj g_polygons[MAX_SHAPES];
static int g_polygon_count = 0;
static DashedLineObj g_dashed_lines[MAX_SHAPES];
static int g_dashed_line_count = 0;
static ArcObj g_arcs[MAX_SHAPES];
static int g_arc_count = 0;
static PointObj g_points[MAX_SHAPES];
static int g_point_count = 0;
static TextObj g_texts[MAX_SHAPES];
static int g_text_count = 0;

#define CMD_RECT 0
#define CMD_CIRCLE 1
#define CMD_LINE 2
#define CMD_ELLIPSE 3
#define CMD_POLYGON 4
#define CMD_DASHED_LINE 5
#define CMD_ARC 6
#define CMD_POINT 7
#define CMD_TEXT 8

#define MAX_DRAW_CMDS 16384
static DrawCmd g_draw_cmds[MAX_DRAW_CMDS];
static int g_draw_cmd_count = 0;

static double g_aspect_ratio = 16.0 / 9.0;
static int g_min_width = 320;

BOOL WINAPI DllMain(HINSTANCE hinstDLL, DWORD fdwReason, LPVOID lpvReserved) {
    (void)lpvReserved;
    (void)hinstDLL;
    return TRUE;
}

static LRESULT CALLBACK WndProc(HWND hwnd, UINT msg, WPARAM wParam, LPARAM lParam) {
    switch (msg) {
        case WM_CLOSE:
            DestroyWindow(hwnd);
            return 0;
        case WM_DESTROY:
            PostQuitMessage(0);
            return 0;
        case WM_SIZE:
            if (wParam != SIZE_MINIMIZED && g_is_ready) {
                g_framebuffer_resized = true;
            }
            return DefWindowProcW(hwnd, msg, wParam, lParam);
        case WM_SIZING: {
            RECT *r = (RECT *)lParam;
            int w = r->right - r->left;
            int h = r->bottom - r->top;
            int border = (int)(GetSystemMetrics(SM_CXEDGE) * 2);
            int caption = (int)(GetSystemMetrics(SM_CYCAPTION) + GetSystemMetrics(SM_CYEDGE) * 2);
            int inner_w = w - border;
            int inner_h = h - caption;
            if (inner_w <= 0 || inner_h <= 0) return 0;
            int d = wParam;
            if (d == WMSZ_LEFT || d == WMSZ_RIGHT) {
                int new_h = (int)(inner_w / g_aspect_ratio + 0.5);
                if (d == WMSZ_LEFT) r->top = r->bottom - new_h - caption;
                else r->bottom = r->top + new_h + caption;
            } else if (d == WMSZ_TOP || d == WMSZ_BOTTOM) {
                int new_w = (int)(inner_h * g_aspect_ratio + 0.5);
                if (d == WMSZ_TOP) r->left = r->right - new_w - border;
                else r->right = r->left + new_w + border;
            } else {
                int new_h = (int)(inner_w / g_aspect_ratio + 0.5);
                r->bottom = r->top + new_h + caption;
            }
            return 0;
        }
        case WM_GETMINMAXINFO: {
            MINMAXINFO *mmi = (MINMAXINFO *)lParam;
            int border = (int)(GetSystemMetrics(SM_CXEDGE) * 2);
            int caption = (int)(GetSystemMetrics(SM_CYCAPTION) + GetSystemMetrics(SM_CYEDGE) * 2);
            mmi->ptMinTrackSize.x = g_min_width + border;
            mmi->ptMinTrackSize.y = (LONG)(g_min_width / g_aspect_ratio + 0.5) + caption;
            return 0;
        }
        default:
            return DefWindowProcW(hwnd, msg, wParam, lParam);
    }
}

// Load logo.ico from the DLL's directory (or its parent, the project root).
// Returns the icon, or NULL if it cannot be loaded.
static HICON LoadWindowIcon(void) {
    HMODULE hm = GetModuleHandleW(L"vulkan_core.dll");
    if (!hm) hm = g_hinst;
    wchar_t dll_path[MAX_PATH];
    DWORD len = GetModuleFileNameW(hm, dll_path, MAX_PATH);
    if (len == 0) return NULL;
    wchar_t *slash = wcsrchr(dll_path, L'\\');
    if (slash) *(slash + 1) = L'\0';
    for (int try_parent = 0; try_parent <= 1; try_parent++) {
        wchar_t ico[MAX_PATH];
        wcscpy_s(ico, MAX_PATH, dll_path);
        if (try_parent) wcscat_s(ico, MAX_PATH, L"..\\");
        wcscat_s(ico, MAX_PATH, L"logo.ico");
        HICON icon = (HICON)LoadImageW(NULL, ico, IMAGE_ICON, 0, 0,
                                       LR_LOADFROMFILE | LR_DEFAULTSIZE);
        if (icon) return icon;
    }
    return NULL;
}

__declspec(dllexport) int Vulkan_Init(int w, int h) {
    SetProcessDPIAware();
    g_hinst = GetModuleHandleW(NULL);
    g_aspect_ratio = (double)w / (double)h;
    g_min_width = w / 4;
    if (g_min_width < 320) g_min_width = 320;
    HICON win_icon = LoadWindowIcon();
    WNDCLASSEXW wc = {
        .cbSize = sizeof(WNDCLASSEXW),
        .lpfnWndProc = WndProc,
        .hInstance = g_hinst,
        .hIcon = win_icon,
        .hIconSm = win_icon,
        .lpszClassName = L"ManimVulkanClass",
        .hCursor = LoadCursor(NULL, IDC_ARROW),
        .hbrBackground = (HBRUSH)GetStockObject(BLACK_BRUSH)
    };
    RegisterClassExW(&wc);

    RECT rect = { 0, 0, w, h };
    AdjustWindowRect(&rect, WS_OVERLAPPEDWINDOW, FALSE);

    g_hwnd = CreateWindowExW(
        0, L"ManimVulkanClass", L"Real Time Manim",
        WS_OVERLAPPEDWINDOW,
        CW_USEDEFAULT, CW_USEDEFAULT,
        rect.right - rect.left, rect.bottom - rect.top,
        NULL, NULL, g_hinst, NULL
    );

    if (!g_hwnd) {
        fprintf(stderr, "[FATAL] CreateWindowExW failed\n");
        return 0;
    }

    Render_Init(g_hwnd, w, h, g_hinst);

    if (!Render_IsReady()) {
        fprintf(stderr, "[ERROR] Vulkan renderer failed to initialize\n");
        return 0;
    }

    ShowWindow(g_hwnd, SW_SHOW);
    UpdateWindow(g_hwnd);
    return 1;
}

__declspec(dllexport) void AddRect(float x, float y, float hw, float hh, float rot, int r, int g, int b, int border_r, int border_g, int border_b, float border_width, float stroke_progress, float alpha) {
    if (g_rect_count < MAX_SHAPES && g_draw_cmd_count < MAX_DRAW_CMDS) {
        g_rects[g_rect_count] = (Rect){ x, y, hw, hh, rot, r, g, b, border_r, border_g, border_b, border_width, stroke_progress, alpha };
        g_draw_cmds[g_draw_cmd_count++] = (DrawCmd){ CMD_RECT, g_rect_count };
        g_rect_count++;
    }
}

__declspec(dllexport) void AddCircle(float x, float y, float radius, int r, int g, int b, int border_r, int border_g, int border_b, float border_width, float stroke_progress, float alpha) {
    if (g_circle_count < MAX_SHAPES && g_draw_cmd_count < MAX_DRAW_CMDS) {
        g_circles[g_circle_count] = (Circle){ x, y, radius, r, g, b, border_r, border_g, border_b, border_width, stroke_progress, alpha };
        g_draw_cmds[g_draw_cmd_count++] = (DrawCmd){ CMD_CIRCLE, g_circle_count };
        g_circle_count++;
    }
}

__declspec(dllexport) void AddLine(float x1, float y1, float x2, float y2, int width, int r, int g, int b, float alpha) {
    if (g_line_count < MAX_SHAPES && g_draw_cmd_count < MAX_DRAW_CMDS) {
        g_lines[g_line_count] = (LineObj){ x1, y1, x2, y2, width, r, g, b, alpha };
        g_draw_cmds[g_draw_cmd_count++] = (DrawCmd){ CMD_LINE, g_line_count };
        g_line_count++;
    }
}

__declspec(dllexport) void AddEllipse(float x, float y, float rx, float ry, int r, int g, int b, int border_r, int border_g, int border_b, float border_width, float stroke_progress, float alpha) {
    if (g_ellipse_count < MAX_SHAPES && g_draw_cmd_count < MAX_DRAW_CMDS) {
        g_ellipses[g_ellipse_count] = (EllipseObj){ x, y, rx, ry, r, g, b, border_r, border_g, border_b, border_width, stroke_progress, alpha };
        g_draw_cmds[g_draw_cmd_count++] = (DrawCmd){ CMD_ELLIPSE, g_ellipse_count };
        g_ellipse_count++;
    }
}

__declspec(dllexport) void AddPolygon(float x, float y, int r, int g, int b, int border_r, int border_g, int border_b, float border_width, int vert_count, const float* verts, float stroke_progress, float alpha, int close_path) {
    if (g_polygon_count < MAX_SHAPES && g_draw_cmd_count < MAX_DRAW_CMDS && vert_count <= MAX_POLYGON_VERTS) {
        PolygonObj* p = &g_polygons[g_polygon_count];
        p->x = x; p->y = y;
        p->r = r; p->g = g; p->b = b;
        p->border_r = border_r; p->border_g = border_g; p->border_b = border_b;
        p->border_width = border_width;
        p->vert_count = vert_count;
        p->stroke_progress = stroke_progress;
        p->alpha = alpha;
        p->close_path = close_path;
        memcpy(p->verts, verts, sizeof(float) * vert_count * 2);
        g_draw_cmds[g_draw_cmd_count++] = (DrawCmd){ CMD_POLYGON, g_polygon_count };
        g_polygon_count++;
    }
}

__declspec(dllexport) void AddDashedLine(float x1, float y1, float x2, float y2, int width, int r, int g, int b, float dash_length, float gap_length, float alpha) {
    if (g_dashed_line_count < MAX_SHAPES && g_draw_cmd_count < MAX_DRAW_CMDS) {
        g_dashed_lines[g_dashed_line_count] = (DashedLineObj){ x1, y1, x2, y2, width, r, g, b, dash_length, gap_length, alpha };
        g_draw_cmds[g_draw_cmd_count++] = (DrawCmd){ CMD_DASHED_LINE, g_dashed_line_count };
        g_dashed_line_count++;
    }
}

__declspec(dllexport) void AddArc(float x, float y, float radius, float start_angle, float angle, int r, int g, int b, float stroke_width, float alpha) {
    if (g_arc_count < MAX_SHAPES && g_draw_cmd_count < MAX_DRAW_CMDS) {
        g_arcs[g_arc_count] = (ArcObj){ x, y, radius, start_angle, angle, r, g, b, stroke_width, alpha };
        g_draw_cmds[g_draw_cmd_count++] = (DrawCmd){ CMD_ARC, g_arc_count };
        g_arc_count++;
    }
}

__declspec(dllexport) void AddPoint(float x, float y, int r, int g, int b, float alpha) {
    if (g_point_count < MAX_SHAPES && g_draw_cmd_count < MAX_DRAW_CMDS) {
        g_points[g_point_count] = (PointObj){ x, y, r, g, b, alpha };
        g_draw_cmds[g_draw_cmd_count++] = (DrawCmd){ CMD_POINT, g_point_count };
        g_point_count++;
    }
}

__declspec(dllexport) void AddText(float x, float y, int r, int g, int b, float font_size, float opacity, const char* text, float alpha) {
    if (g_text_count < MAX_SHAPES && g_draw_cmd_count < MAX_DRAW_CMDS && text) {
        TextObj* t = &g_texts[g_text_count];
        t->x = x; t->y = y;
        t->r = r; t->g = g; t->b = b;
        t->font_size = font_size;
        t->opacity = opacity;
        t->alpha = alpha;
        int len = 0;
        while (text[len] && len < MAX_TEXT_LEN - 1) {
            t->text[len] = text[len];
            len++;
        }
        t->text[len] = '\0';
        g_draw_cmds[g_draw_cmd_count++] = (DrawCmd){ CMD_TEXT, g_text_count };
        g_text_count++;
    }
}

__declspec(dllexport) void ClearShapes(void) {
    g_rect_count = 0;
    g_circle_count = 0;
    g_line_count = 0;
    g_ellipse_count = 0;
    g_polygon_count = 0;
    g_dashed_line_count = 0;
    g_arc_count = 0;
    g_point_count = 0;
    g_text_count = 0;
    g_draw_cmd_count = 0;
}

__declspec(dllexport) int Vulkan_Tick(void) {
    MSG msg;
    while (PeekMessageW(&msg, NULL, 0, 0, PM_REMOVE)) {
        if (msg.message == WM_QUIT) return 0;
        TranslateMessage(&msg);
        DispatchMessageW(&msg);
    }

    if (g_hwnd && IsWindow(g_hwnd)) {
        if (g_framebuffer_resized) {
            g_framebuffer_resized = false;
            RecreateSwapchain();
        }
        Render_DrawScene(
            g_rects, g_rect_count,
            g_circles, g_circle_count,
            g_lines, g_line_count,
            g_ellipses, g_ellipse_count,
            g_polygons, g_polygon_count,
            g_dashed_lines, g_dashed_line_count,
            g_arcs, g_arc_count,
            g_points, g_point_count,
            g_texts, g_text_count,
            g_draw_cmds, g_draw_cmd_count
        );
        extern uint32_t g_vertex_count;
        Render_DrawFrame(g_vertex_count);
        RECT rc;
        GetClientRect(g_hwnd, &rc);
        int cw = rc.right - rc.left;
        int ch = rc.bottom - rc.top;
        return (cw << 16) | (ch & 0xFFFF);
    }
    return 0;
}

static void FreeScreenshotBuffer(void);

__declspec(dllexport) void Vulkan_Shutdown(void) {
    FreeScreenshotBuffer();
    Render_Cleanup();
    if (g_hwnd && IsWindow(g_hwnd)) {
        DestroyWindow(g_hwnd);
        g_hwnd = NULL;
    }
    UnregisterClassW(L"ManimVulkanClass", g_hinst);
}

uint32_t g_last_img_idx = 0;

// Persistent staging buffer for SaveScreenshot readback (allocated once,
// reused across frames). Per-frame create/destroy of an 8MB buffer is slow.
static VkBuffer g_ss_buf = VK_NULL_HANDLE;
static VkDeviceMemory g_ss_mem = VK_NULL_HANDLE;
static VkDeviceSize g_ss_size = 0;
static void *g_ss_map = NULL;

static int EnsureScreenshotBuffer(VkDeviceSize size) {
    if (g_ss_buf != VK_NULL_HANDLE && g_ss_size >= size) return 1;
    if (g_ss_buf != VK_NULL_HANDLE) {
        vkDestroyBuffer(g_dev, g_ss_buf, NULL);
        vkFreeMemory(g_dev, g_ss_mem, NULL);
        g_ss_buf = VK_NULL_HANDLE;
        g_ss_mem = VK_NULL_HANDLE;
    }

    // Allocate a pure host-readable staging buffer (HOST_VISIBLE, NOT
    // DEVICE_LOCAL). FindMemoryType() picks the first matching type, which on
    // many GPUs is device-local host-visible memory whose reads are ~20 MB/s.
    VkBufferCreateInfo bi = {0};
    bi.sType = VK_STRUCTURE_TYPE_BUFFER_CREATE_INFO;
    bi.size = size;
    bi.usage = VK_BUFFER_USAGE_TRANSFER_DST_BIT;
    bi.sharingMode = VK_SHARING_MODE_EXCLUSIVE;
    if (vkCreateBuffer(g_dev, &bi, NULL, &g_ss_buf) != VK_SUCCESS) return 0;

    VkMemoryRequirements mr;
    vkGetBufferMemoryRequirements(g_dev, g_ss_buf, &mr);
    VkPhysicalDeviceMemoryProperties mp;
    vkGetPhysicalDeviceMemoryProperties(g_phys_dev, &mp);
    uint32_t chosen = UINT32_MAX;
    for (uint32_t i = 0; i < mp.memoryTypeCount; i++) {
        VkMemoryPropertyFlags f = mp.memoryTypes[i].propertyFlags;
        if ((mr.memoryTypeBits & (1u << i)) &&
            (f & VK_MEMORY_PROPERTY_HOST_VISIBLE_BIT) &&
            (f & VK_MEMORY_PROPERTY_HOST_COHERENT_BIT) &&
            !(f & VK_MEMORY_PROPERTY_DEVICE_LOCAL_BIT)) {
            chosen = i; break;
        }
    }
    if (chosen == UINT32_MAX) {
        for (uint32_t i = 0; i < mp.memoryTypeCount; i++) {
            VkMemoryPropertyFlags f = mp.memoryTypes[i].propertyFlags;
            if ((mr.memoryTypeBits & (1u << i)) &&
                (f & VK_MEMORY_PROPERTY_HOST_VISIBLE_BIT) &&
                (f & VK_MEMORY_PROPERTY_HOST_COHERENT_BIT)) {
                chosen = i; break;
            }
        }
    }
    if (chosen == UINT32_MAX) {
        vkDestroyBuffer(g_dev, g_ss_buf, NULL);
        g_ss_buf = VK_NULL_HANDLE;
        return 0;
    }

    VkMemoryAllocateInfo ai = {0};
    ai.sType = VK_STRUCTURE_TYPE_MEMORY_ALLOCATE_INFO;
    ai.allocationSize = mr.size;
    ai.memoryTypeIndex = chosen;
    if (vkAllocateMemory(g_dev, &ai, NULL, &g_ss_mem) != VK_SUCCESS ||
        vkBindBufferMemory(g_dev, g_ss_buf, g_ss_mem, 0) != VK_SUCCESS) {
        vkDestroyBuffer(g_dev, g_ss_buf, NULL);
        g_ss_buf = VK_NULL_HANDLE;
        g_ss_mem = VK_NULL_HANDLE;
        return 0;
    }
    g_ss_size = size;
    vkMapMemory(g_dev, g_ss_mem, 0, size, 0, &g_ss_map);
    return 1;
}

static void FreeScreenshotBuffer(void) {
    if (g_ss_buf != VK_NULL_HANDLE) {
        if (g_ss_map) vkUnmapMemory(g_dev, g_ss_mem);
        g_ss_map = NULL;
        vkDestroyBuffer(g_dev, g_ss_buf, NULL);
        vkFreeMemory(g_dev, g_ss_mem, NULL);
        g_ss_buf = VK_NULL_HANDLE;
        g_ss_mem = VK_NULL_HANDLE;
        g_ss_size = 0;
    }
}

// Copy the last presented swapchain image into a host-visible staging buffer.
// Reuses ONE persistent command buffer (per-frame vkAllocate/vkFreeCommandBuffers
// was slow) and is submitted on the same queue the render used, so a single
// wait is enough.
static VkCommandBuffer g_ss_cmd = VK_NULL_HANDLE;
static void CopySwapchainImageToBuffer(uint32_t img_idx, VkBuffer dst, int w, int h) {
    if (g_ss_cmd == VK_NULL_HANDLE) {
        VkCommandBufferAllocateInfo ai = {0};
        ai.sType = VK_STRUCTURE_TYPE_COMMAND_BUFFER_ALLOCATE_INFO;
        ai.commandPool = g_cmd_pool;
        ai.level = VK_COMMAND_BUFFER_LEVEL_PRIMARY;
        ai.commandBufferCount = 1;
        if (vkAllocateCommandBuffers(g_dev, &ai, &g_ss_cmd) != VK_SUCCESS) {
            g_ss_cmd = VK_NULL_HANDLE;
            return;
        }
    } else {
        vkResetCommandBuffer(g_ss_cmd, 0);
    }
    VkCommandBuffer cmd = g_ss_cmd;

    VkCommandBufferBeginInfo bi = {0};
    bi.sType = VK_STRUCTURE_TYPE_COMMAND_BUFFER_BEGIN_INFO;
    bi.flags = VK_COMMAND_BUFFER_USAGE_ONE_TIME_SUBMIT_BIT;
    vkBeginCommandBuffer(cmd, &bi);

    VkImageMemoryBarrier b = {0};
    b.sType = VK_STRUCTURE_TYPE_IMAGE_MEMORY_BARRIER;
    b.oldLayout = VK_IMAGE_LAYOUT_PRESENT_SRC_KHR;
    b.newLayout = VK_IMAGE_LAYOUT_TRANSFER_SRC_OPTIMAL;
    b.srcQueueFamilyIndex = VK_QUEUE_FAMILY_IGNORED;
    b.dstQueueFamilyIndex = VK_QUEUE_FAMILY_IGNORED;
    b.image = g_swapchain_imgs[img_idx];
    b.subresourceRange.aspectMask = VK_IMAGE_ASPECT_COLOR_BIT;
    b.subresourceRange.baseMipLevel = 0;
    b.subresourceRange.levelCount = 1;
    b.subresourceRange.baseArrayLayer = 0;
    b.subresourceRange.layerCount = 1;
    b.srcAccessMask = VK_ACCESS_MEMORY_READ_BIT;
    b.dstAccessMask = VK_ACCESS_TRANSFER_READ_BIT;
    vkCmdPipelineBarrier(cmd,
        VK_PIPELINE_STAGE_TRANSFER_BIT, VK_PIPELINE_STAGE_TRANSFER_BIT, 0,
        0, NULL, 0, NULL, 1, &b);

    VkBufferImageCopy region = {0};
    region.imageSubresource.aspectMask = VK_IMAGE_ASPECT_COLOR_BIT;
    region.imageSubresource.layerCount = 1;
    region.imageExtent = (VkExtent3D){(uint32_t)w, (uint32_t)h, 1};
    vkCmdCopyImageToBuffer(cmd, g_swapchain_imgs[img_idx],
        VK_IMAGE_LAYOUT_TRANSFER_SRC_OPTIMAL, dst, 1, &region);

    VkImageMemoryBarrier b2 = b;
    b2.oldLayout = VK_IMAGE_LAYOUT_TRANSFER_SRC_OPTIMAL;
    b2.newLayout = VK_IMAGE_LAYOUT_PRESENT_SRC_KHR;
    b2.srcAccessMask = VK_ACCESS_TRANSFER_READ_BIT;
    b2.dstAccessMask = VK_ACCESS_MEMORY_READ_BIT;
    vkCmdPipelineBarrier(cmd,
        VK_PIPELINE_STAGE_TRANSFER_BIT, VK_PIPELINE_STAGE_TRANSFER_BIT, 0,
        0, NULL, 0, NULL, 1, &b2);

    vkEndCommandBuffer(cmd);
    VkSubmitInfo si = {0};
    si.sType = VK_STRUCTURE_TYPE_SUBMIT_INFO;
    si.commandBufferCount = 1;
    si.pCommandBuffers = &cmd;
    vkQueueSubmit(g_gfx_queue, 1, &si, VK_NULL_HANDLE);
    vkQueueWaitIdle(g_gfx_queue);
}

// Convert the BGRA swapchain readback (g_ss_map, w*h*4 bytes) into BGR.
// The mapped GPU buffer reads slowly byte-by-byte on Intel iGPUs, so we first
// bulk-copy the raw bytes into CPU cache (vectorized memcpy) and convert there.
static unsigned char *g_conv_buf = NULL;
static VkDeviceSize g_conv_size = 0;
static void ConvertBGRAtoBGR(int w, int h, unsigned char *out) {
    VkDeviceSize raw_size = (VkDeviceSize)w * (VkDeviceSize)h * 4;
    if (g_conv_size < raw_size) {
        free(g_conv_buf);
        g_conv_buf = (unsigned char *)malloc((size_t)raw_size);
        g_conv_size = raw_size;
    }
    if (g_conv_buf == NULL) return;
    unsigned char *raw = g_conv_buf;
    memcpy(raw, g_ss_map, (size_t)raw_size);
    int rowBytes = ((w * 3 + 3) & ~3);
    for (int y = 0; y < h; y++) {
        const unsigned char *row = raw + (VkDeviceSize)y * (VkDeviceSize)w * 4;
        unsigned char *dst = out + (VkDeviceSize)y * (VkDeviceSize)rowBytes;
        for (int x = 0; x < w; x++) {
            dst[x * 3 + 0] = row[x * 4 + 0];  // B
            dst[x * 3 + 1] = row[x * 4 + 1];  // G
            dst[x * 3 + 2] = row[x * 4 + 2];  // R
        }
    }
}

// SaveScreenshot reads the swapchain framebuffer directly (independent of the
// window's on-screen size/visibility). The previous GDI BitBlt version returned
// solid white because Vulkan swapchain content is not present in the window DC.
__declspec(dllexport) int SaveScreenshot(const char *path) {
    if (!g_is_ready || !g_swapchain) return 0;
    int w = (int)g_swapchain_ext.width;
    int h = (int)g_swapchain_ext.height;
    if (w <= 0 || h <= 0) return 0;

    VkDeviceSize img_size = (VkDeviceSize)w * (VkDeviceSize)h * 4;
    if (!EnsureScreenshotBuffer(img_size)) return 0;

    CopySwapchainImageToBuffer(g_last_img_idx, g_ss_buf, w, h);

    int rowBytes = ((w * 3 + 3) & ~3);
    unsigned char *bgr = (unsigned char *)malloc((size_t)rowBytes * (size_t)h);
    ConvertBGRAtoBGR(w, h, bgr);

    BITMAPINFOHEADER bi = {0};
    bi.biSize = sizeof(BITMAPINFOHEADER);
    bi.biWidth = w;
    bi.biHeight = -h;  // top-down
    bi.biPlanes = 1;
    bi.biBitCount = 24;
    bi.biCompression = BI_RGB;
    int imgSize = rowBytes * h;
    BITMAPFILEHEADER bfh = {0};
    bfh.bfType = 0x4D42;
    bfh.bfOffBits = sizeof(BITMAPFILEHEADER) + sizeof(BITMAPINFOHEADER);
    bfh.bfSize = bfh.bfOffBits + imgSize;

    int ok = 0;
    FILE *fp = fopen(path, "wb");
    if (fp) {
        fwrite(&bfh, sizeof(bfh), 1, fp);
        fwrite(&bi, sizeof(bi), 1, fp);
        fwrite(bgr, imgSize, 1, fp);
        fclose(fp);
        ok = 1;
    }
    free(bgr);
    return ok;
}

// SaveScreenshotRaw fills a caller-provided buffer with raw BGR pixels
// (no 54-byte BMP header, no disk I/O). rowBytes == w*3 (1280x720 has no
// padding). Returns 1 on success and sets *out_size to w*h*3.
__declspec(dllexport) int SaveScreenshotRaw(unsigned char *out, int *out_size) {
    if (!g_is_ready || !g_swapchain || !out) return 0;
    int w = (int)g_swapchain_ext.width;
    int h = (int)g_swapchain_ext.height;
    if (w <= 0 || h <= 0) return 0;

    VkDeviceSize img_size = (VkDeviceSize)w * (VkDeviceSize)h * 4;
    if (!EnsureScreenshotBuffer(img_size)) return 0;

    CopySwapchainImageToBuffer(g_last_img_idx, g_ss_buf, w, h);

    int rowBytes = ((w * 3 + 3) & ~3);
    ConvertBGRAtoBGR(w, h, out);
    if (out_size) *out_size = rowBytes * h;
    return 1;
}
