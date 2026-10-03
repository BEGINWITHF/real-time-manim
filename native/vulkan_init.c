#include "vulkan_core.h"
#include "vulkan_texture.h"
#include "draw_common.h"

#define VK_CHECK(call) do { \
    VkResult _result = (call); \
    if (_result != VK_SUCCESS) { \
        fprintf(stderr, "[Vulkan ERROR] %s returned %d\n", #call, _result); \
    } \
} while(0)

VkInstance g_inst = VK_NULL_HANDLE;

VkPhysicalDevice g_phys_dev = VK_NULL_HANDLE;

VkDevice g_dev = VK_NULL_HANDLE;

VkQueue g_gfx_queue = VK_NULL_HANDLE;

VkQueue g_present_queue = VK_NULL_HANDLE;

VkSurfaceKHR g_surface = VK_NULL_HANDLE;

VkSwapchainKHR g_swapchain = VK_NULL_HANDLE;

VkFormat g_swapchain_fmt;

VkExtent2D g_swapchain_ext;

VkImage *g_swapchain_imgs = NULL;

VkImageView *g_swapchain_img_views = NULL;

uint32_t g_swapchain_img_count = 0;

VkRenderPass g_render_pass = VK_NULL_HANDLE;

VkFramebuffer *g_framebuffers = NULL;

VkPipelineLayout g_pipeline_layout = VK_NULL_HANDLE;

VkPipeline g_pipeline = VK_NULL_HANDLE;

VkCommandPool g_cmd_pool = VK_NULL_HANDLE;

VkCommandBuffer *g_cmd_bufs = NULL;

uint32_t g_cmd_buf_count = 0;

VkSemaphore *g_img_avail_sems = NULL;

VkSemaphore *g_render_done_sems = NULL;

VkFence *g_in_flight_fences = NULL;

VkBuffer g_vert_buf = VK_NULL_HANDLE;

VkDeviceMemory g_vert_buf_mem = VK_NULL_HANDLE;

#ifdef _WIN32
HWND g_hwnd = NULL;

HINSTANCE g_hinst = NULL;
#else
void *g_metal_layer = NULL;

uint32_t g_last_img_idx = 0;

int g_readback_requested = 0;
int g_readback_available = 0;
uint32_t g_readback_fence_idx = 0;
VkBuffer g_readback_buf = VK_NULL_HANDLE;
VkDeviceMemory g_readback_mem = VK_NULL_HANDLE;
void *g_readback_map = NULL;
#endif

bool g_is_ready = false;

uint32_t g_current_frame = 0;

bool g_framebuffer_resized = false;

