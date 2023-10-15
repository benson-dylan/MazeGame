#version 330 core

layout (location=0) in vec3 vertexPos;
layout (location=1) in vec2 vertexTexCoord;

uniform mat4 model_matrix;
uniform mat4 projection_matrix;

out vec2 fragmentTexCoord;

void main()
{
    gl_Position = projection_matrix * model_matrix * vec4(vertexPos, 1.0);
    fragmentTexCoord = vertexTexCoord;
}