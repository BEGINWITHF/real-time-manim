#version 450

// Lambert + optional Blinn-Phong highlight with a fixed camera-space viewer.
// Two-sided: a normal facing away is flipped, so back faces of an open surface
// are lit like the front instead of turning black.
layout(location = 0) in vec3 v_normal;
layout(location = 1) in vec4 v_color;
layout(location = 0) out vec4 out_color;

layout(push_constant) uniform Push {
    vec4 light;     // xyz: camera-space direction to the light; w: ambient
    vec4 material;  // x: diffuse, y: specular, z: shininess
} pc;

void main() {
    vec3 N = normalize(v_normal);
    vec3 V = vec3(0.0, 0.0, 1.0);
    if (dot(N, V) < 0.0) {
        N = -N;
    }

    vec3 L = normalize(pc.light.xyz);
    float ndl = max(dot(N, L), 0.0);

    vec3 H = normalize(L + V);
    float spec = pow(max(dot(N, H), 0.0), max(pc.material.z, 1.0))
               * pc.material.y;

    vec3 rgb = v_color.rgb * (pc.light.w + pc.material.x * ndl)
             + vec3(spec);
    out_color = vec4(rgb, v_color.a);
}
