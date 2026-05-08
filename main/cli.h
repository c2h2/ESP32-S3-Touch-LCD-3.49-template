#pragma once
#ifdef __cplusplus
extern "C" {
#endif

/* Bring up the USB-Serial-JTAG console with a small set of debug commands:
   help, mem, wifi, audio_off, radio_init, radio_play <url>, radio_stop,
   radio_status, radio_test. Call once after Wi-Fi/UI are running. */
void cli_start(void);

#ifdef __cplusplus
}
#endif
