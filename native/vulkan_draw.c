#include "vulkan_core.h"
#include "vulkan_render.h"
#include "vulkan_texture.h"
#include "draw_common.h"

#ifdef __APPLE__
// Set by RecordCommandBuffer when it records a readback copy this frame;
// consumed by Render_DrawFrame at submit time (mac-only, two-phase readback).
static int g_readback_copied = 0;
#endif

// Cleared background colour, linear RGB 0..1.  manim lets a scene override it
// (`self.camera.background_color`), so it is published per frame from Python
// instead of being hard-coded -- measured: the gallery logo scene's light grey
// background came out black (CE luma 220 vs RTM 9.5).
float g_clear_rgb[3] = {0.0f, 0.0f, 0.0f};

void Render_SetBackgroundColor(float r, float g, float b) {
    g_clear_rgb[0] = r < 0.0f ? 0.0f : (r > 1.0f ? 1.0f : r);
    g_clear_rgb[1] = g < 0.0f ? 0.0f : (g > 1.0f ? 1.0f : g);
    g_clear_rgb[2] = b < 0.0f ? 0.0f : (b > 1.0f ? 1.0f : b);
}

float g_vertices[MAX_VERTICES * 6];
uint32_t g_vertex_count = 0;

void BuildVerticesFromRects(const Rect *rects, int count);
void BuildVerticesFromCircles(const Circle *circles, int count);
void BuildVerticesFromLines(const LineObj *lines, int count);
void BuildVerticesFromEllipses(const EllipseObj *ellipses, int count);
void BuildVerticesFromPolygons(const PolygonObj *polygons, int count);
void BuildVerticesFromDashedLines(const DashedLineObj *lines, int count);
void BuildVerticesFromArcs(const ArcObj *arcs, int count);
void BuildVerticesFromPoints(const PointObj *points, int count);
void BuildVerticesFromTexts(const TextObj *texts, int count);
void BuildVerticesFromBezierPathAt(int i);
void BuildVerticesFromLineStripAt(int si);
void ResetBezierPaths(void);
void ResetLineStrips(void);

void Render_DrawScene(const Rect* rects, int rect_count,
                      const Circle* circles, int circle_count,
                      const LineObj* lines, int line_count,
                      const EllipseObj* ellipses, int ellipse_count,
                      const PolygonObj* polygons, int polygon_count,
                      const DashedLineObj* dashed_lines, int dashed_line_count,
                      const ArcObj* arcs, int arc_count,
                      const PointObj* points, int point_count,
                      const TextObj* texts, int text_count,
                      const DrawCmd* cmds, int cmd_count) {

    g_vertex_count = 0;
    Tex_BeginFrame();

    for (int i = 0; i < cmd_count; i++) {
        int idx = cmds[i].index;
        switch (cmds[i].type) {
            case CMD_RECT:
                if (idx < rect_count) BuildVerticesFromRects(&rects[idx], 1);
                break;
            case CMD_CIRCLE:
                if (idx < circle_count) BuildVerticesFromCircles(&circles[idx], 1);
                break;
            case CMD_LINE:
                if (idx < line_count) BuildVerticesFromLines(&lines[idx], 1);
                break;
            case CMD_ELLIPSE:
                if (idx < ellipse_count) BuildVerticesFromEllipses(&ellipses[idx], 1);
                break;
            case CMD_POLYGON:
                if (idx < polygon_count) BuildVerticesFromPolygons(&polygons[idx], 1);
                break;
            case CMD_DASHED_LINE:
                if (idx < dashed_line_count) BuildVerticesFromDashedLines(&dashed_lines[idx], 1);
                break;
            case CMD_ARC:
                if (idx < arc_count) BuildVerticesFromArcs(&arcs[idx], 1);
                break;
            case CMD_POINT:
                if (idx < point_count) BuildVerticesFromPoints(&points[idx], 1);
                break;
            case CMD_TEXT:
                if (idx < text_count) BuildVerticesFromTexts(&texts[idx], 1);
                break;
            case CMD_IMAGE:
                BuildVerticesFromImageQuad(idx);
                break;
            case CMD_BEZIER:
                BuildVerticesFromBezierPathAt(idx);
                break;
            case CMD_LINE_STRIP:
                BuildVerticesFromLineStripAt(idx);
                break;
        }
    }

    /* Everything above replayed in submission order; drop whatever the
       command queue could not hold instead of drawing it a frame late. */
    ResetBezierPaths();
    ResetLineStrips();
    Tex_EndFrame();

    if (g_vertex_count > 0) {
        update_vertex_buffer(g_vertices, g_vertex_count * 6 * sizeof(float));
    }
}

