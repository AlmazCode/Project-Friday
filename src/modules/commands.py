from .serialization.pather import Pather
from .console import Console
from .utilities import tokens_to_digits
from core import data

from transliterate import translit
from gtts import gTTS
from typing import NoReturn

import hashlib
import os
import random
import pyttsx3
import pygame
import time
import sys
import subprocess
import webbrowser
import threading

pygame.mixer.init()


pyttsx3_voice_engine = pyttsx3.init()
pyttsx3_voice_engine.setProperty("rate", 150)
pyttsx3_voice_engine.setProperty("volume", 1)


# ===== Functions =====

def tts(*args):
    text = " ".join(args)

    # offline mode
    if not data.HAS_INTERNET: # uses PYTTSX3
        
        pyttsx3_voice_engine.say(text)
        pyttsx3_voice_engine.runAndWait()
    
    # online mode
    elif data.HAS_INTERNET: # uses GTTS
        
        file_name = Pather.collect_path("data", hashlib.sha256(text.encode()).hexdigest() + ".mp3")
        voice = gTTS(text = text, lang = "ru", slow = False)
        voice.save(file_name)
        
        player = pygame.mixer.Sound(file_name)
        player.play()
        
        os.remove(file_name)
        time.sleep(player.get_length())

def cyrillic_to_latin(text: str) -> str:
    return translit(text, 'ru', reversed=True)

def reply(token: str) -> None:

    if token in data.ASSISTANTS_LEXICON:
        answer = random.choice(data.ASSISTANTS_LEXICON[token]).format(**data.CONTEXT)
        tts(answer)

def launch_app(path: str) -> None:
    try:
        subprocess.Popen([path])
    except:
        Console.error(f"couldn't open the {path}")
        tts("К сожалению, у меня не получилось открыть данное приложение.")

def open_url(url: str) -> None:
    webbrowser.open_new(url)

def _timer(string: str) -> None:

    string = string.split()
    numbers, mul = string[:-1], string[-1]
    value = sum([int(i) for i in tokens_to_digits(numbers)])

    match mul.lower()[0]:
        case "s":
            ...
        case "m":
            value *= 60
        case "h":
            value *= 3600
    
    time.sleep(value)
    
    player = pygame.mixer.Sound(Pather.collect_path("assets", "sounds", "timer_sound.mp3"))
    player.play()

def start_timer(string: str) -> None:
    stream = threading.Thread(target = _timer, args = (string,))
    stream.start()
    tts("Запустила!")

def random_number(a: str, b: str) -> None:

    a = tokens_to_digits([a])[0]
    b = tokens_to_digits([b])[0]

    if a >= b:
        tts(str(random.randint(b, a)))
    else:
        tts(str(random.randint(a, b)))

def quit() -> NoReturn:
    sys.exit(0)

# ==========