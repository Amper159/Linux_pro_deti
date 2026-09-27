# ISKRA - originální hrdinka, vlastní příběh, žádné cizí postavy.
STORY = {
    "start": {
        "text": "Ve městě Nové Ostravě začaly bez varování zhasínat celé čtvrti. Ty jsi Iskra - "
                "po nehodě ve školní laboratoři umíš ovládat světlo a elektřinu. Vyrážíš zjistit, co se děje.",
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
        "text": "Jiskřící kabely vedou dvěma směry - jedny hluboko do města, druhé ke staré elektrárně.",
        "options": [
            (1, "Sledovat kabely až k elektrárně", "elektrarna"),
            (2, "Stopa naopak vede zpátky k továrně", "tovarna"),
        ],
    },
    "tovarna_potichu": {
        "text": "Potichu se vplížíš dovnitř a vyslechneš plán záhadného Stína - a jeho slabinu.",
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
    "trik": {"text": "Tvůj trik zabere - Stín na chvíli zaváhá a síť povolí.", "options": [(1, "Pokračovat k elektrárně", "elektrarna")]},
    "strecha_skok": {"text": "Skok se povede jen tak tak - jsi rychle u elektrárny.", "options": [(1, "Pokračovat", "elektrarna")]},
    "strecha_opatrne": {"text": "Bezpečná cesta tě zpozdí, ale dorazíš v pořádku.", "options": [(1, "Pokračovat", "elektrarna")]},
    "couvnout": {"text": "S posilami po boku se vracíš připravená na cokoliv.", "options": [(1, "Konfrontovat Stína společně", "END_vitezstvi_tym")]},
    "pockat_posily": {"text": "Posily dorazí právě včas.", "options": [(1, "Zastavit stroj společně", "END_vitezstvi_tym")]},
    "past_vyboj": {"text": "Výboj energie roztrhne síť!", "options": [(1, "Utéct za Stínem k elektrárně", "END_unik_bez_planu")]},
    "past_potichu": {"text": "Potichu se vyprostíš, ale Stín mezitím zmizel.", "options": [(1, "Zjistit, co dál", "END_past_prohra")]},
    "konfrontace_pripravena": {"text": "Se znalostí slabiny Stína snadno přemůžeš.", "options": [], "ending": "vitezstvi"},
    "END_vitezstvi_rychle": {"text": "Stroj se vypne, světlo se vrací do celého města. Rychlé a rozhodné vítězství!", "options": [], "ending": "vitezstvi_rychle"},
    "END_stroj_opatrne": {"text": "Opatrný postup stroj bezpečně zastaví, i když to chvíli trvalo. Město je zachráněné.", "options": [], "ending": "stroj_opatrne"},
    "END_vitezstvi_tym": {"text": "Společnými silami Stína zastavíte. Někdy je tým silnější než jednotlivec!", "options": [], "ending": "vitezstvi_tym"},
    "END_unik_bez_planu": {"text": "Stín unikl, ale stroj je zničený a město zachráněné. Ne každé vítězství je dokonalé.", "options": [], "ending": "unik_bez_planu"},
    "END_past_prohra": {"text": "Stín zmizel beze stopy a část města zůstává ve tmě. Někdy prohra znamená jen 'zkus to jinak příště'.", "options": [], "ending": "prohra"},
}
