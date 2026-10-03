#ifndef PLATFORM_H
#define PLATFORM_H

#ifdef __cplusplus
extern "C" {
#endif

__declspec(dllexport) int Vulkan_Init(int w, int h);
// Same as Vulkan_Init, but the window is created WITHOUT being shown, so
// offline work (frame export, fast record) never pops a window up.  Use
// Vulkan_SetWindowVisible(1) later to reveal it.
__declspec(dllexport) int Vulkan_InitEx(int w, int h, int hidden);
// Show/hide the window after creation (SW_SHOW / SW_HIDE).
__declspec(dllexport) void Vulkan_SetWindowVisible(int visible);
__declspec(dllexport) int Vulkan_Tick(void);
// Arm the next drawn frame to copy itself into the readback staging buffer
// (before present, while the image is still ours).  Call before the tick that
// draws the frame you want; then SaveScreenshot/SaveScreenshotRaw can read it.
__declspec(dllexport) void Vulkan_RequestReadback(void);
__declspec(dllexport) void Vulkan_Shutdown(void);

__declspec(dllexport) void AddRect(float x, float y, float hw, float hh, float rot, int r, int g, int b, int border_r, int border_g, int border_b, float border_width, float stroke_progress, float alpha);
__declspec(dllexport) void AddCircle(float x, float y, float radius, int r, int g, int b, int border_r, int border_g, int border_b, float border_width, float stroke_progress, float alpha);
__declspec(dllexport) void AddLine(float x1, float y1, float x2, float y2, int width, int r, int g, int b, float alpha);
__declspec(dllexport) void AddEllipse(float x, float y, float rx, float ry, int r, int g, int b, int border_r, int border_g, int border_b, float border_width, float stroke_progress, float alpha);
__declspec(dllexport) void AddPolygon(float x, float y, int r, int g, int b, int border_r, int border_g, int border_b, float border_width, int vert_count, const float* verts, float stroke_progress, float alpha, int close_path);
__declspec(dllexport) void AddDashedLine(float x1, float y1, float x2, float y2, int width, int r, int g, int b, float dash_length, float gap_length, float alpha);
__declspec(dllexport) void AddArc(float x, float y, float radius, float start_angle, float angle, int r, int g, int b, float stroke_width, float alpha);
__declspec(dllexport) void AddPoint(float x, float y, int r, int g, int b, float alpha, float radius);
__declspec(dllexport) void AddText(float x, float y, int r, int g, int b, float font_size, float opacity, const char* text, float alpha);
__declspec(dllexport) int Text_LoadFont(const unsigned char *data, int data_len);
__declspec(dllexport) void AddBezierPath(const float *points, int num_points, int sr, int sg, int sb, float stroke_width, int fr, int fg, int fb, float fill_opacity, float progress, int show_stroke, int show_fill, float alpha);
// Textured quad: ``rgba`` (w*h*4 bytes) is uploaded once under ``token`` and
// reused for later frames; ``xy8`` holds the four corners in window pixels, in
// top-left, top-right, bottom-right, bottom-left order.
__declspec(dllexport) void AddImageQuad(unsigned long long token, unsigned long long digest, const unsigned char *rgba, int w, int h, const float *xy8, float opacity);

// Background colour used to clear the frame (linear RGB 0..1); scenes with a
// custom `camera.background_color` publish theirs each frame.
__declspec(dllexport) void SetBackgroundColor(float r, float g, float b);
__declspec(dllexport) void ClearShapes(void);
__declspec(dllexport) int SaveScreenshot(const char *path);

#ifdef __cplusplus
}
#endif

#endif