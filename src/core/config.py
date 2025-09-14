from modules.commands import cyrillic_to_latin


VERSION = "1.0 pre-alpha"

USER_NAME = "Джон"
USER_NAME_LATIN = cyrillic_to_latin(USER_NAME)
ASSISTANT_NAME = "Пятница"

TITLE_TEXT = f"Project Friday\nv{VERSION}"
FISRT_START_TEXT = f"Здравствуйте, я {ASSISTANT_NAME}, ваш голосовой помощник."
CAN_ADD_AUTOSTART_TEXT = "Для вашего удобства, могу ли я добавить себя в автозапуск?"

TEXT_ART_FONTS = [
    "standart",
    "colossal",
    "tarty1",
]

VOSK_MODEL = "vosk-model-small-ru-0.22"

STARTUP_FILE =  "chp 65001\n" + \
                "python \"{0}\""

# ===== Sounddevice settings =====
SD_SAMPLERATE   = 16000
SD_BLOCKSIZE    = 8000
SD_DTYPE        = "int16"
SD_CHANNELS     = 1