"""
KOBKA - textové RPG s inventářem
==================================
Projdi 9 náhodných místností plných příšer, pokladů a pastí, a nakonec
poraz strážce hlubin. Skutečné volby ovlivňují tvoje šance!

Spusť: python kobka.py
"""
import random

MONSTERS = [
    {"jmeno": "Kobkový krysák", "obtiznost": 9, "zraneni": (2, 4)},
    {"jmeno": "Kostěná hlídka", "obtiznost": 12, "zraneni": (3, 5)},
    {"jmeno": "Stínový plaz", "obtiznost": 11, "zraneni": (2, 5)},
]
BOSS = {"jmeno": "Strážce hlubin", "obtiznost": 15, "zraneni": (4, 7)}

PREDMETY = [
    {"jmeno": "Ostrý meč", "efekt": "attack", "hodnota": 3, "popis": "+3 k útoku natrvalo"},
    {"jmeno": "Kožená zbroj", "efekt": "max_hp", "hodnota": 5, "popis": "+5 k max. HP natrvalo"},
    {"jmeno": "Lektvar zdraví", "efekt": "heal", "hodnota": 7, "popis": "+7 HP okamžitě"},
]

POCET_MISTNOSTI = 9


def vypis_stav(hrac):
    print(f"\n❤️  HP: {max(0, hrac['hp'])} / {hrac['max_hp']}   🎒 Inventář: "
          f"{', '.join(hrac['predmety']) if hrac['predmety'] else 'prázdný'}")


def zeptej_se(otazky):
    """otazky: seznam (klic, popis). Vrátí zvolený klíč."""
    for i, (klic, popis) in enumerate(otazky, start=1):
        print(f"  {i}) {popis}")
    platne = {str(i) for i in range(1, len(otazky) + 1)}
    volba = None
    while volba not in platne:
        volba = input("Tvoje volba: ").strip()
    return otazky[int(volba) - 1][0]


