#version 450

// Textured-quad vertex stage.  Positions arrive already in NDC (the same space
// the solid-colour pipeline feeds gl_Position), so this stage only forwards the
// texture coordinate and the per-vertex alpha.
layout(location = 0) in vec2 in_pos;
layout(location = 1) in vec2 in_uv;
layout(location = 2) in float in_alpha;

layout(location = 0) out vec2 v_uv;
layout(location = 1) out float v_alpha;

void main() {
    gl_Position = vec4(in_pos, 0.0, 1.0);
    v_uv = in_uv;
    v_alpha = in_alpha;
}