void RecordCommandBuffer(VkCommandBuffer cmd_buf, uint32_t img_idx,
                         uint32_t vertex_count) {
    VkCommandBufferBeginInfo begin_info = {0};
    begin_info.sType = VK_STRUCTURE_TYPE_COMMAND_BUFFER_BEGIN_INFO;

    vkBeginCommandBuffer(cmd_buf, &begin_info);

    VkClearValue clear_color = {{{g_clear_rgb[0], g_clear_rgb[1], g_clear_rgb[2], 1.0f}}};
    VkRenderPassBeginInfo render_pass_info = {0};
    render_pass_info.sType = VK_STRUCTURE_TYPE_RENDER_PASS_BEGIN_INFO;
    render_pass_info.renderPass = g_render_pass;
    render_pass_info.framebuffer = g_framebuffers[img_idx];
    render_pass_info.renderArea.offset.x = 0;
    render_pass_info.renderArea.offset.y = 0;
    render_pass_info.renderArea.extent = g_swapchain_ext;
    render_pass_info.clearValueCount = 1;
    render_pass_info.pClearValues = &clear_color;

    vkCmdBeginRenderPass(cmd_buf, &render_pass_info, VK_SUBPASS_CONTENTS_INLINE);

    vkCmdBindPipeline(cmd_buf, VK_PIPELINE_BIND_POINT_GRAPHICS, g_pipeline);

    VkViewport vp = {0, 0, (float)g_swapchain_ext.width, (float)g_swapchain_ext.height, 0, 1};
    vkCmdSetViewport(cmd_buf, 0, 1, &vp);

    VkRect2D sc = {{0, 0}, g_swapchain_ext};
    vkCmdSetScissor(cmd_buf, 0, 1, &sc);

    VkBuffer vertex_buffers[] = { g_vert_buf };
    VkDeviceSize offsets[] = { 0 };
    vkCmdBindVertexBuffers(cmd_buf, 0, 1, vertex_buffers, offsets);

    if (Tex_ItemCount() > 0) {
        Tex_RecordInterleaved(cmd_buf, vertex_count);
    } else if (vertex_count > 0) {
        vkCmdDraw(cmd_buf, vertex_count, 1, 0, 0);
    }

    vkCmdEndRenderPass(cmd_buf);

#ifdef __APPLE__
    // MoltenVK cannot read a swapchain image after it has been presented
    // (the CAMetalLayer drawable is recycled).  When a readback is requested,
    // copy the frame into the staging buffer INSIDE this command buffer,
    // before present.  The Python side drives this with a two-phase API:
    // SaveScreenshot arms the request, the next frame performs the copy.
    if (__atomic_load_n(&g_readback_requested, __ATOMIC_SEQ_CST) && g_readback_buf != VK_NULL_HANDLE) {
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
        b.srcAccessMask = VK_ACCESS_COLOR_ATTACHMENT_WRITE_BIT;
        b.dstAccessMask = VK_ACCESS_TRANSFER_READ_BIT;
        vkCmdPipelineBarrier(cmd_buf,
            VK_PIPELINE_STAGE_COLOR_ATTACHMENT_OUTPUT_BIT, VK_PIPELINE_STAGE_TRANSFER_BIT, 0,
            0, NULL, 0, NULL, 1, &b);

        VkBufferImageCopy region = {0};
        region.imageSubresource.aspectMask = VK_IMAGE_ASPECT_COLOR_BIT;
        region.imageSubresource.layerCount = 1;
        region.imageExtent = (VkExtent3D){ g_swapchain_ext.width, g_swapchain_ext.height, 1 };
        vkCmdCopyImageToBuffer(cmd_buf, g_swapchain_imgs[img_idx],
            VK_IMAGE_LAYOUT_TRANSFER_SRC_OPTIMAL, g_readback_buf, 1, &region);

        VkImageMemoryBarrier b2 = b;
        b2.oldLayout = VK_IMAGE_LAYOUT_TRANSFER_SRC_OPTIMAL;
        b2.newLayout = VK_IMAGE_LAYOUT_PRESENT_SRC_KHR;
        b2.srcAccessMask = VK_ACCESS_TRANSFER_READ_BIT;
        b2.dstAccessMask = VK_ACCESS_MEMORY_READ_BIT;
        vkCmdPipelineBarrier(cmd_buf,
            VK_PIPELINE_STAGE_TRANSFER_BIT, VK_PIPELINE_STAGE_BOTTOM_OF_PIPE_BIT, 0,
            0, NULL, 0, NULL, 1, &b2);

        __atomic_store_n(&g_readback_requested, 0, __ATOMIC_SEQ_CST);
        g_readback_copied = 1;
    }
#endif

#ifdef _WIN32
    // Windows readback: copy the image into the staging buffer inside this
    // command buffer, before present -- afterwards the presentation engine owns
    // the image and reading it gives undefined (observed: stale/black) pixels.
    Platform_RecordReadbackCopy(cmd_buf, img_idx, g_current_frame);
#endif

    vkEndCommandBuffer(cmd_buf);
}

