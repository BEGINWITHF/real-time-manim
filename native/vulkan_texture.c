#include "vulkan_core.h"
#include "vulkan_render.h"
#include "vulkan_texture.h"
#include "draw_common.h"
#include "tex_shaders.h"

// Textured-quad pipeline.  The renderer used to have exactly one way to draw --
// a batch of solid triangles -- so an ImageMobject came out as an opaque white
// quad and a Camera subclass had nowhere to go.  This adds the missing half:
// RGBA textures sampled with a combined image sampler, interleaved with the
// solid geometry at the position it was submitted.

#define MAX_TEXTURES 64
#define TEX_FLOATS_PER_VERTEX 5   // ndc x, ndc y, u, v, alpha

typedef struct {
    unsigned long long token;    // stable per mobject (assigned by the caller)
    unsigned long long digest;   // content hash of the pixels currently uploaded
    int w, h;
    VkImage image;
    VkDeviceMemory mem;
    VkImageView view;
    VkDescriptorSet dset;
} TexEntry;

static TexEntry g_textures[MAX_TEXTURES];
static int g_tex_count = 0;

static VkDescriptorSetLayout g_tex_desc_layout = VK_NULL_HANDLE;
static VkDescriptorPool g_tex_desc_pool = VK_NULL_HANDLE;
static VkSampler g_tex_sampler = VK_NULL_HANDLE;
static VkPipelineLayout g_tex_pl_layout = VK_NULL_HANDLE;
static VkPipeline g_tex_pipeline = VK_NULL_HANDLE;
static VkBuffer g_tex_vert_buf = VK_NULL_HANDLE;
static VkDeviceMemory g_tex_vert_buf_mem = VK_NULL_HANDLE;

// This frame's textured vertices and the order they interleave with solids.
static float g_tex_vertices[MAX_IMAGE_QUADS * 6 * TEX_FLOATS_PER_VERTEX];
static uint32_t g_tex_vertex_count = 0;
static TexDrawItem g_tex_items[MAX_IMAGE_QUADS];
static uint32_t g_tex_item_count = 0;

// Quads submitted by the Python side for this frame.
ImageQuad g_image_quads[MAX_IMAGE_QUADS];
int g_image_quad_count = 0;

// ---------------------------------------------------------------- textures --

static int Tex_Find(unsigned long long token) {
    for (int i = 0; i < g_tex_count; i++) {
        if (g_textures[i].token == token) return i;
    }
    return -1;
}

// --- upload ----------------------------------------------------------------
// One slot per mobject: the caller owns the token, native owns the storage, and a
// content digest says whether the pixels changed since the last upload.  An
// animating image (a fade rewrites the alpha channel) therefore keeps reusing a
// single slot instead of consuming a new one every frame.

static void Tex_WriteDescriptor(TexEntry *e) {
    VkDescriptorImageInfo dii = {0};
    dii.imageLayout = VK_IMAGE_LAYOUT_SHADER_READ_ONLY_OPTIMAL;
    dii.imageView = e->view;
    dii.sampler = g_tex_sampler;
    VkWriteDescriptorSet wds = {0};
    wds.sType = VK_STRUCTURE_TYPE_WRITE_DESCRIPTOR_SET;
    wds.dstSet = e->dset;
    wds.dstBinding = 0;
    wds.descriptorCount = 1;
    wds.descriptorType = VK_DESCRIPTOR_TYPE_COMBINED_IMAGE_SAMPLER;
    wds.pImageInfo = &dii;
    vkUpdateDescriptorSets(g_dev, 1, &wds, 0, NULL);
}

