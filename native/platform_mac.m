// platform_mac.m — macOS platform layer for the manim Vulkan renderer.
//
// This file is the Cocoa/MoltenVK equivalent of platform.c (Win32).  It
// provides the exact same exported API (Vulkan_Init / Vulkan_Tick /
// Vulkan_Shutdown / Add* / ClearShapes / SaveScreenshot) so the Python
// ctypes bindings are platform-independent.
//
// REPO RULES:
//  * The Windows pipeline (platform.c, vulkan_init.c, vulkan_draw.c,
//    draw/*.c) keeps its identifiers; this file shims the two names that
//    collide with the macOS SDK (Rect, Circle — see MacTypes.h) at the
//    preprocessor level, exactly as documented in the porting skill.

#import <Cocoa/Cocoa.h>
#import <QuartzCore/CAMetalLayer.h>
#import <Metal/Metal.h>

// ── Name shims: the macOS SDK's MacTypes.h already defines Rect/Circle. ──
// Rename OUR type tokens at the include site; MacTypes' typedefs are untouched.
#define Rect ManimRect
#define Circle ManimCircle
#include "platform.h"
#include "vulkan_render.h"
#include "vulkan_core.h"
#include "shared_types.h"
#undef Rect
#undef Circle

#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <stdint.h>
#include <time.h>

// Defined further down; used by Vulkan_Init / Vulkan_Shutdown above it.
void Mac_FreeReadbackBuffer(void);

// ── Shape pools (identical layout to platform.c) ────────────────────────
// X-macro table: each row = (type, pool, count, CMD tag, add-fn name,
// signature params, struct-literal init).  Expanding the table with the
// DECL_POOL / ADD_FN / RESET_POOL macros below regenerates identifiers
// byte-identical to platform.c (g_rects, g_rect_count, AddRect, ...) —
// nothing is renamed, only deduplicated.
#define FOR_EACH_SHAPE(X)                                                        \
    X(ManimRect,   g_rects,        g_rect_count,        CMD_RECT,        AddRect,        \
      (float x, float y, float hw, float hh, float rot, int r, int g, int b, int border_r, int border_g, int border_b, float border_width, float stroke_progress, float alpha), \
      (x, y, hw, hh, rot, r, g, b, border_r, border_g, border_b, border_width, stroke_progress, alpha)) \
    X(ManimCircle, g_circles,      g_circle_count,      CMD_CIRCLE,      AddCircle,      \
      (float x, float y, float radius, int r, int g, int b, int border_r, int border_g, int border_b, float border_width, float stroke_progress, float alpha), \
      (x, y, radius, r, g, b, border_r, border_g, border_b, border_width, stroke_progress, alpha)) \
    X(LineObj,     g_lines,        g_line_count,        CMD_LINE,        AddLine,        \
      (float x1, float y1, float x2, float y2, int width, int r, int g, int b, float alpha), \
      (x1, y1, x2, y2, width, r, g, b, alpha)) \
    X(EllipseObj,  g_ellipses,     g_ellipse_count,     CMD_ELLIPSE,     AddEllipse,     \
      (float x, float y, float rx, float ry, int r, int g, int b, int border_r, int border_g, int border_b, float border_width, float stroke_progress, float alpha), \
      (x, y, rx, ry, r, g, b, border_r, border_g, border_b, border_width, stroke_progress, alpha)) \
    X(DashedLineObj, g_dashed_lines, g_dashed_line_count, CMD_DASHED_LINE, AddDashedLine, \
      (float x1, float y1, float x2, float y2, int width, int r, int g, int b, float dash_length, float gap_length, float alpha), \
      (x1, y1, x2, y2, width, r, g, b, dash_length, gap_length, alpha)) \
    X(ArcObj,      g_arcs,         g_arc_count,         CMD_ARC,         AddArc,         \
      (float x, float y, float radius, float start_angle, float angle, int r, int g, int b, float stroke_width, float alpha), \
      (x, y, radius, start_angle, angle, r, g, b, stroke_width, alpha)) \
    X(PointObj,    g_points,       g_point_count,       CMD_POINT,       AddPoint,       \
      (float x, float y, int r, int g, int b, float alpha, float radius), \
      (x, y, r, g, b, alpha, radius))

#define DECL_POOL(type, pool, count, cmd, ...) \
    static type pool[MAX_SHAPES];              \
    static int count = 0;
FOR_EACH_SHAPE(DECL_POOL)
#undef DECL_POOL

