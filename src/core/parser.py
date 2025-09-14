from .data import COMMANDS, CONTEXT
from modules.commands import *

class Parser:
    def __init__(self) -> None:
        self.executed_actions: list[tuple[str, list[str]]] = []

    def run_actions(self, actions: list[dict[str, str]], args):
        for action in actions:
            func_name = action["func"]
            raw_args = action.get("args", [])
            formatted_args = [a.format(*args, **CONTEXT) for a in raw_args]
            globals()[func_name](*formatted_args)
            self.executed_actions.append((func_name, formatted_args))

    def process(self, tokens: list[str], node=None, args=None):
        if node is None:
            node = COMMANDS
            self.executed_actions.clear()

        if args is None:
            args = []
        
        if not tokens:
            if "actions" in node:
                self.run_actions(node["actions"], args)
                return True
            return False

        current = tokens[0]
        rest = tokens[1:]

        for key, subnode in node.items():
            if key == "actions":
                continue
            if key == "<ARG>":
                if "actions" in subnode:
                    new_arg = " ".join([current] + rest)
                    if self.process([], subnode, args + [new_arg]):
                        return True
                else:
                    if self.process(rest, subnode, args + [current]):
                        return True
            elif current == key:
                if self.process(rest, subnode, args):
                    return True

        return False

parser = Parser()