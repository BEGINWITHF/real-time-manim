/* Offscreen bloom + tonemap post-processing.
 *
 * The scene render pass is untouched: it resolves MSAA directly into the
 * swapchain image, exactly as before.  When post is enabled, the frame's
 * command buffer then:
 *
 *   1. copies the swapchain image into a sampleable texture,
 *   2. runs a soft-knee bright pass at half resolution,
 *   3. blurs it horizontally and vertically (separable Gaussian),
 *   4. composites scene + bloom, exposure and an optional tone curve back
 *      into the swapchain.
 *
 * Everything happens inside the same command buffer, before screenshot
 * readback and present, so recorded video and screenshots include the effect.
 * With post disabled (the default) no post resources are even recorded.
 */
#include "vulkan_core.h"
#include "vulkan_post.h"
#include "post_shaders.h"

typedef struct {
    float p0[4];       /* threshold, knee, strength, exposure */
    float p1[4];       /* tonemap, radius, unused, unused     */
} PostPush;

typedef struct {
    int enabled;
    float threshold;
    float knee;
    float strength;
    float exposure;
    float radius;
    int tonemap;
} PostParams;

static PostParams g_post = {
    0,          /* enabled   */
    0.82f,      /* threshold */
    0.12f,      /* knee      */
    0.60f,      /* strength  */
    1.00f,      /* exposure  */
    1.60f,      /* radius    */
    0,          /* tonemap: none */
};

static int g_post_ready = 0;
static VkExtent2D g_post_ext;

static VkImage g_scene_copy_img = VK_NULL_HANDLE;
static VkDeviceMemory g_scene_copy_mem = VK_NULL_HANDLE;
static VkImageView g_scene_copy_view = VK_NULL_HANDLE;

static VkImage g_bloom_img[2] = { VK_NULL_HANDLE, VK_NULL_HANDLE };
static VkDeviceMemory g_bloom_mem[2] = { VK_NULL_HANDLE, VK_NULL_HANDLE };
static VkImageView g_bloom_view[2] = { VK_NULL_HANDLE, VK_NULL_HANDLE };
static VkFramebuffer g_bloom_fb[2] = { VK_NULL_HANDLE, VK_NULL_HANDLE };

static VkFramebuffer *g_present_fb = NULL;
static uint32_t g_present_fb_count = 0;

static VkSampler g_sampler = VK_NULL_HANDLE;
static VkDescriptorSetLayout g_set_layout = VK_NULL_HANDLE;
static VkDescriptorPool g_pool = VK_NULL_HANDLE;
static VkDescriptorSet g_set_scene_a = VK_NULL_HANDLE;
static VkDescriptorSet g_set_scene_b = VK_NULL_HANDLE;

static VkPipelineLayout g_post_layout = VK_NULL_HANDLE;
static VkRenderPass g_target_pass = VK_NULL_HANDLE;
static VkRenderPass g_present_pass = VK_NULL_HANDLE;
static VkPipeline g_bright_pipe = VK_NULL_HANDLE;
static VkPipeline g_blur_pipe = VK_NULL_HANDLE;
static VkPipeline g_composite_pipe = VK_NULL_HANDLE;

static float post_clamp(float v, float lo, float hi) {
    return v < lo ? lo : (v > hi ? hi : v);
}

static int post_make_image(uint32_t w, uint32_t h, VkImageUsageFlags usage,
                           VkImage *img, VkDeviceMemory *mem,
                           VkImageView *view) {
    VkImageCreateInfo ici = {0};
    ici.sType = VK_STRUCTURE_TYPE_IMAGE_CREATE_INFO;
    ici.imageType = VK_IMAGE_TYPE_2D;
    ici.format = g_swapchain_fmt;
    ici.extent = (VkExtent3D){ w, h, 1 };
    ici.mipLevels = 1;
    ici.arrayLayers = 1;
    ici.samples = VK_SAMPLE_COUNT_1_BIT;
    ici.tiling = VK_IMAGE_TILING_OPTIMAL;
    ici.usage = usage;
    ici.sharingMode = VK_SHARING_MODE_EXCLUSIVE;
    ici.initialLayout = VK_IMAGE_LAYOUT_UNDEFINED;
    if (vkCreateImage(g_dev, &ici, NULL, img) != VK_SUCCESS) return -1;

    VkMemoryRequirements mr;
    vkGetImageMemoryRequirements(g_dev, *img, &mr);
    VkMemoryAllocateInfo mai = {0};
    mai.sType = VK_STRUCTURE_TYPE_MEMORY_ALLOCATE_INFO;
    mai.allocationSize = mr.size;
    mai.memoryTypeIndex = FindMemoryType(mr.memoryTypeBits,
                                         VK_MEMORY_PROPERTY_DEVICE_LOCAL_BIT);
    if (vkAllocateMemory(g_dev, &mai, NULL, mem) != VK_SUCCESS) return -1;
    if (vkBindImageMemory(g_dev, *img, *mem, 0) != VK_SUCCESS) return -1;

    VkImageViewCreateInfo vci = {0};
    vci.sType = VK_STRUCTURE_TYPE_IMAGE_VIEW_CREATE_INFO;
    vci.image = *img;
    vci.viewType = VK_IMAGE_VIEW_TYPE_2D;
    vci.format = g_swapchain_fmt;
    vci.subresourceRange.aspectMask = VK_IMAGE_ASPECT_COLOR_BIT;
    vci.subresourceRange.levelCount = 1;
    vci.subresourceRange.layerCount = 1;
    if (vkCreateImageView(g_dev, &vci, NULL, view) != VK_SUCCESS) return -1;
    return 0;
}

