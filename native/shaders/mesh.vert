#version 450

layout(location = 0) in vec2 in_pos;
layout(location = 1) in float in_depth;
layout(location = 2) in vec4 in_color;

layout(location = 0) out vec4 frag_color;

void main() {
    gl_Position = vec4(in_pos, in_depth, 1.0);
    frag_color = in_color;
}
