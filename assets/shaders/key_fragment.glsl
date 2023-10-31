#version 330 core
out vec4 FragColor;

void main()
{
    vec3 goldColor = vec3(1.0, 0.84, 0.0);  // RGB values for gold
    FragColor = vec4(goldColor, 1.0);
}