// (Re)create the image and view of a slot at ``w`` x ``h``; the descriptor set is
// kept and re-pointed at the new view.
static int Tex_MakeImage(TexEntry *e, int w, int h) {
    if (e->view != VK_NULL_HANDLE) vkDestroyImageView(g_dev, e->view, NULL);
    if (e->image != VK_NULL_HANDLE) vkDestroyImage(g_dev, e->image, NULL);
    if (e->mem != VK_NULL_HANDLE) vkFreeMemory(g_dev, e->mem, NULL);
    e->view = VK_NULL_HANDLE;
    e->image = VK_NULL_HANDLE;
    e->mem = VK_NULL_HANDLE;

    VkImageCreateInfo ici = {0};
    ici.sType = VK_STRUCTURE_TYPE_IMAGE_CREATE_INFO;
    ici.imageType = VK_IMAGE_TYPE_2D;
    ici.format = VK_FORMAT_R8G8B8A8_UNORM;
    ici.extent = (VkExtent3D){(uint32_t)w, (uint32_t)h, 1};
    ici.mipLevels = 1;
    ici.arrayLayers = 1;
    ici.samples = VK_SAMPLE_COUNT_1_BIT;
    ici.tiling = VK_IMAGE_TILING_OPTIMAL;
    ici.usage = VK_IMAGE_USAGE_SAMPLED_BIT | VK_IMAGE_USAGE_TRANSFER_DST_BIT;
    ici.sharingMode = VK_SHARING_MODE_EXCLUSIVE;
    ici.initialLayout = VK_IMAGE_LAYOUT_UNDEFINED;
    if (vkCreateImage(g_dev, &ici, NULL, &e->image) != VK_SUCCESS) return 0;

    VkMemoryRequirements req;
    vkGetImageMemoryRequirements(g_dev, e->image, &req);
    VkMemoryAllocateInfo mai = {0};
    mai.sType = VK_STRUCTURE_TYPE_MEMORY_ALLOCATE_INFO;
    mai.allocationSize = req.size;
    mai.memoryTypeIndex = FindMemoryType(req.memoryTypeBits, VK_MEMORY_PROPERTY_DEVICE_LOCAL_BIT);
    if (vkAllocateMemory(g_dev, &mai, NULL, &e->mem) != VK_SUCCESS) return 0;
    if (vkBindImageMemory(g_dev, e->image, e->mem, 0) != VK_SUCCESS) return 0;

    VkImageViewCreateInfo vci = {0};
    vci.sType = VK_STRUCTURE_TYPE_IMAGE_VIEW_CREATE_INFO;
    vci.image = e->image;
    vci.viewType = VK_IMAGE_VIEW_TYPE_2D;
    vci.format = VK_FORMAT_R8G8B8A8_UNORM;
    vci.subresourceRange.aspectMask = VK_IMAGE_ASPECT_COLOR_BIT;
    vci.subresourceRange.levelCount = 1;
    vci.subresourceRange.layerCount = 1;
    if (vkCreateImageView(g_dev, &vci, NULL, &e->view) != VK_SUCCESS) return 0;

    e->w = w;
    e->h = h;
    return 1;
}

