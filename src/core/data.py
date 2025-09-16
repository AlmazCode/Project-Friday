import datetime
import platform

from .config import USER_NAME, ASSISTANT_NAME
from .constants import Constants

from modules.serialization.pather import Pather
from modules.utilities import get_browser_path, has_internet

# ===== Constants =====
HAS_INTERNET    = has_internet()
PLATFORM        = platform.system()

# ===== Global context =====
CONTEXT = {
    "user": USER_NAME,
    "assistant": ASSISTANT_NAME,
    "time": datetime.datetime.now().strftime("%H:%M"),
    "browser": get_browser_path(),
    "youtube": "https://www.youtube.com/",
    "github": "https://github.com/"
}

# ===== Lexicons =====
LEXICON: dict[str, list[str]]               = Pather.load_json("data\\lexicon.json")
ASSISTANTS_LEXICON: dict[str, list[str]]    = Pather.load_json("data\\assistants_lexicon.json")

PHRASES = []
for token, variants in LEXICON.items():
    for v in variants:
        PHRASES.append((v.lower().split(), token.upper()))

VARIANT_TO_DIGIT = {}
for token, variants in LEXICON.items():
    for v in variants:
        if v.isdigit():
            VARIANT_TO_DIGIT[token] = int(v)

PHRASES.sort(key=lambda x: -len(x[0]))

# ===== Commands =====
COMMANDS = Pather.load_yaml("data\\commands.yaml")

# ===== Important data =====
FIRST_START: bool           = Pather.read(Constants.Filenames.FIRST_START, True)
USER_ALLOWED_STARTUP: bool  = Pather.read(Constants.Filenames.USER_ALLOWED_STARTUP, False)
# CONSOLE_MODE = False