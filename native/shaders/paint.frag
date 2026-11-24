#version 450

layout(location = 0) in vec3 frag_color;
layout(location = 1) in float frag_alpha;
layout(location = 0) out vec4 out_color;

void main() {
    out_color = vec4(frag_color, frag_alpha);
}
