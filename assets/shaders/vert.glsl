#version 330 core

uniform mat4 view;
uniform mat4 projection;

// Attributes
layout (location = 0) in vec3 position;    // we can also use layout to specify the location of the attribute
layout (location = 1) in vec2 uv;
layout (location = 2) in vec3 color;

out vec3 fragColor;
out vec2 fragUV;

void main(){
    vec4 viewPosition = view * vec4(position, 1.0);
    gl_Position = projection * viewPosition;
    fragUV = uv;
    fragColor = color;
}