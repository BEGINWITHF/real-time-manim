#version 450

// Solid-colour vertex stage.  Positions arrive already in NDC (the Python
// senders do the camera projection); z is a per-paint-unit depth used by the
// depth test against the mesh, and 0 means "in front of everything" for 2D
// overlays.
layout(location = 0) in vec2 in_pos;
layout(location = 1) in float in_z;
layout(location = 2) in vec3 in_color;
layout(location = 3) in float in_alpha;

layout(location = 0) out vec3 frag_color;
layout(location = 1) out float frag_alpha;

void main() {
    gl_Position = vec4(in_pos, in_z, 1.0);
    frag_color = in_color;
    frag_alpha = in_alpha;
}
