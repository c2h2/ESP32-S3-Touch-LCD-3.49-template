#pragma once
#include <stdint.h>
#include <stdbool.h>
#include "esp_err.h"

#ifdef __cplusplus
extern "C" {
#endif

esp_err_t audio_min_init(void);
void      audio_min_play_midi(bool play);
bool      audio_min_is_playing(void);
/* Software gain, 0..100. Applied per-sample before I2S write. */
void      audio_min_set_volume(uint8_t vol_0_100);

#ifdef __cplusplus
}
#endif