// Copy pixel data in.  ``fresh``: the image never held data (layout UNDEFINED);
// otherwise it is SHADER_READ_ONLY and gets cycled through TRANSFER_DST.  Uploads
// happen between frames (the Python side calls AddImageQuad before the tick), so
// the shared command pool is free.
static void Tex_WriteImage(TexEntry *e, const unsigned char *rgba, int w, int h, int fresh) {
    VkDeviceSize bytes = (VkDeviceSize)w * h * 4;
    VkBuffer stage_buf = VK_NULL_HANDLE;
    VkDeviceMemory stage_mem = VK_NULL_HANDLE;
    CreateBuffer(bytes, VK_BUFFER_USAGE_TRANSFER_SRC_BIT,
                 VK_MEMORY_PROPERTY_HOST_VISIBLE_BIT | VK_MEMORY_PROPERTY_HOST_COHERENT_BIT,
                 &stage_buf, &stage_mem);
    void *mapped = NULL;
    vkMapMemory(g_dev, stage_mem, 0, bytes, 0, &mapped);
    memcpy(mapped, rgba, (size_t)bytes);
    vkUnmapMemory(g_dev, stage_mem);

    VkCommandBuffer cmd = VK_NULL_HANDLE;
    VkCommandBufferAllocateInfo cai = {0};
    cai.sType = VK_STRUCTURE_TYPE_COMMAND_BUFFER_ALLOCATE_INFO;
    cai.commandPool = g_cmd_pool;
    cai.level = VK_COMMAND_BUFFER_LEVEL_PRIMARY;
    cai.commandBufferCount = 1;
    vkAllocateCommandBuffers(g_dev, &cai, &cmd);

    VkCommandBufferBeginInfo bi = {0};
    bi.sType = VK_STRUCTURE_TYPE_COMMAND_BUFFER_BEGIN_INFO;
    bi.flags = VK_COMMAND_BUFFER_USAGE_ONE_TIME_SUBMIT_BIT;
    vkBeginCommandBuffer(cmd, &bi);

    VkImageMemoryBarrier b = {0};
    b.sType = VK_STRUCTURE_TYPE_IMAGE_MEMORY_BARRIER;
    b.oldLayout = fresh ? VK_IMAGE_LAYOUT_UNDEFINED : VK_IMAGE_LAYOUT_SHADER_READ_ONLY_OPTIMAL;
    b.newLayout = VK_IMAGE_LAYOUT_TRANSFER_DST_OPTIMAL;
    b.srcQueueFamilyIndex = VK_QUEUE_FAMILY_IGNORED;
    b.dstQueueFamilyIndex = VK_QUEUE_FAMILY_IGNORED;
    b.image = e->image;
    b.subresourceRange.aspectMask = VK_IMAGE_ASPECT_COLOR_BIT;
    b.subresourceRange.levelCount = 1;
    b.subresourceRange.layerCount = 1;
    b.srcAccessMask = fresh ? 0 : VK_ACCESS_SHADER_READ_BIT;
    b.dstAccessMask = VK_ACCESS_TRANSFER_WRITE_BIT;
    vkCmdPipelineBarrier(cmd,
        fresh ? VK_PIPELINE_STAGE_TOP_OF_PIPE_BIT : VK_PIPELINE_STAGE_FRAGMENT_SHADER_BIT,
        VK_PIPELINE_STAGE_TRANSFER_BIT, 0, 0, NULL, 0, NULL, 1, &b);

    VkBufferImageCopy region = {0};
    region.imageSubresource.aspectMask = VK_IMAGE_ASPECT_COLOR_BIT;
    region.imageSubresource.layerCount = 1;
    region.imageExtent = (VkExtent3D){(uint32_t)w, (uint32_t)h, 1};
    vkCmdCopyBufferToImage(cmd, stage_buf, e->image,
                           VK_IMAGE_LAYOUT_TRANSFER_DST_OPTIMAL, 1, &region);

    b.oldLayout = VK_IMAGE_LAYOUT_TRANSFER_DST_OPTIMAL;
    b.newLayout = VK_IMAGE_LAYOUT_SHADER_READ_ONLY_OPTIMAL;
    b.srcAccessMask = VK_ACCESS_TRANSFER_WRITE_BIT;
    b.dstAccessMask = VK_ACCESS_SHADER_READ_BIT;
    vkCmdPipelineBarrier(cmd, VK_PIPELINE_STAGE_TRANSFER_BIT,
                         VK_PIPELINE_STAGE_FRAGMENT_SHADER_BIT, 0, 0, NULL, 0, NULL, 1, &b);

    vkEndCommandBuffer(cmd);

    VkFence fence = VK_NULL_HANDLE;
    VkFenceCreateInfo fci = {0};
    fci.sType = VK_STRUCTURE_TYPE_FENCE_CREATE_INFO;
    vkCreateFence(g_dev, &fci, NULL, &fence);
    VkSubmitInfo si = {0};
    si.sType = VK_STRUCTURE_TYPE_SUBMIT_INFO;
    si.commandBufferCount = 1;
    si.pCommandBuffers = &cmd;
    vkQueueSubmit(g_gfx_queue, 1, &si, fence);
    vkWaitForFences(g_dev, 1, &fence, VK_TRUE, UINT64_MAX);
    vkDestroyFence(g_dev, fence, NULL);
    vkFreeCommandBuffers(g_dev, g_cmd_pool, 1, &cmd);
    vkDestroyBuffer(g_dev, stage_buf, NULL);
    vkFreeMemory(g_dev, stage_mem, NULL);
}