static const uint32_t vert_spv[] = {
    0x07230203,0x00010000,0x000d000b,0x00000026,0x00000000,0x00020011,0x00000001,0x0006000b,0x00000001,0x4c534c47,0x6474732e,0x3035342e,0x00000000,0x0003000e,0x00000000,0x00000001,0x000b000f,0x00000000,0x00000004,0x6e69616d,0x00000000,0x0000000d,0x00000012,0x0000001d,0x0000001f,0x00000022,0x00000024,0x00030003,0x00000002,0x000001c2,0x000a0004,0x475f4c47,0x4c474f4f,0x70635f45,0x74735f70,0x5f656c79,0x656e696c,0x7269645f,0x69746365,0x00006576,0x00080004,0x475f4c47,0x4c474f4f,0x6e695f45,0x64756c63,0x69645f65,0x74636572,0x00657669,0x00040005,0x00000004,0x6e69616d,0x00000000,0x00060005,0x0000000b,0x505f6c67,0x65567265,0x78657472,0x00000000,0x00060006,0x0000000b,0x00000000,0x505f6c67,0x7469736f,0x006e6f69,0x00070006,0x0000000b,0x00000001,0x505f6c67,0x746e696f,0x657a6953,0x00000000,0x00070006,0x0000000b,0x00000002,0x435f6c67,0x4470696c,0x61747369,0x0065636e,0x00070006,0x0000000b,0x00000003,0x435f6c67,0x446c6c75,0x61747369,0x0065636e,0x00030005,0x0000000d,0x00000000,0x00040005,0x00000012,0x705f6e69,0x0000736f,0x00050005,0x0000001d,0x67617266,0x6c6f635f,0x0000726f,0x00050005,0x0000001f,0x635f6e69,0x726f6c6f,0x00000000,0x00050005,0x00000022,0x67617266,0x706c615f,0x00006168,0x00050005,0x00000024,0x615f6e69,0x6168706c,0x00000000,0x00030047,0x0000000b,0x00000002,0x00050048,0x0000000b,0x00000000,0x0000000b,0x00000000,0x00050048,0x0000000b,0x00000001,0x0000000b,0x00000001,0x00050048,0x0000000b,0x00000002,0x0000000b,0x00000003,0x00050048,0x0000000b,0x00000003,0x0000000b,0x00000004,0x00040047,0x00000012,0x0000001e,0x00000000,0x00040047,0x0000001d,0x0000001e,0x00000000,0x00040047,0x0000001f,0x0000001e,0x00000001,0x00040047,0x00000022,0x0000001e,0x00000001,0x00040047,0x00000024,0x0000001e,0x00000002,0x00020013,0x00000002,0x00030021,0x00000003,0x00000002,0x00030016,0x00000006,0x00000020,0x00040017,0x00000007,0x00000006,0x00000004,0x00040015,0x00000008,0x00000020,0x00000000,0x0004002b,0x00000008,0x00000009,0x00000001,0x0004001c,0x0000000a,0x00000006,0x00000009,0x0006001e,0x0000000b,0x00000007,0x00000006,0x0000000a,0x0000000a,0x00040020,0x0000000c,0x00000003,0x0000000b,0x0004003b,0x0000000c,0x0000000d,0x00000003,0x00040015,0x0000000e,0x00000020,0x00000001,0x0004002b,0x0000000e,0x0000000f,0x00000000,0x00040017,0x00000010,0x00000006,0x00000002,0x00040020,0x00000011,0x00000001,0x00000010,0x0004003b,0x00000011,0x00000012,0x00000001,0x0004002b,0x00000006,0x00000014,0x00000000,0x0004002b,0x00000006,0x00000015,0x3f800000,0x00040020,0x00000019,0x00000003,0x00000007,0x00040017,0x0000001b,0x00000006,0x00000003,0x00040020,0x0000001c,0x00000003,0x0000001b,0x0004003b,0x0000001c,0x0000001d,0x00000003,0x00040020,0x0000001e,0x00000001,0x0000001b,0x0004003b,0x0000001e,0x0000001f,0x00000001,0x00040020,0x00000021,0x00000003,0x00000006,0x0004003b,0x00000021,0x00000022,0x00000003,0x00040020,0x00000023,0x00000001,0x00000006,0x0004003b,0x00000023,0x00000024,0x00000001,0x00050036,0x00000002,0x00000004,0x00000000,0x00000003,0x000200f8,0x00000005,0x0004003d,0x00000010,0x00000013,0x00000012,0x00050051,0x00000006,0x00000016,0x00000013,0x00000000,0x00050051,0x00000006,0x00000017,0x00000013,0x00000001,0x00070050,0x00000007,0x00000018,0x00000016,0x00000017,0x00000014,0x00000015,0x00050041,0x00000019,0x0000001a,0x0000000d,0x0000000f,0x0003003e,0x0000001a,0x00000018,0x0004003d,0x0000001b,0x00000020,0x0000001f,0x0003003e,0x0000001d,0x00000020,0x0004003d,0x00000006,0x00000025,0x00000024,0x0003003e,0x00000022,0x00000025,0x000100fd,0x00010038
};


