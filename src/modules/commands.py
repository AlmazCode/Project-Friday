from .serialization.pather import Pather
from .console import Console
from .utilities import tokens_to_digits, encode_text
from core import data

from core.config import (
    WP_DISAMBIGUATION_ERROR, WP_PAGE_ERROR, WP_ANOTHER_ERROR,
    TM_STARTED_TEXT, TM_SOUND_PATH,
    PYTTSX3_RATE, PYTTSX3_VOLUME
)

from transliterate import translit
from gtts import gTTS

import random
import pyttsx3
import pygame
import time
import subprocess
import webbrowser
import threading
import wikipedia


pyttsx3_voice_engine = pyttsx3.init()
pyttsx3_voice_engine.setProperty("rate", PYTTSX3_RATE)
pyttsx3_voice_engine.setProperty("volume", PYTTSX3_VOLUME)


#region Commands

def tts(*args: tuple[str]) -> None:
    from core import Assistant

    text = " ".join(args)
    file_name = Pather.collect_path("data", encode_text(text) + ".mp3")

    # offline mode; uses Pyttsx3 library
    if not data.HAS_INTERNET:
        
        pyttsx3_voice_engine.save_to_file(file_name)
        Assistant._instance.equalizer.play_audio(file_name)
    
    # online mode; uses Google Text To Speech library
    elif data.HAS_INTERNET:
        
        voice = gTTS(text = text, lang = "ru", slow = False)
        voice.save(file_name)

        Assistant._instance.equalizer.play_audio(file_name)

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
        Console.error(f"Couldn't open the {path}")
        tts("К сожалению, у меня не получилось открыть данное приложение.")

def open_url(url: str) -> None:
    webbrowser.open_new(url)

def _timer(string: str) -> None:

    string = string.split()
    numbers, mul = string[:-1], string[-1]
    value = sum([i for i in tokens_to_digits(numbers)])

    match mul.lower()[0]:
        case "s":
            ...
        case "m":
            value *= 60
        case "h":
            value *= 3600
    
    time.sleep(value)
    
    player = pygame.mixer.Sound(Pather.collect_path(TM_SOUND_PATH))
    player.play()

def start_timer(string: str) -> None:
    stream = threading.Thread(target = _timer, args = (string,))
    stream.start()
    tts(TM_STARTED_TEXT)

def random_number(a: str, b: str) -> None:

    a = tokens_to_digits([a])[0]
    b = tokens_to_digits([b])[0]

    if a >= b:
        tts(str(random.randint(b, a)))
    else:
        tts(str(random.randint(a, b)))


def search(query: str, lang: str = 'ru', sentences: int = 5) -> str:
    """
    Fetches a brief summary from Wikipedia for a given query.

    This function attempts to find a Wikipedia page matching the query
    and return a summary of the specified length. It handles common
    errors like missing pages or ambiguous search terms.

    :param query: The search term (e.g., "Apple").
    :type query: str
    :param lang: The language code for Wikipedia (e.g., 'en', 'ru'). 
                 Default is 'ru'.
    :type lang: str
    :param sentences: The desired number of sentences in the summary.
                  Default is 5.
    :type sentences: int
    :return: A string containing the summary or a user-friendly
             error message if the page is not found or is ambiguous.
    :rtype: str
    """
    
    try:
        wikipedia.set_lang(lang)
        
        # Get the summary. 
        # auto_suggest=True will try to fix typos
        summary = wikipedia.summary(query, sentences=sentences, auto_suggest=True)
        return summary
    
    except wikipedia.exceptions.DisambiguationError as e:
        # This error occurs if the query is ambiguous (e.g., "Luk" or "Bow")
        options = ", ".join(e.options[:5]) # Get the first 5 options
        return WP_DISAMBIGUATION_ERROR.format(query=query, options=options)
        
    except wikipedia.exceptions.PageError:
        # This error occurs if no page matches the query
        return WP_PAGE_ERROR.format(query=query)
        
    except Exception as e:
        # Catch all other potential errors (e.g., network issues)
        Console.error(f"An error occurred while searching for '{query}': {e}")
        return WP_ANOTHER_ERROR

#endregion