#version 450

// Final composite: scene + bloom, exposure, then an optional tone curve.
// `none` only clamps, so enabling bloom does not change the base image; `aces`
// and `reinhard` are opt-in grades for a filmic highlight roll-off.
layout(location = 0) in vec2 v_uv;
layout(location = 0) out vec4 out_color;

layout(set = 0, binding = 0) uniform sampler2D u_scene;
layout(set = 0, binding = 1) uniform sampler2D u_bloom;

layout(push_constant) uniform Push {
    vec4 p0;   // threshold, knee, strength, exposure
    vec4 p1;   // tonemap, radius, unused, unused
} pc;

vec3 aces(vec3 x) {
    return clamp((x * (2.51 * x + 0.03)) /
                 (x * (2.43 * x + 0.59) + 0.14), 0.0, 1.0);
}

vec3 reinhard(vec3 x) {
    return x / (1.0 + x);
}

void main() {
    vec3 scene = texture(u_scene, v_uv).rgb;
    vec3 bloom = texture(u_bloom, v_uv).rgb;
    vec3 c = (scene + bloom * pc.p0.z) * pc.p0.w;

    int mode = int(pc.p1.x + 0.5);
    if (mode == 1) {
        c = aces(c);
    } else if (mode == 2) {
        c = reinhard(c);
    }
    out_color = vec4(clamp(c, 0.0, 1.0), 1.0);
}