int Tex_Ensure(unsigned long long token, unsigned long long digest,
               const unsigned char *rgba, int w, int h) {
    if (w <= 0 || h <= 0 || rgba == NULL) return -1;

    int slot = Tex_Find(token);
    if (slot < 0) {
        if (g_tex_count >= MAX_TEXTURES) return -1;
        TexEntry *e = &g_textures[g_tex_count];
        memset(e, 0, sizeof(*e));
        e->token = token;

        VkDescriptorSetAllocateInfo dsai = {0};
        dsai.sType = VK_STRUCTURE_TYPE_DESCRIPTOR_SET_ALLOCATE_INFO;
        dsai.descriptorPool = g_tex_desc_pool;
        dsai.descriptorSetCount = 1;
        dsai.pSetLayouts = &g_tex_desc_layout;
        if (vkAllocateDescriptorSets(g_dev, &dsai, &e->dset) != VK_SUCCESS) return -1;
        if (!Tex_MakeImage(e, w, h)) return -1;
        Tex_WriteDescriptor(e);
        Tex_WriteImage(e, rgba, w, h, 1);
        e->digest = digest;
        return g_tex_count++;
    }

    TexEntry *e = &g_textures[slot];
    if (e->digest == digest && e->w == w && e->h == h) return slot;   // unchanged
    if (e->w != w || e->h != h) {
        if (!Tex_MakeImage(e, w, h)) return -1;
        Tex_WriteDescriptor(e);
        Tex_WriteImage(e, rgba, w, h, 1);
    } else {
        Tex_WriteImage(e, rgba, w, h, 0);
    }
    e->digest = digest;
    return slot;
}

// ---------------------------------------------------------------- pipeline --