static const uint32_t frag_spv[] = {
    0x07230203,0x00010000,0x000d000b,0x00000015,0x00000000,0x00020011,0x00000001,0x0006000b,0x00000001,0x4c534c47,0x6474732e,0x3035342e,0x00000000,0x0003000e,0x00000000,0x00000001,0x0008000f,0x00000004,0x00000004,0x6e69616d,0x00000000,0x00000009,0x0000000c,0x0000000f,0x00030010,0x00000004,0x00000007,0x00030003,0x00000002,0x000001c2,0x000a0004,0x475f4c47,0x4c474f4f,0x70635f45,0x74735f70,0x5f656c79,0x656e696c,0x7269645f,0x69746365,0x00006576,0x00080004,0x475f4c47,0x4c474f4f,0x6e695f45,0x64756c63,0x69645f65,0x74636572,0x00657669,0x00040005,0x00000004,0x6e69616d,0x00000000,0x00050005,0x00000009,0x5f74756f,0x6f6c6f63,0x00000072,0x00050005,0x0000000c,0x67617266,0x6c6f635f,0x0000726f,0x00050005,0x0000000f,0x67617266,0x706c615f,0x00006168,0x00040047,0x00000009,0x0000001e,0x00000000,0x00040047,0x0000000c,0x0000001e,0x00000000,0x00040047,0x0000000f,0x0000001e,0x00000001,0x00020013,0x00000002,0x00030021,0x00000003,0x00000002,0x00030016,0x00000006,0x00000020,0x00040017,0x00000007,0x00000006,0x00000004,0x00040020,0x00000008,0x00000003,0x00000007,0x0004003b,0x00000008,0x00000009,0x00000003,0x00040017,0x0000000a,0x00000006,0x00000003,0x00040020,0x0000000b,0x00000001,0x0000000a,0x0004003b,0x0000000b,0x0000000c,0x00000001,0x00040020,0x0000000e,0x00000001,0x00000006,0x0004003b,0x0000000e,0x0000000f,0x00000001,0x00050036,0x00000002,0x00000004,0x00000000,0x00000003,0x000200f8,0x00000005,0x0004003d,0x0000000a,0x0000000d,0x0000000c,0x0004003d,0x00000006,0x00000010,0x0000000f,0x00050051,0x00000006,0x00000011,0x0000000d,0x00000000,0x00050051,0x00000006,0x00000012,0x0000000d,0x00000001,0x00050051,0x00000006,0x00000013,0x0000000d,0x00000002,0x00070050,0x00000007,0x00000014,0x00000011,0x00000012,0x00000013,0x00000010,0x0003003e,0x00000009,0x00000014,0x000100fd,0x00010038
};


VkShaderModule CreateShaderModule(const uint32_t *code, size_t size) {

    VkShaderModuleCreateInfo ci = {0};

    ci.sType = VK_STRUCTURE_TYPE_SHADER_MODULE_CREATE_INFO;

    ci.codeSize = size;

    ci.pCode = code;

    VkShaderModule mod;

    VK_CHECK(vkCreateShaderModule(g_dev, &ci, NULL, &mod));

    return mod;

}

uint32_t FindMemoryType(uint32_t type_filter, VkMemoryPropertyFlags props) {

    VkPhysicalDeviceMemoryProperties mem_props;

    vkGetPhysicalDeviceMemoryProperties(g_phys_dev, &mem_props);

    for (uint32_t i = 0; i < mem_props.memoryTypeCount; i++) {

        if ((type_filter & (1 << i)) && 

            (mem_props.memoryTypes[i].propertyFlags & props) == props) {

            return i;

        }

    }

    fprintf(stderr, "Failed to find suitable memory type!\n");

    exit(-1);

}

void CreateBuffer(VkDeviceSize size, VkBufferUsageFlags usage,

                  VkMemoryPropertyFlags props, VkBuffer *buf, VkDeviceMemory *mem) {

    VkBufferCreateInfo bi = {0};

    bi.sType = VK_STRUCTURE_TYPE_BUFFER_CREATE_INFO;

    bi.size = size;

    bi.usage = usage;

    bi.sharingMode = VK_SHARING_MODE_EXCLUSIVE;

    VK_CHECK(vkCreateBuffer(g_dev, &bi, NULL, buf));

    VkMemoryRequirements mr;

    vkGetBufferMemoryRequirements(g_dev, *buf, &mr);

    VkMemoryAllocateInfo ai = {0};

    ai.sType = VK_STRUCTURE_TYPE_MEMORY_ALLOCATE_INFO;

    ai.allocationSize = mr.size;

    ai.memoryTypeIndex = FindMemoryType(mr.memoryTypeBits, props);

    VK_CHECK(vkAllocateMemory(g_dev, &ai, NULL, mem));

    VK_CHECK(vkBindBufferMemory(g_dev, *buf, *mem, 0));

}

