"""
OBĚŠENEC - klasická slovní hra
=================================
Hádej písmena, dokud neuhodneš celé slovo, nebo neuděláš 6 chyb.
Slova jsou schválně propojená s Linuxhrou.cz - Python pojmy i postavy
z ostatních her.

Spusť: python obesenec.py
"""
import random

SLOVA = [
    ("PROMENNA", "Python pojem"), ("FUNKCE", "Python pojem"), ("SMYCKA", "Python pojem"),
    ("SEZNAM", "Python pojem"), ("SLOVNIK", "Python pojem"), ("PODMINKA", "Python pojem"),
    ("ODSAZENI", "Python pojem"), ("ISKRA", "Postava z naší hry"), ("KOBKA", "Místo z naší hry"),
    ("STRAZCE", "Nepřítel z Kobky"), ("PINGVIN", "Zvíře (jako Tux!)"), ("HAD", "Zvíře (jako Pyt!)"),
    ("POCITAC", "Technika"), ("KLAVESNICE", "Technika"), ("TERMINAL", "Technika"),
]

MAX_CHYB = 6

STADIA = [
"""  +---+
  |   |
      |
      |
      |
      |
=========""",
"""  +---+
  |   |
  O   |
      |
      |
      |
=========""",
"""  +---+
  |   |
  O   |
  |   |
      |
      |
=========""",
"""  +---+
  |   |
  O   |
 /|   |
      |
      |
=========""",
"""  +---+
  |   |
  O   |
 /|\\  |
      |
      |
=========""",
"""  +---+
  |   |
  O   |
 /|\\  |
 /    |
      |
=========""",
"""  +---+
  |   |
  O   |
 /|\\  |
 / \\  |
      |
=========""",
]


def vypis_stav(slovo, hadana, chyby):
    print(STADIA[chyby])
    zobrazeni = " ".join(pismeno if pismeno in hadana else "_" for pismeno in slovo)
    print(f"\n{zobrazeni}")
    print(f"Chyby: {chyby} / {MAX_CHYB}")
    if hadana:
        print(f"Hádaná písmena: {', '.join(sorted(hadana))}")


def hraj():
    print("=" * 50)
    print("  OBĚŠENEC")
    print("=" * 50)

    slovo, kategorie = random.choice(SLOVA)
    hadana = set()
    chyby = 0

    while True:
        print(f"\nKategorie: {kategorie}")
        vypis_stav(slovo, hadana, chyby)

        if all(pismeno in hadana for pismeno in slovo):
            print(f"\n🏆 Uhodl jsi: {slovo}!")
            break
        if chyby >= MAX_CHYB:
            print(f"\n💀 Škoda! Slovo bylo: {slovo}")
            break

        pismeno = input("\nTipni si písmeno: ").strip().upper()
        if len(pismeno) != 1 or not pismeno.isalpha():
            print("Zadej prosím jedno písmeno.")
            continue
        if pismeno in hadana:
            print("Tohle písmeno už jsi zkoušel.")
            continue

        hadana.add(pismeno)
        if pismeno in slovo:
            print(f"Ano, '{pismeno}' je ve slově!")
        else:
            chyby += 1
            print(f"Bohužel, '{pismeno}' tam není.")


if __name__ == "__main__":
    hraj()