static VkFramebuffer post_make_fb(VkRenderPass pass, VkImageView view,
                                  uint32_t w, uint32_t h) {
    VkFramebufferCreateInfo fci = {0};
    fci.sType = VK_STRUCTURE_TYPE_FRAMEBUFFER_CREATE_INFO;
    fci.renderPass = pass;
    fci.attachmentCount = 1;
    fci.pAttachments = &view;
    fci.width = w;
    fci.height = h;
    fci.layers = 1;
    VkFramebuffer fb = VK_NULL_HANDLE;
    if (vkCreateFramebuffer(g_dev, &fci, NULL, &fb) != VK_SUCCESS) {
        return VK_NULL_HANDLE;
    }
    return fb;
}

static VkRenderPass post_make_pass(VkImageLayout initial,
                                   VkImageLayout final_layout) {
    VkAttachmentDescription att = {0};
    att.format = g_swapchain_fmt;
    att.samples = VK_SAMPLE_COUNT_1_BIT;
    att.loadOp = VK_ATTACHMENT_LOAD_OP_DONT_CARE;
    att.storeOp = VK_ATTACHMENT_STORE_OP_STORE;
    att.stencilLoadOp = VK_ATTACHMENT_LOAD_OP_DONT_CARE;
    att.stencilStoreOp = VK_ATTACHMENT_STORE_OP_DONT_CARE;
    att.initialLayout = initial;
    att.finalLayout = final_layout;

    VkAttachmentReference ref = {0};
    ref.attachment = 0;
    ref.layout = VK_IMAGE_LAYOUT_COLOR_ATTACHMENT_OPTIMAL;

    VkSubpassDescription sub = {0};
    sub.pipelineBindPoint = VK_PIPELINE_BIND_POINT_GRAPHICS;
    sub.colorAttachmentCount = 1;
    sub.pColorAttachments = &ref;

    VkSubpassDependency dep = {0};
    dep.srcSubpass = VK_SUBPASS_EXTERNAL;
    dep.dstSubpass = 0;
    dep.srcStageMask = VK_PIPELINE_STAGE_COLOR_ATTACHMENT_OUTPUT_BIT
                     | VK_PIPELINE_STAGE_FRAGMENT_SHADER_BIT
                     | VK_PIPELINE_STAGE_TRANSFER_BIT;
    dep.srcAccessMask = VK_ACCESS_COLOR_ATTACHMENT_WRITE_BIT
                      | VK_ACCESS_SHADER_READ_BIT
                      | VK_ACCESS_TRANSFER_READ_BIT
                      | VK_ACCESS_TRANSFER_WRITE_BIT;
    dep.dstStageMask = VK_PIPELINE_STAGE_COLOR_ATTACHMENT_OUTPUT_BIT
                     | VK_PIPELINE_STAGE_FRAGMENT_SHADER_BIT;
    dep.dstAccessMask = VK_ACCESS_COLOR_ATTACHMENT_WRITE_BIT
                      | VK_ACCESS_SHADER_READ_BIT;

    VkRenderPassCreateInfo rpci = {0};
    rpci.sType = VK_STRUCTURE_TYPE_RENDER_PASS_CREATE_INFO;
    rpci.attachmentCount = 1;
    rpci.pAttachments = &att;
    rpci.subpassCount = 1;
    rpci.pSubpasses = &sub;
    rpci.dependencyCount = 1;
    rpci.pDependencies = &dep;
    VkRenderPass pass = VK_NULL_HANDLE;
    if (vkCreateRenderPass(g_dev, &rpci, NULL, &pass) != VK_SUCCESS) {
        return VK_NULL_HANDLE;
    }
    return pass;
}