static void CreateInstance(void) {

    VkApplicationInfo app_info = {0};

    app_info.sType = VK_STRUCTURE_TYPE_APPLICATION_INFO;

    app_info.pApplicationName = "Real Time Manim";

    app_info.applicationVersion = VK_MAKE_VERSION(1, 0, 0);

    app_info.pEngineName = "No Engine";

    app_info.engineVersion = VK_MAKE_VERSION(1, 0, 0);

    app_info.apiVersion = VK_API_VERSION_1_0;

#ifdef _WIN32
    const char *extensions[] = {

        VK_KHR_SURFACE_EXTENSION_NAME,

        VK_KHR_WIN32_SURFACE_EXTENSION_NAME

    };

    VkInstanceCreateInfo ci = {0};

    ci.sType = VK_STRUCTURE_TYPE_INSTANCE_CREATE_INFO;

    ci.pApplicationInfo = &app_info;

    ci.enabledExtensionCount = 2;

    ci.ppEnabledExtensionNames = extensions;

    if (vkCreateInstance(&ci, NULL, &g_inst) != VK_SUCCESS) {

        fprintf(stderr, "Failed to create Vulkan instance!\n");

        exit(-1);

    }
#else
    const char *extensions[] = {

        VK_KHR_SURFACE_EXTENSION_NAME,

        VK_EXT_METAL_SURFACE_EXTENSION_NAME

    };

    VkInstanceCreateInfo ci = {0};

    ci.sType = VK_STRUCTURE_TYPE_INSTANCE_CREATE_INFO;

    ci.pApplicationInfo = &app_info;

    ci.enabledExtensionCount = 2;

    ci.ppEnabledExtensionNames = extensions;

    // MoltenVK is a portability implementation: without this flag the
    // loader hides it and vkEnumeratePhysicalDevices returns nothing.
    ci.flags |= VK_INSTANCE_CREATE_ENUMERATE_PORTABILITY_BIT_KHR;

    if (vkCreateInstance(&ci, NULL, &g_inst) != VK_SUCCESS) {

        fprintf(stderr, "Failed to create Vulkan instance!\n");

        exit(-1);

    }
#endif

}

static void CreateSurface(void) {

#ifdef _WIN32
    VkWin32SurfaceCreateInfoKHR ci = {0};

    ci.sType = VK_STRUCTURE_TYPE_WIN32_SURFACE_CREATE_INFO_KHR;

    ci.hinstance = g_hinst;

    ci.hwnd = g_hwnd;

    if (vkCreateWin32SurfaceKHR(g_inst, &ci, NULL, &g_surface) != VK_SUCCESS) {

        fprintf(stderr, "Failed to create Win32 surface!\n");

        exit(-1);

    }
#else
    VkMetalSurfaceCreateInfoEXT ci = {0};

    ci.sType = VK_STRUCTURE_TYPE_METAL_SURFACE_CREATE_INFO_EXT;

    ci.pLayer = (const CAMetalLayer *)g_metal_layer;

    if (vkCreateMetalSurfaceEXT(g_inst, &ci, NULL, &g_surface) != VK_SUCCESS) {

        fprintf(stderr, "Failed to create Metal surface!\n");

        exit(-1);

    }
#endif
}

static void PickPhysicalDevice(void) {

    uint32_t count = 0;

    vkEnumeratePhysicalDevices(g_inst, &count, NULL);

    if (count == 0) { fprintf(stderr, "No GPU found!\n"); exit(-1); }

    VkPhysicalDevice *devs = malloc(sizeof(VkPhysicalDevice) * count);

    vkEnumeratePhysicalDevices(g_inst, &count, devs);

    g_phys_dev = devs[0];

    free(devs);

}

