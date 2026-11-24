#version 450

// Separable Gaussian blur.  Five linear-sampled taps approximate a 9-tap
// kernel; the direction and radius come from the push constants so the same
// pipeline does horizontal and vertical passes.
layout(location = 0) in vec2 v_uv;
layout(location = 0) out vec4 out_color;

layout(set = 0, binding = 1) uniform sampler2D u_src;

layout(push_constant) uniform Push {
    vec4 p0;   // threshold, knee, strength, exposure (unused here)
    vec4 p1;   // tonemap, radius, direction.x, direction.y
} pc;

void main() {
    vec2 texel = 1.0 / vec2(textureSize(u_src, 0));
    vec2 dir = pc.p1.zw;
    float len = length(dir);
    dir = len > 1e-5 ? dir / len : vec2(0.0);
    vec2 d = dir * max(pc.p1.y, 0.0) * texel;

    vec3 c = texture(u_src, v_uv).rgb * 0.227027;
    c += (texture(u_src, v_uv + d * 1.3846).rgb +
          texture(u_src, v_uv - d * 1.3846).rgb) * 0.316216;
    c += (texture(u_src, v_uv + d * 3.2308).rgb +
          texture(u_src, v_uv - d * 3.2308).rgb) * 0.070270;
    out_color = vec4(c, 1.0);
}
