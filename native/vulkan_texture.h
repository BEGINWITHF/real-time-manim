#ifndef VULKAN_TEXTURE_H
#define VULKAN_TEXTURE_H

#include "vulkan_render.h"

// Quads submitted for this frame (filled by AddImageQuad in platform.c).
extern ImageQuad g_image_quads[];
extern int g_image_quad_count;

// Sampling pipeline for textured quads (ImageMobject pixels, rasterised camera
// frames).  Everything solid-colour goes through the original pipeline in
// vulkan_init.c; this one draws with a combined image sampler.
//
// Layout: the Python side uploads pixel data as RGBA8, native caches it under a
// 64-bit token, and each frame the caller submits quads referencing that token.
// Quad corners are window pixels in TL, TR, BR, BL order (matching the texture
// coordinates), and quad opacity folds into the sampled alpha.

// One textured quad to draw, plus how many solid-colour vertices were queued
// before it -- that is what keeps painter's order across the two pipelines.
typedef struct {
    unsigned int solid_count;
    int quad;
} TexDrawItem;

void Tex_CreateResources(void);
void Tex_DestroyResources(void);

// Per-frame lifecycle, called from Render_DrawScene.
void Tex_BeginFrame(void);
void Tex_EndFrame(void);

// Append the six vertices of quad ``idx`` (called from the command loop).
void BuildVerticesFromImageQuad(int idx);

// Record the frame's textured quads, interleaved with the solid geometry that
// preceded each of them.  ``solid_vertex_count`` is the frame's total.
void Tex_RecordInterleaved(VkCommandBuffer cmd_buf, uint32_t solid_vertex_count);

// How many textured quads this frame queued (0 means the fast path applies).
uint32_t Tex_ItemCount(void);

// Upload ``rgba`` (w*h*4 bytes) into ``token``'s slot.  ``digest`` hashes the
// pixels: an unchanged digest skips the upload entirely, a changed one refreshes
// the slot in place.  Returns the texture slot, or -1 when the table is full or
// the upload failed.
int Tex_Ensure(unsigned long long token, unsigned long long digest,
               const unsigned char *rgba, int w, int h);

#endif
