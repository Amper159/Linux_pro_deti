"""Filtr nevhodných uživatelských jmen (web je i pro děti).

Jméno se před kontrolou zjednoduší: malá písmena bez diakritiky, náhrada
číslic za písmena (k0k0t -> kokot), bez oddělovačů a opakovaných písmen.
Dlouhé kmeny hledáme kdekoli ve jménu, krátké jen jako celé jméno, aby
nevznikaly zbytečné falešné poplachy.
"""

import re
import unicodedata

# Hledá se kdekoli ve jménu (kmeny mají aspoň 4 znaky).
_STEMS = (
    "kokot", "curak", "cural", "kurva", "kurvi", "kurev", "pizd", "pico",
    "picus", "pojeb", "jebat", "jebni", "jebak", "zmrd", "mrdat", "mrdka",
    "hovno", "hovna", "prdel", "hajzl", "srac", "kreten", "debil", "idiot",
    "buzer", "buzna", "kunda", "kundy", "mrdk", "chcij", "chcan", "zasran",
    "cunt", "fuck", "shit", "bitch", "whore", "slut", "penis", "vagin",
    "porn", "nigg", "hitler", "nazi", "rape", "znasil",
)
# Jen jako celé jméno (krátká slova).
_EXACT = ("pica", "pic", "cur", "pich", "kok", "sex", "sexy", "kurw", "fck")

_LEET = str.maketrans({
    "0": "o", "1": "i", "3": "e", "4": "a", "5": "s", "7": "t",
    "8": "b", "9": "g", "@": "a", "$": "s", "!": "i",
})


def _simplify(name: str) -> str:
    text = unicodedata.normalize("NFKD", name.lower())
    text = "".join(c for c in text if not unicodedata.combining(c))
    text = text.translate(_LEET)
    text = re.sub(r"[^a-z]", "", text)
    return re.sub(r"(.)\1+", r"\1", text)


def is_inappropriate(name: str) -> bool:
    simple = _simplify(name or "")
    if simple in _EXACT:
        return True
    return any(stem in simple for stem in _STEMS)
