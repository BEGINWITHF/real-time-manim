#version 450

// Lit mesh vertex stage.  Positions are already in NDC; the normal is in
// camera space (the Python side rotates it with the viewport), so the
// fragment stage can use a fixed viewer direction.
layout(location = 0) in vec3 in_pos;
layout(location = 1) in vec3 in_normal;
layout(location = 2) in vec4 in_color;

layout(location = 0) out vec3 v_normal;
layout(location = 1) out vec4 v_color;

void main() {
    gl_Position = vec4(in_pos, 1.0);
    v_normal = in_normal;
    v_color = in_color;
}
