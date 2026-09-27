"""
ISKRA - interaktivní textová hra
=================================
Originální hrdinka s elektrickými schopnostmi zachraňuje město před
záhadným Stínem. 10 rozhodovacích bodů, 6 různých konců.

Spusť: python iskra.py
"""

# Každý uzel příběhu: text scény + možnosti (číslo volby, popisek, kam vede)
# Uzly, co mají "konec" místo "options", jsou konce příběhu.
STORY = {
    "start": {
        "text": "Ve městě Nové Ostravě začaly bez varování zhasínat celé čtvrti.\n"
                 "Ty jsi Iskra - po nehodě ve školní laboratoři umíš ovládat světlo\n"
                 "a elektřinu. Vyrážíš zjistit, co se děje.",
        "options": [
            (1, "Vydat se ke staré továrně na okraji města", "tovarna"),
            (2, "Promluvit s vyděšeným svědkem na ulici", "svedek"),
            (3, "Sledovat podivně jiskřící kabely", "kabely"),
        ],
    },
    "tovarna": {
        "text": "U staré továrny slyšíš zevnitř hlasy. Někdo tam je.",
        "options": [
            (1, "Vplížit se potichu dovnitř", "tovarna_potichu"),
            (2, "Vtrhnout dovnitř rovnou", "tovarna_primo"),
        ],
    },
    "svedek": {
        "text": "Svědek se třese: \"Byl to stín... ukradl světlo z celé ulice a zmizel.\"",
        "options": [
            (1, "Vydat se po stopě, kterou popsal", "svedek_stopa"),
            (2, "Radši prošetřit ty jiskřící kabely", "kabely"),
        ],
    },
    "kabely": {
        "text": "Jiskřící kabely vedou dvěma směry - jedny hluboko do města, druhé\n"
                 "ke staré elektrárně.",
        "options": [
            (1, "Sledovat kabely až k elektrárně", "elektrarna"),
            (2, "Stopa naopak vede zpátky k továrně", "tovarna"),
        ],
    },
    "tovarna_potichu": {
        "text": "Potichu se vplížíš dovnitř a vyslechneš plán záhadného Stína -\n"
                 "a jeho slabinu.",
        "options": [
            (1, "Použít tu informaci a rovnou Stína konfrontovat", "konfrontace_pripravena"),
            (2, "Potichu couvnout a přivolat posily", "couvnout"),
        ],
    },
    "tovarna_primo": {
        "text": "Vtrhneš dovnitř - a spustíš past! Energetická síť tě spoutá k zemi.",
        "options": [
            (1, "Zkusit se vysílit z pasti vlastní silou", "boj_past"),
            (2, "Zkusit Stína přelstít slovy a získat čas", "trik"),
        ],
    },
    "svedek_stopa": {
        "text": "Stopa tě vede na střechy města, kde vidíš temnou postavu prchat dál.",
        "options": [
            (1, "Riskovat skok mezi střechami", "strecha_skok"),
            (2, "Jít bezpečnější, ale pomalejší cestou", "strecha_opatrne"),
        ],
    },
    "elektrarna": {
        "text": "U staré elektrárny najdeš stroj, který vysává světlo z celého města.",
        "options": [
            (1, "Zkusit stroj rovnou vypnout", "vypnout_stroj"),
            (2, "Nejdřív počkat a přivolat posily", "pockat_posily"),
        ],
    },
    "boj_past": {
        "text": "Rveš se s pastí ze všech sil...",
        "options": [
            (1, "Soustředit sílu do jednoho výboje", "past_vyboj"),
            (2, "Zkusit se vyklouznout potichu", "past_potichu"),
        ],
    },
    "vypnout_stroj": {
        "text": "Saháš po hlavnímu vypínači stroje...",
        "options": [
            (1, "Vypnout ho okamžitě", "END_vitezstvi_rychle"),
            (2, "Nejdřív najít bezpečný způsob, jak ho zastavit", "END_stroj_opatrne"),
        ],
    },
    "trik": {"text": "Tvůj trik zabere - Stín na chvíli zaváhá a síť povolí.",
             "options": [(1, "Pokračovat k elektrárně", "elektrarna")]},
    "strecha_skok": {"text": "Skok se povede jen tak tak - jsi rychle u elektrárny.",
                      "options": [(1, "Pokračovat", "elektrarna")]},
    "strecha_opatrne": {"text": "Bezpečná cesta tě zpozdí, ale dorazíš v pořádku.",
                         "options": [(1, "Pokračovat", "elektrarna")]},
    "couvnout": {"text": "S posilami po boku se vracíš připravená na cokoliv.",
                 "options": [(1, "Konfrontovat Stína společně", "END_vitezstvi_tym")]},
    "pockat_posily": {"text": "Posily dorazí právě včas.",
                       "options": [(1, "Zastavit stroj společně", "END_vitezstvi_tym")]},
    "past_vyboj": {"text": "Výboj energie roztrhne síť!",
                   "options": [(1, "Utéct za Stínem k elektrárně", "END_unik_bez_planu")]},
    "past_potichu": {"text": "Potichu se vyprostíš, ale Stín mezitím zmizel.",
                      "options": [(1, "Zjistit, co dál", "END_past_prohra")]},
    "konfrontace_pripravena": {"text": "Se znalostí slabiny Stína snadno přemůžeš protivníka!",
                                "options": [], "ending": "🏆 NEJLEPŠÍ KONEC: Dokonalé vítězství"},
    "END_vitezstvi_rychle": {"text": "Stroj se vypne, světlo se vrací do celého města. Rychlé\na rozhodné vítězství!",
                              "options": [], "ending": "🏆 Rychlé vítězství"},
    "END_stroj_opatrne": {"text": "Opatrný postup stroj bezpečně zastaví. Město je zachráněné.",
                           "options": [], "ending": "✅ Opatrné vítězství"},
    "END_vitezstvi_tym": {"text": "Společnými silami Stína zastavíte. Někdy je tým silnější\nnež jednotlivec!",
                           "options": [], "ending": "✅ Vítězství s týmem"},
    "END_unik_bez_planu": {"text": "Stín unikl, ale stroj je zničený a město zachráněné. Ne\nkaždé vítězství je dokonalé.",
                            "options": [], "ending": "🤝 Nedokonalé vítězství"},
    "END_past_prohra": {"text": "Stín zmizel beze stopy a část města zůstává ve tmě.\nNěkdy prohra znamená jen 'zkus to jinak příště'.",
                         "options": [], "ending": "💀 Prohra - zkus to znovu!"},
}


def hraj():
    print("=" * 60)
    print("  ISKRA - interaktivní mise")
    print("=" * 60)

    uzel = "start"
    while True:
        scena = STORY[uzel]
        print("\n" + scena["text"])

        if "ending" in scena:
            print("\n" + "=" * 60)
            print(f"  KONEC: {scena['ending']}")
            print("=" * 60)
            break

        print()
        for cislo, popis, _ in scena["options"]:
            print(f"  {cislo}) {popis}")

        platne_volby = {cislo for cislo, _, _ in scena["options"]}
        volba = None
        while volba not in platne_volby:
            try:
                volba = int(input("\nTvoje volba: "))
            except ValueError:
                continue

        for cislo, _, dalsi_uzel in scena["options"]:
            if cislo == volba:
                uzel = dalsi_uzel
                break


if __name__ == "__main__":
    hraj()
