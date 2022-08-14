from typing import Dict
from abbreviations import elongate_word


class Organization:
    def __init__(self, name: str, link: str):
        # Link -> n
        self.children: Dict[str, int] = {}

        self.name = name
        self.link = link

        # Split size and type of name
        words = [elongate_word(w) for w in name.split()]
        self.size, self.type = words[-1], " ".join(words[:-1])

    # Add child
    def add_child(self, link):
        if link not in self.children.keys():
            self.children[link] = 0
        self.children[link] += 1
