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

const int MAX_LIGHTS = 100;

uniform sampler2D imageTexture;
uniform int numLights;
uniform PointLight Lights[MAX_LIGHTS];
uniform vec3 cameraPosition;
uniform int lightsOn;

vec3 calculatePointLight(PointLight light, vec3 fragmentPosition, vec3 fragmentNormal);

void main()
{
    // Ambient Light
    vec4 baseTexture = texture(imageTexture, fragmentTexCoord);
    vec3 temp = 0.03 * baseTexture.rgb;

    //printf("%d", numLights);

    if (lightsOn == 1) {
        for (int i = 0; i < numLights; i++)
        {
            temp += calculatePointLight(Lights[i], fragmentPosition, fragmentNormal);
        }
    }

    color = vec4(temp, baseTexture.a);
    
}

vec3 calculatePointLight(PointLight light, vec3 fragmentPosition, vec3 fragmentNormal) {

    vec3 result = vec3(0.0);

    // Geometric Data
    vec3 N = normalize(fragmentNormal);
    vec3 L = light.position.xyz - fragmentPosition;
    // vec3 L = light.position.xyz;
    float distance = length(L);
    L = normalize(L);
    vec3 fragCamera = normalize(cameraPosition - fragmentPosition);
    vec3 HV = normalize(L + fragCamera);

    // Diffuse Light
    result += light.color * light.intensity * max(0.0, dot(N, L)) / (distance * distance) * texture(imageTexture, fragmentTexCoord).rgb;

    // Specular Light
    // result += light.color * light.intensity * pow(max(0.0, dot(fragmentNormal, HV)), 32) / (distance * distance);

    return result;
}