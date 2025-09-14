from . import data
from .constants import Constants
from .config import *
from .lexer import lexer
from .parser import parser

from modules import Pather, WORK_DIR, STARTUP_PATH
from modules import commands
from modules import Console

from art import tprint
from typing import NoReturn
from vosk import Model, KaldiRecognizer
from queue import Queue

import random
import sounddevice as sd
import json
import os


class Assistant:

    def __init__(self) -> None:
        
        self.model = Model(Pather.collect_path("models", VOSK_MODEL))
        self.recognizer = KaldiRecognizer(self.model, SD_SAMPLERATE)
        self.queue = Queue()

        ...

        Console.clear()

        # Title text printing
        print(Console.Color.Fore.GREEN)
        tprint(TITLE_TEXT, random.choice(TEXT_ART_FONTS))
        print(Console.Color.Style.RESET)

        Console.log(f"Vosk recognizer model: {VOSK_MODEL}")

        if data.HAS_INTERNET:
            Console.log("You're online")
        else:
            Console.warning("You're offline")

        if data.FIRST_START:
            commands.tts(FISRT_START_TEXT)
            Pather.save(Constants.Filenames.FIRST_START, False)
            commands.tts(CAN_ADD_AUTOSTART_TEXT)

            if self.yn_listen():
                Pather.save(Constants.Filenames.USER_ALLOWED_STARTUP, True)
                path = self._create_startup_file()
                Console.log(f"The startup file was created at this path: {path}")
        
        else:
            commands.reply("GREETINGS")

    
    def listen(self, loop: bool = True) -> None | list[str]:

        with sd.RawInputStream(
            samplerate=SD_SAMPLERATE, blocksize=SD_BLOCKSIZE, dtype=SD_DTYPE,
            channels=SD_CHANNELS, callback=self._callback
        ):
            while 1:
                data = self.queue.get()
                if self.recognizer.AcceptWaveform(data):
                    text = self._get_text_from_result()
                    if text:
                        tokens = self._process_text(text, loop)
                        if not loop:
                            return tokens
    
    def yn_listen(self) -> bool:
        
        while 1:
            tokens = self.listen(False)

            if tokens[0] == "YES":
                return True
            elif tokens[0] == "NO":
                return False
    
    # ===== Private Methods =====

    def _get_text_from_result(self) -> str:
        
        result = json.loads(self.recognizer.Result())
        return result.get("text", "").strip()

    def _process_text(self, text: str, loop: bool) -> list[str]:
        
        Console.fill("-")
        Console.u_input(f"Input: {text.capitalize()}")

        tokens = lexer.tokenize(text)
        Console.u_output(f"Output: {' '.join(tokens)}")

        if loop:
            self._process_tokens(tokens)

        Console.fill("-")
        return tokens

    def _process_tokens(self, tokens: list[str]) -> None:
        
        parser.process(tokens)
        if parser.executed_actions:
            executed_actions = [
                f"\t- {e[0]}({', '.join(e[1])})" for e in parser.executed_actions
            ]
            Console.log("The functions have been executed:\n" + "\n".join(executed_actions))
    
    def _callback(self, indata, frames, time, status) -> None:
        self.queue.put(bytes(indata))
    
    def _create_startup_file(self) -> str:

        path = os.path.join(STARTUP_PATH, "assistant.bat")
        with open(path, "w+", encoding = "utf-8") as f:
            f.write(
                STARTUP_FILE.format(Pather.collect_path("src", "main.py"))
            )
        
        return path