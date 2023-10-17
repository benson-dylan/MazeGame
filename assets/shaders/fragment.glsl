#version 330 core

struct PointLight {
    vec3 position;
    vec3 color;
    float intensity;
};

in vec2 fragmentTexCoord;
in vec3 fragmentPosition;
in vec3 fragmentNormal;

out vec4 color;

uniform sampler2D imageTexture;
uniform PointLight Light;

vec3 calculatePointLight(PointLight light, vec3 fragmentPosition, vec3 fragmentNormal);

void main()
{
    vec3 temp = vec3(0.0);

    temp += calculatePointLight(Light, fragmentPosition, fragmentNormal);

    color = vec4(temp,1.0);
}

vec3 calculatePointLight(PointLight light, vec3 fragmentPosition, vec3 fragmentNormal) {

    vec3 result = vec3(0.0);
    vec3 baseTexture = texture(imageTexture, fragmentTexCoord).rgb;

    // Geometric Data
    vec3 fragLight = light.position - fragmentPosition;
    float distance = length(fragLight);
    fragLight = normalize(fragLight);

    // Ambient Light
    result += 0.2 * baseTexture;

    // Diffuse Light
    result += light.color * light.intensity * max(0.0, dot(fragmentNormal, fragLight)) / (distance * distance);

    return result;
}