static void CreateLogicalDevice(void) {

    float prio = 1.0f;

    VkDeviceQueueCreateInfo qci = {0};

    qci.sType = VK_STRUCTURE_TYPE_DEVICE_QUEUE_CREATE_INFO;

    qci.queueFamilyIndex = 0;

    qci.queueCount = 1;

    qci.pQueuePriorities = &prio;

#ifdef _WIN32
    const char *exts[] = { VK_KHR_SWAPCHAIN_EXTENSION_NAME };

    VkDeviceCreateInfo dci = {0};

    dci.sType = VK_STRUCTURE_TYPE_DEVICE_CREATE_INFO;

    dci.queueCreateInfoCount = 1;

    dci.pQueueCreateInfos = &qci;

    dci.enabledExtensionCount = 1;

    dci.ppEnabledExtensionNames = exts;
#else
    const char *exts[] = { VK_KHR_SWAPCHAIN_EXTENSION_NAME, "VK_KHR_portability_subset" };

    VkDeviceCreateInfo dci = {0};

    dci.sType = VK_STRUCTURE_TYPE_DEVICE_CREATE_INFO;

    dci.queueCreateInfoCount = 1;

    dci.pQueueCreateInfos = &qci;

    dci.enabledExtensionCount = 2;

    dci.ppEnabledExtensionNames = exts;
#endif

    vkCreateDevice(g_phys_dev, &dci, NULL, &g_dev);

    vkGetDeviceQueue(g_dev, 0, 0, &g_gfx_queue);

    vkGetDeviceQueue(g_dev, 0, 0, &g_present_queue);

}

void CreateSwapchain(void) {

    VkSwapchainCreateInfoKHR sci = {0};

    sci.sType = VK_STRUCTURE_TYPE_SWAPCHAIN_CREATE_INFO_KHR;

    sci.surface = g_surface;

    sci.minImageCount = 2;

    sci.imageFormat = VK_FORMAT_B8G8R8A8_UNORM;

    sci.imageColorSpace = VK_COLOR_SPACE_SRGB_NONLINEAR_KHR;

    sci.imageExtent = g_swapchain_ext;

    sci.imageArrayLayers = 1;

#ifdef _WIN32
    sci.imageUsage = VK_IMAGE_USAGE_COLOR_ATTACHMENT_BIT;
#else
    // The readback path copies the swapchain image inside the draw command
    // buffer (MoltenVK forbids reads after present), so TRANSFER_SRC is needed.
    sci.imageUsage = VK_IMAGE_USAGE_COLOR_ATTACHMENT_BIT | VK_IMAGE_USAGE_TRANSFER_SRC_BIT;
#endif

    sci.imageSharingMode = VK_SHARING_MODE_EXCLUSIVE;

    sci.preTransform = VK_SURFACE_TRANSFORM_IDENTITY_BIT_KHR;

    sci.compositeAlpha = VK_COMPOSITE_ALPHA_OPAQUE_BIT_KHR;

    sci.presentMode = VK_PRESENT_MODE_FIFO_KHR;

    sci.clipped = VK_TRUE;

    VK_CHECK(vkCreateSwapchainKHR(g_dev, &sci, NULL, &g_swapchain));

    g_swapchain_fmt = VK_FORMAT_B8G8R8A8_UNORM;

    vkGetSwapchainImagesKHR(g_dev, g_swapchain, &g_swapchain_img_count, NULL);

    g_swapchain_imgs = malloc(sizeof(VkImage) * g_swapchain_img_count);

    vkGetSwapchainImagesKHR(g_dev, g_swapchain, &g_swapchain_img_count, g_swapchain_imgs);

}

void CreateImageViews(void) {

    g_swapchain_img_views = malloc(sizeof(VkImageView) * g_swapchain_img_count);

    for (uint32_t i = 0; i < g_swapchain_img_count; i++) {

        VkImageViewCreateInfo vci = {0};

        vci.sType = VK_STRUCTURE_TYPE_IMAGE_VIEW_CREATE_INFO;

        vci.image = g_swapchain_imgs[i];

        vci.viewType = VK_IMAGE_VIEW_TYPE_2D;

        vci.format = g_swapchain_fmt;

        vci.subresourceRange.aspectMask = VK_IMAGE_ASPECT_COLOR_BIT;

        vci.subresourceRange.baseMipLevel = 0;

        vci.subresourceRange.levelCount = 1;

        vci.subresourceRange.baseArrayLayer = 0;

        vci.subresourceRange.layerCount = 1;

        vkCreateImageView(g_dev, &vci, NULL, &g_swapchain_img_views[i]);

    }

}

