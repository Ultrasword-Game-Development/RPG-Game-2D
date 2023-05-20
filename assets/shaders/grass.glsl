###
#vertex
#version 300 es

in vec3 vvert;
in vec2 vuv;
in vec4 vcolor;

out vec2 fuv;
out vec4 fcolor;

void main() {
    gl_Position = vec4(vvert, 1.0);
    fuv = vuv;
    fcolor = vcolor;
}

###
#fragment
#version 300 es
precision mediump float;

in vec2 fuv;
in vec4 fcolor;

out vec4 fragColor;

uniform float utime;
uniform sampler2D framebuffer, debugbuffer;

void main() {
    utime+0.01;
    vec4 frame = texture(framebuffer, fuv);
    vec4 debug = texture(debugbuffer, fuv);
    vec4 tex = frame + debug;
    if (debug.a > 0.0)
        tex = debug;
    fragColor = tex;
}
