idf_component_register(
    SRCS "recorder.c"
    INCLUDE_DIRS "."
    REQUIRES driver fatfs i2c_bsp sdcard_bsp
             espressif__esp_codec_dev)
