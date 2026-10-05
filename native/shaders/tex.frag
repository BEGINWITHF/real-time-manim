#version 450

// Textured-quad fragment stage.  Samples the mobject's pixel data (an
// ImageMobject / rasterised camera frame) and folds the per-quad opacity into
// the alpha channel; the pipeline uses the same SRC_ALPHA /
// ONE_MINUS_SRC_ALPHA blend as the solid-colour pipeline, so fading an image
// fades it exactly like a shape.
layout(location = 0) in vec2 v_uv;
layout(location = 1) in float v_alpha;

layout(location = 0) out vec4 out_color;

layout(set = 0, binding = 0) uniform sampler2D tex;

void main() {
    vec4 c = texture(tex, v_uv);
    out_color = vec4(c.rgb, c.a * v_alpha);
}
