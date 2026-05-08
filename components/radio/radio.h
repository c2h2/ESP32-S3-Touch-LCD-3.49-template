#pragma once

#include <stdbool.h>
#include "esp_err.h"

#ifdef __cplusplus
extern "C" {
#endif

/* Initialise the radio engine (ES8311 + I2S + esp_audio_simple_player).
   Must be called *after* audio_min_shutdown() so the I2S/codec is free. */
esp_err_t radio_init(void);

/* Start playing a URI. The player auto-detects MP3/AAC/FLAC/etc.
   For HTTPS streams the IDF default cert bundle must be enabled. */
esp_err_t radio_play(const char *uri);

/* Stop playback. Safe to call when already stopped. */
esp_err_t radio_stop(void);

/* True iff the player is currently in the RUNNING state. */
bool      radio_is_playing(void);

#ifdef __cplusplus
}
#endif
