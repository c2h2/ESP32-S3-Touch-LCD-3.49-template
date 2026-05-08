/* Curated internet-radio station list. Each URL was probed live with
   scripts/probe_radio.py and confirmed to return MP3 or AAC bytes:
     - HTTP 200/206 with audio/mpeg or audio/aac(p) Content-Type
     - First few KB carry an MPEG/ADTS sync (or ID3 tag prefix)
     - No HLS m3u8 / DASH / HTML splash redirects
   Stations are grouped by region. Ordered roughly by public popularity
   within each group.

   Notes:
   - BBC public streams are HLS-only as of 2024; not playable here.
   - URLs without a .mp3 extension rely on simple_player content sniffing,
     which works because we hand it audio/mpeg or audio/aacp bytes.
   - Some stations (Radio Paradise, WNYC, Triple J) advertise audio/aac
     even on "mp3" endpoints; esp_audio_codec handles both.
*/
#pragma once

#include <stdint.h>

typedef struct {
    const char *name;
    const char *genre;
    const char *url;
} radio_station_t;

static const radio_station_t k_stations[] = {
    /* North America */
    { "KEXP Seattle",          "Indie",        "https://kexp-mp3-128.streamguys1.com/kexp128.mp3" },
    { "NPR News",              "News US",      "https://npr-ice.streamguys1.com/live.mp3" },
    { "WNYC FM",               "News/talk NY", "https://fm939.wnyc.org/wnycfm.aac" },
    { "WFMU",                  "Free-form",    "http://stream0.wfmu.org/freeform-128k.mp3" },
    { "Radio Paradise",        "Eclectic",     "http://stream.radioparadise.com/mp3-128" },
    { "Radio Paradise Mellow", "Mellow mix",   "http://stream.radioparadise.com/mellow-128" },
    { "Radio Paradise Rock",   "Rock mix",     "http://stream.radioparadise.com/rock-128" },

    /* SomaFM */
    { "SomaFM Groove Salad",   "Ambient",      "http://ice1.somafm.com/groovesalad-128-mp3" },
    { "SomaFM Drone Zone",     "Deep ambient", "http://ice1.somafm.com/dronezone-128-mp3" },
    { "SomaFM Lush",           "Vocal chill",  "http://ice1.somafm.com/lush-128-mp3" },
    { "SomaFM Indie Pop",      "Indie pop",    "http://ice1.somafm.com/indiepop-128-mp3" },
    { "SomaFM Secret Agent",   "Spy lounge",   "http://ice1.somafm.com/secretagent-128-mp3" },
    { "SomaFM Deep Space One", "Space music",  "http://ice1.somafm.com/deepspaceone-128-mp3" },

    /* UK */
    { "Classic FM",            "Classical UK", "https://media-ice.musicradio.com/ClassicFMMP3" },
    { "Capital FM",            "Pop UK",       "https://media-ssl.musicradio.com/CapitalMP3" },

    /* Germany / Austria */
    { "Antenne Bayern",        "Pop DE",       "http://s6-webradio.antenne.de/antenne" },
    { "Rock Antenne",           "Rock DE",      "http://stream.rockantenne.de/rockantenne" },
    { "FM4",                    "Alt AT",       "https://orf-live.ors-shoutcast.at/fm4-q2a" },

    /* France */
    { "Radio FIP",             "Eclectic FR",  "https://icecast.radiofrance.fr/fip-midfi.mp3" },
    { "Radio Nova FR",         "Eclectic FR",  "http://novazz.ice.infomaniak.ch/novazz-128.mp3" },

    /* Italy */
    { "RAI Radio 1",            "News IT",      "https://icestreaming.rai.it/1.mp3" },
    { "RAI Radio 2",            "Pop IT",       "https://icestreaming.rai.it/2.mp3" },
    { "RAI Radio 3",            "Classical IT", "https://icestreaming.rai.it/3.mp3" },
    { "RTL 102.5",              "Pop IT",       "https://streamingv2.shoutcast.com/rtl-1025" },

    /* Switzerland */
    { "Radio Swiss Jazz",      "Jazz CH",      "http://stream.srg-ssr.ch/m/rsj/mp3_128" },
    { "Radio Swiss Classic",   "Classical CH", "http://stream.srg-ssr.ch/m/rsc_de/mp3_128" },

    /* Benelux */
    { "VRT Klara",              "Classical BE", "https://icecast.vrtcdn.be/klara-high.mp3" },
    { "VRT Studio Brussel",     "Indie BE",     "https://icecast.vrtcdn.be/stubru-high.mp3" },
    { "Radio 1 NL",             "News NL",      "https://icecast.omroep.nl/radio1-bb-mp3" },
    { "3FM NL",                 "Pop NL",       "https://icecast.omroep.nl/3fm-bb-mp3" },

    /* Spain */
    { "Cadena SER",             "News ES",      "https://playerservices.streamtheworld.com/api/livestream-redirect/CADENASER.mp3" },

    /* Poland */
    { "RMF FM",                 "Pop PL",       "http://195.150.20.5/rmf_fm" },

    /* Asia / Oceania */
    { "MetaRadio Tokyo",        "Pop JP",       "http://192.95.39.65:5607/stream" },
    { "Triple J",              "Alt pop AU",   "https://abc.streamguys1.com/live/triplejnsw/icecast.audio" },
};

#define RADIO_STATION_COUNT ((int)(sizeof(k_stations) / sizeof(k_stations[0])))
