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
#include "draw_common.h"
#include "vulkan_texture.h"
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
    X(PointObj,    g_points,       g_point_count,       CMD_POINT,       AddPoint,       \
      (float x, float y, int r, int g, int b, float alpha, float radius), \
      (x, y, r, g, b, alpha, radius))

#define DECL_POOL(type, pool, count, cmd, ...) \
    static type pool[MAX_SHAPES];              \
    static int count = 0;
FOR_EACH_SHAPE(DECL_POOL)
#undef DECL_POOL

// Polygon adders need a non-uniform body (vertex memcpy), so only their pool
// is declared here; the function is below.
static PolygonObj g_polygons[MAX_SHAPES];
static int g_polygon_count = 0;

// One entry per submitted primitive now that the bezier fill and the
// line-strip stroke are replayed in place (draw_common.h), and a text-heavy
// frame pushes ~870 of them: a dropped entry would be a dropped shape.
#define MAX_DRAW_CMDS 65536
static DrawCmd g_draw_cmds[MAX_DRAW_CMDS];
static int g_draw_cmd_count = 0;

void DrawCmd_Push(int type, int index) {
    if (g_draw_cmd_count < MAX_DRAW_CMDS) {
        g_draw_cmds[g_draw_cmd_count++] = (DrawCmd){ type, index };
    }
}

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

static int Mac_InitWindow(int w, int h, int hidden);

int Vulkan_Init(int w, int h) {
    return Mac_InitWindow(w, h, 0);
}

// Hidden-window init (mirrors platform.c): the window is created but never
// ordered on screen, at the EXACT requested size with a 1x layer -- the 2.0
// record pipeline (ffmpeg -video_size, fast-record buffers) assumes the
// framebuffer is w x h, and a screen-clamped 2x Retina window breaks that.
// Offline work never shows a window anyway, so nothing is lost.
int Vulkan_InitEx(int w, int h, int hidden) {
    return Mac_InitWindow(w, h, hidden);
}

static int g_init_hidden = 0;
// Set by Vulkan_SetPreviewBarReserve before a hidden window is revealed.
static int g_preview_bar_reserved = 0;
// Recording override: while non-zero the layer's drawable is pinned to this
// physical size, so the framebuffer the readback sees is exactly the video's
// 1920x1080 even though the on-screen window is screen-clamped and Retina
// (3420x1924 on a 1710x962-point window).  Without it the live recorder had to
// downscale 6.6 MP per frame in ffmpeg, which could not keep up with 60 fps.
static int g_capture_w = 0;
static int g_capture_h = 0;