static void CreateRenderPass(void) {

    VkAttachmentDescription att = {0};

    att.format = g_swapchain_fmt;

    att.samples = VK_SAMPLE_COUNT_1_BIT;

    att.loadOp = VK_ATTACHMENT_LOAD_OP_CLEAR;

    att.storeOp = VK_ATTACHMENT_STORE_OP_STORE;

    att.stencilLoadOp = VK_ATTACHMENT_LOAD_OP_DONT_CARE;

    att.stencilStoreOp = VK_ATTACHMENT_STORE_OP_DONT_CARE;

    att.initialLayout = VK_IMAGE_LAYOUT_UNDEFINED;

    att.finalLayout = VK_IMAGE_LAYOUT_PRESENT_SRC_KHR;

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

    dep.srcStageMask = VK_PIPELINE_STAGE_COLOR_ATTACHMENT_OUTPUT_BIT;

    dep.dstStageMask = VK_PIPELINE_STAGE_COLOR_ATTACHMENT_OUTPUT_BIT;

    dep.dstAccessMask = VK_ACCESS_COLOR_ATTACHMENT_WRITE_BIT;

    VkRenderPassCreateInfo rpci = {0};

    rpci.sType = VK_STRUCTURE_TYPE_RENDER_PASS_CREATE_INFO;

    rpci.attachmentCount = 1;

    rpci.pAttachments = &att;

    rpci.subpassCount = 1;

    rpci.pSubpasses = &sub;

    rpci.dependencyCount = 1;

    rpci.pDependencies = &dep;

    vkCreateRenderPass(g_dev, &rpci, NULL, &g_render_pass);

}

static void CreateGraphicsPipeline(void) {

    VkShaderModule vs = CreateShaderModule(vert_spv, sizeof(vert_spv));

    VkShaderModule fs = CreateShaderModule(frag_spv, sizeof(frag_spv));

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

    bind_desc.stride = sizeof(float) * 6;

    bind_desc.inputRate = VK_VERTEX_INPUT_RATE_VERTEX;

    VkVertexInputAttributeDescription attr_descs[3] = {{0}};

    attr_descs[0].location = 0;

    attr_descs[0].binding = 0;

    attr_descs[0].format = VK_FORMAT_R32G32_SFLOAT;

    attr_descs[0].offset = 0;

    attr_descs[1].location = 1;

    attr_descs[1].binding = 0;

    attr_descs[1].format = VK_FORMAT_R32G32B32_SFLOAT;

    attr_descs[1].offset = sizeof(float) * 2;

    attr_descs[2].location = 2;

    attr_descs[2].binding = 0;

    attr_descs[2].format = VK_FORMAT_R32_SFLOAT;

    attr_descs[2].offset = sizeof(float) * 5;

    VkPipelineVertexInputStateCreateInfo vi = {0};

    vi.sType = VK_STRUCTURE_TYPE_PIPELINE_VERTEX_INPUT_STATE_CREATE_INFO;

    vi.vertexBindingDescriptionCount = 1;

    vi.pVertexBindingDescriptions = &bind_desc;

    vi.vertexAttributeDescriptionCount = 3;

    vi.pVertexAttributeDescriptions = attr_descs;

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

    VkPipelineLayoutCreateInfo plci = {0};

    plci.sType = VK_STRUCTURE_TYPE_PIPELINE_LAYOUT_CREATE_INFO;

    vkCreatePipelineLayout(g_dev, &plci, NULL, &g_pipeline_layout);

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

    VkDynamicState dynamic_states[] = { VK_DYNAMIC_STATE_VIEWPORT, VK_DYNAMIC_STATE_SCISSOR };
    VkPipelineDynamicStateCreateInfo ds = {0};
    ds.sType = VK_STRUCTURE_TYPE_PIPELINE_DYNAMIC_STATE_CREATE_INFO;
    ds.dynamicStateCount = 2;
    ds.pDynamicStates = dynamic_states;
    pci.pDynamicState = &ds;

    pci.layout = g_pipeline_layout;

    pci.renderPass = g_render_pass;

    vkCreateGraphicsPipelines(g_dev, VK_NULL_HANDLE, 1, &pci, NULL, &g_pipeline);

    vkDestroyShaderModule(g_dev, vs, NULL);

    vkDestroyShaderModule(g_dev, fs, NULL);

}

