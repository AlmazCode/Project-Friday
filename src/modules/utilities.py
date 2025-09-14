from .console import Console

from core import data

import socket


def tokens_to_digits(tokens: list[str]) -> list[int]:
    return [data.VARIANT_TO_DIGIT[n] for n in tokens if n in data.VARIANT_TO_DIGIT]

def get_browser_path() -> str | None:

    if data.PLATFORM == 'Windows':
        try:
            from winreg import HKEY_CLASSES_ROOT, HKEY_CURRENT_USER, OpenKey, QueryValueEx

            with OpenKey(
                HKEY_CURRENT_USER,
                r'SOFTWARE\Microsoft\Windows\Shell\Associations\UrlAssociations\http\UserChoice'
            ) as regkey:
                browser_choice = QueryValueEx(regkey, 'ProgId')[0]

            with OpenKey(HKEY_CLASSES_ROOT, r'{}\shell\open\command'.format(browser_choice)) as regkey:
                browser_path_tuple = QueryValueEx(regkey, None)
                browser_path = browser_path_tuple[0].split('"')[1]
                return browser_path

        except Exception:
            Console.error('Failed to look up default browser in system registry. Using fallback value.')
            return None

def has_internet(host="8.8.8.8", port=53, timeout=3):
    """
    Проверка интернета через попытку соединения с Google DNS (8.8.8.8:53).
    Возвращает True, если удалось соединиться.
    """
    try:
        socket.setdefaulttimeout(timeout)
        socket.socket(socket.AF_INET, socket.SOCK_STREAM).connect((host, port))
        return True
    except Exception:
        return False