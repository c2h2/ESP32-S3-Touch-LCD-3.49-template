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

/* Stop the MIDI task, disable + destroy I2S TX channel and ES8311 device.
   Call before handing the codec/I2S over to another engine (radio etc). */
void      audio_min_shutdown(void);

#ifdef __cplusplus
}
#endif