void CreateFramebuffers(void) {

    g_framebuffers = malloc(sizeof(VkFramebuffer) * g_swapchain_img_count);

    for (uint32_t i = 0; i < g_swapchain_img_count; i++) {

        VkFramebufferCreateInfo fci = {0};

        fci.sType = VK_STRUCTURE_TYPE_FRAMEBUFFER_CREATE_INFO;

        fci.renderPass = g_render_pass;

        fci.attachmentCount = 1;

        fci.pAttachments = &g_swapchain_img_views[i];

        fci.width = g_swapchain_ext.width;

        fci.height = g_swapchain_ext.height;

        fci.layers = 1;

        vkCreateFramebuffer(g_dev, &fci, NULL, &g_framebuffers[i]);

    }

}

static void CreateCommandPool(void) {

    VkCommandPoolCreateInfo cpci = {0};

    cpci.sType = VK_STRUCTURE_TYPE_COMMAND_POOL_CREATE_INFO;

    cpci.queueFamilyIndex = 0;

    cpci.flags = VK_COMMAND_POOL_CREATE_RESET_COMMAND_BUFFER_BIT;

    vkCreateCommandPool(g_dev, &cpci, NULL, &g_cmd_pool);

}

static void CreateCommandBuffers(void) {

    g_cmd_buf_count = g_swapchain_img_count;

    g_cmd_bufs = malloc(sizeof(VkCommandBuffer) * g_cmd_buf_count);

    VkCommandBufferAllocateInfo ai = {0};

    ai.sType = VK_STRUCTURE_TYPE_COMMAND_BUFFER_ALLOCATE_INFO;

    ai.commandPool = g_cmd_pool;

    ai.level = VK_COMMAND_BUFFER_LEVEL_PRIMARY;

    ai.commandBufferCount = g_cmd_buf_count;

    vkAllocateCommandBuffers(g_dev, &ai, g_cmd_bufs);

}

static void CreateSyncObjects(void) {

    g_img_avail_sems = malloc(sizeof(VkSemaphore) * g_swapchain_img_count);

    g_render_done_sems = malloc(sizeof(VkSemaphore) * g_swapchain_img_count);

    g_in_flight_fences = malloc(sizeof(VkFence) * g_swapchain_img_count);

    VkSemaphoreCreateInfo sci = {0};

    sci.sType = VK_STRUCTURE_TYPE_SEMAPHORE_CREATE_INFO;

    VkFenceCreateInfo fci = {0};

    fci.sType = VK_STRUCTURE_TYPE_FENCE_CREATE_INFO;

    fci.flags = VK_FENCE_CREATE_SIGNALED_BIT;

    for (uint32_t i = 0; i < g_swapchain_img_count; i++) {

        vkCreateSemaphore(g_dev, &sci, NULL, &g_img_avail_sems[i]);

        vkCreateSemaphore(g_dev, &sci, NULL, &g_render_done_sems[i]);

        vkCreateFence(g_dev, &fci, NULL, &g_in_flight_fences[i]);

    }

}

static void CreateVertexBuffer(void) {

    VkDeviceSize buf_size = sizeof(float) * 6 * MAX_VERTICES;

    CreateBuffer(buf_size, VK_BUFFER_USAGE_VERTEX_BUFFER_BIT,

                 VK_MEMORY_PROPERTY_HOST_VISIBLE_BIT | VK_MEMORY_PROPERTY_HOST_COHERENT_BIT,

                 &g_vert_buf, &g_vert_buf_mem);

}