static VkPipeline post_make_pipeline(VkRenderPass pass,
                                     const uint32_t *frag_spv,
                                     size_t frag_size) {
    VkShaderModule vs = CreateShaderModule(post_vert_spv,
                                           sizeof(post_vert_spv));
    VkShaderModule fs = CreateShaderModule(frag_spv, frag_size);
    if (vs == VK_NULL_HANDLE || fs == VK_NULL_HANDLE) return VK_NULL_HANDLE;

    VkPipelineShaderStageCreateInfo stages[2] = {{0}};
    stages[0].sType = VK_STRUCTURE_TYPE_PIPELINE_SHADER_STAGE_CREATE_INFO;
    stages[0].stage = VK_SHADER_STAGE_VERTEX_BIT;
    stages[0].module = vs;
    stages[0].pName = "main";
    stages[1].sType = VK_STRUCTURE_TYPE_PIPELINE_SHADER_STAGE_CREATE_INFO;
    stages[1].stage = VK_SHADER_STAGE_FRAGMENT_BIT;
    stages[1].module = fs;
    stages[1].pName = "main";

    VkPipelineVertexInputStateCreateInfo vi = {0};
    vi.sType = VK_STRUCTURE_TYPE_PIPELINE_VERTEX_INPUT_STATE_CREATE_INFO;

    VkPipelineInputAssemblyStateCreateInfo ia = {0};
    ia.sType = VK_STRUCTURE_TYPE_PIPELINE_INPUT_ASSEMBLY_STATE_CREATE_INFO;
    ia.topology = VK_PRIMITIVE_TOPOLOGY_TRIANGLE_LIST;

    VkPipelineViewportStateCreateInfo vps = {0};
    vps.sType = VK_STRUCTURE_TYPE_PIPELINE_VIEWPORT_STATE_CREATE_INFO;
    vps.viewportCount = 1;
    vps.scissorCount = 1;

    VkPipelineRasterizationStateCreateInfo rs = {0};
    rs.sType = VK_STRUCTURE_TYPE_PIPELINE_RASTERIZATION_STATE_CREATE_INFO;
    rs.polygonMode = VK_POLYGON_MODE_FILL;
    rs.cullMode = VK_CULL_MODE_NONE;
    rs.frontFace = VK_FRONT_FACE_COUNTER_CLOCKWISE;
    rs.lineWidth = 1.0f;

    VkPipelineMultisampleStateCreateInfo ms = {0};
    ms.sType = VK_STRUCTURE_TYPE_PIPELINE_MULTISAMPLE_STATE_CREATE_INFO;
    ms.rasterizationSamples = VK_SAMPLE_COUNT_1_BIT;

    VkPipelineColorBlendAttachmentState cba = {0};
    cba.blendEnable = VK_FALSE;
    cba.colorWriteMask = VK_COLOR_COMPONENT_R_BIT | VK_COLOR_COMPONENT_G_BIT
                       | VK_COLOR_COMPONENT_B_BIT | VK_COLOR_COMPONENT_A_BIT;
    VkPipelineColorBlendStateCreateInfo cb = {0};
    cb.sType = VK_STRUCTURE_TYPE_PIPELINE_COLOR_BLEND_STATE_CREATE_INFO;
    cb.attachmentCount = 1;
    cb.pAttachments = &cba;

    VkDynamicState dyn_states[] = {
        VK_DYNAMIC_STATE_VIEWPORT, VK_DYNAMIC_STATE_SCISSOR
    };
    VkPipelineDynamicStateCreateInfo dyn = {0};
    dyn.sType = VK_STRUCTURE_TYPE_PIPELINE_DYNAMIC_STATE_CREATE_INFO;
    dyn.dynamicStateCount = 2;
    dyn.pDynamicStates = dyn_states;

    VkGraphicsPipelineCreateInfo pci = {0};
    pci.sType = VK_STRUCTURE_TYPE_GRAPHICS_PIPELINE_CREATE_INFO;
    pci.stageCount = 2;
    pci.pStages = stages;
    pci.pVertexInputState = &vi;
    pci.pInputAssemblyState = &ia;
    pci.pViewportState = &vps;
    pci.pRasterizationState = &rs;
    pci.pMultisampleState = &ms;
    pci.pColorBlendState = &cb;
    pci.pDynamicState = &dyn;
    pci.layout = g_post_layout;
    pci.renderPass = pass;

    VkPipeline pipe = VK_NULL_HANDLE;
    vkCreateGraphicsPipelines(g_dev, VK_NULL_HANDLE, 1, &pci, NULL, &pipe);
    vkDestroyShaderModule(g_dev, vs, NULL);
    vkDestroyShaderModule(g_dev, fs, NULL);
    return pipe;
}

