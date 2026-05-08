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

/* Curated station list. Indices are stable; see components/radio/stations.h. */
int          radio_station_count(void);
const char  *radio_station_name(int idx);
const char  *radio_station_genre(int idx);
const char  *radio_station_url(int idx);

/* Start a station from the curated list. Stops any current stream first. */
esp_err_t    radio_play_index(int idx);

/* Index of the most recently requested station, -1 if none yet. */
int          radio_current_index(void);

/* Output volume 0..100. Applied through the ES8311 codec, so it's a real
   analog gain change (not just a digital scale). */
void         radio_set_volume(int vol_0_100);
int          radio_get_volume(void);

#ifdef __cplusplus
}
#endif
