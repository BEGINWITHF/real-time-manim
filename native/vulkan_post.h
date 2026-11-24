#ifndef VULKAN_POST_H
#define VULKAN_POST_H

#include <stdint.h>
#include <vulkan/vulkan.h>

/* Offscreen bloom + tonemap.  The scene is rendered exactly as without post;
   when enabled, Post_Record copies the swapchain image into a sampleable
   texture, builds a half-resolution bloom chain and composites scene+bloom
   back into the swapchain in the same command buffer. */

int Post_Init(void);
void Post_Cleanup(void);

/* enabled: 0/1.  threshold/knee shape the bright pass; strength scales the
   bloom add; exposure multiplies before the curve; radius widens the blur;
   tonemap: 0 none, 1 aces, 2 reinhard. */
void Post_Set(int enabled, float threshold, float knee, float strength,
              float exposure, float radius, int tonemap);

int Post_IsEnabled(void);

/* Called after the scene render pass, before readback/present. */
void Post_Record(VkCommandBuffer cmd, uint32_t img_idx);

#endif
