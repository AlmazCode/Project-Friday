VERSION = "1.0 pre-alpha"

USER_NAME               = "Джон"
ASSISTANT_NAME          = "Пятница"

TITLE_TEXT              = f"Project Friday\nv{VERSION}"
FISRT_START_TEXT        = f"Здравствуйте, я {ASSISTANT_NAME}, ваш голосовой помощник."
CAN_ADD_AUTOSTART_TEXT  = "Для вашего удобства, могу ли я добавить себя в автозапуск?"

TEXT_ART_FONTS = [
    "standart",
    "colossal",
    "tarty1",
]

VOSK_MODEL      = "vosk-model-small-ru-0.22"

STARTUP_FILE    = \
    "chcp 65001\n" + \
    "python \"{0}\""
STARTUP_FILE_NAME = f"assistant-[{VERSION}]-startup"

# ===== Sounddevice settings =====
SD_SAMPLERATE   = 16000
SD_BLOCKSIZE    = 8000
SD_DTYPE        = "int16"
SD_CHANNELS     = 1

# === Wikipedia Settings ===
WP_DISAMBIGUATION_ERROR = ("Запрос '{query}' является неоднозначным. "
                "Вы имели в виду: {options}...")
WP_PAGE_ERROR = "К сожалению, страница Википедии не найдена для '{query}'."
WP_ANOTHER_ERROR = "Произошла ошибка при подключении к Википедии. Повторите попытку позже."

# === Timer Settings ===
TM_STARTED_TEXT = "Запустила!"
TM_SOUND_NAME = "timer_sound.mp3"
TM_SOUND_PATH = ("assets", "sounds", TM_SOUND_NAME)

# === Pyttsx3 Settings ===
PYTTSX3_RATE = 100
PYTTSX3_VOLUME = 1