static void CreateTexPipeline(void) {
    VkDescriptorSetLayoutBinding binding = {0};
    binding.binding = 0;
    binding.descriptorType = VK_DESCRIPTOR_TYPE_COMBINED_IMAGE_SAMPLER;
    binding.descriptorCount = 1;
    binding.stageFlags = VK_SHADER_STAGE_FRAGMENT_BIT;

    VkDescriptorSetLayoutCreateInfo dlci = {0};
    dlci.sType = VK_STRUCTURE_TYPE_DESCRIPTOR_SET_LAYOUT_CREATE_INFO;
    dlci.bindingCount = 1;
    dlci.pBindings = &binding;
    vkCreateDescriptorSetLayout(g_dev, &dlci, NULL, &g_tex_desc_layout);

    VkDescriptorPoolSize pool_size = {0};
    pool_size.type = VK_DESCRIPTOR_TYPE_COMBINED_IMAGE_SAMPLER;
    pool_size.descriptorCount = MAX_TEXTURES;

    VkDescriptorPoolCreateInfo dpci = {0};
    dpci.sType = VK_STRUCTURE_TYPE_DESCRIPTOR_POOL_CREATE_INFO;
    dpci.maxSets = MAX_TEXTURES;
    dpci.poolSizeCount = 1;
    dpci.pPoolSizes = &pool_size;
    vkCreateDescriptorPool(g_dev, &dpci, NULL, &g_tex_desc_pool);

    VkSamplerCreateInfo sci = {0};
    sci.sType = VK_STRUCTURE_TYPE_SAMPLER_CREATE_INFO;
    sci.magFilter = VK_FILTER_LINEAR;
    sci.minFilter = VK_FILTER_LINEAR;
    sci.mipmapMode = VK_SAMPLER_MIPMAP_MODE_NEAREST;
    sci.addressModeU = VK_SAMPLER_ADDRESS_MODE_CLAMP_TO_EDGE;
    sci.addressModeV = VK_SAMPLER_ADDRESS_MODE_CLAMP_TO_EDGE;
    sci.addressModeW = VK_SAMPLER_ADDRESS_MODE_CLAMP_TO_EDGE;
    sci.compareEnable = VK_FALSE;
    sci.maxLod = 0.0f;
    vkCreateSampler(g_dev, &sci, NULL, &g_tex_sampler);

    VkPipelineLayoutCreateInfo plci = {0};
    plci.sType = VK_STRUCTURE_TYPE_PIPELINE_LAYOUT_CREATE_INFO;
    plci.setLayoutCount = 1;
    plci.pSetLayouts = &g_tex_desc_layout;
    vkCreatePipelineLayout(g_dev, &plci, NULL, &g_tex_pl_layout);

    VkShaderModule vs = CreateShaderModule(tex_vert_spv, sizeof(tex_vert_spv));
    VkShaderModule fs = CreateShaderModule(tex_frag_spv, sizeof(tex_frag_spv));

    VkPipelineShaderStageCreateInfo stages[2] = {{0}};
    stages[0].sType = VK_STRUCTURE_TYPE_PIPELINE_SHADER_STAGE_CREATE_INFO;
    stages[0].stage = VK_SHADER_STAGE_VERTEX_BIT;
    stages[0].module = vs;
    stages[0].pName = "main";
    stages[1].sType = VK_STRUCTURE_TYPE_PIPELINE_SHADER_STAGE_CREATE_INFO;
    stages[1].stage = VK_SHADER_STAGE_FRAGMENT_BIT;
    stages[1].module = fs;
    stages[1].pName = "main";

    VkVertexInputBindingDescription bind_desc = {0};
    bind_desc.binding = 0;
    bind_desc.stride = sizeof(float) * TEX_FLOATS_PER_VERTEX;
    bind_desc.inputRate = VK_VERTEX_INPUT_RATE_VERTEX;

    VkVertexInputAttributeDescription attrs[3] = {{0}};
    attrs[0].location = 0;
    attrs[0].binding = 0;
    attrs[0].format = VK_FORMAT_R32G32_SFLOAT;
    attrs[0].offset = 0;
    attrs[1].location = 1;
    attrs[1].binding = 0;
    attrs[1].format = VK_FORMAT_R32G32_SFLOAT;
    attrs[1].offset = sizeof(float) * 2;
    attrs[2].location = 2;
    attrs[2].binding = 0;
    attrs[2].format = VK_FORMAT_R32_SFLOAT;
    attrs[2].offset = sizeof(float) * 4;

    VkPipelineVertexInputStateCreateInfo vi = {0};
    vi.sType = VK_STRUCTURE_TYPE_PIPELINE_VERTEX_INPUT_STATE_CREATE_INFO;
    vi.vertexBindingDescriptionCount = 1;
    vi.pVertexBindingDescriptions = &bind_desc;
    vi.vertexAttributeDescriptionCount = 3;
    vi.pVertexAttributeDescriptions = attrs;

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
    rs.frontFace = VK_FRONT_FACE_CLOCKWISE;
    rs.lineWidth = 1.0f;

    VkPipelineMultisampleStateCreateInfo ms = {0};
    ms.sType = VK_STRUCTURE_TYPE_PIPELINE_MULTISAMPLE_STATE_CREATE_INFO;
    ms.rasterizationSamples = VK_SAMPLE_COUNT_1_BIT;

    // Same blending as the solid pipeline, so an image fades like a shape.
    VkPipelineColorBlendAttachmentState cba = {0};
    cba.colorWriteMask = VK_COLOR_COMPONENT_R_BIT | VK_COLOR_COMPONENT_G_BIT |
                         VK_COLOR_COMPONENT_B_BIT | VK_COLOR_COMPONENT_A_BIT;
    cba.blendEnable = VK_TRUE;
    cba.srcColorBlendFactor = VK_BLEND_FACTOR_SRC_ALPHA;
    cba.dstColorBlendFactor = VK_BLEND_FACTOR_ONE_MINUS_SRC_ALPHA;
    cba.colorBlendOp = VK_BLEND_OP_ADD;
    cba.srcAlphaBlendFactor = VK_BLEND_FACTOR_ONE;
    cba.dstAlphaBlendFactor = VK_BLEND_FACTOR_ZERO;
    cba.alphaBlendOp = VK_BLEND_OP_ADD;

    VkPipelineColorBlendStateCreateInfo cb = {0};
    cb.sType = VK_STRUCTURE_TYPE_PIPELINE_COLOR_BLEND_STATE_CREATE_INFO;
    cb.attachmentCount = 1;
    cb.pAttachments = &cba;

    VkDynamicState dynamic_states[] = {VK_DYNAMIC_STATE_VIEWPORT, VK_DYNAMIC_STATE_SCISSOR};
    VkPipelineDynamicStateCreateInfo ds = {0};
    ds.sType = VK_STRUCTURE_TYPE_PIPELINE_DYNAMIC_STATE_CREATE_INFO;
    ds.dynamicStateCount = 2;
    ds.pDynamicStates = dynamic_states;

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
    pci.pDynamicState = &ds;
    pci.layout = g_tex_pl_layout;
    pci.renderPass = g_render_pass;
    vkCreateGraphicsPipelines(g_dev, VK_NULL_HANDLE, 1, &pci, NULL, &g_tex_pipeline);

    vkDestroyShaderModule(g_dev, vs, NULL);
    vkDestroyShaderModule(g_dev, fs, NULL);
}