static void post_write_descriptor(VkDescriptorSet set, VkImageView src) {
    VkDescriptorImageInfo scene = {0};
    scene.sampler = g_sampler;
    scene.imageView = g_scene_copy_view;
    scene.imageLayout = VK_IMAGE_LAYOUT_SHADER_READ_ONLY_OPTIMAL;

    VkDescriptorImageInfo bloom = {0};
    bloom.sampler = g_sampler;
    bloom.imageView = src;
    bloom.imageLayout = VK_IMAGE_LAYOUT_SHADER_READ_ONLY_OPTIMAL;

    VkWriteDescriptorSet writes[2] = {{0}};
    writes[0].sType = VK_STRUCTURE_TYPE_WRITE_DESCRIPTOR_SET;
    writes[0].dstSet = set;
    writes[0].dstBinding = 0;
    writes[0].descriptorCount = 1;
    writes[0].descriptorType = VK_DESCRIPTOR_TYPE_COMBINED_IMAGE_SAMPLER;
    writes[0].pImageInfo = &scene;
    writes[1].sType = VK_STRUCTURE_TYPE_WRITE_DESCRIPTOR_SET;
    writes[1].dstSet = set;
    writes[1].dstBinding = 1;
    writes[1].descriptorCount = 1;
    writes[1].descriptorType = VK_DESCRIPTOR_TYPE_COMBINED_IMAGE_SAMPLER;
    writes[1].pImageInfo = &bloom;
    vkUpdateDescriptorSets(g_dev, 2, writes, 0, NULL);
}

