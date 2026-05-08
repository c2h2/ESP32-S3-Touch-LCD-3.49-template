idf_component_register(
    SRCS "radio.c"
    INCLUDE_DIRS "."
    REQUIRES driver i2c_bsp
             espressif__esp_codec_dev
             espressif__esp_audio_simple_player
             espressif__gmf_core)
