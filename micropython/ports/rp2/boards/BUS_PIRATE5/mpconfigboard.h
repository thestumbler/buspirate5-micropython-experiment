// Board and hardware specific configuration
#define MICROPY_HW_BOARD_NAME                   "Bus Pirate 5 RP2040"
#define MICROPY_HW_FLASH_STORAGE_BYTES          (1408 * 1024)
// #define MICROPY_HW_FLASH_STORAGE_BYTES          (8 * 1024 * 1024)

// Define flash label (this doesn't work on RP2 port)
// #define MICROPY_HW_FLASH_FS_LABEL     "rp5"
// Whether to include doc strings (increases RAM usage)
#define MICROPY_ENABLE_DOC_STRING (1)

//#define MICROPY_PY_BUILTINS_HELP_TEXT           bp5_help_text
#define BUS_PIRATE5_HELP