static int post_create_resources(void) {
    uint32_t w = g_swapchain_ext.width;
    uint32_t h = g_swapchain_ext.height;
    if (w == 0 || h == 0) return -1;
    g_post_ext = (VkExtent2D){ (w + 1) / 2, (h + 1) / 2 };

    if (post_make_image(w, h,
                        VK_IMAGE_USAGE_TRANSFER_DST_BIT
                        | VK_IMAGE_USAGE_SAMPLED_BIT,
                        &g_scene_copy_img, &g_scene_copy_mem,
                        &g_scene_copy_view) != 0) return -1;

    for (int i = 0; i < 2; i++) {
        if (post_make_image(g_post_ext.width, g_post_ext.height,
                            VK_IMAGE_USAGE_COLOR_ATTACHMENT_BIT
                            | VK_IMAGE_USAGE_SAMPLED_BIT,
                            &g_bloom_img[i], &g_bloom_mem[i],
                            &g_bloom_view[i]) != 0) return -1;
    }

    VkSamplerCreateInfo sci = {0};
    sci.sType = VK_STRUCTURE_TYPE_SAMPLER_CREATE_INFO;
    sci.magFilter = VK_FILTER_LINEAR;
    sci.minFilter = VK_FILTER_LINEAR;
    sci.mipmapMode = VK_SAMPLER_MIPMAP_MODE_NEAREST;
    sci.addressModeU = VK_SAMPLER_ADDRESS_MODE_CLAMP_TO_EDGE;
    sci.addressModeV = VK_SAMPLER_ADDRESS_MODE_CLAMP_TO_EDGE;
    sci.addressModeW = VK_SAMPLER_ADDRESS_MODE_CLAMP_TO_EDGE;
    sci.maxLod = 0.0f;
    if (vkCreateSampler(g_dev, &sci, NULL, &g_sampler) != VK_SUCCESS) {
        return -1;
    }

    VkDescriptorSetLayoutBinding bindings[2] = {{0}};
    for (int i = 0; i < 2; i++) {
        bindings[i].binding = (uint32_t)i;
        bindings[i].descriptorType =
            VK_DESCRIPTOR_TYPE_COMBINED_IMAGE_SAMPLER;
        bindings[i].descriptorCount = 1;
        bindings[i].stageFlags = VK_SHADER_STAGE_FRAGMENT_BIT;
    }
    VkDescriptorSetLayoutCreateInfo slci = {0};
    slci.sType = VK_STRUCTURE_TYPE_DESCRIPTOR_SET_LAYOUT_CREATE_INFO;
    slci.bindingCount = 2;
    slci.pBindings = bindings;
    if (vkCreateDescriptorSetLayout(g_dev, &slci, NULL, &g_set_layout)
            != VK_SUCCESS) {
        return -1;
    }

    VkDescriptorPoolSize size = {0};
    size.type = VK_DESCRIPTOR_TYPE_COMBINED_IMAGE_SAMPLER;
    size.descriptorCount = 4;
    VkDescriptorPoolCreateInfo pci = {0};
    pci.sType = VK_STRUCTURE_TYPE_DESCRIPTOR_POOL_CREATE_INFO;
    pci.maxSets = 2;
    pci.poolSizeCount = 1;
    pci.pPoolSizes = &size;
    if (vkCreateDescriptorPool(g_dev, &pci, NULL, &g_pool) != VK_SUCCESS) {
        return -1;
    }

    VkDescriptorSetLayout layouts[2] = { g_set_layout, g_set_layout };
    VkDescriptorSet sets[2] = { VK_NULL_HANDLE, VK_NULL_HANDLE };
    VkDescriptorSetAllocateInfo dsai = {0};
    dsai.sType = VK_STRUCTURE_TYPE_DESCRIPTOR_SET_ALLOCATE_INFO;
    dsai.descriptorPool = g_pool;
    dsai.descriptorSetCount = 2;
    dsai.pSetLayouts = layouts;
    if (vkAllocateDescriptorSets(g_dev, &dsai, sets) != VK_SUCCESS) {
        return -1;
    }
    g_set_scene_a = sets[0];
    g_set_scene_b = sets[1];
    post_write_descriptor(g_set_scene_a, g_bloom_view[0]);
    post_write_descriptor(g_set_scene_b, g_bloom_view[1]);

    VkPushConstantRange range = {0};
    range.stageFlags = VK_SHADER_STAGE_FRAGMENT_BIT;
    range.offset = 0;
    range.size = sizeof(PostPush);
    VkPipelineLayoutCreateInfo plci = {0};
    plci.sType = VK_STRUCTURE_TYPE_PIPELINE_LAYOUT_CREATE_INFO;
    plci.setLayoutCount = 1;
    plci.pSetLayouts = &g_set_layout;
    plci.pushConstantRangeCount = 1;
    plci.pPushConstantRanges = &range;
    if (vkCreatePipelineLayout(g_dev, &plci, NULL, &g_post_layout)
            != VK_SUCCESS) {
        return -1;
    }

    g_target_pass = post_make_pass(VK_IMAGE_LAYOUT_UNDEFINED,
                                   VK_IMAGE_LAYOUT_SHADER_READ_ONLY_OPTIMAL);
    g_present_pass = post_make_pass(VK_IMAGE_LAYOUT_COLOR_ATTACHMENT_OPTIMAL,
                                    VK_IMAGE_LAYOUT_PRESENT_SRC_KHR);
    if (g_target_pass == VK_NULL_HANDLE || g_present_pass == VK_NULL_HANDLE) {
        return -1;
    }

    g_bright_pipe = post_make_pipeline(g_target_pass, post_bright_frag_spv,
                                       sizeof(post_bright_frag_spv));
    g_blur_pipe = post_make_pipeline(g_target_pass, post_blur_frag_spv,
                                     sizeof(post_blur_frag_spv));
    g_composite_pipe = post_make_pipeline(g_present_pass,
                                          post_composite_frag_spv,
                                          sizeof(post_composite_frag_spv));
    if (g_bright_pipe == VK_NULL_HANDLE || g_blur_pipe == VK_NULL_HANDLE
            || g_composite_pipe == VK_NULL_HANDLE) {
        return -1;
    }

    g_bloom_fb[0] = post_make_fb(g_target_pass, g_bloom_view[0],
                                 g_post_ext.width, g_post_ext.height);
    g_bloom_fb[1] = post_make_fb(g_target_pass, g_bloom_view[1],
                                 g_post_ext.width, g_post_ext.height);
    if (g_bloom_fb[0] == VK_NULL_HANDLE || g_bloom_fb[1] == VK_NULL_HANDLE) {
        return -1;
    }

    g_present_fb_count = g_swapchain_img_count;
    g_present_fb = calloc(g_present_fb_count, sizeof(VkFramebuffer));
    if (g_present_fb == NULL) return -1;
    for (uint32_t i = 0; i < g_present_fb_count; i++) {
        g_present_fb[i] = post_make_fb(g_present_pass,
                                       g_swapchain_img_views[i],
                                       g_swapchain_ext.width,
                                       g_swapchain_ext.height);
        if (g_present_fb[i] == VK_NULL_HANDLE) return -1;
    }
    return 0;
}

int Post_Init(void) {
    if (g_dev == VK_NULL_HANDLE || g_swapchain == VK_NULL_HANDLE) return 0;
    Post_Cleanup();
    if (post_create_resources() != 0) {
        Post_Cleanup();
        return 0;
    }
    g_post_ready = 1;
    return 1;
}