int Render_DrawFrame(uint32_t vertex_count) {
    if (!g_is_ready) return 0;

    vkWaitForFences(g_dev, 1, &g_in_flight_fences[g_current_frame], VK_TRUE, UINT64_MAX);
    vkResetFences(g_dev, 1, &g_in_flight_fences[g_current_frame]);

    uint32_t img_idx;
#ifdef _WIN32
    vkAcquireNextImageKHR(g_dev, g_swapchain, UINT64_MAX,
                          g_img_avail_sems[g_current_frame], VK_NULL_HANDLE, &img_idx);
#else
    VkResult ar = vkAcquireNextImageKHR(g_dev, g_swapchain, UINT64_MAX,
                          g_img_avail_sems[g_current_frame], VK_NULL_HANDLE, &img_idx);
    if (ar != VK_SUCCESS && ar != VK_SUBOPTIMAL_KHR) {
        // Window is mid-resize: the next Vulkan_Tick size check rebuilds the
        // swapchain.  Skip this frame instead of submitting stale geometry.
        if (ar == VK_ERROR_OUT_OF_DATE_KHR) g_framebuffer_resized = true;
        return 0;
    }
#endif
    g_last_img_idx = img_idx;

    vkResetCommandBuffer(g_cmd_bufs[g_current_frame], 0);
    RecordCommandBuffer(g_cmd_bufs[g_current_frame], img_idx, vertex_count);

#ifdef __APPLE__
    if (g_readback_copied) {
        g_readback_copied = 0;
        g_readback_fence_idx = g_current_frame;
        // seq-cst store: acts as a release barrier, so the fence_idx write
        // above is visible to the worker that acquires this flag.
        __atomic_store_n(&g_readback_available, 1, __ATOMIC_SEQ_CST);
    }
#endif

    VkSubmitInfo submit_info = {0};
    submit_info.sType = VK_STRUCTURE_TYPE_SUBMIT_INFO;

    VkSemaphore wait_sems[] = { g_img_avail_sems[g_current_frame] };
    VkPipelineStageFlags wait_stages[] = { VK_PIPELINE_STAGE_COLOR_ATTACHMENT_OUTPUT_BIT };
    submit_info.waitSemaphoreCount = 1;
    submit_info.pWaitSemaphores = wait_sems;
    submit_info.pWaitDstStageMask = wait_stages;
    submit_info.commandBufferCount = 1;
    submit_info.pCommandBuffers = &g_cmd_bufs[g_current_frame];

    VkSemaphore signal_sems[] = { g_render_done_sems[g_current_frame] };
    submit_info.signalSemaphoreCount = 1;
    submit_info.pSignalSemaphores = signal_sems;

    vkQueueSubmit(g_gfx_queue, 1, &submit_info, g_in_flight_fences[g_current_frame]);

    VkPresentInfoKHR present_info = {0};
    present_info.sType = VK_STRUCTURE_TYPE_PRESENT_INFO_KHR;
    present_info.waitSemaphoreCount = 1;
    present_info.pWaitSemaphores = signal_sems;
    present_info.swapchainCount = 1;
    present_info.pSwapchains = &g_swapchain;
    present_info.pImageIndices = &img_idx;

    vkQueuePresentKHR(g_present_queue, &present_info);

    g_current_frame = (g_current_frame + 1) % g_swapchain_img_count;

    return 1;
}
