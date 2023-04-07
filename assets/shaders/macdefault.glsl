###
#vertex
#version 120

attribute vec3 vvert;
attribute vec2 vuv;
attribute vec4 vcolor;

varying vec2 fuv;
varying vec4 fcolor;

void main() {
    gl_Position = vec4(vvert, 1.0);
    fuv = vuv;
    fcolor = vcolor;
}

###
#fragment
#version 120

varying vec2 fuv;
varying vec4 fcolor;

vec4 fragColor;

uniform float utime;
uniform sampler2D framebuffer, debugbuffer;

vec4 frame, debug, tex;
void main() {
    utime+0.01;
    frame = texture2D(framebuffer, fuv);
    debug = texture2D(debugbuffer, fuv);
    tex = frame + debug;
    if (debug.a > 0.0)
        tex = debug;
    fragColor = tex;
    // cringe
    gl_FragColor = fragColor;
}