// Polygon and Text adders need non-uniform bodies (vertex memcpy / string
// copy), so only their pools are declared here; the functions are below.
static PolygonObj g_polygons[MAX_SHAPES];
static int g_polygon_count = 0;
static TextObj g_texts[MAX_SHAPES];
static int g_text_count = 0;

#define MAX_DRAW_CMDS 16384
static DrawCmd g_draw_cmds[MAX_DRAW_CMDS];
static int g_draw_cmd_count = 0;

// ── Cocoa state ─────────────────────────────────────────────────────────
static NSWindow *g_window = nil;
static NSView *g_view = nil;
static CAMetalLayer *g_layer = nil;
static int g_should_close = 0;
static double g_aspect_ratio = 16.0 / 9.0;

@interface MLWindowDelegate : NSObject <NSWindowDelegate>
@end
@implementation MLWindowDelegate
- (BOOL)windowShouldClose:(NSWindow *)sender {
    (void)sender;
    g_should_close = 1;
    return YES;
}
@end
static MLWindowDelegate *g_delegate = nil;

// ── Exported API (mirrors platform.c) ───────────────────────────────────

int Vulkan_Init(int w, int h) {
    @autoreleasepool {
        [NSApplication sharedApplication];
        [NSApp setActivationPolicy:NSApplicationActivationPolicyRegular];
        [NSApp finishLaunching];
    }

    g_aspect_ratio = (double)w / (double)h;
    g_should_close = 0;

    // macOS may clamp an oversized window to the screen, breaking the
    // requested aspect ratio.  Compute the largest rect with the REQUESTED
    // aspect that fits the visible frame and use it for both the window
    // and the swapchain, so scene layout matches Windows exactly.
    NSRect screenFrame = [[NSScreen mainScreen] visibleFrame];
    double screen_aspect = screenFrame.size.width / screenFrame.size.height;
    int cw, ch;
    if (screen_aspect > g_aspect_ratio) {
        ch = (h < (int)screenFrame.size.height) ? h : (int)screenFrame.size.height;
        cw = (int)(ch * g_aspect_ratio + 0.5);
    } else {
        cw = (w < (int)screenFrame.size.width) ? w : (int)screenFrame.size.width;
        ch = (int)(cw / g_aspect_ratio + 0.5);
    }
    if (cw < 16) cw = 16;
    if (ch < 16) ch = 16;

    NSRect contentRect = NSMakeRect(0, 0, cw, ch);
    g_window = [[NSWindow alloc]
        initWithContentRect:contentRect
                  styleMask:(NSWindowStyleMaskTitled | NSWindowStyleMaskClosable |
                             NSWindowStyleMaskMiniaturizable | NSWindowStyleMaskResizable)
                    backing:NSBackingStoreBuffered
                      defer:NO];
    [g_window setTitle:@"Real Time Manim"];
    [g_window setReleasedWhenClosed:NO];
    // Keep the window at the requested aspect during user resizes
    // (the Win32 equivalent of the WM_SIZING aspect enforcement).
    [g_window setContentAspectRatio:NSMakeSize(w, h)];

    g_delegate = [[MLWindowDelegate alloc] init];
    [g_window setDelegate:g_delegate];

    g_view = [[NSView alloc] initWithFrame:contentRect];
    g_view.wantsLayer = YES;
    g_layer = [CAMetalLayer layer];
    g_layer.device = MTLCreateSystemDefaultDevice();
    // UNORM layer: raw values written by the renderer are displayed as-is
    // (the compositor treats them as gamma-encoded, same as the Windows DWM)
    // and read back unmodified — pixel-exact parity with the Windows build.
    g_layer.pixelFormat = MTLPixelFormatBGRA8Unorm;
    // MoltenVK requires framebufferOnly=NO for swapchain images that are
    // used as transfer sources (vkCmdCopyImageToBuffer readback).
    g_layer.framebufferOnly = NO;
    [g_view setLayer:g_layer];
    [g_window setContentView:g_view];

    // Place the window on the MAIN screen (menu-bar screen) instead of
    // letting AppKit pick a screen from keyboard focus — batch renders
    // otherwise jump between displays and change size run-to-run.
    NSRect mv = [[NSScreen mainScreen] visibleFrame];
    [g_window setFrameOrigin:NSMakePoint(NSMidX(mv) - cw / 2.0,
                                         NSMidY(mv) - ch / 2.0)];
    [g_window makeKeyAndOrderFront:nil];
    [NSApp activateIgnoringOtherApps:YES];

    // Match the window's REAL backing scale (2x on Retina, 1x on non-Retina)
    // and size the drawable in PHYSICAL pixels.  Read the scale AFTER the
    // window is ordered on screen: before that the window has no screen and
    // the scale can report 1, producing a swapchain that gets rebuilt on the
    // first ticks (and, pre-lock, a race with the readback worker).
    g_layer.contentsScale = [g_window backingScaleFactor];
    if (g_layer.contentsScale < 1.0) g_layer.contentsScale = 1.0;
    g_layer.drawableSize = CGSizeMake(cw * g_layer.contentsScale,
                                      ch * g_layer.contentsScale);

    Render_Init((void *)g_layer, cw, ch);
    if (!Render_IsReady()) {
        fprintf(stderr, "[ERROR] Vulkan renderer failed to initialize\n");
        return 0;
    }
    // Size the staging buffer from the SWAPCHAIN extent (physical pixels),
    // not from cw/ch: AppKit can re-scale the layer after ordering the
    // window, so Render_Init's drawableSize read is the source of truth.
    Mac_CreateReadbackBuffer(g_swapchain_ext.width, g_swapchain_ext.height);
    return 1;
}

