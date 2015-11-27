#pragma once

#pragma include "Includes/Configuration.inc.glsl"

uniform sampler3D IESDatasetTex;


float get_ies_factor(vec3 light_vector, int profile) {
    if (profile < 0) return 1.0;

    float horiz_angle = acos(light_vector.z) / M_PI;
    float vert_angle = atan(light_vector.y, light_vector.x) / TWO_PI + 0.5;
    float profile_coord = (profile+0.5) / MAX_IES_PROFILES;
    float data = textureLod(IESDatasetTex, vec3(horiz_angle, vert_angle, profile_coord), 0).x;

    return data;
}