def souboj(hrac, sok, umoznit_utek=True):
    """Vrátí True, pokud hráč vyhrál (nebo utekl), False při smrtelném zásahu."""
    moznosti = [("silny", "⚔️  Útočit naplno (vyšší šance, ale plné zranění při neúspěchu)"),
                ("opatrny", "🛡️  Útočit opatrně (nižší šance, poloviční zranění při neúspěchu)")]
    if umoznit_utek:
        moznosti.append(("utek", "🏃 Utéct (45% šance uniknout bez boje)"))

    styl = zeptej_se(moznosti)

    if styl == "utek":
        if random.random() < 0.45:
            print("Podařilo se ti uniknout bez boje!")
        else:
            zraneni = random.randint(3, 6)
            hrac["hp"] -= zraneni
            print(f"Útěk se nepovedl - {sok['jmeno']} tě zasáhl za {zraneni} HP!")
        return True

    bonus = 3 if styl == "silny" else 1
    hod = random.randint(1, 20)
    celkem = hod + hrac["attack"] + bonus
    if celkem >= sok["obtiznost"]:
        leceni = random.randint(0, 2)
        hrac["hp"] = min(hrac["max_hp"], hrac["hp"] + leceni)
        print(f"Hod {hod} + útok {hrac['attack']} + bonus {bonus} = {celkem} >= {sok['obtiznost']} -> VYHRÁL JSI!")
        return True
    else:
        zraneni = random.randint(*sok["zraneni"])
        if styl == "opatrny":
            zraneni = max(1, zraneni // 2)
        hrac["hp"] -= zraneni
        print(f"Hod {hod} + útok {hrac['attack']} + bonus {bonus} = {celkem} < {sok['obtiznost']} "
              f"-> prohrál jsi, -{zraneni} HP")
        return hrac["hp"] > 0


def mistnost_prisera(hrac):
    sok = random.choice(MONSTERS)
    print(f"\nVyskočí na tebe {sok['jmeno']}!")
    return souboj(hrac, sok)


def mistnost_poklad(hrac):
    nabidka = random.sample(PREDMETY, 2)
    print("\nTruhla s poklady! Vyber si JEDEN z nabízených předmětů:")
    predmet = zeptej_se([(p["jmeno"], f"{p['jmeno']} - {p['popis']}") for p in nabidka])
    vybrany = next(p for p in nabidka if p["jmeno"] == predmet)
    hrac["predmety"].append(vybrany["jmeno"])
    if vybrany["efekt"] == "attack":
        hrac["attack"] += vybrany["hodnota"]
    elif vybrany["efekt"] == "max_hp":
        hrac["max_hp"] += vybrany["hodnota"]
        hrac["hp"] += vybrany["hodnota"]
    elif vybrany["efekt"] == "heal":
        hrac["hp"] = min(hrac["max_hp"], hrac["hp"] + vybrany["hodnota"])
    print(f"Získal jsi: {vybrany['jmeno']}!")


def mistnost_past(hrac):
    print("\nPodlaha vypadá podezřele. Jak projdeš?")
    styl = zeptej_se([
        ("opatrne", "🔍 Prohledat opatrně (65% šance projít bez zranění)"),
        ("rychle", "🏃 Projít rychle (vždy malé, předvídatelné zranění)"),
    ])
    if styl == "opatrne":
        if random.random() < 0.65:
            hrac["hp"] = min(hrac["max_hp"], hrac["hp"] + 2)
            print("Prošel jsi bez úhony a ještě sis trochu odpočinul!")
        else:
            zraneni = random.randint(2, 4)
            hrac["hp"] -= zraneni
            print(f"Přesto tě past škrábla za {zraneni} HP.")
    else:
        zraneni = random.randint(1, 3)
        hrac["hp"] -= zraneni
        print(f"Proběhl jsi rychle, past tě jen škrábla ({zraneni} HP).")


def mistnost_fontana(hrac):
    print("\nLéčivá fontána! Jak z ní budeš pít?")
    styl = zeptej_se([
        ("poradne", "💧 Napít se pořádně (velké okamžité léčení)"),
        ("setrne", "🍶 Napít se šetrně a naplnit lahev (menší léčení, ale +2 max. HP navždy)"),
    ])
    if styl == "poradne":
        leceni = random.randint(5, 10)
        hrac["hp"] = min(hrac["max_hp"], hrac["hp"] + leceni)
        print(f"Napil ses pořádně a doléčil se o {leceni} HP.")
    else:
        hrac["max_hp"] += 2
        leceni = random.randint(2, 4)
        hrac["hp"] = min(hrac["max_hp"], hrac["hp"] + leceni + 2)
        hrac["predmety"].append("Lahev vody")
        print("Napil ses šetrně a naplnil lahev - trvale silnější (+2 max. HP)!")


def mistnost_prazdna(hrac):
    print("\nTahle místnost vypadá prázdná. Prozkoumáš ji pořádně?")
    styl = zeptej_se([
        ("prozkoumat", "🔦 Prozkoumat důkladně (40% šance najít drobné léčení)"),
        ("dal", "🚶 Jít rovnou dál (bezpečné, ale jistě nic nezískáš)"),
    ])
    if styl == "prozkoumat" and random.random() < 0.4:
        leceni = random.randint(2, 5)
        hrac["hp"] = min(hrac["max_hp"], hrac["hp"] + leceni)
        print(f"Našel jsi skrytou zásobu a doléčil se o {leceni} HP!")
    else:
        print("Nic zajímavého jsi nenašel." if styl == "prozkoumat" else "Prošel jsi bez zastavování dál.")


def hraj():
    print("=" * 60)
    print("  KOBKA")
    print("=" * 60)
    print(f"Vstupuješ do staré kobky. Čeká tě {POCET_MISTNOSTI} místností")
    print("plných příšer, pastí i pokladů, a nakonec strážce hlubin.\n")

    hrac = {"hp": 20, "max_hp": 20, "attack": 1, "predmety": []}

    for cislo_mistnosti in range(1, POCET_MISTNOSTI + 1):
        if hrac["hp"] <= 0:
            break
        print(f"\n--- Místnost {cislo_mistnosti} / {POCET_MISTNOSTI} ---")
        vypis_stav(hrac)
        typ = random.choices(
            ["prisera", "poklad", "past", "fontana", "prazdna"],
            weights=[40, 25, 15, 10, 10],
        )[0]
        {"prisera": mistnost_prisera, "poklad": mistnost_poklad,
         "past": mistnost_past, "fontana": mistnost_fontana,
         "prazdna": mistnost_prazdna}[typ](hrac)

    print("\n" + "=" * 60)
    if hrac["hp"] <= 0:
        print("  💀 Kobka tě přemohla...")
        print("=" * 60)
        return

    print(f"  Před tebou stojí {BOSS['jmeno']}, strážce hlubin! Útěk nepřipadá v úvahu.")
    print("=" * 60)
    vypis_stav(hrac)
    vyhral = souboj(hrac, BOSS, umoznit_utek=False)

    print("\n" + "=" * 60)
    if vyhral and hrac["hp"] > 0:
        print("  🏆 VYHRÁL JSI! Strážce hlubin poražen.")
    else:
        print("  💀 Kobka tě přemohla u posledního souboje...")
    print(f"  Nasbírané předměty: {', '.join(hrac['predmety']) if hrac['predmety'] else 'žádné'}")
    print("=" * 60)


if __name__ == "__main__":
    hraj()
