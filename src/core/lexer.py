from .data import PHRASES

import re


class Lexer:
    def __init__(self): ...

        
    def tokenize(self, text: str) -> list[str]:
        
        words = re.findall(r"\w+", text.lower())
        tokens = []
        last_token_not_matched = False
        index = 0

        while index < len(words):
            matched = False
            for phrase, token in PHRASES:
                length = len(phrase)
                if words[index:index+length] == phrase:
                    tokens.append(token)
                    index += length
                    matched = True
                    last_token_not_matched = False
                    break
            if not matched:
                if not last_token_not_matched:
                    tokens.append([words[index]])
                    last_token_not_matched = True
                else:
                    tokens[-1].append(words[index])
                index += 1
        
        for index, token in enumerate(tokens):
            if isinstance(token, list):
                tokens[index] = " ".join(tokens[index])

        return tokens
    
lexer = Lexer()