void Tex_CreateResources(void) {
    CreateTexPipeline();
    CreateBuffer(sizeof(float) * TEX_FLOATS_PER_VERTEX * 6 * MAX_IMAGE_QUADS,
                 VK_BUFFER_USAGE_VERTEX_BUFFER_BIT,
                 VK_MEMORY_PROPERTY_HOST_VISIBLE_BIT | VK_MEMORY_PROPERTY_HOST_COHERENT_BIT,
                 &g_tex_vert_buf, &g_tex_vert_buf_mem);
}

void Tex_DestroyResources(void) {
    for (int i = 0; i < g_tex_count; i++) {
        TexEntry *e = &g_textures[i];
        if (e->view) vkDestroyImageView(g_dev, e->view, NULL);
        if (e->image) vkDestroyImage(g_dev, e->image, NULL);
        if (e->mem) vkFreeMemory(g_dev, e->mem, NULL);
    }
    g_tex_count = 0;
    if (g_tex_desc_pool) vkDestroyDescriptorPool(g_dev, g_tex_desc_pool, NULL);
    if (g_tex_desc_layout) vkDestroyDescriptorSetLayout(g_dev, g_tex_desc_layout, NULL);
    if (g_tex_sampler) vkDestroySampler(g_dev, g_tex_sampler, NULL);
    if (g_tex_pipeline) vkDestroyPipeline(g_dev, g_tex_pipeline, NULL);
    if (g_tex_pl_layout) vkDestroyPipelineLayout(g_dev, g_tex_pl_layout, NULL);
    if (g_tex_vert_buf) vkDestroyBuffer(g_dev, g_tex_vert_buf, NULL);
    if (g_tex_vert_buf_mem) vkFreeMemory(g_dev, g_tex_vert_buf_mem, NULL);
    g_tex_desc_pool = VK_NULL_HANDLE;
    g_tex_desc_layout = VK_NULL_HANDLE;
    g_tex_sampler = VK_NULL_HANDLE;
    g_tex_pipeline = VK_NULL_HANDLE;
    g_tex_pl_layout = VK_NULL_HANDLE;
    g_tex_vert_buf = VK_NULL_HANDLE;
    g_tex_vert_buf_mem = VK_NULL_HANDLE;
}

// ------------------------------------------------------------------ frames --

void Tex_BeginFrame(void) {
    g_tex_vertex_count = 0;
    g_tex_item_count = 0;
}

uint32_t Tex_ItemCount(void) {
    return g_tex_item_count;
}