void Post_Cleanup(void) {
    g_post_ready = 0;
    if (g_dev == VK_NULL_HANDLE) return;

    if (g_present_fb != NULL) {
        for (uint32_t i = 0; i < g_present_fb_count; i++) {
            if (g_present_fb[i] != VK_NULL_HANDLE) {
                vkDestroyFramebuffer(g_dev, g_present_fb[i], NULL);
            }
        }
        free(g_present_fb);
        g_present_fb = NULL;
    }
    g_present_fb_count = 0;

    for (int i = 0; i < 2; i++) {
        if (g_bloom_fb[i] != VK_NULL_HANDLE) {
            vkDestroyFramebuffer(g_dev, g_bloom_fb[i], NULL);
            g_bloom_fb[i] = VK_NULL_HANDLE;
        }
    }
    if (g_composite_pipe != VK_NULL_HANDLE) {
        vkDestroyPipeline(g_dev, g_composite_pipe, NULL);
        g_composite_pipe = VK_NULL_HANDLE;
    }
    if (g_blur_pipe != VK_NULL_HANDLE) {
        vkDestroyPipeline(g_dev, g_blur_pipe, NULL);
        g_blur_pipe = VK_NULL_HANDLE;
    }
    if (g_bright_pipe != VK_NULL_HANDLE) {
        vkDestroyPipeline(g_dev, g_bright_pipe, NULL);
        g_bright_pipe = VK_NULL_HANDLE;
    }
    if (g_present_pass != VK_NULL_HANDLE) {
        vkDestroyRenderPass(g_dev, g_present_pass, NULL);
        g_present_pass = VK_NULL_HANDLE;
    }
    if (g_target_pass != VK_NULL_HANDLE) {
        vkDestroyRenderPass(g_dev, g_target_pass, NULL);
        g_target_pass = VK_NULL_HANDLE;
    }
    if (g_post_layout != VK_NULL_HANDLE) {
        vkDestroyPipelineLayout(g_dev, g_post_layout, NULL);
        g_post_layout = VK_NULL_HANDLE;
    }
    if (g_pool != VK_NULL_HANDLE) {
        vkDestroyDescriptorPool(g_dev, g_pool, NULL);
        g_pool = VK_NULL_HANDLE;
        g_set_scene_a = VK_NULL_HANDLE;
        g_set_scene_b = VK_NULL_HANDLE;
    }
    if (g_set_layout != VK_NULL_HANDLE) {
        vkDestroyDescriptorSetLayout(g_dev, g_set_layout, NULL);
        g_set_layout = VK_NULL_HANDLE;
    }
    if (g_sampler != VK_NULL_HANDLE) {
        vkDestroySampler(g_dev, g_sampler, NULL);
        g_sampler = VK_NULL_HANDLE;
    }

    for (int i = 0; i < 2; i++) {
        if (g_bloom_view[i] != VK_NULL_HANDLE) {
            vkDestroyImageView(g_dev, g_bloom_view[i], NULL);
            g_bloom_view[i] = VK_NULL_HANDLE;
        }
        if (g_bloom_img[i] != VK_NULL_HANDLE) {
            vkDestroyImage(g_dev, g_bloom_img[i], NULL);
            g_bloom_img[i] = VK_NULL_HANDLE;
        }
        if (g_bloom_mem[i] != VK_NULL_HANDLE) {
            vkFreeMemory(g_dev, g_bloom_mem[i], NULL);
            g_bloom_mem[i] = VK_NULL_HANDLE;
        }
    }
    if (g_scene_copy_view != VK_NULL_HANDLE) {
        vkDestroyImageView(g_dev, g_scene_copy_view, NULL);
        g_scene_copy_view = VK_NULL_HANDLE;
    }
    if (g_scene_copy_img != VK_NULL_HANDLE) {
        vkDestroyImage(g_dev, g_scene_copy_img, NULL);
        g_scene_copy_img = VK_NULL_HANDLE;
    }
    if (g_scene_copy_mem != VK_NULL_HANDLE) {
        vkFreeMemory(g_dev, g_scene_copy_mem, NULL);
        g_scene_copy_mem = VK_NULL_HANDLE;
    }
}

void Post_Set(int enabled, float threshold, float knee, float strength,
              float exposure, float radius, int tonemap) {
    g_post.enabled = enabled ? 1 : 0;
    if (threshold >= 0.0f) g_post.threshold = post_clamp(threshold, 0.0f, 8.0f);
    if (knee >= 0.0f) g_post.knee = post_clamp(knee, 0.0f, 2.0f);
    if (strength >= 0.0f) g_post.strength = post_clamp(strength, 0.0f, 8.0f);
    if (exposure > 0.0f) g_post.exposure = post_clamp(exposure, 0.01f, 16.0f);
    if (radius >= 0.0f) g_post.radius = post_clamp(radius, 0.0f, 8.0f);
    g_post.tonemap = tonemap < 0 ? 0 : (tonemap > 2 ? 2 : tonemap);
}

int Post_IsEnabled(void) {
    return g_post_ready && g_post.enabled;
}

