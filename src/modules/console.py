import sys
import os
import time


class Console:

    WIDTH = os.get_terminal_size().columns
    
    class Color:
        
        class Style:

            RESET:          str = '\033[0m'
            BOLD:           str = '\033[1m'
            DIM:            str = '\033[2m'
            ITALIC:         str = '\033[3m'
            UNDERLINE:      str = '\033[4m'
            BLINK:          str = '\033[5m'
            INVERSE:        str = '\033[7m'
            HIDDEN:         str = '\033[8m'
            STRIKETHROUGH:  str = '\033[9m'
        
        class Fore:

            BLACK:          str = '\033[30m'
            RED:            str = '\033[31m'
            GREEN:          str = '\033[32m'
            YELLOW:         str = '\033[33m'
            BLUE:           str = '\033[34m'
            MAGENTA:        str = '\033[35m'
            CYAN:           str = '\033[36m'
            WHITE:          str = '\033[37m'
            BRIGHT_BLACK:   str = '\033[90m'
            BRIGHT_RED:     str = '\033[91m'
            BRIGHT_GREEN:   str = '\033[92m'
            BRIGHT_YELLOW:  str = '\033[93m'
            BRIGHT_BLUE:    str = '\033[94m'
            BRIGHT_MAGENTA: str = '\033[95m'
            BRIGHT_CYAN:    str = '\033[96m'
            BRIGHT_WHITE:   str = '\033[97m'
        
        class Back:

            BLACK:          str = '\033[40m'
            RED:            str = '\033[41m'
            GREEN:          str = '\033[42m'
            YELLOW:         str = '\033[43m'
            BLUE:           str = '\033[44m'
            MAGENTA:        str = '\033[45m'
            CYAN:           str = '\033[46m'
            WHITE:          str = '\033[47m'
            BRIGHT_BLACK:   str = '\033[100m'
            BRIGHT_RED:     str = '\033[101m'
            BRIGHT_GREEN:   str = '\033[102m'
            BRIGHT_YELLOW:  str = '\033[103m'
            BRIGHT_BLUE:    str = '\033[104m'
            BRIGHT_MAGENTA: str = '\033[105m'
            BRIGHT_CYAN:    str = '\033[106m'
            BRIGHT_WHITE:   str = '\033[107m'

    @staticmethod
    def _get_formatted_time() -> str:
        return time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())

    @staticmethod
    def _print_message(message: str, color: str, type: str = "!Type") -> None:
        print(
            f"[{Console._get_formatted_time()}][{type}] {color}{message}{Console.Color.Style.RESET}",
            flush = True)

    @staticmethod
    def log(message: str) -> None:
        Console._print_message(message, Console.Color.Fore.WHITE, "*")
    
    @staticmethod
    def u_input(message: str) -> None:
        Console._print_message(message, Console.Color.Fore.GREEN, ">>")
    
    @staticmethod
    def u_output(message: str) -> None:
        Console._print_message(message, Console.Color.Fore.GREEN, "<<")
    
    @staticmethod
    def warning(message: str) -> None:
        Console._print_message(message, Console.Color.Fore.YELLOW, "!")

    @staticmethod
    def error(message: str) -> None:
        Console._print_message(message, Console.Color.Fore.RED, "?")

    @staticmethod
    def clear() -> None:
        os.system("cls" if sys.platform == "win32" else "clear -r")
    
    @staticmethod
    def fill(char: str) -> None:
        print(char * Console.WIDTH)