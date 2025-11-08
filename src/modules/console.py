import sys
import os
import time
from typing import ClassVar


class Console:
    """
    A utility class providing methods for formatted console output, logging,
    and managing the terminal interface (clearing, width).

    It uses ANSI escape codes for coloring and styling terminal messages.
    """

    # Class variable to store the current width of the terminal.
    # Updated upon class definition.
    WIDTH: ClassVar[int] = os.get_terminal_size().columns
    
    class Color:
        """Container for ANSI escape codes defining colors and styles."""
        
        class Style:
            """ANSI escape codes for text formatting styles."""

            RESET: str          = '\033[0m'
            BOLD: str           = '\033[1m'
            DIM: str            = '\033[2m'
            ITALIC: str         = '\033[3m'
            UNDERLINE: str      = '\033[4m'
            BLINK: str          = '\033[5m'
            INVERSE: str        = '\033[7m'
            HIDDEN: str         = '\033[8m'
            STRIKETHROUGH: str  = '\033[9m'
        
        class Fore:
            """ANSI escape codes for foreground (text) colors."""

            BLACK: str          = '\033[30m'
            RED: str            = '\033[31m'
            GREEN: str          = '\033[32m'
            YELLOW: str         = '\033[33m'
            BLUE: str           = '\033[34m'
            MAGENTA: str        = '\033[35m'
            CYAN: str           = '\033[36m'
            WHITE: str          = '\033[37m'
            BRIGHT_BLACK: str   = '\033[90m'
            BRIGHT_RED: str     = '\033[91m'
            BRIGHT_GREEN: str   = '\033[92m'
            BRIGHT_YELLOW: str  = '\033[93m'
            BRIGHT_BLUE: str    = '\033[94m'
            BRIGHT_MAGENTA: str = '\033[95m'
            BRIGHT_CYAN: str    = '\033[96m'
            BRIGHT_WHITE: str   = '\033[97m'
        
        class Back:
            """ANSI escape codes for background colors."""

            BLACK: str          = '\033[40m'
            RED: str            = '\033[41m'
            GREEN: str          = '\033[42m'
            YELLOW: str         = '\033[43m'
            BLUE: str           = '\033[44m'
            MAGENTA: str        = '\033[45m'
            CYAN: str           = '\033[46m'
            WHITE: str          = '\033[47m'
            BRIGHT_BLACK: str   = '\033[100m'
            BRIGHT_RED: str     = '\033[101m'
            BRIGHT_GREEN: str   = '\033[102m'
            BRIGHT_YELLOW: str  = '\033[103m'
            BRIGHT_BLUE: str    = '\033[104m'
            BRIGHT_MAGENTA: str = '\033[105m'
            BRIGHT_CYAN: str    = '\033[106m'
            BRIGHT_WHITE: str   = '\033[107m'

    @staticmethod
    def _get_formatted_time() -> str:
        """
        Retrieves the current local time formatted as YYYY-MM-DD HH:MM:SS.

        Returns:
            The formatted time string.
        """
        return time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())

    @staticmethod
    def _print_message(message: str, color: str, type: str = "Null") -> None:
        """
        Internal method to format and print a message to the console.

        The output includes a timestamp, a type indicator, and the colored message.

        Args:
            message: The string content of the message.
            color: The ANSI escape code for the foreground color.
            type: The type indicator (e.g., "*", "!", "?") displayed in the message header.
        """
        print(
            f"[{Console._get_formatted_time()}][{type}] {color}{message}{Console.Color.Style.RESET}",
            flush = True)

    @staticmethod
    def log(message: str) -> None:
        """Prints a standard informational log message (White text, type "*")."""
        Console._print_message(message, Console.Color.Fore.WHITE, "*")
    
    @staticmethod
    def u_input(message: str) -> None:
        """Prints a message indicating user input is expected (Green text, type ">>")."""
        Console._print_message(message, Console.Color.Fore.GREEN, ">>")
    
    @staticmethod
    def u_output(message: str) -> None:
        """Prints a message indicating program output to the user (Green text, type "<<")."""
        Console._print_message(message, Console.Color.Fore.GREEN, "<<")
    
    @staticmethod
    def warning(message: str) -> None:
        """Prints a warning message (Yellow text, type "!")."""
        Console._print_message(message, Console.Color.Fore.YELLOW, "!")

    @staticmethod
    def error(message: str) -> None:
        """Prints an error message (Red text, type "?")."""
        Console._print_message(message, Console.Color.Fore.RED, "?")

    @staticmethod
    def clear() -> None:
        """Clears the console screen using the appropriate command for the operating system."""
        # 'cls' for Windows, 'clear -r' for most Linux/Unix systems
        os.system("cls" if sys.platform == "win32" else "clear -r")
    
    @staticmethod
    def fill(char: str) -> None:
        """
        Prints a line of the specified character spanning the entire width of the terminal.

        Args:
            char: The single character used to fill the line.
        """
        print(char * Console.WIDTH)