static void post_barrier(VkCommandBuffer cmd, VkImage image,
                         VkImageLayout old_layout, VkImageLayout new_layout,
                         VkAccessFlags src_access, VkAccessFlags dst_access,
                         VkPipelineStageFlags src_stage,
                         VkPipelineStageFlags dst_stage) {
    VkImageMemoryBarrier b = {0};
    b.sType = VK_STRUCTURE_TYPE_IMAGE_MEMORY_BARRIER;
    b.oldLayout = old_layout;
    b.newLayout = new_layout;
    b.srcQueueFamilyIndex = VK_QUEUE_FAMILY_IGNORED;
    b.dstQueueFamilyIndex = VK_QUEUE_FAMILY_IGNORED;
    b.image = image;
    b.subresourceRange.aspectMask = VK_IMAGE_ASPECT_COLOR_BIT;
    b.subresourceRange.baseMipLevel = 0;
    b.subresourceRange.levelCount = 1;
    b.subresourceRange.baseArrayLayer = 0;
    b.subresourceRange.layerCount = 1;
    b.srcAccessMask = src_access;
    b.dstAccessMask = dst_access;
    vkCmdPipelineBarrier(cmd, src_stage, dst_stage, 0, 0, NULL, 0, NULL, 1, &b);
}

static void post_begin(VkCommandBuffer cmd, VkRenderPass pass,
                       VkFramebuffer fb, uint32_t w, uint32_t h) {
    VkRenderPassBeginInfo bi = {0};
    bi.sType = VK_STRUCTURE_TYPE_RENDER_PASS_BEGIN_INFO;
    bi.renderPass = pass;
    bi.framebuffer = fb;
    bi.renderArea.offset = (VkOffset2D){0, 0};
    bi.renderArea.extent = (VkExtent2D){ w, h };
    vkCmdBeginRenderPass(cmd, &bi, VK_SUBPASS_CONTENTS_INLINE);

    VkViewport vp = {0.0f, 0.0f, (float)w, (float)h, 0.0f, 1.0f};
    vkCmdSetViewport(cmd, 0, 1, &vp);
    VkRect2D sc = {{0, 0}, { w, h }};
    vkCmdSetScissor(cmd, 0, 1, &sc);
}

static void post_draw(VkCommandBuffer cmd, VkPipeline pipe, VkDescriptorSet set,
                      const PostPush *push) {
    vkCmdBindPipeline(cmd, VK_PIPELINE_BIND_POINT_GRAPHICS, pipe);
    vkCmdBindDescriptorSets(cmd, VK_PIPELINE_BIND_POINT_GRAPHICS, g_post_layout,
                            0, 1, &set, 0, NULL);
    vkCmdPushConstants(cmd, g_post_layout, VK_SHADER_STAGE_FRAGMENT_BIT, 0,
                       sizeof(PostPush), push);
    vkCmdDraw(cmd, 3, 1, 0, 0);
}