#ifdef _WIN32
void Render_Init(HWND hwnd, int width, int height, HINSTANCE hinst) {

    g_hwnd = hwnd;

    g_hinst = hinst;

    g_swapchain_ext = (VkExtent2D){(uint32_t)width, (uint32_t)height};
#else
void Render_Init(void *metal_layer, int width, int height) {

    g_metal_layer = metal_layer;

    // The swapchain must track the CAMetalLayer's PHYSICAL pixel size
    // (drawableSize), not the requested point size.
    Mac_GetDrawableSize(&width, &height);

    g_swapchain_ext = (VkExtent2D){(uint32_t)width, (uint32_t)height};
#endif

    CreateInstance();

    CreateSurface();

    PickPhysicalDevice();

    CreateLogicalDevice();

    CreateSwapchain();

    CreateImageViews();

    CreateRenderPass();

    CreateGraphicsPipeline();

    CreateFramebuffers();

    CreateCommandPool();

    CreateCommandBuffers();

    CreateSyncObjects();

    CreateVertexBuffer();

    Tex_CreateResources();

    g_is_ready = true;

}

int Render_IsReady(void) {

    return g_is_ready ? 1 : 0;

}

void update_vertex_buffer(const void *data, VkDeviceSize size) {

    void *mapped_data;

    vkMapMemory(g_dev, g_vert_buf_mem, 0, size, 0, &mapped_data);

    memcpy(mapped_data, data, size);

    vkUnmapMemory(g_dev, g_vert_buf_mem);

}

void CleanupSwapchain(void) {
    for (uint32_t i = 0; i < g_swapchain_img_count; i++) {
        vkDestroyFramebuffer(g_dev, g_framebuffers[i], NULL);
    }
    free(g_framebuffers);

    for (uint32_t i = 0; i < g_swapchain_img_count; i++) {
        vkDestroyImageView(g_dev, g_swapchain_img_views[i], NULL);
    }
    free(g_swapchain_img_views);
    free(g_swapchain_imgs);

    vkDestroySwapchainKHR(g_dev, g_swapchain, NULL);
}

void RecreateSwapchain(void) {
    int width = 0, height = 0;
#ifdef _WIN32
    RECT rect;
    if (GetClientRect(g_hwnd, &rect)) {
        width = rect.right - rect.left;
        height = rect.bottom - rect.top;
    }
#else
    Mac_GetDrawableSize(&width, &height);
#endif
    if (width == 0 || height == 0) return;

#ifdef __APPLE__
    // Cancel pending reads FIRST.  A reader that already passed its
    // available check is holding the busy flag and will read the OLD
    // extent+buffer pair — still intact at this point, so it is safe;
    // Mac_CreateReadbackBuffer below waits it out.
    __atomic_store_n(&g_readback_requested, 0, __ATOMIC_SEQ_CST);
    __atomic_store_n(&g_readback_available, 0, __ATOMIC_SEQ_CST);
#endif

    vkDeviceWaitIdle(g_dev);

#ifdef __APPLE__
    // Wait out any in-flight CPU read (it finishes on the old pair because
    // the extent has not been touched yet), then replace the staging buffer.
    Mac_CreateReadbackBuffer((uint32_t)width, (uint32_t)height);
#endif

    CleanupSwapchain();

    g_swapchain_ext = (VkExtent2D){(uint32_t)width, (uint32_t)height};
    CreateSwapchain();
    CreateImageViews();
    CreateFramebuffers();
}

void Render_Cleanup(void) {

    if (!g_is_ready) return;

    vkDeviceWaitIdle(g_dev);

    CleanupSwapchain();

    for (uint32_t i = 0; i < g_swapchain_img_count; i++) {
        vkDestroySemaphore(g_dev, g_img_avail_sems[i], NULL);
        vkDestroySemaphore(g_dev, g_render_done_sems[i], NULL);
        vkDestroyFence(g_dev, g_in_flight_fences[i], NULL);
    }
    free(g_img_avail_sems);
    free(g_render_done_sems);
    free(g_in_flight_fences);

    vkFreeCommandBuffers(g_dev, g_cmd_pool, g_cmd_buf_count, g_cmd_bufs);
    free(g_cmd_bufs);
    vkDestroyCommandPool(g_dev, g_cmd_pool, NULL);

    Tex_DestroyResources();

    vkDestroyPipeline(g_dev, g_pipeline, NULL);
    vkDestroyPipelineLayout(g_dev, g_pipeline_layout, NULL);
    vkDestroyRenderPass(g_dev, g_render_pass, NULL);

    vkDestroyBuffer(g_dev, g_vert_buf, NULL);
    vkFreeMemory(g_dev, g_vert_buf_mem, NULL);

    vkDestroySurfaceKHR(g_inst, g_surface, NULL);
    vkDestroyDevice(g_dev, NULL);
    vkDestroyInstance(g_inst, NULL);

    g_is_ready = false;
}