import pathlib
from typing import Dict

_abbrs: Dict[str, str] = {}


def _add_abbreviations(path: str):
    file = open(pathlib.Path(__file__).parent / path, "r")

    lines = file.read().splitlines()
    for line in lines:
        if line == "":
            continue

        full, *abbreviations = line.split(",")

        for abbr in abbreviations:
            key = abbr.strip().lower()
            if key in _abbrs.keys():
                print("COLLISION WITH" + key)
                quit()

            _abbrs[key] = full

    file.close()


_add_abbreviations("scripts/abbr-type.abbr")
_add_abbreviations("scripts/abbr-size.abbr")


# Give word you want, and returns word you need
def elongate_word(word: str):
    w = word.lower()
    if w in _abbrs.keys():
        return _abbrs[w]
    return w
