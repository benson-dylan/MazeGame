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
float constant = 1.0;
float linear = 0.05;
float quadratic = 0.003;

uniform sampler2D imageTexture;
uniform int numLights;
uniform PointLight Lights[MAX_LIGHTS];
uniform vec3 cameraPosition;
uniform vec3 cameraDirection;
uniform int lightsOn;
uniform int flashlight;

vec3 calculatePointLight(PointLight light, vec3 fragmentPosition, vec3 fragmentNormal);
vec3 calculateSpotLight();

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
        if (flashlight == 1)
            temp += calculateSpotLight();
    }
    else if (flashlight == 1)
            temp += calculateSpotLight();
    
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

vec3 calculateSpotLight()
{
    vec3 LightToPixel = normalize(cameraPosition - fragmentPosition);
    float SpotFactor = dot(LightToPixel, cameraDirection);
    float cutoff = 0.9;

    if (SpotFactor > cutoff)
    {
        vec3 Color = texture(imageTexture, fragmentTexCoord).rgb;
        float intensity = (1.0 - (1.0 - SpotFactor)/(1.0 - cutoff));
        return Color * intensity;
    }
    else
    {
        return vec3(0.0, 0.0, 0.0);
    }

    // vec3 result = vec3(0.0);

    // float distance = length(cameraPosition - fragmentPosition);
    // float attenuation = 1.0 / (constant + linear * distance + quadratic * (distance * distance));
    

    // float cutoff = 30;
    // float outerCutoff = 45;
    // vec3 toCamera = normalize(cameraPosition - fragmentPosition);
    // float theta = dot(cameraDirection, toCamera);
    // float epsilon = cutoff - outerCutoff;
    // float intensity = clamp((theta - outerCutoff) / epsilon, 0.0, 1.0);

    // float innerOuterConeSmoothStep = smoothstep(outerCutoff, cutoff, theta);
    // attenuation *= innerOuterConeSmoothStep;

    // result += vec3(1.0) * intensity * texture(imageTexture, fragmentTexCoord).rgb * attenuation;
    // return result;
}