void Post_Record(VkCommandBuffer cmd, uint32_t img_idx) {
    if (!Post_IsEnabled()) return;
    if (img_idx >= g_present_fb_count || g_present_fb[img_idx] == VK_NULL_HANDLE)
        return;

    uint32_t w = g_swapchain_ext.width;
    uint32_t h = g_swapchain_ext.height;

    /* Scene -> sampleable copy. */
    post_barrier(cmd, g_swapchain_imgs[img_idx],
                 VK_IMAGE_LAYOUT_PRESENT_SRC_KHR,
                 VK_IMAGE_LAYOUT_TRANSFER_SRC_OPTIMAL,
                 VK_ACCESS_COLOR_ATTACHMENT_WRITE_BIT,
                 VK_ACCESS_TRANSFER_READ_BIT,
                 VK_PIPELINE_STAGE_COLOR_ATTACHMENT_OUTPUT_BIT,
                 VK_PIPELINE_STAGE_TRANSFER_BIT);
    post_barrier(cmd, g_scene_copy_img,
                 VK_IMAGE_LAYOUT_UNDEFINED,
                 VK_IMAGE_LAYOUT_TRANSFER_DST_OPTIMAL,
                 0, VK_ACCESS_TRANSFER_WRITE_BIT,
                 VK_PIPELINE_STAGE_TOP_OF_PIPE_BIT,
                 VK_PIPELINE_STAGE_TRANSFER_BIT);

    VkImageCopy region = {0};
    region.srcSubresource.aspectMask = VK_IMAGE_ASPECT_COLOR_BIT;
    region.srcSubresource.layerCount = 1;
    region.dstSubresource.aspectMask = VK_IMAGE_ASPECT_COLOR_BIT;
    region.dstSubresource.layerCount = 1;
    region.extent = (VkExtent3D){ w, h, 1 };
    vkCmdCopyImage(cmd, g_swapchain_imgs[img_idx],
                   VK_IMAGE_LAYOUT_TRANSFER_SRC_OPTIMAL,
                   g_scene_copy_img, VK_IMAGE_LAYOUT_TRANSFER_DST_OPTIMAL,
                   1, &region);

    post_barrier(cmd, g_scene_copy_img,
                 VK_IMAGE_LAYOUT_TRANSFER_DST_OPTIMAL,
                 VK_IMAGE_LAYOUT_SHADER_READ_ONLY_OPTIMAL,
                 VK_ACCESS_TRANSFER_WRITE_BIT,
                 VK_ACCESS_SHADER_READ_BIT,
                 VK_PIPELINE_STAGE_TRANSFER_BIT,
                 VK_PIPELINE_STAGE_FRAGMENT_SHADER_BIT);
    post_barrier(cmd, g_swapchain_imgs[img_idx],
                 VK_IMAGE_LAYOUT_TRANSFER_SRC_OPTIMAL,
                 VK_IMAGE_LAYOUT_COLOR_ATTACHMENT_OPTIMAL,
                 VK_ACCESS_TRANSFER_READ_BIT,
                 VK_ACCESS_COLOR_ATTACHMENT_WRITE_BIT,
                 VK_PIPELINE_STAGE_TRANSFER_BIT,
                 VK_PIPELINE_STAGE_COLOR_ATTACHMENT_OUTPUT_BIT);

    PostPush push = {{0}};
    push.p0[0] = g_post.threshold;
    push.p0[1] = g_post.knee;
    push.p0[2] = g_post.strength;
    push.p0[3] = g_post.exposure;
    push.p1[0] = (float)g_post.tonemap;
    push.p1[1] = g_post.radius;

    /* Bright pass: scene -> bloom A (half resolution). */
    post_begin(cmd, g_target_pass, g_bloom_fb[0],
               g_post_ext.width, g_post_ext.height);
    post_draw(cmd, g_bright_pipe, g_set_scene_a, &push);
    vkCmdEndRenderPass(cmd);
    post_barrier(cmd, g_bloom_img[0],
                 VK_IMAGE_LAYOUT_SHADER_READ_ONLY_OPTIMAL,
                 VK_IMAGE_LAYOUT_SHADER_READ_ONLY_OPTIMAL,
                 VK_ACCESS_COLOR_ATTACHMENT_WRITE_BIT,
                 VK_ACCESS_SHADER_READ_BIT,
                 VK_PIPELINE_STAGE_COLOR_ATTACHMENT_OUTPUT_BIT,
                 VK_PIPELINE_STAGE_FRAGMENT_SHADER_BIT);

    /* Horizontal blur: A -> B. */
    PostPush blur = push;
    blur.p1[2] = 1.0f;
    blur.p1[3] = 0.0f;
    post_begin(cmd, g_target_pass, g_bloom_fb[1],
               g_post_ext.width, g_post_ext.height);
    post_draw(cmd, g_blur_pipe, g_set_scene_a, &blur);
    vkCmdEndRenderPass(cmd);
    post_barrier(cmd, g_bloom_img[1],
                 VK_IMAGE_LAYOUT_SHADER_READ_ONLY_OPTIMAL,
                 VK_IMAGE_LAYOUT_SHADER_READ_ONLY_OPTIMAL,
                 VK_ACCESS_COLOR_ATTACHMENT_WRITE_BIT,
                 VK_ACCESS_SHADER_READ_BIT,
                 VK_PIPELINE_STAGE_COLOR_ATTACHMENT_OUTPUT_BIT,
                 VK_PIPELINE_STAGE_FRAGMENT_SHADER_BIT);

    /* Vertical blur: B -> A. */
    blur.p1[2] = 0.0f;
    blur.p1[3] = 1.0f;
    post_begin(cmd, g_target_pass, g_bloom_fb[0],
               g_post_ext.width, g_post_ext.height);
    post_draw(cmd, g_blur_pipe, g_set_scene_b, &blur);
    vkCmdEndRenderPass(cmd);
    post_barrier(cmd, g_bloom_img[0],
                 VK_IMAGE_LAYOUT_SHADER_READ_ONLY_OPTIMAL,
                 VK_IMAGE_LAYOUT_SHADER_READ_ONLY_OPTIMAL,
                 VK_ACCESS_COLOR_ATTACHMENT_WRITE_BIT,
                 VK_ACCESS_SHADER_READ_BIT,
                 VK_PIPELINE_STAGE_COLOR_ATTACHMENT_OUTPUT_BIT,
                 VK_PIPELINE_STAGE_FRAGMENT_SHADER_BIT);

    /* Composite: scene + bloom -> swapchain. */
    post_begin(cmd, g_present_pass, g_present_fb[img_idx], w, h);
    post_draw(cmd, g_composite_pipe, g_set_scene_a, &push);
    vkCmdEndRenderPass(cmd);
}