int Vulkan_Tick(void) {
    @autoreleasepool {
        // Drain pending events without blocking (the Python main thread
        // drives the frame loop; NSApp's run loop is never started).
        while (1) {
            NSEvent *ev = [NSApp nextEventMatchingMask:NSEventMaskAny
                                             untilDate:[NSDate distantPast]
                                                inMode:NSDefaultRunLoopMode
                                               dequeue:YES];
            if (!ev) break;
            [NSApp sendEvent:ev];
        }
    }
    if (g_should_close) return 0;

    if (g_window && g_view && g_layer) {
        // Keep the layer's drawable size glued to the view; recreate the
        // swapchain whenever the physical size actually changed.  Re-assert
        // contentsScale every tick — AppKit can reset it if the window moves
        // to a display with a different backing scale.
        NSRect vb = [g_view bounds];
        g_layer.contentsScale = [g_window backingScaleFactor];
        if (g_layer.contentsScale < 1.0) g_layer.contentsScale = 1.0;
        int dw = (int)(vb.size.width * g_layer.contentsScale + 0.5);
        int dh = (int)(vb.size.height * g_layer.contentsScale + 0.5);
        if (dw < 1) dw = 1;
        if (dh < 1) dh = 1;
        g_layer.drawableSize = CGSizeMake(dw, dh);
        if (dw != (int)g_swapchain_ext.width || dh != (int)g_swapchain_ext.height) {
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

        // Return the SWAPCHAIN size (physical px == points at scale 1.0):
        // the Python side computes coordinates in exactly this space.
        int cw = (int)g_swapchain_ext.width;
        int ch = (int)g_swapchain_ext.height;
        return (cw << 16) | (ch & 0xFFFF);
    }
    return 0;
}

void Vulkan_Shutdown(void) {
    Mac_FreeReadbackBuffer();
    Render_Cleanup();
    if (g_window) {
        [g_window orderOut:nil];
        [g_window close];
        g_window = nil;
    }
}

// ── Shape adders (identical logic to platform.c) ────────────────────────
// Seven shapes share one pattern: bounds-check → store struct → push draw
// command → bump count.  Generated from FOR_EACH_SHAPE; the function names,
// signatures, and bodies are byte-equivalent to the hand-written
// platform.c versions.
#define UNPAREN(...) __VA_ARGS__
#define ADD_FN(type, pool, count, cmd, name, params, init)             \
    void name params {                                                 \
        if (count < MAX_SHAPES && g_draw_cmd_count < MAX_DRAW_CMDS) {  \
            pool[count] = (type){ UNPAREN init };                      \
            g_draw_cmds[g_draw_cmd_count++] = (DrawCmd){ cmd, count }; \
            count++;                                                   \
        }                                                              \
    }
FOR_EACH_SHAPE(ADD_FN)
#undef ADD_FN
#undef UNPAREN

void AddPolygon(float x, float y, int r, int g, int b, int border_r, int border_g, int border_b, float border_width, int vert_count, const float* verts, float stroke_progress, float alpha, int close_path) {
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

void AddText(float x, float y, int r, int g, int b, float font_size, float opacity, const char* text, float alpha) {
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

#define RESET_POOL(type, pool, count, cmd, ...) count = 0;

void ClearShapes(void) {
    FOR_EACH_SHAPE(RESET_POOL)
    g_polygon_count = 0;
    g_text_count = 0;
    g_draw_cmd_count = 0;
}

#undef RESET_POOL
#undef FOR_EACH_SHAPE

// ── Framebuffer readback (two-phase, MoltenVK-safe) ─────────────────────
//
// Reading a swapchain image AFTER present crashes MoltenVK, so the copy
// happens inside the draw command buffer (see RecordCommandBuffer in
// vulkan_draw.c), before vkQueuePresentKHR.  SaveScreenshot therefore works
// in two phases:
//   1. not armed  → arm the request, return 0 (no frame written);
//   2. armed and copy done → wait on the copy frame's own in-flight fence,
//      convert BGRA→BGR and write the BMP, return 1.
// The record worker polls each loop iteration, so every capture costs at
// most one extra arm/read cycle.

// The record worker is the only thread that sets this; the main thread
// (resize → Mac_FreeReadbackBuffer) only waits on it.  Ordering rule that
// makes the handshake race-free: the worker takes busy BEFORE checking
// g_readback_available, and the main thread clears g_readback_available
// BEFORE waiting on busy.  Both flags are accessed with seq-cst atomics
// (Dekker-style mutual exclusion — release/acquire alone is not enough on
// ARM).  Either the main thread observes busy and waits out the read, or
// the worker later sees available==0 and skips.
static volatile int g_readback_busy = 0;

void Mac_CreateReadbackBuffer(uint32_t w, uint32_t h) {
    Mac_FreeReadbackBuffer();
    VkDeviceSize size = (VkDeviceSize)w * (VkDeviceSize)h * 4;
    if (size == 0) return;

    VkBufferCreateInfo bi = {0};
    bi.sType = VK_STRUCTURE_TYPE_BUFFER_CREATE_INFO;
    bi.size = size;
    bi.usage = VK_BUFFER_USAGE_TRANSFER_DST_BIT;
    bi.sharingMode = VK_SHARING_MODE_EXCLUSIVE;
    if (vkCreateBuffer(g_dev, &bi, NULL, &g_readback_buf) != VK_SUCCESS) return;

    VkMemoryRequirements mr;
    vkGetBufferMemoryRequirements(g_dev, g_readback_buf, &mr);
    VkPhysicalDeviceMemoryProperties mp;
    vkGetPhysicalDeviceMemoryProperties(g_phys_dev, &mp);
    uint32_t chosen = UINT32_MAX;
    // Prefer non-device-local host-visible memory (fast CPU reads).
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
        vkDestroyBuffer(g_dev, g_readback_buf, NULL);
        g_readback_buf = VK_NULL_HANDLE;
        return;
    }

    VkMemoryAllocateInfo ai = {0};
    ai.sType = VK_STRUCTURE_TYPE_MEMORY_ALLOCATE_INFO;
    ai.allocationSize = mr.size;
    ai.memoryTypeIndex = chosen;
    if (vkAllocateMemory(g_dev, &ai, NULL, &g_readback_mem) != VK_SUCCESS ||
        vkBindBufferMemory(g_dev, g_readback_buf, g_readback_mem, 0) != VK_SUCCESS) {
        vkDestroyBuffer(g_dev, g_readback_buf, NULL);
        g_readback_buf = VK_NULL_HANDLE;
        g_readback_mem = VK_NULL_HANDLE;
        return;
    }
    vkMapMemory(g_dev, g_readback_mem, 0, size, 0, &g_readback_map);
    g_readback_requested = 0;
    g_readback_available = 0;
}

void Mac_FreeReadbackBuffer(void) {
    // Cancel pending requests, then wait out any CPU read still in flight:
    // a reader that already passed the available check may be inside
    // memcpy() on the mapped pointer right now.  vkDeviceWaitIdle in
    // RecreateSwapchain drains the GPU first, so the fence the reader is
    // blocked on gets signaled and it will finish shortly.
    g_readback_requested = 0;
    __atomic_store_n(&g_readback_available, 0, __ATOMIC_SEQ_CST);
    while (__atomic_load_n(&g_readback_busy, __ATOMIC_SEQ_CST)) {
        struct timespec ts = {0, 500000};  // 0.5 ms
        nanosleep(&ts, NULL);
    }
    if (g_readback_buf != VK_NULL_HANDLE) {
        if (g_readback_map) vkUnmapMemory(g_dev, g_readback_mem);
        g_readback_map = NULL;
        vkDestroyBuffer(g_dev, g_readback_buf, NULL);
        vkFreeMemory(g_dev, g_readback_mem, NULL);
        g_readback_buf = VK_NULL_HANDLE;
        g_readback_mem = VK_NULL_HANDLE;
    }
    g_readback_requested = 0;
    g_readback_available = 0;
}

void Mac_GetDrawableSize(int *w, int *h) {
    if (!g_layer) { *w = 0; *h = 0; return; }
    CGSize s = g_layer.drawableSize;
    *w = (int)(s.width + 0.5);
    *h = (int)(s.height + 0.5);
}

// Convert the BGRA staging buffer (w*h*4) into BGR with 4-byte row padding.
// The mapped GPU buffer reads slowly byte-by-byte on Apple Silicon, so bulk
// copy into CPU cache first (same trick as platform.c).
static void ConvertBGRAtoBGR(int w, int h, unsigned char *out) {
    VkDeviceSize raw_size = (VkDeviceSize)w * (VkDeviceSize)h * 4;
    unsigned char *raw = (unsigned char *)malloc((size_t)raw_size);
    memcpy(raw, g_readback_map, (size_t)raw_size);
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
    free(raw);
}

// Wait for the copy frame's own in-flight fence, then hand back the BGR
// pixel buffer (malloc'd, row-padded).  Returns 1 when a fresh frame was
// produced.  Takes the busy slot BEFORE checking g_readback_available and
// reads the extent INSIDE the guarded section: once available==1 is
// observed (seq-cst), no resize can have occurred since the copy, so the
// extent and the staging buffer are the matching pair.
static int ReadbackFrame(unsigned char **out_bgr, int *out_w, int *out_h) {
    __atomic_store_n(&g_readback_busy, 1, __ATOMIC_SEQ_CST);
    if (!__atomic_load_n(&g_readback_available, __ATOMIC_SEQ_CST)) {
        __atomic_store_n(&g_readback_busy, 0, __ATOMIC_SEQ_CST);
        return 0;
    }
    int w = (int)g_swapchain_ext.width;
    int h = (int)g_swapchain_ext.height;
    vkWaitForFences(g_dev, 1, &g_in_flight_fences[g_readback_fence_idx], VK_TRUE, UINT64_MAX);
    __atomic_store_n(&g_readback_available, 0, __ATOMIC_SEQ_CST);
    int rowBytes = ((w * 3 + 3) & ~3);
    unsigned char *bgr = (unsigned char *)malloc((size_t)rowBytes * (size_t)h);
    ConvertBGRAtoBGR(w, h, bgr);
    __atomic_store_n(&g_readback_busy, 0, __ATOMIC_SEQ_CST);
    *out_bgr = bgr;
    *out_w = w;
    *out_h = h;
    return 1;
}

// BMP layout identical to the Windows BITMAPFILEHEADER + BITMAPINFOHEADER
// (14 + 40 = 54-byte header, negative biHeight = top-down rows).
static int WriteBMP(const char *path, int w, int h, const unsigned char *bgr) {
    int rowBytes = ((w * 3 + 3) & ~3);
    int imgSize = rowBytes * h;
    unsigned char hdr[54];
    memset(hdr, 0, sizeof(hdr));
    hdr[0] = 'B'; hdr[1] = 'M';
    uint32_t fileSize = (uint32_t)(54 + imgSize);
    uint32_t offBits = 54;
    memcpy(hdr + 2, &fileSize, 4);
    memcpy(hdr + 10, &offBits, 4);
    uint32_t biSize = 40;
    int32_t biWidth = w;
    int32_t biHeight = -h;  // top-down
    uint16_t biPlanes = 1;
    uint16_t biBitCount = 24;
    uint32_t biCompression = 0;
    uint32_t biSizeImage = (uint32_t)imgSize;
    memcpy(hdr + 14, &biSize, 4);
    memcpy(hdr + 18, &biWidth, 4);
    memcpy(hdr + 22, &biHeight, 4);
    memcpy(hdr + 26, &biPlanes, 2);
    memcpy(hdr + 28, &biBitCount, 2);
    memcpy(hdr + 30, &biCompression, 4);
    memcpy(hdr + 34, &biSizeImage, 4);

    int ok = 0;
    FILE *fp = fopen(path, "wb");
    if (fp) {
        fwrite(hdr, sizeof(hdr), 1, fp);
        fwrite(bgr, (size_t)imgSize, 1, fp);
        fclose(fp);
        ok = 1;
    }
    return ok;
}

int SaveScreenshot(const char *path) {
    if (!g_is_ready || !g_swapchain) return 0;
    if (g_readback_buf == VK_NULL_HANDLE) return 0;

    int w = 0, h = 0;
    unsigned char *bgr = NULL;
    if (!ReadbackFrame(&bgr, &w, &h)) {
        g_readback_requested = 1;  // next drawn frame performs the copy
        return 0;
    }
    int ok = WriteBMP(path, w, h, bgr);
    free(bgr);
    return ok;
}
