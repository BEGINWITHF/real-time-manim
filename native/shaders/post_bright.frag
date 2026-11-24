#version 450

// Bright-pass + 2x downsample.  The target is half the scene resolution, so
// v_uv sits at the centre of a 2x2 source block; averaging the four texels
// avoids the aliasing a single point sample would give.
layout(location = 0) in vec2 v_uv;
layout(location = 0) out vec4 out_color;

layout(set = 0, binding = 0) uniform sampler2D u_scene;

layout(push_constant) uniform Push {
    vec4 p0;   // threshold, knee, strength, exposure
    vec4 p1;   // tonemap, radius, unused, unused
} pc;

void main() {
    vec2 t = 1.0 / vec2(textureSize(u_scene, 0));
    vec3 c = 0.25 * (
        texture(u_scene, v_uv + vec2(-0.5, -0.5) * t).rgb +
        texture(u_scene, v_uv + vec2( 0.5, -0.5) * t).rgb +
        texture(u_scene, v_uv + vec2(-0.5,  0.5) * t).rgb +
        texture(u_scene, v_uv + vec2( 0.5,  0.5) * t).rgb);

    // Soft-knee threshold: below `threshold` the contribution is zero, and the
    // knee ramps it in so a gradient of highlights does not get a hard edge.
    float l = max(c.r, max(c.g, c.b));
    float knee = max(pc.p0.y, 1e-4);
    float soft = clamp(l - pc.p0.x + knee, 0.0, 2.0 * knee);
    soft = soft * soft / (4.0 * knee + 1e-4);
    float weight = max(soft, l - pc.p0.x) / max(l, 1e-4);
    out_color = vec4(c * weight, 1.0);
}
