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
uniform PointLight Lights[8];
uniform vec3 cameraPosition;

vec3 calculatePointLight(PointLight light, vec3 fragmentPosition, vec3 fragmentNormal);

void main()
{
    // Ambient Light
    vec4 baseTexture = texture(imageTexture, fragmentTexCoord);
    vec3 temp = 0.2 * baseTexture.rgb;

    for (int i = 0; i < 8; i++)
    {
        temp += calculatePointLight(Lights[i], fragmentPosition, fragmentNormal);
    }

    color = vec4(temp, baseTexture.a);
    
}

vec3 calculatePointLight(PointLight light, vec3 fragmentPosition, vec3 fragmentNormal) {

    vec3 result = vec3(0.0);

    // Geometric Data
    vec3 fragLight = light.position - fragmentPosition;
    float distance = length(fragLight);
    fragLight = normalize(fragLight);
    vec3 fragCamera = normalize(cameraPosition - fragmentPosition);
    vec3 HV = normalize(fragLight + fragCamera);

    

    // Diffuse Light
    result += light.color * light.intensity * max(0.0, dot(fragmentNormal, fragLight)) / (distance * distance) * texture(imageTexture, fragmentTexCoord).rgb;

    // Specular Light
    result += light.color * light.intensity * pow(max(0.0, dot(fragmentNormal, HV)), 32) / (distance * distance);

    return result;
}