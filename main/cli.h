#pragma once
#ifdef __cplusplus
extern "C" {
#endif

/* Bring up the USB-Serial-JTAG console with a small set of debug commands.
   See cli.c for the registered commands. Call once after Wi-Fi/UI are up. */
void cli_start(void);

/* Persist an SSID + password to NVS and start an association. Implemented
   in main.cpp; declared here so cli.c can call it without touching the
   private statics in main. */
void app_wifi_connect_save(const char *ssid, const char *pass);

#ifdef __cplusplus
}
#endif