void Tex_EndFrame(void) {
    if (g_tex_vertex_count == 0) return;
    void *mapped = NULL;
    VkDeviceSize size = sizeof(float) * g_tex_vertex_count * TEX_FLOATS_PER_VERTEX;
    vkMapMemory(g_dev, g_tex_vert_buf_mem, 0, size, 0, &mapped);
    memcpy(mapped, g_tex_vertices, (size_t)size);
    vkUnmapMemory(g_dev, g_tex_vert_buf_mem);
}

void BuildVerticesFromImageQuad(int idx) {
    if (idx < 0 || idx >= g_image_quad_count) return;
    if (g_tex_item_count >= MAX_IMAGE_QUADS) return;
    if (g_tex_vertex_count + 6 > MAX_IMAGE_QUADS * 6) return;

    const ImageQuad *q = &g_image_quads[idx];
    static const float uvs[4][2] = {{0.0f, 0.0f}, {1.0f, 0.0f}, {1.0f, 1.0f}, {0.0f, 1.0f}};
    static const int order[6] = {0, 1, 2, 0, 2, 3};

    float nx[4], ny[4];
    for (int c = 0; c < 4; c++) {
        ToNDC(q->xy[c * 2], q->xy[c * 2 + 1], &nx[c], &ny[c]);
    }
    for (int v = 0; v < 6; v++) {
        int c = order[v];
        float *out = &g_tex_vertices[g_tex_vertex_count * TEX_FLOATS_PER_VERTEX];
        out[0] = nx[c];
        out[1] = ny[c];
        out[2] = uvs[c][0];
        out[3] = uvs[c][1];
        out[4] = q->opacity;
        g_tex_vertex_count++;
    }

    // Solid vertices queued before this quad -- the interleave point.
    g_tex_items[g_tex_item_count].solid_count = g_vertex_count;
    g_tex_items[g_tex_item_count].quad = idx;
    g_tex_item_count++;
}

void Tex_RecordInterleaved(VkCommandBuffer cmd_buf, uint32_t solid_vertex_count) {
    VkDeviceSize offsets[] = {0};
    uint32_t solid_drawn = 0;

    for (uint32_t i = 0; i < g_tex_item_count; i++) {
        uint32_t upto = g_tex_items[i].solid_count;
        if (upto > solid_vertex_count) upto = solid_vertex_count;
        if (upto > solid_drawn) {
            VkBuffer bufs[] = {g_vert_buf};
            vkCmdBindPipeline(cmd_buf, VK_PIPELINE_BIND_POINT_GRAPHICS, g_pipeline);
            vkCmdBindVertexBuffers(cmd_buf, 0, 1, bufs, offsets);
            vkCmdDraw(cmd_buf, upto - solid_drawn, 1, solid_drawn, 0);
            solid_drawn = upto;
        }
        // draw this quad with its own bound texture
        int quad = g_tex_items[i].quad;
        int slot = Tex_Find(g_image_quads[quad].token);
        if (slot < 0) continue;
        VkBuffer bufs[] = {g_tex_vert_buf};
        vkCmdBindPipeline(cmd_buf, VK_PIPELINE_BIND_POINT_GRAPHICS, g_tex_pipeline);
        vkCmdBindVertexBuffers(cmd_buf, 0, 1, bufs, offsets);
        vkCmdBindDescriptorSets(cmd_buf, VK_PIPELINE_BIND_POINT_GRAPHICS, g_tex_pl_layout,
                                0, 1, &g_textures[slot].dset, 0, NULL);
        vkCmdDraw(cmd_buf, 6, 1, (uint32_t)quad * 6, 0);
    }

    if (solid_drawn < solid_vertex_count) {
        VkBuffer bufs[] = {g_vert_buf};
        vkCmdBindPipeline(cmd_buf, VK_PIPELINE_BIND_POINT_GRAPHICS, g_pipeline);
        vkCmdBindVertexBuffers(cmd_buf, 0, 1, bufs, offsets);
        vkCmdDraw(cmd_buf, solid_vertex_count - solid_drawn, 1, solid_drawn, 0);
    }
}
