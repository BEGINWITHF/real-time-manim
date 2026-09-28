#ifndef VULKAN_CORE_H
#define VULKAN_CORE_H
#include "vulkan_render.h"
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <math.h>
#include <stdbool.h>

extern VkInstance g_inst;
extern VkPhysicalDevice g_phys_dev;
extern VkDevice g_dev;
extern VkQueue g_gfx_queue;
extern VkQueue g_present_queue;
extern VkSurfaceKHR g_surface;
extern VkSwapchainKHR g_swapchain;
extern VkFormat g_swapchain_fmt;
extern VkExtent2D g_swapchain_ext;
extern VkImage *g_swapchain_imgs;
extern VkImageView *g_swapchain_img_views;
extern uint32_t g_swapchain_img_count;
extern VkRenderPass g_render_pass;
extern VkFramebuffer *g_framebuffers;
extern VkPipelineLayout g_pipeline_layout;
extern VkPipeline g_pipeline;
extern VkCommandPool g_cmd_pool;
extern VkCommandBuffer *g_cmd_bufs;
extern uint32_t g_cmd_buf_count;
extern VkSemaphore *g_img_avail_sems;
extern VkSemaphore *g_render_done_sems;
extern VkFence *g_in_flight_fences;
extern VkBuffer g_vert_buf;
extern VkDeviceMemory g_vert_buf_mem;
#ifdef _WIN32
extern HWND g_hwnd;
extern HINSTANCE g_hinst;
#else
extern void *g_metal_layer;
extern int g_readback_requested;
extern int g_readback_available;
extern uint32_t g_readback_fence_idx;
extern VkBuffer g_readback_buf;
extern VkDeviceMemory g_readback_mem;
extern void *g_readback_map;
#endif
extern bool g_is_ready;
extern uint32_t g_current_frame;
extern uint32_t g_last_img_idx;
extern bool g_framebuffer_resized;

VkShaderModule CreateShaderModule(const uint32_t *code, size_t size);

uint32_t FindMemoryType(uint32_t type_filter, VkMemoryPropertyFlags props);

void CreateBuffer(VkDeviceSize size, VkBufferUsageFlags usage, 
                  VkMemoryPropertyFlags props, VkBuffer *buf, VkDeviceMemory *mem);

void RecordCommandBuffer(VkCommandBuffer cmd_buf, uint32_t img_idx,
                         uint32_t vertex_count);

void RecreateSwapchain(void);
void CleanupSwapchain(void);
void CreateSwapchain(void);
void CreateImageViews(void);
void CreateFramebuffers(void);
void update_vertex_buffer(const void *data, VkDeviceSize size);

int Render_DrawFrame(uint32_t vertex_count);

// Called by the renderer from inside the frame's command buffer (after the
// render pass, before present) to perform a requested readback copy -- the
// image is still ours at that point, so the pixels are well defined.  Returns 1
// when it copied.  Implemented per platform (platform.c / platform_mac.m).
int Platform_RecordReadbackCopy(VkCommandBuffer cmd, uint32_t img_idx,
                                uint32_t frame_idx);

#endif