static int Mac_InitWindow(int w, int h, int hidden) {
    g_init_hidden = hidden;

    @autoreleasepool {
        [NSApplication sharedApplication];
        [NSApp setActivationPolicy:NSApplicationActivationPolicyRegular];
        [NSApp finishLaunching];
    }

    g_aspect_ratio = (double)w / (double)h;
    g_should_close = 0;
    g_preview_bar_reserved = 0;

    // macOS may clamp an oversized window to the screen, breaking the
    // requested aspect ratio.  Compute the largest rect with the REQUESTED
    // aspect that fits the visible frame and use it for both the window
    // and the swapchain, so scene layout matches Windows exactly.
    // (Hidden windows are never seen: keep the exact requested size.)
    int cw = w, ch = h;
    if (!hidden) {
        NSRect screenFrame = [[NSScreen mainScreen] visibleFrame];
        double screen_aspect = screenFrame.size.width / screenFrame.size.height;
        if (screen_aspect > g_aspect_ratio) {
            ch = (h < (int)screenFrame.size.height) ? h : (int)screenFrame.size.height;
            cw = (int)(ch * g_aspect_ratio + 0.5);
        } else {
            cw = (w < (int)screenFrame.size.width) ? w : (int)screenFrame.size.width;
            ch = (int)(cw / g_aspect_ratio + 0.5);
        }
        if (cw < 16) cw = 16;
        if (ch < 16) ch = 16;
    }

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

    if (!hidden) {
        // Place the window on the MAIN screen (menu-bar screen) instead of
        // letting AppKit pick a screen from keyboard focus — batch renders
        // otherwise jump between displays and change size run-to-run.
        NSRect mv = [[NSScreen mainScreen] visibleFrame];
        [g_window setFrameOrigin:NSMakePoint(NSMidX(mv) - cw / 2.0,
                                             NSMidY(mv) - ch / 2.0)];
        [g_window makeKeyAndOrderFront:nil];
        [NSApp activateIgnoringOtherApps:YES];
    }

    // Match the window's REAL backing scale (2x on Retina, 1x on non-Retina)
    // and size the drawable in PHYSICAL pixels.  Read the scale AFTER the
    // window is ordered on screen: before that the window has no screen and
    // the scale can report 1, producing a swapchain that gets rebuilt on the
    // first ticks (and, pre-lock, a race with the readback worker).  Hidden
    // windows force 1x so the framebuffer is exactly w x h physical pixels.
    g_layer.contentsScale = hidden ? 1.0 : [g_window backingScaleFactor];
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

// ── Preview control bar ─────────────────────────────────────────────────
// macOS counterpart of Win32Bar in real_time_manim/preview.py: a small
// native window docked right below the video window (never a second content
// area in the video window).  AppKit only runs on the main thread, which is
// also where FramePreview._loop calls Vulkan_Tick, so the native side queues
// clicks/keystrokes and Python polls that queue (Vulkan_PollPreviewBar).  No
// Python callback ever runs inside AppKit.
//
// The scrubber is a custom NSView rather than NSSlider on purpose: NSSlider's
// mouseDown: runs a modal tracking loop, which would freeze this main-thread
// event pump (and therefore frame scrubbing) until the mouse is released.
// RTMScrubber returns immediately and handles mouseDragged:/mouseUp: as
// separate events, so every drag step reaches Python and can draw a frame.

enum {
    RTM_BAR_NONE = 0,
    RTM_BAR_SUBMIT = 1,
    RTM_BAR_SAVE = 2,
    RTM_BAR_QUIT = 3,
    RTM_BAR_SEEK = 4,
};

#define RTM_BAR_QUEUE 128

typedef struct {
    int kind;
    int value;
    char text[256];
} RTMBarEvent;

static const CGFloat RTM_BAR_HEIGHT = 36.0;   // client height, like Win32Bar
static const CGFloat RTM_BAR_GAP = 4.0;
static const CGFloat RTM_BAR_TITLE = 28.0;    // fallback until a bar exists
// Space between the bar's bottom edge and the display's visible frame.  The
// Dock can auto-reveal over the bottom ~60 pt; a click there would go to the
// Dock instead of the scrubber, so keep the whole bar above that strip.
static const CGFloat RTM_BAR_BOTTOM_MARGIN = 64.0;

@interface RTMScrubber : NSView {
    int _frameCount;
    int _value;
    BOOL _dragging;
    id _target;
    SEL _action;
}
- (void)setFrameCount:(int)count;
- (int)frameValue;
- (void)setFrameValue:(int)value;
- (void)setTarget:(id)target action:(SEL)action;
@end

@implementation RTMScrubber

- (id)initWithFrame:(NSRect)frame {
    self = [super initWithFrame:frame];
    if (self) {
        _frameCount = 1;
        _value = 0;
        _dragging = NO;
        _target = nil;
        _action = NULL;
    }
    return self;
}

- (BOOL)acceptsFirstResponder { return YES; }
- (BOOL)acceptsFirstMouse:(NSEvent *)event { (void)event; return YES; }

- (void)setFrameCount:(int)count {
    _frameCount = count > 0 ? count : 1;
    [self setNeedsDisplay:YES];
}

- (int)frameValue { return _value; }

- (void)setFrameValue:(int)value {
    int last = _frameCount > 1 ? _frameCount - 1 : 0;
    if (value < 0) value = 0;
    if (value > last) value = last;
    if (value == _value) return;
    _value = value;
    [self setNeedsDisplay:YES];
}

- (void)setTarget:(id)target action:(SEL)action {
    _target = target;
    _action = action;
}

- (void)notify {
    if (_target && _action) [NSApp sendAction:_action to:_target from:self];
}

- (void)seekToPoint:(NSPoint)p {
    NSRect b = [self bounds];
    CGFloat margin = 9.0;
    CGFloat span = b.size.width - 2.0 * margin;
    if (span < 1.0) span = 1.0;
    double frac = (p.x - margin) / span;
    if (frac < 0.0) frac = 0.0;
    if (frac > 1.0) frac = 1.0;
    int last = _frameCount > 1 ? _frameCount - 1 : 0;
    int value = (int)llround(frac * (double)last);
    [self setFrameValue:value];
    [self notify];
}

- (void)mouseDown:(NSEvent *)event {
    _dragging = YES;
    [[self window] makeFirstResponder:self];
    [self seekToPoint:[self convertPoint:[event locationInWindow] fromView:nil]];
}

- (void)mouseDragged:(NSEvent *)event {
    if (_dragging)
        [self seekToPoint:[self convertPoint:[event locationInWindow] fromView:nil]];
}

- (void)mouseUp:(NSEvent *)event {
    if (_dragging) {
        [self seekToPoint:[self convertPoint:[event locationInWindow] fromView:nil]];
        _dragging = NO;
    }
}

- (void)keyDown:(NSEvent *)event {
    int last = _frameCount > 1 ? _frameCount - 1 : 0;
    int step = 0;
    switch ([event keyCode]) {
        case 123: step = -1; break;                  // left
        case 124: step = +1; break;                  // right
        case 116: step = -10; break;                 // page up
        case 121: step = +10; break;                 // page down
        case 115: [self setFrameValue:0]; [self notify]; return;   // home
        case 119: [self setFrameValue:last]; [self notify]; return; // end
        default: [super keyDown:event]; return;
    }
    [self setFrameValue:_value + step];
    [self notify];
}

- (void)drawRect:(NSRect)dirtyRect {
    (void)dirtyRect;
    NSRect b = [self bounds];
    CGFloat margin = 9.0;
    CGFloat trackW = b.size.width - 2.0 * margin;
    if (trackW < 1.0) trackW = 1.0;
    CGFloat cy = NSMidY(b);
    CGFloat trackH = 4.0;
    NSRect track = NSMakeRect(margin, cy - trackH / 2.0, trackW, trackH);

    if ([[self window] firstResponder] == self) {
        [[NSColor keyboardFocusIndicatorColor] setStroke];
        NSBezierPath *focus = [NSBezierPath bezierPathWithRoundedRect:
                               NSInsetRect(b, 1.5, 1.5) xRadius:4.0 yRadius:4.0];
        [focus setLineWidth:2.0];
        [focus stroke];
    }

    [[NSColor quaternaryLabelColor] setFill];
    [[NSBezierPath bezierPathWithRoundedRect:track xRadius:2.0 yRadius:2.0] fill];

    int last = _frameCount > 1 ? _frameCount - 1 : 0;
    double frac = last > 0 ? (double)_value / (double)last : 0.0;

    // TBS_AUTOTICKS in the Win32 bar: about ten reference marks.
    int ticks = last > 0 ? 11 : 1;
    [[NSColor tertiaryLabelColor] setStroke];
    NSBezierPath *marks = [NSBezierPath bezierPath];
    [marks setLineWidth:1.0];
    for (int i = 0; i < ticks; i++) {
        CGFloat tx = margin + trackW * (ticks > 1 ? (double)i / (double)(ticks - 1) : 0.0);
        [marks moveToPoint:NSMakePoint(tx, cy - 7.0)];
        [marks lineToPoint:NSMakePoint(tx, cy - 2.0)];
    }
    [marks stroke];

    NSRect filled = track;
    filled.size.width = trackW * frac;
    [[NSColor controlAccentColor] setFill];
    [[NSBezierPath bezierPathWithRoundedRect:filled xRadius:2.0 yRadius:2.0] fill];

    CGFloat diameter = 14.0;
    CGFloat kx = margin + trackW * frac;
    NSRect knob = NSMakeRect(kx - diameter / 2.0, cy - diameter / 2.0,
                             diameter, diameter);
    [[NSColor controlBackgroundColor] setFill];
    [[NSBezierPath bezierPathWithOvalInRect:knob] fill];
    [[NSColor controlAccentColor] setStroke];
    NSBezierPath *ring = [NSBezierPath bezierPathWithOvalInRect:
                          NSInsetRect(knob, 0.75, 0.75)];
    [ring setLineWidth:1.5];
    [ring stroke];
}

@end

@interface RTMPreviewBar : NSObject <NSWindowDelegate> {
    NSWindow *_window;
    NSTextField *_edit;
    RTMScrubber *_scrubber;
    NSButton *_jump;
    NSButton *_save;
    NSButton *_quit;
    int _nFrames;
    int _sliderMode;
    BOOL _closing;
    RTMBarEvent _events[RTM_BAR_QUEUE];
    int _head;
    int _tail;
    CGFloat _lastWidth;
}
- (BOOL)createWithFrames:(int)frames mode:(int)slider title:(const char *)title;
- (void)destroy;
- (void)tick;
- (void)setCaption:(const char *)text;
- (void)setPosition:(int)frame;
- (CGFloat)frameHeight;
- (int)pollValue:(int *)value text:(char *)text cap:(int)cap;
@end

@interface RTMPreviewBar ()
- (void)layout;
- (void)dock;
- (void)focusInput;
- (void)push:(int)kind value:(int)value text:(NSString *)text;
@end

@implementation RTMPreviewBar

- (id)init {
    self = [super init];
    if (self) {
        _head = _tail = 0;
        _closing = NO;
        _lastWidth = 0;
    }
    return self;
}

- (void)push:(int)kind value:(int)value text:(NSString *)text {
    int next = (_tail + 1) % RTM_BAR_QUEUE;
    if (next == _head)                      // full: drop the oldest event
        _head = (_head + 1) % RTM_BAR_QUEUE;
    _events[_tail].kind = kind;
    _events[_tail].value = value;
    _events[_tail].text[0] = 0;
    if (text) {
        const char *s = [text UTF8String];
        if (s) snprintf(_events[_tail].text, sizeof(_events[_tail].text), "%s", s);
    }
    _tail = next;
}

- (BOOL)createWithFrames:(int)frames mode:(int)slider title:(const char *)title {
    if (_window) [self destroy];
    _nFrames = frames > 0 ? frames : 1;
    _sliderMode = slider ? 1 : 0;
    _closing = NO;
    _head = _tail = 0;
    _lastWidth = 0;

    CGFloat width = 900.0;
    if (g_window) width = MAX(360.0, NSWidth([g_window frame]));

    NSRect contentRect = NSMakeRect(0, 0, width, RTM_BAR_HEIGHT);
    _window = [[NSWindow alloc]
        initWithContentRect:contentRect
                  styleMask:(NSWindowStyleMaskTitled | NSWindowStyleMaskClosable)
                    backing:NSBackingStoreBuffered
                      defer:NO];
    [_window setReleasedWhenClosed:NO];
    [_window setDelegate:self];
    [_window setHidesOnDeactivate:NO];
    [_window setTitle:(title ? [NSString stringWithUTF8String:title]
                             : @"RTM frame preview")];

    NSView *content = [[NSView alloc] initWithFrame:contentRect];
    [_window setContentView:content];
    [content release];

    _edit = [[NSTextField alloc] initWithFrame:NSZeroRect];
    [_edit setBezeled:YES];
    [_edit setDrawsBackground:YES];
    [_edit setEditable:YES];
    [_edit setSelectable:YES];
    [_edit setFont:[NSFont systemFontOfSize:13.0]];
    [_edit setTarget:self];
    [_edit setAction:@selector(submit:)];
    [content addSubview:_edit];
    [_edit release];

    _jump = [NSButton buttonWithTitle:@"Jump" target:self action:@selector(submit:)];
    [_jump setBezelStyle:NSBezelStyleRounded];
    [_jump setKeyEquivalent:@"\r"];
    [_jump setKeyEquivalentModifierMask:0];
    [content addSubview:_jump];

    _save = [NSButton buttonWithTitle:@"Save PNG" target:self
                              action:@selector(savePressed:)];
    [_save setBezelStyle:NSBezelStyleRounded];
    [content addSubview:_save];

    _quit = [NSButton buttonWithTitle:@"Quit" target:self
                              action:@selector(quitPressed:)];
    [_quit setBezelStyle:NSBezelStyleRounded];
    [content addSubview:_quit];

    _scrubber = [[RTMScrubber alloc] initWithFrame:NSZeroRect];
    [_scrubber setFrameCount:_nFrames];
    [_scrubber setTarget:self action:@selector(scrubberMoved:)];
    [content addSubview:_scrubber];
    [_scrubber release];

    if (_sliderMode) {
        [_edit setHidden:YES];
        [_jump setHidden:YES];
    } else {
        [_scrubber setHidden:YES];
    }

    [self layout];
    if (g_window) [g_window addChildWindow:_window ordered:NSWindowAbove];
    [self dock];
    [_window makeKeyAndOrderFront:nil];
    [NSApp activateIgnoringOtherApps:YES];
    [self focusInput];
    return YES;
}

- (void)layout {
    if (!_window) return;
    NSRect b = [[_window contentView] bounds];
    CGFloat pad = 6.0;
    CGFloat btnW = 80.0;          // Jump / Quit
    CGFloat saveW = 104.0;        // "Save PNG" at 13 pt is ~60 pt + bezel
    CGFloat h = b.size.height - 2.0 * pad;
    CGFloat x = pad;
    if (h < 18.0) h = 18.0;
    if (_sliderMode) {
        CGFloat w = b.size.width - saveW - btnW - 3.0 * pad;
        if (w < 60.0) w = 60.0;
        [_scrubber setFrame:NSMakeRect(x, pad, w, h)];
        x += w + pad;
        [_save setFrame:NSMakeRect(x, pad, saveW, h)];
        x += saveW + 2.0;
        [_quit setFrame:NSMakeRect(x, pad, btnW, h)];
    } else {
        CGFloat w = b.size.width - 2.0 * btnW - saveW - 4.0 * pad;
        if (w < 60.0) w = 60.0;
        [_edit setFrame:NSMakeRect(x, pad, w, h)];
        x += w + pad;
        [_jump setFrame:NSMakeRect(x, pad, btnW, h)];
        x += btnW + 2.0;
        [_save setFrame:NSMakeRect(x, pad, saveW, h)];
        x += saveW + 2.0;
        [_quit setFrame:NSMakeRect(x, pad, btnW, h)];
    }
}

- (void)dock {
    if (!_window || !g_window) return;
    NSRect vf = [g_window frame];
    NSRect wf = [_window frame];
    CGFloat width = MAX(360.0, vf.size.width);
    NSScreen *screen = [g_window screen];
    if (!screen) screen = [NSScreen mainScreen];
    NSRect vis = [screen visibleFrame];
    if (width > vis.size.width) width = vis.size.width;
    CGFloat x = vf.origin.x;
    if (x + width > NSMaxX(vis)) x = NSMaxX(vis) - width;
    if (x < vis.origin.x) x = vis.origin.x;
    CGFloat y = vf.origin.y - wf.size.height - RTM_BAR_GAP;
    if (y < vis.origin.y) y = vf.origin.y + RTM_BAR_GAP;
    NSRect target = NSMakeRect(x, y, width, wf.size.height);
    if (!NSEqualRects(wf, target)) [_window setFrame:target display:YES];
    if (fabs(width - _lastWidth) > 0.5) {
        _lastWidth = width;
        [self layout];
    }
}

- (void)tick {
    [self dock];
}

- (void)focusInput {
    if (!_window) return;
    if (_edit && ![_edit isHidden]) [_window makeFirstResponder:_edit];
    else if (_scrubber) [_window makeFirstResponder:_scrubber];
}

- (void)submit:(id)sender {
    (void)sender;
    if (!_edit) return;
    NSString *text = [_edit stringValue];
    if (text.length == 0) {             // Enter can reach both field and button
        [self focusInput];
        return;
    }
    [self push:RTM_BAR_SUBMIT value:0 text:text];
    [_edit setStringValue:@""];
    [self focusInput];
}

- (void)savePressed:(id)sender {
    (void)sender;
    [self push:RTM_BAR_SAVE value:0 text:nil];
    [self focusInput];
}

- (void)quitPressed:(id)sender {
    (void)sender;
    [self push:RTM_BAR_QUIT value:0 text:nil];
}

- (void)scrubberMoved:(id)sender {
    (void)sender;
    [self push:RTM_BAR_SEEK value:[_scrubber frameValue] text:nil];
}

- (void)setCaption:(const char *)text {
    if (!_window) return;
    NSString *s = text ? [NSString stringWithUTF8String:text] : @"";
    [_window setTitle:(s ? s : @"")];
}

- (void)setPosition:(int)frame {
    if (_scrubber) [_scrubber setFrameValue:frame];
}

- (CGFloat)frameHeight {
    return _window ? NSHeight([_window frame]) : 0.0;
}

- (int)pollValue:(int *)value text:(char *)text cap:(int)cap {
    if (_head == _tail) return RTM_BAR_NONE;
    RTMBarEvent *event = &_events[_head];
    _head = (_head + 1) % RTM_BAR_QUEUE;
    if (value) *value = event->value;
    if (text && cap > 0) {
        if (event->kind == RTM_BAR_SUBMIT) {
            strncpy(text, event->text, (size_t)cap - 1);
            text[cap - 1] = 0;
        } else {
            text[0] = 0;
        }
    }
    return event->kind;
}

- (void)windowWillClose:(NSNotification *)note {
    (void)note;
    if (_closing) return;
    [self push:RTM_BAR_QUIT value:0 text:nil];
}

- (void)destroy {
    if (!_window) return;
    _closing = YES;
    NSWindow *window = _window;
    _window = nil;
    if (g_window) [g_window removeChildWindow:window];
    [window setDelegate:nil];
    [window orderOut:nil];
    [window close];
    [window release];
    _edit = nil;
    _scrubber = nil;
    _jump = nil;
    _save = nil;
    _quit = nil;
    _head = _tail = 0;
    _lastWidth = 0;
}

@end

static RTMPreviewBar *g_preview_bar = nil;

// Set by FramePreview before it reveals a hidden window: yes, a control bar
// will be docked below the video, so leave room for it.  Reveal happens
// before the bar is created, hence the hint instead of probing the bar.
void Vulkan_SetPreviewBarReserve(int reserved) {
    g_preview_bar_reserved = reserved ? 1 : 0;
}

int Vulkan_CreatePreviewBar(int n_frames, int mode, const char *title) {
    @autoreleasepool {
        if (!g_preview_bar) g_preview_bar = [[RTMPreviewBar alloc] init];
        return [g_preview_bar createWithFrames:n_frames mode:mode title:title] ? 1 : 0;
    }
}

int Vulkan_PollPreviewBar(int *value, char *text, int text_cap) {
    if (!g_preview_bar) return RTM_BAR_NONE;
    return [g_preview_bar pollValue:value text:text cap:text_cap];
}

void Vulkan_SetPreviewBarCaption(const char *text) {
    if (g_preview_bar) [g_preview_bar setCaption:text];
}

void Vulkan_SetPreviewBarPosition(int frame) {
    if (g_preview_bar) [g_preview_bar setPosition:frame];
}

void Vulkan_DestroyPreviewBar(void) {
    if (g_preview_bar) [g_preview_bar destroy];
}

static void MacBar_Tick(void) {
    if (g_preview_bar) [g_preview_bar tick];
}

// ── Compile-wait popup ──────────────────────────────────────────────────
// macOS counterpart of render_wait.WaitPopup (Windows).  A formula compile
// blocks the main thread inside MathTex.__init__, so -- unlike the Windows
// popup, which owns a message-loop thread -- this panel is created, shown and
// advanced by explicit pumps from the compile's wait loops
// (Vulkan_WaitPopupPump).  Everything stays on the AppKit main thread.
// Python owns the 0.35 s "only if slow" delay and supplies the determinate
// percentage (Vulkan_WaitPopupSetProgress); the slow SVG/mobject build runs on
// a worker thread so those pumps keep flowing.

static const CGFloat RTM_WAIT_WIDTH = 430.0;
static const CGFloat RTM_WAIT_HEIGHT = 104.0;

@interface RTMWaitPopup : NSObject {
    NSPanel *_window;
    NSTextField *_line1;
    NSTextField *_line2;
    NSTextField *_snippet;
    NSProgressIndicator *_bar;
    NSTextField *_percent;
    NSTimer *_timer;
    NSDate *_shownAt;
    NSString *_line2Fmt;
    BOOL _visible;
}
- (void)armTitle:(NSString *)title
           line1:(NSString *)line1
        line2Fmt:(NSString *)fmt
         snippet:(NSString *)snippet;
- (void)show;
- (void)setProgress:(double)percent;
- (void)pump:(double)seconds;
- (void)destroy;
@end

@implementation RTMWaitPopup

- (id)init {
    self = [super init];
    if (self) {
        _visible = NO;
    }
    return self;
}

- (NSTextField *)newLabel:(NSRect)frame
                     font:(NSFont *)font
                    color:(NSColor *)color {
    NSTextField *field = [[NSTextField alloc] initWithFrame:frame];
    [field setBezeled:NO];
    [field setBordered:NO];
    [field setDrawsBackground:NO];
    [field setEditable:NO];
    [field setSelectable:NO];
    [field setFont:font];
    [field setTextColor:color];
    [field setLineBreakMode:NSLineBreakByTruncatingTail];
    [field setAutoresizingMask:NSViewWidthSizable];
    return field;                       // caller adds and releases
}

- (void)armTitle:(NSString *)title
           line1:(NSString *)line1
        line2Fmt:(NSString *)fmt
         snippet:(NSString *)snippet {
    [self destroy];

    NSRect contentRect = NSMakeRect(0, 0, RTM_WAIT_WIDTH, RTM_WAIT_HEIGHT);
    _window = [[NSPanel alloc]
        initWithContentRect:contentRect
                  styleMask:(NSWindowStyleMaskTitled |
                             NSWindowStyleMaskNonactivatingPanel)
                    backing:NSBackingStoreBuffered
                      defer:NO];
    [_window setFloatingPanel:YES];
    [_window setBecomesKeyOnlyIfNeeded:YES];
    [_window setTitle:(title ? title : @"")];
    [_window setReleasedWhenClosed:NO];
    [_window setLevel:NSFloatingWindowLevel];
    [_window setHidesOnDeactivate:NO];
    [_window setIgnoresMouseEvents:YES];
    [_window setCollectionBehavior:
        (NSWindowCollectionBehaviorCanJoinAllSpaces |
         NSWindowCollectionBehaviorFullScreenAuxiliary)];

    NSView *content = [[NSView alloc] initWithFrame:contentRect];
    [_window setContentView:content];
    [content release];

    CGFloat w = RTM_WAIT_WIDTH - 28.0;
    _line1 = [self newLabel:NSMakeRect(14, 68, w, 20)
                       font:[NSFont systemFontOfSize:13.0
                                              weight:NSFontWeightSemibold]
                      color:[NSColor labelColor]];
    _line2 = [self newLabel:NSMakeRect(14, 48, w, 16)
                       font:[NSFont systemFontOfSize:11.0]
                      color:[NSColor secondaryLabelColor]];
    _snippet = [self newLabel:NSMakeRect(14, 28, w, 16)
                         font:[NSFont systemFontOfSize:10.0]
                        color:[NSColor tertiaryLabelColor]];
    [_line1 setStringValue:(line1 ? line1 : @"")];
    [_line2 setStringValue:@""];
    [_snippet setStringValue:(snippet ? snippet : @"")];
    [_snippet setHidden:(snippet.length == 0)];
    [content addSubview:_line1];
    [content addSubview:_line2];
    [content addSubview:_snippet];
    [_line1 release];
    [_line2 release];
    [_snippet release];

    _bar = [[NSProgressIndicator alloc] initWithFrame:NSMakeRect(14, 12, w - 44, 8)];
    [_bar setStyle:NSProgressIndicatorStyleBar];
    [_bar setControlSize:NSControlSizeSmall];
    [_bar setIndeterminate:NO];
    [_bar setMinValue:0.0];
    [_bar setMaxValue:100.0];
    [_bar setDoubleValue:0.0];
    [content addSubview:_bar];
    [_bar release];

    _percent = [self newLabel:NSMakeRect(RTM_WAIT_WIDTH - 14 - 42, 8, 42, 14)
                        font:[NSFont monospacedDigitSystemFontOfSize:10.0
                                                              weight:NSFontWeightRegular]
                       color:[NSColor secondaryLabelColor]];
    [_percent setAlignment:NSTextAlignmentRight];
    [_percent setStringValue:@"0%"];
    [content addSubview:_percent];
    [_percent release];

    _line2Fmt = [fmt copy];
}

- (void)position {
    if (!_window) return;
    NSScreen *screen = g_window ? [g_window screen] : nil;
    if (!screen) screen = [NSScreen mainScreen];
    NSRect vis = [screen visibleFrame];
    NSRect wf = [_window frame];
    CGFloat x, y;
    if (g_window) {
        // Same corner as the Windows popup: just inside the video's top-right.
        NSRect vf = [g_window frame];
        x = NSMaxX(vf) - wf.size.width - 24.0;
        y = NSMaxY(vf) - wf.size.height - 24.0;
    } else {
        x = NSMidX(vis) - wf.size.width / 2.0;
        y = NSMidY(vis) - wf.size.height / 2.0;
    }
    if (x < NSMinX(vis)) x = NSMinX(vis);
    if (x + wf.size.width > NSMaxX(vis)) x = NSMaxX(vis) - wf.size.width;
    if (y < NSMinY(vis)) y = NSMinY(vis);
    if (y + wf.size.height > NSMaxY(vis)) y = NSMaxY(vis) - wf.size.height;
    [_window setFrameOrigin:NSMakePoint(floor(x), floor(y))];
}

- (void)updateElapsed {
    if (!_line2 || !_shownAt || !_line2Fmt) return;
    double elapsed = -[_shownAt timeIntervalSinceNow];
    if (elapsed < 0.0) elapsed = 0.0;
    [_line2 setStringValue:[NSString stringWithFormat:_line2Fmt, elapsed]];
}

- (void)tick:(NSTimer *)timer {
    (void)timer;
    [self updateElapsed];
}

- (void)setProgress:(double)percent {
    if (percent < 0.0) percent = 0.0;
    if (percent > 100.0) percent = 100.0;
    if (_bar) [_bar setDoubleValue:percent];
    if (_percent) {
        [_percent setStringValue:
            [NSString stringWithFormat:@"%.0f%%", percent]];
    }
}

- (void)show {
    if (!_window || _visible) return;
    [self position];
    [_shownAt release];
    _shownAt = [[NSDate alloc] init];
    [self setProgress:0.0];
    [self updateElapsed];
    [_window orderFrontRegardless];
    [_window displayIfNeeded];
    _visible = YES;
    if (!_timer) {
        _timer = [NSTimer scheduledTimerWithTimeInterval:0.1
                                                  target:self
                                                selector:@selector(tick:)
                                                userInfo:nil
                                                 repeats:YES];
    }
}

- (void)pump:(double)seconds {
    if (!_visible) return;
    // The run loop fires NSTimer; the elapsed counter is also refreshed here
    // because Python sets the percentage on every pump and runMode may return
    // as soon as it has handled one source.
    [self updateElapsed];
    NSDate *limit = [NSDate dateWithTimeIntervalSinceNow:
                     (seconds > 0.0 ? seconds : 0.01)];
    [[NSRunLoop currentRunLoop] runMode:NSDefaultRunLoopMode beforeDate:limit];
}

- (void)destroy {
    if (_timer) {
        [_timer invalidate];
        _timer = nil;
    }
    if (_bar) [_bar stopAnimation:nil];
    if (_window) {
        [_window orderOut:nil];
        [_window close];
        [_window release];
        _window = nil;
    }
    _line1 = nil;
    _line2 = nil;
    _snippet = nil;
    _bar = nil;
    _percent = nil;
    [_line2Fmt release];
    _line2Fmt = nil;
    [_shownAt release];
    _shownAt = nil;
    _visible = NO;
}

@end

static RTMWaitPopup *g_wait_popup = nil;

void Vulkan_WaitPopupArm(const char *title, const char *line1,
                         const char *line2_fmt, const char *snippet) {
    @autoreleasepool {
        if (!g_wait_popup) g_wait_popup = [[RTMWaitPopup alloc] init];
        [g_wait_popup
            armTitle:(title ? [NSString stringWithUTF8String:title] : @"")
              line1:(line1 ? [NSString stringWithUTF8String:line1] : @"")
           line2Fmt:(line2_fmt ? [NSString stringWithUTF8String:line2_fmt] : @"")
            snippet:(snippet ? [NSString stringWithUTF8String:snippet] : @"")];
    }
}

void Vulkan_WaitPopupShow(void) {
    if (g_wait_popup) [g_wait_popup show];
}

void Vulkan_WaitPopupPump(double seconds) {
    if (g_wait_popup) [g_wait_popup pump:seconds];
}

void Vulkan_WaitPopupSetProgress(double percent) {
    if (g_wait_popup) [g_wait_popup setProgress:percent];
}

void Vulkan_WaitPopupDestroy(void) {
    if (g_wait_popup) [g_wait_popup destroy];
}

// Show/hide the window after a hidden Vulkan_InitEx.  The preview builds its
// window hidden (so offline work never pops up), then calls this through
// MLWindow.set_visible(True).  A hidden 1920x1080 window is larger than most
// screens, so fit it to the screen while preserving the scene's aspect ratio.
// When a control bar is coming (Vulkan_SetPreviewBarReserve), also keep room
// for it and for the auto-hiding Dock underneath, so the bar is never covered.
void Vulkan_SetWindowVisible(int visible) {
    if (!g_window) return;
    if (!visible) {
        [g_window orderOut:nil];
        g_init_hidden = 1;
        return;
    }

    int was_hidden = g_init_hidden;
    g_init_hidden = 0;
    if (was_hidden) {
        NSScreen *screen = [g_window screen];
        if (!screen) screen = [NSScreen mainScreen];
        NSRect vis = [screen visibleFrame];

        // Space below the video: the bar itself plus a margin that keeps its
        // scrubber clear of the Dock's auto-reveal strip.
        CGFloat bottom = 0.0;
        if (g_preview_bar_reserved) {
            CGFloat barH = g_preview_bar ? [g_preview_bar frameHeight] : 0.0;
            if (barH < 1.0) barH = RTM_BAR_HEIGHT + RTM_BAR_TITLE;
            bottom = RTM_BAR_BOTTOM_MARGIN + barH + RTM_BAR_GAP;
        }
        CGFloat titleH = NSHeight([g_window frame]) -
                         NSHeight([[g_window contentView] bounds]);
        if (titleH < 0.0) titleH = 0.0;

        CGFloat maxH = vis.size.height - bottom - titleH;
        CGFloat maxW = vis.size.width;
        CGFloat ar = g_aspect_ratio > 0 ? g_aspect_ratio : (16.0 / 9.0);
        if (maxH < 120.0) maxH = 120.0;
        CGFloat cw = [[g_window contentView] bounds].size.width;
        CGFloat ch = [[g_window contentView] bounds].size.height;
        if (cw <= 0 || ch <= 0) { ch = maxH; cw = ch * ar; }
        if (cw > maxW || ch > maxH) {
            ch = maxH;
            cw = ch * ar;
            if (cw > maxW) { cw = maxW; ch = cw / ar; }
        }
        if (cw < 16.0) cw = 16.0;
        if (ch < 16.0) ch = 16.0;
        [g_window setContentSize:NSMakeSize(cw, ch)];
        CGFloat x = vis.origin.x + (vis.size.width - cw) / 2.0;
        // With a bar the video is anchored just above it; without one, keep
        // the old vertically centred placement.
        CGFloat y = bottom > 0.0
            ? vis.origin.y + bottom
            : vis.origin.y + (vis.size.height - ch - titleH) / 2.0;
        [g_window setFrameOrigin:NSMakePoint(floor(x), floor(y))];
    }
    [g_window makeKeyAndOrderFront:nil];
    [NSApp activateIgnoringOtherApps:YES];
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
        MacBar_Tick();
    }
    if (g_should_close) return 0;

    if (g_window && g_view && g_layer) {
        // Keep the layer's drawable size glued to the view; recreate the
        // swapchain whenever the physical size actually changed.  Re-assert
        // contentsScale every tick — AppKit can reset it if the window moves
        // to a display with a different backing scale.
        NSRect vb = [g_view bounds];
        int dw, dh;
        if (g_capture_w > 0 && g_capture_h > 0) {
            // Recording: pin the drawable to the output size.  The window is
            // still the same rectangle on screen; the compositor scales the
            // (now exactly 1920x1080) content up to the Retina backing store.
            dw = g_capture_w;
            dh = g_capture_h;
            g_layer.contentsScale =
                (vb.size.width > 0) ? (double)dw / vb.size.width : 1.0;
        } else {
            // Re-assert contentsScale every tick — AppKit can reset it if the
            // window moves to a display with a different backing scale.
            g_layer.contentsScale = g_init_hidden ? 1.0 : [g_window backingScaleFactor];
            if (g_layer.contentsScale < 1.0) g_layer.contentsScale = 1.0;
            dw = (int)(vb.size.width * g_layer.contentsScale + 0.5);
            dh = (int)(vb.size.height * g_layer.contentsScale + 0.5);
        }
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
            g_points, g_point_count,
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
    Vulkan_WaitPopupDestroy();
    Vulkan_DestroyPreviewBar();
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

// Textured quad — copied verbatim from platform.c (pure bookkeeping: pool
// checks, texture upload, draw-cmd append; no Win32 calls, so it ports as-is).
void AddImageQuad(unsigned long long token, unsigned long long digest, const unsigned char *rgba, int w, int h, const float *xy8, float opacity) {
    if (g_image_quad_count >= MAX_IMAGE_QUADS || g_draw_cmd_count >= MAX_DRAW_CMDS) return;
    if (rgba == NULL || xy8 == NULL || w <= 0 || h <= 0) return;
    if (Tex_Ensure(token, digest, rgba, w, h) < 0) return;         // upload failed / table full
    ImageQuad *q = &g_image_quads[g_image_quad_count];
    q->token = token;
    q->opacity = opacity;
    for (int i = 0; i < 8; i++) q->xy[i] = xy8[i];
    g_draw_cmds[g_draw_cmd_count++] = (DrawCmd){ CMD_IMAGE, g_image_quad_count };
    g_image_quad_count++;
}

#define RESET_POOL(type, pool, count, cmd, ...) count = 0;

void ClearShapes(void) {
    FOR_EACH_SHAPE(RESET_POOL)
    g_polygon_count = 0;
    g_image_quad_count = 0;
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

// ── Raw readback (mirrors platform.c's exports) ─────────────────────────
// The Windows main line added these after the original port: the 2.0 frame
// server and the record pipe call them unconditionally.  They ride the same
// two-phase machinery as SaveScreenshot above -- arm before the tick, the
// frame's own command buffer copies before present, then wait on the copy
// frame's fence and read the mapped staging buffer.

int Vulkan_GetReadbackSize(int *w, int *h) {
    if (!g_is_ready || !g_swapchain) return 0;
    if (w) *w = (int)g_swapchain_ext.width;
    if (h) *h = (int)g_swapchain_ext.height;
    return 1;
}

int Vulkan_RequestReadback(void) {
    if (!g_is_ready || !g_swapchain) return -1;
    int w = (int)g_swapchain_ext.width;
    int h = (int)g_swapchain_ext.height;
    if (w <= 0 || h <= 0) return -1;
    g_readback_requested = 1;  // next drawn frame copies before present
    return 0;                  // slot 0: the single mac staging buffer
}

// Pin (or release) the drawable size used while recording.  w/h == 0 restores
// the window's normal backing scale on the next tick.  The swapchain is
// rebuilt synchronously so the first armed frame after this call already has
// the requested extent: a lazy rebuild inside the next tick would clear
// g_readback_requested and silently lose that frame from the recording.
int Vulkan_SetDrawableSize(int w, int h) {
    if (!g_is_ready || !g_layer || !g_view) return 0;
    if (w <= 0 || h <= 0) {
        g_capture_w = 0;
        g_capture_h = 0;
        return 1;
    }
    NSRect vb = [g_view bounds];
    if (vb.size.width <= 0 || vb.size.height <= 0) return 0;
    g_capture_w = w;
    g_capture_h = h;
    g_layer.contentsScale = (double)w / vb.size.width;
    g_layer.drawableSize = CGSizeMake(w, h);
    RecreateSwapchain();
    return 1;
}

int SaveScreenshotRaw(unsigned char *out, int out_cap, int *out_size) {
    if (!g_is_ready || !g_swapchain || !out) return 0;
    if (g_readback_buf == VK_NULL_HANDLE) return 0;
    int w = (int)g_swapchain_ext.width;
    int h = (int)g_swapchain_ext.height;
    if (w <= 0 || h <= 0) return 0;

    int rowBytes = ((w * 3 + 3) & ~3);
    VkDeviceSize need = (VkDeviceSize)rowBytes * (VkDeviceSize)h;
    if (out_size) *out_size = (int)need;    // also the "retry with this" hint
    if (out_cap <= 0 || (VkDeviceSize)out_cap < need) return 0;

    unsigned char *bgr = NULL;
    int rw = 0, rh = 0;
    if (!ReadbackFrame(&bgr, &rw, &rh)) {
        g_readback_requested = 1;
        return 0;
    }
    // ReadbackFrame's copy and the extent it measured are a matched pair
    // (a resize clears available and is observed inside the guard), so the
    // current-extent size is exactly what it handed back.
    memcpy(out, bgr, (size_t)need);
    free(bgr);
    if (out_size) *out_size = (int)need;
    return 1;
}

int SaveScreenshotRawBGRA(unsigned char *out, int out_cap, int *out_size) {
    if (!g_is_ready || !g_swapchain || !out) return 0;
    if (g_readback_buf == VK_NULL_HANDLE) return 0;
    int w = (int)g_swapchain_ext.width;
    int h = (int)g_swapchain_ext.height;
    if (w <= 0 || h <= 0) return 0;

    VkDeviceSize need = (VkDeviceSize)w * (VkDeviceSize)h * 4;
    if (out_size) *out_size = (int)need;    // also the "retry with this" hint
    if (out_cap <= 0 || (VkDeviceSize)out_cap < need) return 0;

    // Same guarded section as ReadbackFrame, but no colour conversion: one
    // bulk memcpy out of the mapped staging buffer (raw BGRA, tight-packed).
    __atomic_store_n(&g_readback_busy, 1, __ATOMIC_SEQ_CST);
    if (!__atomic_load_n(&g_readback_available, __ATOMIC_SEQ_CST)) {
        __atomic_store_n(&g_readback_busy, 0, __ATOMIC_SEQ_CST);
        g_readback_requested = 1;
        return 0;
    }
    vkWaitForFences(g_dev, 1, &g_in_flight_fences[g_readback_fence_idx],
                    VK_TRUE, UINT64_MAX);
    __atomic_store_n(&g_readback_available, 0, __ATOMIC_SEQ_CST);
    memcpy(out, g_readback_map, (size_t)need);
    __atomic_store_n(&g_readback_busy, 0, __ATOMIC_SEQ_CST);
    if (out_size) *out_size = (int)need;
    return 1;
}
