#version 450

// Full-screen triangle for every post pass.  The three vertices cover the
// target, and v_uv interpolates 0..1 across it regardless of resolution.
layout(location = 0) out vec2 v_uv;

void main() {
    vec2 p = vec2(float((gl_VertexIndex << 1) & 2), float(gl_VertexIndex & 2));
    gl_Position = vec4(p * 2.0 - 1.0, 0.0, 1.0);
    v_uv = p;
}
