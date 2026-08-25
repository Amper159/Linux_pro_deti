"""90 úkolů pískoviště – 3 sady po 30, reálné dovednosti Linuxu.

Splnění se **neporovnává s napsaným příkazem** – kontroluje se skutečný stav
souborového systému (a běžících procesů) v kontejneru přes `test`/`grep`/atd.
Je jedno, jestli k výsledku dojdeš jedním příkazem nebo deseti oklikami;
důležité je, jak to dopadlo.

Sady se odemykají popořadě (viz `sandbox/gamification.py` a frontend):
  Sada 1 – Základy Linuxu     (úkoly  1-30)
  Sada 2 – Soubory a sítě     (úkoly 31-60)
  Sada 3 – Mistr systému      (úkoly 61-90)
"""

from typing import List

from . import auth, engine

TASKS = [
    {
        "id": 1,
        "set": 1,
        "tier": 1,
        "difficulty": "Sada 1 – 1. Fáze: Základy",
        "cmd_name": "pwd",
        "title": "Kde právě jsem?",
        "story": "Přistál jsi na vesmírné stanici TUX-1. Čas prozkoumat, co máš k dispozici.",
        "goal": "Zjisti, ve které složce právě stojíš (pwd), a výstup ulož do souboru. Výstup ulož do souboru 'misto1.txt'.",
        "hint": "cd ~\npwd > misto1.txt",
        "commands": [
            "pwd",
            ">"
        ],
        "checks": [
            {
                "label": "'misto1.txt' obsahuje správnou cestu",
                "test": "grep -qF \"kadet_\" \"$HOME/misto1.txt\""
            }
        ]
    },
    {
        "id": 2,
        "set": 1,
        "tier": 2,
        "difficulty": "Sada 1 – 2. Fáze: Posádka",
        "cmd_name": "pwd",
        "title": "Kde právě jsem?",
        "story": "Pokračuješ v průzkumu základny.",
        "goal": "Přejdi do složky 'data' a znovu si ověř, kde teď jsi (pwd). Výstup ulož do souboru 'misto2.txt'.",
        "hint": "cd ~\ncd data\npwd > misto2.txt",
        "commands": [
            "pwd",
            ">"
        ],
        "checks": [
            {
                "label": "'misto2.txt' obsahuje správnou cestu",
                "test": "grep -qF \"data\" \"$HOME/data/misto2.txt\""
            }
        ]
    },
    {
        "id": 3,
        "set": 1,
        "tier": 3,
        "difficulty": "Sada 1 – 3. Fáze: Mistr",
        "cmd_name": "pwd",
        "title": "Kde právě jsem?",
        "story": "Pokračuješ v průzkumu základny.",
        "goal": "Ať jsi kdekoliv, vrať se domů (cd ~) a potřetí si ověř polohu (pwd). Výstup ulož do souboru 'misto3.txt'.",
        "hint": "cd ~\npwd > misto3.txt",
        "commands": [
            "pwd",
            ">"
        ],
        "checks": [
            {
                "label": "'misto3.txt' obsahuje správnou cestu",
                "test": "grep -qF \"kadet_\" \"$HOME/misto3.txt\""
            }
        ]
    },
    {
        "id": 4,
        "set": 1,
        "tier": 1,
        "difficulty": "Sada 1 – 1. Fáze: Základy",
        "cmd_name": "ls",
        "title": "Co je kolem mě?",
        "story": "Ve složce může být spousta věcí – vypiš si je.",
        "goal": "Vypiš obsah složky a ulož výstup do souboru 'obsah1.txt'.",
        "hint": "cd ~\nls > obsah1.txt",
        "commands": [
            "ls",
            ">"
        ],
        "checks": [
            {
                "label": "soubor 'obsah1.txt' obsahuje výpis (najdeš tam 'README.txt')",
                "test": "grep -qF \"README.txt\" \"$HOME/obsah1.txt\""
            }
        ]
    },
    {
        "id": 5,
        "set": 1,
        "tier": 2,
        "difficulty": "Sada 1 – 2. Fáze: Posádka",
        "cmd_name": "ls",
        "title": "Co je kolem mě?",
        "story": "Ve složce může být spousta věcí – vypiš si je.",
        "goal": "Vypiš obsah složky a ulož výstup do souboru 'obsah2.txt'.",
        "hint": "cd ~\nls data > obsah2.txt",
        "commands": [
            "ls",
            ">"
        ],
        "checks": [
            {
                "label": "soubor 'obsah2.txt' obsahuje výpis (najdeš tam 'planety.txt')",
                "test": "grep -qF \"planety.txt\" \"$HOME/obsah2.txt\""
            }
        ]
    },
    {
        "id": 6,
        "set": 1,
        "tier": 3,
        "difficulty": "Sada 1 – 3. Fáze: Mistr",
        "cmd_name": "ls",
        "title": "Co je kolem mě?",
        "story": "Ve složce může být spousta věcí – vypiš si je.",
        "goal": "Vypiš obsah složky a ulož výstup do souboru 'obsah3.txt'.",
        "hint": "cd ~\nls -l > obsah3.txt",
        "commands": [
            "ls",
            ">"
        ],
        "checks": [
            {
                "label": "soubor 'obsah3.txt' obsahuje výpis (najdeš tam 'README.txt')",
                "test": "grep -qF \"README.txt\" \"$HOME/obsah3.txt\""
            }
        ]
    },
    {
        "id": 7,
        "set": 1,
        "tier": 1,
        "difficulty": "Sada 1 – 1. Fáze: Základy",
        "cmd_name": "ls -a",
        "title": "Odhal skrytá tajemství",
        "story": "Někde tu prý je i skrytý soubor s kódem k základně.",
        "goal": "Vypiš i skryté soubory (ls -a) a ulož výstup do 'skryte1.txt'.",
        "hint": "cd ~\nls -a > skryte1.txt",
        "commands": [
            "ls -a",
            ">"
        ],
        "checks": [
            {
                "label": "'skryte1.txt' obsahuje skrytý soubor '.tajny_kod.txt'",
                "test": "grep -qF \".tajny_kod.txt\" \"$HOME/skryte1.txt\""
            }
        ]
    },
    {
        "id": 8,
        "set": 1,
        "tier": 2,
        "difficulty": "Sada 1 – 2. Fáze: Posádka",
        "cmd_name": "ls -a",
        "title": "Odhal skrytá tajemství",
        "story": "Někde tu prý je i skrytý soubor s kódem k základně.",
        "goal": "Vypiš i skryté soubory (ls -a) a ulož výstup do 'skryte2.txt'.",
        "hint": "cd ~\nls -a > skryte2.txt",
        "commands": [
            "ls -a",
            ">"
        ],
        "checks": [
            {
                "label": "'skryte2.txt' obsahuje skrytý soubor '.tajny_kod.txt'",
                "test": "grep -qF \".tajny_kod.txt\" \"$HOME/skryte2.txt\""
            }
        ]
    },
    {
        "id": 9,
        "set": 1,
        "tier": 3,
        "difficulty": "Sada 1 – 3. Fáze: Mistr",
        "cmd_name": "ls -a",
        "title": "Odhal skrytá tajemství",
        "story": "Někde tu prý je i skrytý soubor s kódem k základně.",
        "goal": "Vypiš i skryté soubory (ls -a) a ulož výstup do 'skryte3.txt'.",
        "hint": "cd ~\nls -a > skryte3.txt",
        "commands": [
            "ls -a",
            ">"
        ],
        "checks": [
            {
                "label": "'skryte3.txt' obsahuje skrytý soubor '.tajny_kod.txt'",
                "test": "grep -qF \".tajny_kod.txt\" \"$HOME/skryte3.txt\""
            }
        ]
    },
    {
        "id": 10,
        "set": 1,
        "tier": 1,
        "difficulty": "Sada 1 – 1. Fáze: Základy",
        "cmd_name": "cat",
        "title": "Přečti hlášení",
        "story": "Ve složce leží soubor, který stojí za přečtení.",
        "goal": "Přečti soubor 'README.txt' (cat) a ulož jeho obsah do 'precteno1.txt'.",
        "hint": "cd ~\ncat README.txt > precteno1.txt",
        "commands": [
            "cat",
            ">"
        ],
        "checks": [
            {
                "label": "soubor 'precteno1.txt' obsahuje text z 'README.txt'",
                "test": "grep -qF \"PÍSKOVIŠTI\" \"$HOME/precteno1.txt\""
            }
        ]
    },
    {
        "id": 11,
        "set": 1,
        "tier": 2,
        "difficulty": "Sada 1 – 2. Fáze: Posádka",
        "cmd_name": "cat",
        "title": "Přečti hlášení",
        "story": "Ve složce leží soubor, který stojí za přečtení.",
        "goal": "Přečti soubor 'data/planety.txt' (cat) a ulož jeho obsah do 'precteno2.txt'.",
        "hint": "cd ~\ncat data/planety.txt > precteno2.txt",
        "commands": [
            "cat",
            ">"
        ],
        "checks": [
            {
                "label": "soubor 'precteno2.txt' obsahuje text z 'data/planety.txt'",
                "test": "grep -qF \"Jupiter\" \"$HOME/precteno2.txt\""
            }
        ]
    },
    {
        "id": 12,
        "set": 1,
        "tier": 3,
        "difficulty": "Sada 1 – 3. Fáze: Mistr",
        "cmd_name": "cat",
        "title": "Přečti hlášení",
        "story": "Ve složce leží soubor, který stojí za přečtení.",
        "goal": "Přečti soubor 'data/posadka.txt' (cat) a ulož jeho obsah do 'precteno3.txt'.",
        "hint": "cd ~\ncat data/posadka.txt > precteno3.txt",
        "commands": [
            "cat",
            ">"
        ],
        "checks": [
            {
                "label": "soubor 'precteno3.txt' obsahuje text z 'data/posadka.txt'",
                "test": "grep -qF \"Kapitán\" \"$HOME/precteno3.txt\""
            }
        ]
    },
    {
        "id": 13,
        "set": 1,
        "tier": 1,
        "difficulty": "Sada 1 – 1. Fáze: Základy",
        "cmd_name": "cd",
        "title": "Vejdi do skladu dat",
        "story": "Musíš se umět pohybovat mezi složkami.",
        "goal": "Přejdi do složky 'data' (cd) a vytvoř tam prázdný soubor 'marker1.txt'.",
        "hint": "cd ~\ncd data\ntouch marker1.txt",
        "commands": [
            "cd",
            "touch"
        ],
        "checks": [
            {
                "label": "ve složce 'data' existuje soubor 'marker1.txt'",
                "test": "test -f \"$HOME/data/marker1.txt\""
            }
        ]
    },
    {
        "id": 14,
        "set": 1,
        "tier": 2,
        "difficulty": "Sada 1 – 2. Fáze: Posádka",
        "cmd_name": "cd",
        "title": "Vejdi do skladu dat",
        "story": "Musíš se umět pohybovat mezi složkami.",
        "goal": "Přejdi do složky 'data' (cd) a vytvoř tam prázdný soubor 'marker2.txt'.",
        "hint": "cd ~\ncd data\ntouch marker2.txt",
        "commands": [
            "cd",
            "touch"
        ],
        "checks": [
            {
                "label": "ve složce 'data' existuje soubor 'marker2.txt'",
                "test": "test -f \"$HOME/data/marker2.txt\""
            }
        ]
    },
    {
        "id": 15,
        "set": 1,
        "tier": 3,
        "difficulty": "Sada 1 – 3. Fáze: Mistr",
        "cmd_name": "cd",
        "title": "Vejdi do skladu dat",
        "story": "Musíš se umět pohybovat mezi složkami.",
        "goal": "Přejdi do složky 'data' (cd) a vytvoř tam prázdný soubor 'marker3.txt'.",
        "hint": "cd ~\ncd data\ntouch marker3.txt",
        "commands": [
            "cd",
            "touch"
        ],
        "checks": [
            {
                "label": "ve složce 'data' existuje soubor 'marker3.txt'",
                "test": "test -f \"$HOME/data/marker3.txt\""
            }
        ]
    },
    {
        "id": 16,
        "set": 1,
        "tier": 1,
        "difficulty": "Sada 1 – 1. Fáze: Základy",
        "cmd_name": "grep",
        "title": "Hledej v datech",
        "story": "Najdi konkrétní řádek v souboru, aniž bys ho musel číst celý.",
        "goal": "V souboru 'data/planety.txt' najdi řádek se slovem 'Země' (grep) a ulož ho do 'zeme.txt'.",
        "hint": "cd ~\ngrep \"Země\" data/planety.txt > zeme.txt",
        "commands": [
            "grep",
            ">"
        ],
        "checks": [
            {
                "label": "'zeme.txt' obsahuje nalezený řádek",
                "test": "grep -qF \"tučňáky\" \"$HOME/zeme.txt\""
            }
        ]
    },
    {
        "id": 17,
        "set": 1,
        "tier": 2,
        "difficulty": "Sada 1 – 2. Fáze: Posádka",
        "cmd_name": "grep",
        "title": "Hledej v datech",
        "story": "Najdi konkrétní řádek v souboru, aniž bys ho musel číst celý.",
        "goal": "V souboru 'data/posadka.txt' najdi řádek se slovem 'Kuchař' (grep) a ulož ho do 'kucharka.txt'.",
        "hint": "cd ~\ngrep \"Kuchař\" data/posadka.txt > kucharka.txt",
        "commands": [
            "grep",
            ">"
        ],
        "checks": [
            {
                "label": "'kucharka.txt' obsahuje nalezený řádek",
                "test": "grep -qF \"Konqi\" \"$HOME/kucharka.txt\""
            }
        ]
    },
    {
        "id": 18,
        "set": 1,
        "tier": 3,
        "difficulty": "Sada 1 – 3. Fáze: Mistr",
        "cmd_name": "grep",
        "title": "Hledej v datech",
        "story": "Najdi konkrétní řádek v souboru, aniž bys ho musel číst celý.",
        "goal": "V souboru 'data/planety.txt' najdi řádek se slovem 'Mars' (grep) a ulož ho do 'mars.txt'.",
        "hint": "cd ~\ngrep \"Mars\" data/planety.txt > mars.txt",
        "commands": [
            "grep",
            ">"
        ],
        "checks": [
            {
                "label": "'mars.txt' obsahuje nalezený řádek",
                "test": "grep -qF \"prach\" \"$HOME/mars.txt\""
            }
        ]
    },
    {
        "id": 19,
        "set": 1,
        "tier": 1,
        "difficulty": "Sada 1 – 1. Fáze: Základy",
        "cmd_name": "mkdir",
        "title": "Postav nový hangár",
        "story": "Základna potřebuje další úložné prostory.",
        "goal": "Vytvoř novou složku 'hangar1'.",
        "hint": "cd ~\nmkdir hangar1",
        "commands": [
            "mkdir"
        ],
        "checks": [
            {
                "label": "existuje složka 'hangar1'",
                "test": "test -d \"$HOME/hangar1\""
            }
        ]
    },
    {
        "id": 20,
        "set": 1,
        "tier": 2,
        "difficulty": "Sada 1 – 2. Fáze: Posádka",
        "cmd_name": "mkdir",
        "title": "Postav nový hangár",
        "story": "Základna potřebuje další úložné prostory.",
        "goal": "Vytvoř novou složku 'hangar2'.",
        "hint": "cd ~\nmkdir hangar2",
        "commands": [
            "mkdir"
        ],
        "checks": [
            {
                "label": "existuje složka 'hangar2'",
                "test": "test -d \"$HOME/hangar2\""
            }
        ]
    },
    {
        "id": 21,
        "set": 1,
        "tier": 3,
        "difficulty": "Sada 1 – 3. Fáze: Mistr",
        "cmd_name": "mkdir",
        "title": "Postav nový hangár",
        "story": "Základna potřebuje další úložné prostory.",
        "goal": "Vytvoř novou složku 'hangar3'.",
        "hint": "cd ~\nmkdir hangar3",
        "commands": [
            "mkdir"
        ],
        "checks": [
            {
                "label": "existuje složka 'hangar3'",
                "test": "test -d \"$HOME/hangar3\""
            }
        ]
    },
    {
        "id": 22,
        "set": 1,
        "tier": 1,
        "difficulty": "Sada 1 – 1. Fáze: Základy",
        "cmd_name": "touch",
        "title": "Založ nový soubor",
        "story": "Ve složce 'hangar1' zatím nic není.",
        "goal": "Ve složce 'hangar1' vytvoř prázdný soubor 'seznam_lodi.txt'.",
        "hint": "cd ~\ntouch hangar1/seznam_lodi.txt",
        "commands": [
            "touch"
        ],
        "checks": [
            {
                "label": "existuje 'hangar1/seznam_lodi.txt'",
                "test": "test -f \"$HOME/hangar1/seznam_lodi.txt\""
            }
        ]
    },
    {
        "id": 23,
        "set": 1,
        "tier": 2,
        "difficulty": "Sada 1 – 2. Fáze: Posádka",
        "cmd_name": "touch",
        "title": "Založ nový soubor",
        "story": "Ve složce 'hangar2' zatím nic není.",
        "goal": "Ve složce 'hangar2' vytvoř prázdný soubor 'zasoby.txt'.",
        "hint": "cd ~\ntouch hangar2/zasoby.txt",
        "commands": [
            "touch"
        ],
        "checks": [
            {
                "label": "existuje 'hangar2/zasoby.txt'",
                "test": "test -f \"$HOME/hangar2/zasoby.txt\""
            }
        ]
    },
    {
        "id": 24,
        "set": 1,
        "tier": 3,
        "difficulty": "Sada 1 – 3. Fáze: Mistr",
        "cmd_name": "touch",
        "title": "Založ nový soubor",
        "story": "Ve složce 'hangar3' zatím nic není.",
        "goal": "Ve složce 'hangar3' vytvoř prázdný soubor 'posadka.txt'.",
        "hint": "cd ~\ntouch hangar3/posadka.txt",
        "commands": [
            "touch"
        ],
        "checks": [
            {
                "label": "existuje 'hangar3/posadka.txt'",
                "test": "test -f \"$HOME/hangar3/posadka.txt\""
            }
        ]
    },
    {
        "id": 25,
        "set": 1,
        "tier": 1,
        "difficulty": "Sada 1 – 1. Fáze: Základy",
        "cmd_name": "wc -l",
        "title": "Spočítej řádky",
        "story": "Kolik toho vlastně ten soubor obsahuje?",
        "goal": "Spočítej řádky v souboru 'data/posadka.txt' (wc -l) a ulož číslo do 'pocet1.txt'.",
        "hint": "cd ~\nwc -l < data/posadka.txt > pocet1.txt",
        "commands": [
            "wc -l",
            ">"
        ],
        "checks": [
            {
                "label": "'pocet1.txt' obsahuje nějaké číslo",
                "test": "grep -qE \"[0-9]+\" \"$HOME/pocet1.txt\""
            }
        ]
    },
    {
        "id": 26,
        "set": 1,
        "tier": 2,
        "difficulty": "Sada 1 – 2. Fáze: Posádka",
        "cmd_name": "wc -l",
        "title": "Spočítej řádky",
        "story": "Kolik toho vlastně ten soubor obsahuje?",
        "goal": "Spočítej řádky v souboru 'data/planety.txt' (wc -l) a ulož číslo do 'pocet2.txt'.",
        "hint": "cd ~\nwc -l < data/planety.txt > pocet2.txt",
        "commands": [
            "wc -l",
            ">"
        ],
        "checks": [
            {
                "label": "'pocet2.txt' obsahuje nějaké číslo",
                "test": "grep -qE \"[0-9]+\" \"$HOME/pocet2.txt\""
            }
        ]
    },
    {
        "id": 27,
        "set": 1,
        "tier": 3,
        "difficulty": "Sada 1 – 3. Fáze: Mistr",
        "cmd_name": "wc -l",
        "title": "Spočítej řádky",
        "story": "Kolik toho vlastně ten soubor obsahuje?",
        "goal": "Spočítej řádky v souboru 'README.txt' (wc -l) a ulož číslo do 'pocet3.txt'.",
        "hint": "cd ~\nwc -l < README.txt > pocet3.txt",
        "commands": [
            "wc -l",
            ">"
        ],
        "checks": [
            {
                "label": "'pocet3.txt' obsahuje nějaké číslo",
                "test": "grep -qE \"[0-9]+\" \"$HOME/pocet3.txt\""
            }
        ]
    },
    {
        "id": 28,
        "set": 1,
        "tier": 1,
        "difficulty": "Sada 1 – 1. Fáze: Základy",
        "cmd_name": "rm",
        "title": "Ukliď nepotřebný soubor",
        "story": "Soubor 'smaz1.txt' už nikdo nepotřebuje.",
        "goal": "Smaž soubor 'smaz1.txt'.",
        "hint": "cd ~\nrm smaz1.txt",
        "commands": [
            "rm"
        ],
        "checks": [
            {
                "label": "soubor 'smaz1.txt' už neexistuje",
                "test": "test ! -e \"$HOME/smaz1.txt\""
            }
        ]
    },
    {
        "id": 29,
        "set": 1,
        "tier": 2,
        "difficulty": "Sada 1 – 2. Fáze: Posádka",
        "cmd_name": "rm",
        "title": "Ukliď nepotřebný soubor",
        "story": "Soubor 'smaz2.txt' už nikdo nepotřebuje.",
        "goal": "Smaž soubor 'smaz2.txt'.",
        "hint": "cd ~\nrm smaz2.txt",
        "commands": [
            "rm"
        ],
        "checks": [
            {
                "label": "soubor 'smaz2.txt' už neexistuje",
                "test": "test ! -e \"$HOME/smaz2.txt\""
            }
        ]
    },
    {
        "id": 30,
        "set": 1,
        "tier": 3,
        "difficulty": "Sada 1 – 3. Fáze: Mistr",
        "cmd_name": "rm",
        "title": "Ukliď nepotřebný soubor",
        "story": "Soubor 'smaz3.txt' už nikdo nepotřebuje.",
        "goal": "Smaž soubor 'smaz3.txt'.",
        "hint": "cd ~\nrm smaz3.txt",
        "commands": [
            "rm"
        ],
        "checks": [
            {
                "label": "soubor 'smaz3.txt' už neexistuje",
                "test": "test ! -e \"$HOME/smaz3.txt\""
            }
        ]
    },
    {
        "id": 31,
        "set": 2,
        "tier": 1,
        "difficulty": "Sada 2 – 1. Fáze: Základy",
        "cmd_name": "cp",
        "title": "Vytvoř zálohu",
        "story": "Než cokoliv upravíš, vždycky si to nejdřív zálohuj.",
        "goal": "Zkopíruj soubor 'data/planety.txt' do nového souboru 'zaloha_planet.txt'.",
        "hint": "cd ~\ncp data/planety.txt zaloha_planet.txt",
        "commands": [
            "cp"
        ],
        "checks": [
            {
                "label": "existuje kopie 'zaloha_planet.txt'",
                "test": "test -f \"$HOME/zaloha_planet.txt\""
            },
            {
                "label": "kopie má správný obsah",
                "test": "grep -qF \"Merkur\" \"$HOME/zaloha_planet.txt\""
            }
        ]
    },
    {
        "id": 32,
        "set": 2,
        "tier": 2,
        "difficulty": "Sada 2 – 2. Fáze: Posádka",
        "cmd_name": "cp",
        "title": "Vytvoř zálohu",
        "story": "Než cokoliv upravíš, vždycky si to nejdřív zálohuj.",
        "goal": "Zkopíruj soubor 'data/posadka.txt' do nového souboru 'zaloha_posadky.txt'.",
        "hint": "cd ~\ncp data/posadka.txt zaloha_posadky.txt",
        "commands": [
            "cp"
        ],
        "checks": [
            {
                "label": "existuje kopie 'zaloha_posadky.txt'",
                "test": "test -f \"$HOME/zaloha_posadky.txt\""
            },
            {
                "label": "kopie má správný obsah",
                "test": "grep -qF \"Tux\" \"$HOME/zaloha_posadky.txt\""
            }
        ]
    },
    {
        "id": 33,
        "set": 2,
        "tier": 3,
        "difficulty": "Sada 2 – 3. Fáze: Mistr",
        "cmd_name": "cp",
        "title": "Vytvoř zálohu",
        "story": "Než cokoliv upravíš, vždycky si to nejdřív zálohuj.",
        "goal": "Zkopíruj soubor 'README.txt' do nového souboru 'zaloha_readme.txt'.",
        "hint": "cd ~\ncp README.txt zaloha_readme.txt",
        "commands": [
            "cp"
        ],
        "checks": [
            {
                "label": "existuje kopie 'zaloha_readme.txt'",
                "test": "test -f \"$HOME/zaloha_readme.txt\""
            },
            {
                "label": "kopie má správný obsah",
                "test": "grep -qF \"PÍSKOVIŠTI\" \"$HOME/zaloha_readme.txt\""
            }
        ]
    },
    {
        "id": 34,
        "set": 2,
        "tier": 1,
        "difficulty": "Sada 2 – 1. Fáze: Základy",
        "cmd_name": "mv",
        "title": "Přejmenuj soubor",
        "story": "Soubor 'zaloha_planet.txt' potřebuje lepší jméno.",
        "goal": "Přejmenuj 'zaloha_planet.txt' na 'planety_final.txt' (mv).",
        "hint": "cd ~\nmv zaloha_planet.txt planety_final.txt",
        "commands": [
            "mv"
        ],
        "checks": [
            {
                "label": "existuje 'planety_final.txt'",
                "test": "test -f \"$HOME/planety_final.txt\""
            },
            {
                "label": "'zaloha_planet.txt' už neexistuje",
                "test": "test ! -e \"$HOME/zaloha_planet.txt\""
            }
        ]
    },
    {
        "id": 35,
        "set": 2,
        "tier": 2,
        "difficulty": "Sada 2 – 2. Fáze: Posádka",
        "cmd_name": "mv",
        "title": "Přejmenuj soubor",
        "story": "Soubor 'zaloha_posadky.txt' potřebuje lepší jméno.",
        "goal": "Přejmenuj 'zaloha_posadky.txt' na 'posadka_final.txt' (mv).",
        "hint": "cd ~\nmv zaloha_posadky.txt posadka_final.txt",
        "commands": [
            "mv"
        ],
        "checks": [
            {
                "label": "existuje 'posadka_final.txt'",
                "test": "test -f \"$HOME/posadka_final.txt\""
            },
            {
                "label": "'zaloha_posadky.txt' už neexistuje",
                "test": "test ! -e \"$HOME/zaloha_posadky.txt\""
            }
        ]
    },
    {
        "id": 36,
        "set": 2,
        "tier": 3,
        "difficulty": "Sada 2 – 3. Fáze: Mistr",
        "cmd_name": "mv",
        "title": "Přejmenuj soubor",
        "story": "Soubor 'zaloha_readme.txt' potřebuje lepší jméno.",
        "goal": "Přejmenuj 'zaloha_readme.txt' na 'readme_final.txt' (mv).",
        "hint": "cd ~\nmv zaloha_readme.txt readme_final.txt",
        "commands": [
            "mv"
        ],
        "checks": [
            {
                "label": "existuje 'readme_final.txt'",
                "test": "test -f \"$HOME/readme_final.txt\""
            },
            {
                "label": "'zaloha_readme.txt' už neexistuje",
                "test": "test ! -e \"$HOME/zaloha_readme.txt\""
            }
        ]
    },
    {
        "id": 37,
        "set": 2,
        "tier": 1,
        "difficulty": "Sada 2 – 1. Fáze: Základy",
        "cmd_name": "find",
        "title": "Najdi soubor v systému",
        "story": "Nevíš přesně, kde soubor leží? Nech to najít 'find'.",
        "goal": "Najdi v domovské složce soubory podle vzoru '*.sh' a výstup ulož do 'vsechny_sh.txt'.",
        "hint": "cd ~\nfind . -name \"*.sh\" > vsechny_sh.txt",
        "commands": [
            "find",
            ">"
        ],
        "checks": [
            {
                "label": "'vsechny_sh.txt' obsahuje výsledek hledání",
                "test": "grep -qF \"start.sh\" \"$HOME/vsechny_sh.txt\""
            }
        ]
    },
    {
        "id": 38,
        "set": 2,
        "tier": 2,
        "difficulty": "Sada 2 – 2. Fáze: Posádka",
        "cmd_name": "find",
        "title": "Najdi soubor v systému",
        "story": "Nevíš přesně, kde soubor leží? Nech to najít 'find'.",
        "goal": "Najdi v domovské složce soubory podle vzoru 'planety.txt' a výstup ulož do 'hledej_planety.txt'.",
        "hint": "cd ~\nfind . -name \"planety.txt\" > hledej_planety.txt",
        "commands": [
            "find",
            ">"
        ],
        "checks": [
            {
                "label": "'hledej_planety.txt' obsahuje výsledek hledání",
                "test": "grep -qF \"planety.txt\" \"$HOME/hledej_planety.txt\""
            }
        ]
    },
    {
        "id": 39,
        "set": 2,
        "tier": 3,
        "difficulty": "Sada 2 – 3. Fáze: Mistr",
        "cmd_name": "find",
        "title": "Najdi soubor v systému",
        "story": "Nevíš přesně, kde soubor leží? Nech to najít 'find'.",
        "goal": "Najdi v domovské složce soubory podle vzoru '.tajny_kod.txt' a výstup ulož do 'hledej_kod.txt'.",
        "hint": "cd ~\nfind . -name \".tajny_kod.txt\" > hledej_kod.txt",
        "commands": [
            "find",
            ">"
        ],
        "checks": [
            {
                "label": "'hledej_kod.txt' obsahuje výsledek hledání",
                "test": "grep -qF \"tajny_kod\" \"$HOME/hledej_kod.txt\""
            }
        ]
    },
    {
        "id": 40,
        "set": 2,
        "tier": 1,
        "difficulty": "Sada 2 – 1. Fáze: Základy",
        "cmd_name": "ping",
        "title": "Otestuj spojení",
        "story": "I bez internetu si můžeš otestovat, že síťová vrstva vůbec funguje – přes 'loopback' (127.0.0.1, sám sobě).",
        "goal": "Pošli 3× ping na 127.0.0.1 (ping -c 3 127.0.0.1) a ulož výstup do 'ping1.txt'.",
        "hint": "cd ~\nping -c 3 127.0.0.1 > ping1.txt",
        "commands": [
            "ping",
            ">"
        ],
        "checks": [
            {
                "label": "spojení proběhlo bez ztráty paketů",
                "test": "grep -qF \"0% packet loss\" \"$HOME/ping1.txt\""
            }
        ]
    },
    {
        "id": 41,
        "set": 2,
        "tier": 2,
        "difficulty": "Sada 2 – 2. Fáze: Posádka",
        "cmd_name": "ping",
        "title": "Otestuj spojení",
        "story": "I bez internetu si můžeš otestovat, že síťová vrstva vůbec funguje – přes 'loopback' (127.0.0.1, sám sobě).",
        "goal": "Pošli 2× ping na 127.0.0.1 (ping -c 2 127.0.0.1) a ulož výstup do 'ping2.txt'.",
        "hint": "cd ~\nping -c 2 127.0.0.1 > ping2.txt",
        "commands": [
            "ping",
            ">"
        ],
        "checks": [
            {
                "label": "spojení proběhlo bez ztráty paketů",
                "test": "grep -qF \"0% packet loss\" \"$HOME/ping2.txt\""
            }
        ]
    },
    {
        "id": 42,
        "set": 2,
        "tier": 3,
        "difficulty": "Sada 2 – 3. Fáze: Mistr",
        "cmd_name": "ping",
        "title": "Otestuj spojení",
        "story": "I bez internetu si můžeš otestovat, že síťová vrstva vůbec funguje – přes 'loopback' (127.0.0.1, sám sobě).",
        "goal": "Pošli 4× ping na 127.0.0.1 (ping -c 4 127.0.0.1) a ulož výstup do 'ping3.txt'.",
        "hint": "cd ~\nping -c 4 127.0.0.1 > ping3.txt",
        "commands": [
            "ping",
            ">"
        ],
        "checks": [
            {
                "label": "spojení proběhlo bez ztráty paketů",
                "test": "grep -qF \"0% packet loss\" \"$HOME/ping3.txt\""
            }
        ]
    },
    {
        "id": 43,
        "set": 2,
        "tier": 1,
        "difficulty": "Sada 2 – 1. Fáze: Základy",
        "cmd_name": "echo",
        "title": "Zapiš hlášení",
        "story": "Velitelství chce písemné hlášení.",
        "goal": "Zapiš větu 'Základna TUX-1 hlásí pořádek' do nového souboru 'hlaseni1.txt' (echo).",
        "hint": "cd ~\necho \"Základna TUX-1 hlásí pořádek\" > hlaseni1.txt",
        "commands": [
            "echo",
            ">"
        ],
        "checks": [
            {
                "label": "'hlaseni1.txt' obsahuje hlášení",
                "test": "grep -qF \"Základna TUX-1 hlásí pořádek\" \"$HOME/hlaseni1.txt\""
            }
        ]
    },
    {
        "id": 44,
        "set": 2,
        "tier": 2,
        "difficulty": "Sada 2 – 2. Fáze: Posádka",
        "cmd_name": "echo",
        "title": "Zapiš hlášení",
        "story": "Velitelství chce písemné hlášení.",
        "goal": "Zapiš větu 'Zásoby doplněny' do nového souboru 'hlaseni2.txt' (echo).",
        "hint": "cd ~\necho \"Zásoby doplněny\" > hlaseni2.txt",
        "commands": [
            "echo",
            ">"
        ],
        "checks": [
            {
                "label": "'hlaseni2.txt' obsahuje hlášení",
                "test": "grep -qF \"Zásoby doplněny\" \"$HOME/hlaseni2.txt\""
            }
        ]
    },
    {
        "id": 45,
        "set": 2,
        "tier": 3,
        "difficulty": "Sada 2 – 3. Fáze: Mistr",
        "cmd_name": "echo",
        "title": "Zapiš hlášení",
        "story": "Velitelství chce písemné hlášení.",
        "goal": "Zapiš větu 'Posádka připravena na start' do nového souboru 'hlaseni3.txt' (echo).",
        "hint": "cd ~\necho \"Posádka připravena na start\" > hlaseni3.txt",
        "commands": [
            "echo",
            ">"
        ],
        "checks": [
            {
                "label": "'hlaseni3.txt' obsahuje hlášení",
                "test": "grep -qF \"Posádka připravena na start\" \"$HOME/hlaseni3.txt\""
            }
        ]
    },
    {
        "id": 46,
        "set": 2,
        "tier": 1,
        "difficulty": "Sada 2 – 1. Fáze: Základy",
        "cmd_name": "head",
        "title": "Nahlédni na začátek",
        "story": "Nemusíš číst celý soubor – stačí první řádky.",
        "goal": "Vypiš prvních 2 řádky souboru 'data/planety.txt' (head -n 2) do 'prvni1.txt'.",
        "hint": "cd ~\nhead -n 2 data/planety.txt > prvni1.txt",
        "commands": [
            "head",
            ">"
        ],
        "checks": [
            {
                "label": "'prvni1.txt' obsahuje 'Merkur'",
                "test": "grep -qF \"Merkur\" \"$HOME/prvni1.txt\""
            },
            {
                "label": "'prvni1.txt' neobsahuje 'Jupiter' (jen první řádky!)",
                "test": "! grep -qF \"Jupiter\" \"$HOME/prvni1.txt\""
            }
        ]
    },
    {
        "id": 47,
        "set": 2,
        "tier": 2,
        "difficulty": "Sada 2 – 2. Fáze: Posádka",
        "cmd_name": "head",
        "title": "Nahlédni na začátek",
        "story": "Nemusíš číst celý soubor – stačí první řádky.",
        "goal": "Vypiš prvních 1 řádky souboru 'data/posadka.txt' (head -n 1) do 'prvni2.txt'.",
        "hint": "cd ~\nhead -n 1 data/posadka.txt > prvni2.txt",
        "commands": [
            "head",
            ">"
        ],
        "checks": [
            {
                "label": "'prvni2.txt' obsahuje 'Kapitán'",
                "test": "grep -qF \"Kapitán\" \"$HOME/prvni2.txt\""
            },
            {
                "label": "'prvni2.txt' neobsahuje 'Kuchař' (jen první řádky!)",
                "test": "! grep -qF \"Kuchař\" \"$HOME/prvni2.txt\""
            }
        ]
    },
    {
        "id": 48,
        "set": 2,
        "tier": 3,
        "difficulty": "Sada 2 – 3. Fáze: Mistr",
        "cmd_name": "head",
        "title": "Nahlédni na začátek",
        "story": "Nemusíš číst celý soubor – stačí první řádky.",
        "goal": "Vypiš prvních 3 řádky souboru 'data/planety.txt' (head -n 3) do 'prvni3.txt'.",
        "hint": "cd ~\nhead -n 3 data/planety.txt > prvni3.txt",
        "commands": [
            "head",
            ">"
        ],
        "checks": [
            {
                "label": "'prvni3.txt' obsahuje 'Země'",
                "test": "grep -qF \"Země\" \"$HOME/prvni3.txt\""
            },
            {
                "label": "'prvni3.txt' neobsahuje 'Saturn' (jen první řádky!)",
                "test": "! grep -qF \"Saturn\" \"$HOME/prvni3.txt\""
            }
        ]
    },
    {
        "id": 49,
        "set": 2,
        "tier": 1,
        "difficulty": "Sada 2 – 1. Fáze: Základy",
        "cmd_name": "tail",
        "title": "Nahlédni na konec",
        "story": "A co poslední řádky souboru?",
        "goal": "Vypiš posledních 2 řádky souboru 'data/planety.txt' (tail -n 2) do 'posledni1.txt'.",
        "hint": "cd ~\ntail -n 2 data/planety.txt > posledni1.txt",
        "commands": [
            "tail",
            ">"
        ],
        "checks": [
            {
                "label": "'posledni1.txt' obsahuje 'Saturn'",
                "test": "grep -qF \"Saturn\" \"$HOME/posledni1.txt\""
            },
            {
                "label": "'posledni1.txt' neobsahuje 'Merkur' (jen poslední řádky!)",
                "test": "! grep -qF \"Merkur\" \"$HOME/posledni1.txt\""
            }
        ]
    },
    {
        "id": 50,
        "set": 2,
        "tier": 2,
        "difficulty": "Sada 2 – 2. Fáze: Posádka",
        "cmd_name": "tail",
        "title": "Nahlédni na konec",
        "story": "A co poslední řádky souboru?",
        "goal": "Vypiš posledních 1 řádky souboru 'data/posadka.txt' (tail -n 1) do 'posledni2.txt'.",
        "hint": "cd ~\ntail -n 1 data/posadka.txt > posledni2.txt",
        "commands": [
            "tail",
            ">"
        ],
        "checks": [
            {
                "label": "'posledni2.txt' obsahuje 'Kuchař'",
                "test": "grep -qF \"Kuchař\" \"$HOME/posledni2.txt\""
            },
            {
                "label": "'posledni2.txt' neobsahuje 'Kapitán' (jen poslední řádky!)",
                "test": "! grep -qF \"Kapitán\" \"$HOME/posledni2.txt\""
            }
        ]
    },
    {
        "id": 51,
        "set": 2,
        "tier": 3,
        "difficulty": "Sada 2 – 3. Fáze: Mistr",
        "cmd_name": "tail",
        "title": "Nahlédni na konec",
        "story": "A co poslední řádky souboru?",
        "goal": "Vypiš posledních 3 řádky souboru 'data/planety.txt' (tail -n 3) do 'posledni3.txt'.",
        "hint": "cd ~\ntail -n 3 data/planety.txt > posledni3.txt",
        "commands": [
            "tail",
            ">"
        ],
        "checks": [
            {
                "label": "'posledni3.txt' obsahuje 'Jupiter'",
                "test": "grep -qF \"Jupiter\" \"$HOME/posledni3.txt\""
            },
            {
                "label": "'posledni3.txt' neobsahuje 'Venuše' (jen poslední řádky!)",
                "test": "! grep -qF \"Venuše\" \"$HOME/posledni3.txt\""
            }
        ]
    },
    {
        "id": 52,
        "set": 2,
        "tier": 1,
        "difficulty": "Sada 2 – 1. Fáze: Základy",
        "cmd_name": "rmdir",
        "title": "Zruš prázdný sklad",
        "story": "Složka 'prazdna1' je prázdná a už se nevyužívá.",
        "goal": "Smaž prázdnou složku 'prazdna1' (rmdir).",
        "hint": "cd ~\nrmdir prazdna1",
        "commands": [
            "rmdir"
        ],
        "checks": [
            {
                "label": "'prazdna1' už neexistuje",
                "test": "test ! -e \"$HOME/prazdna1\""
            }
        ]
    },
    {
        "id": 53,
        "set": 2,
        "tier": 2,
        "difficulty": "Sada 2 – 2. Fáze: Posádka",
        "cmd_name": "rmdir",
        "title": "Zruš prázdný sklad",
        "story": "Složka 'prazdna2' je prázdná a už se nevyužívá.",
        "goal": "Smaž prázdnou složku 'prazdna2' (rmdir).",
        "hint": "cd ~\nrmdir prazdna2",
        "commands": [
            "rmdir"
        ],
        "checks": [
            {
                "label": "'prazdna2' už neexistuje",
                "test": "test ! -e \"$HOME/prazdna2\""
            }
        ]
    },
    {
        "id": 54,
        "set": 2,
        "tier": 3,
        "difficulty": "Sada 2 – 3. Fáze: Mistr",
        "cmd_name": "rmdir",
        "title": "Zruš prázdný sklad",
        "story": "Složka 'prazdna3' je prázdná a už se nevyužívá.",
        "goal": "Smaž prázdnou složku 'prazdna3' (rmdir).",
        "hint": "cd ~\nrmdir prazdna3",
        "commands": [
            "rmdir"
        ],
        "checks": [
            {
                "label": "'prazdna3' už neexistuje",
                "test": "test ! -e \"$HOME/prazdna3\""
            }
        ]
    },
    {
        "id": 55,
        "set": 2,
        "tier": 1,
        "difficulty": "Sada 2 – 1. Fáze: Základy",
        "cmd_name": "df",
        "title": "Zkontroluj místo na disku",
        "story": "Kolik místa vlastně na základně máš?",
        "goal": "Zjisti zaplnění disku (df -h) a ulož výstup do 'misto1.txt'.",
        "hint": "cd ~\ndf -h > misto1.txt",
        "commands": [
            "df -h",
            ">"
        ],
        "checks": [
            {
                "label": "'misto1.txt' obsahuje přehled disku (%)",
                "test": "grep -qE \"%\" \"$HOME/misto1.txt\""
            }
        ]
    },
    {
        "id": 56,
        "set": 2,
        "tier": 2,
        "difficulty": "Sada 2 – 2. Fáze: Posádka",
        "cmd_name": "df",
        "title": "Zkontroluj místo na disku",
        "story": "Kolik místa vlastně na základně máš?",
        "goal": "Zjisti zaplnění disku (df -h) a ulož výstup do 'misto2.txt'.",
        "hint": "cd ~\ndf -h > misto2.txt",
        "commands": [
            "df -h",
            ">"
        ],
        "checks": [
            {
                "label": "'misto2.txt' obsahuje přehled disku (%)",
                "test": "grep -qE \"%\" \"$HOME/misto2.txt\""
            }
        ]
    },
    {
        "id": 57,
        "set": 2,
        "tier": 3,
        "difficulty": "Sada 2 – 3. Fáze: Mistr",
        "cmd_name": "df",
        "title": "Zkontroluj místo na disku",
        "story": "Kolik místa vlastně na základně máš?",
        "goal": "Zjisti zaplnění disku (df -h) a ulož výstup do 'misto3.txt'.",
        "hint": "cd ~\ndf -h > misto3.txt",
        "commands": [
            "df -h",
            ">"
        ],
        "checks": [
            {
                "label": "'misto3.txt' obsahuje přehled disku (%)",
                "test": "grep -qE \"%\" \"$HOME/misto3.txt\""
            }
        ]
    },
    {
        "id": 58,
        "set": 2,
        "tier": 1,
        "difficulty": "Sada 2 – 1. Fáze: Základy",
        "cmd_name": "start.sh",
        "title": "Odblokuj a spusť skript",
        "story": "Skript 'start.sh' čeká na spuštění, ale nemá právo 'x'.",
        "goal": "Přidej souboru 'start.sh' právo ke spuštění (chmod +x) a spusť ho (./start.sh).",
        "hint": "cd ~\nchmod +x start.sh\n./start.sh",
        "commands": [
            "chmod",
            "./start.sh"
        ],
        "checks": [
            {
                "label": "'start.sh' má právo ke spuštění",
                "test": "test -x \"$HOME/start.sh\""
            },
            {
                "label": "skript proběhl (vznikl 'starty.log')",
                "test": "test -s \"$HOME/starty.log\""
            }
        ]
    },
    {
        "id": 59,
        "set": 2,
        "tier": 2,
        "difficulty": "Sada 2 – 2. Fáze: Posádka",
        "cmd_name": "motor.sh",
        "title": "Odblokuj a spusť skript",
        "story": "Skript 'motor.sh' čeká na spuštění, ale nemá právo 'x'.",
        "goal": "Přidej souboru 'motor.sh' právo ke spuštění (chmod +x) a spusť ho (./motor.sh).",
        "hint": "cd ~\nchmod +x motor.sh\n./motor.sh",
        "commands": [
            "chmod",
            "./motor.sh"
        ],
        "checks": [
            {
                "label": "'motor.sh' má právo ke spuštění",
                "test": "test -x \"$HOME/motor.sh\""
            },
            {
                "label": "skript proběhl (vznikl 'motory.log')",
                "test": "test -s \"$HOME/motory.log\""
            }
        ]
    },
    {
        "id": 60,
        "set": 2,
        "tier": 3,
        "difficulty": "Sada 2 – 3. Fáze: Mistr",
        "cmd_name": "majak.sh",
        "title": "Odblokuj a spusť skript",
        "story": "Skript 'majak.sh' čeká na spuštění, ale nemá právo 'x'.",
        "goal": "Přidej souboru 'majak.sh' právo ke spuštění (chmod +x) a spusť ho (./majak.sh).",
        "hint": "cd ~\nchmod +x majak.sh\n./majak.sh",
        "commands": [
            "chmod",
            "./majak.sh"
        ],
        "checks": [
            {
                "label": "'majak.sh' má právo ke spuštění",
                "test": "test -x \"$HOME/majak.sh\""
            },
            {
                "label": "skript proběhl (vznikl 'majak.log')",
                "test": "test -s \"$HOME/majak.log\""
            }
        ]
    },
    {
        "id": 61,
        "set": 3,
        "tier": 1,
        "difficulty": "Sada 3 – 1. Fáze: Základy",
        "cmd_name": "ps",
        "title": "Zkontroluj běžící procesy",
        "story": "Co všechno teď na stanici běží?",
        "goal": "Vypiš běžící procesy (ps) a ulož výstup do 'procesy1.txt'.",
        "hint": "cd ~\nps > procesy1.txt",
        "commands": [
            "ps",
            ">"
        ],
        "checks": [
            {
                "label": "'procesy1.txt' obsahuje výpis procesů (PID)",
                "test": "grep -qF \"PID\" \"$HOME/procesy1.txt\""
            }
        ]
    },
    {
        "id": 62,
        "set": 3,
        "tier": 2,
        "difficulty": "Sada 3 – 2. Fáze: Posádka",
        "cmd_name": "ps",
        "title": "Zkontroluj běžící procesy",
        "story": "Co všechno teď na stanici běží?",
        "goal": "Vypiš běžící procesy (ps) a ulož výstup do 'procesy2.txt'.",
        "hint": "cd ~\nps > procesy2.txt",
        "commands": [
            "ps",
            ">"
        ],
        "checks": [
            {
                "label": "'procesy2.txt' obsahuje výpis procesů (PID)",
                "test": "grep -qF \"PID\" \"$HOME/procesy2.txt\""
            }
        ]
    },
    {
        "id": 63,
        "set": 3,
        "tier": 3,
        "difficulty": "Sada 3 – 3. Fáze: Mistr",
        "cmd_name": "ps",
        "title": "Zkontroluj běžící procesy",
        "story": "Co všechno teď na stanici běží?",
        "goal": "Vypiš běžící procesy (ps) a ulož výstup do 'procesy3.txt'.",
        "hint": "cd ~\nps > procesy3.txt",
        "commands": [
            "ps",
            ">"
        ],
        "checks": [
            {
                "label": "'procesy3.txt' obsahuje výpis procesů (PID)",
                "test": "grep -qF \"PID\" \"$HOME/procesy3.txt\""
            }
        ]
    },
    {
        "id": 64,
        "set": 3,
        "tier": 1,
        "difficulty": "Sada 3 – 1. Fáze: Základy",
        "cmd_name": "free",
        "title": "Zkontroluj paměť",
        "story": "Kolik operační paměti stanice využívá?",
        "goal": "Zjisti stav paměti (free -h) a ulož výstup do 'pamet1.txt'.",
        "hint": "cd ~\nfree -h > pamet1.txt",
        "commands": [
            "free -h",
            ">"
        ],
        "checks": [
            {
                "label": "'pamet1.txt' obsahuje přehled paměti",
                "test": "grep -qF \"Mem\" \"$HOME/pamet1.txt\""
            }
        ]
    },
    {
        "id": 65,
        "set": 3,
        "tier": 2,
        "difficulty": "Sada 3 – 2. Fáze: Posádka",
        "cmd_name": "free",
        "title": "Zkontroluj paměť",
        "story": "Kolik operační paměti stanice využívá?",
        "goal": "Zjisti stav paměti (free -h) a ulož výstup do 'pamet2.txt'.",
        "hint": "cd ~\nfree -h > pamet2.txt",
        "commands": [
            "free -h",
            ">"
        ],
        "checks": [
            {
                "label": "'pamet2.txt' obsahuje přehled paměti",
                "test": "grep -qF \"Mem\" \"$HOME/pamet2.txt\""
            }
        ]
    },
    {
        "id": 66,
        "set": 3,
        "tier": 3,
        "difficulty": "Sada 3 – 3. Fáze: Mistr",
        "cmd_name": "free",
        "title": "Zkontroluj paměť",
        "story": "Kolik operační paměti stanice využívá?",
        "goal": "Zjisti stav paměti (free -h) a ulož výstup do 'pamet3.txt'.",
        "hint": "cd ~\nfree -h > pamet3.txt",
        "commands": [
            "free -h",
            ">"
        ],
        "checks": [
            {
                "label": "'pamet3.txt' obsahuje přehled paměti",
                "test": "grep -qF \"Mem\" \"$HOME/pamet3.txt\""
            }
        ]
    },
    {
        "id": 67,
        "set": 3,
        "tier": 1,
        "difficulty": "Sada 3 – 1. Fáze: Základy",
        "cmd_name": "tar",
        "title": "Zabal hangár do archivu",
        "story": "Obsah složky 'hangar1' z první mise by se měl zálohovat do jednoho souboru.",
        "goal": "Vytvoř archiv 'archiv1.tar' ze složky 'hangar1' (tar -cvf).",
        "hint": "cd ~\ntar -cvf archiv1.tar hangar1",
        "commands": [
            "tar -cvf"
        ],
        "checks": [
            {
                "label": "existuje archiv 'archiv1.tar'",
                "test": "test -s \"$HOME/archiv1.tar\""
            }
        ]
    },
    {
        "id": 68,
        "set": 3,
        "tier": 2,
        "difficulty": "Sada 3 – 2. Fáze: Posádka",
        "cmd_name": "tar",
        "title": "Zabal hangár do archivu",
        "story": "Obsah složky 'hangar2' z první mise by se měl zálohovat do jednoho souboru.",
        "goal": "Vytvoř archiv 'archiv2.tar' ze složky 'hangar2' (tar -cvf).",
        "hint": "cd ~\ntar -cvf archiv2.tar hangar2",
        "commands": [
            "tar -cvf"
        ],
        "checks": [
            {
                "label": "existuje archiv 'archiv2.tar'",
                "test": "test -s \"$HOME/archiv2.tar\""
            }
        ]
    },
    {
        "id": 69,
        "set": 3,
        "tier": 3,
        "difficulty": "Sada 3 – 3. Fáze: Mistr",
        "cmd_name": "tar",
        "title": "Zabal hangár do archivu",
        "story": "Obsah složky 'hangar3' z první mise by se měl zálohovat do jednoho souboru.",
        "goal": "Vytvoř archiv 'archiv3.tar' ze složky 'hangar3' (tar -cvf).",
        "hint": "cd ~\ntar -cvf archiv3.tar hangar3",
        "commands": [
            "tar -cvf"
        ],
        "checks": [
            {
                "label": "existuje archiv 'archiv3.tar'",
                "test": "test -s \"$HOME/archiv3.tar\""
            }
        ]
    },
    {
        "id": 70,
        "set": 3,
        "tier": 1,
        "difficulty": "Sada 3 – 1. Fáze: Základy",
        "cmd_name": "gzip",
        "title": "Zkomprimuj archiv",
        "story": "Archiv 'archiv1.tar' zabírá zbytečně moc místa.",
        "goal": "Zkomprimuj archiv 'archiv1.tar' (gzip -k, aby originál zůstal zachovaný).",
        "hint": "cd ~\ngzip -k archiv1.tar",
        "commands": [
            "gzip -k"
        ],
        "checks": [
            {
                "label": "existuje 'archiv1.tar.gz'",
                "test": "test -s \"$HOME/archiv1.tar.gz\""
            }
        ]
    },
    {
        "id": 71,
        "set": 3,
        "tier": 2,
        "difficulty": "Sada 3 – 2. Fáze: Posádka",
        "cmd_name": "gzip",
        "title": "Zkomprimuj archiv",
        "story": "Archiv 'archiv2.tar' zabírá zbytečně moc místa.",
        "goal": "Zkomprimuj archiv 'archiv2.tar' (gzip -k, aby originál zůstal zachovaný).",
        "hint": "cd ~\ngzip -k archiv2.tar",
        "commands": [
            "gzip -k"
        ],
        "checks": [
            {
                "label": "existuje 'archiv2.tar.gz'",
                "test": "test -s \"$HOME/archiv2.tar.gz\""
            }
        ]
    },
    {
        "id": 72,
        "set": 3,
        "tier": 3,
        "difficulty": "Sada 3 – 3. Fáze: Mistr",
        "cmd_name": "gzip",
        "title": "Zkomprimuj archiv",
        "story": "Archiv 'archiv3.tar' zabírá zbytečně moc místa.",
        "goal": "Zkomprimuj archiv 'archiv3.tar' (gzip -k, aby originál zůstal zachovaný).",
        "hint": "cd ~\ngzip -k archiv3.tar",
        "commands": [
            "gzip -k"
        ],
        "checks": [
            {
                "label": "existuje 'archiv3.tar.gz'",
                "test": "test -s \"$HOME/archiv3.tar.gz\""
            }
        ]
    },
    {
        "id": 73,
        "set": 3,
        "tier": 1,
        "difficulty": "Sada 3 – 1. Fáze: Základy",
        "cmd_name": "alias",
        "title": "Vytvoř si zkratku",
        "story": "Zkušení kadeti si zkracují časté příkazy.",
        "goal": "Přidej do souboru ~/.bashrc trvalou zkratku: alias ll='ls -la'.",
        "hint": "cd ~\necho \"alias ll='ls -la'\" >> ~/.bashrc",
        "commands": [
            "alias",
            ">>"
        ],
        "checks": [
            {
                "label": "~/.bashrc obsahuje zkratku 'll'",
                "test": "grep -qF \"alias ll=\" \"$HOME/.bashrc\""
            }
        ]
    },
    {
        "id": 74,
        "set": 3,
        "tier": 2,
        "difficulty": "Sada 3 – 2. Fáze: Posádka",
        "cmd_name": "alias",
        "title": "Vytvoř si zkratku",
        "story": "Zkušení kadeti si zkracují časté příkazy.",
        "goal": "Přidej do souboru ~/.bashrc trvalou zkratku: alias tecka='pwd'.",
        "hint": "cd ~\necho \"alias tecka='pwd'\" >> ~/.bashrc",
        "commands": [
            "alias",
            ">>"
        ],
        "checks": [
            {
                "label": "~/.bashrc obsahuje zkratku 'tecka'",
                "test": "grep -qF \"alias tecka=\" \"$HOME/.bashrc\""
            }
        ]
    },
    {
        "id": 75,
        "set": 3,
        "tier": 3,
        "difficulty": "Sada 3 – 3. Fáze: Mistr",
        "cmd_name": "alias",
        "title": "Vytvoř si zkratku",
        "story": "Zkušení kadeti si zkracují časté příkazy.",
        "goal": "Přidej do souboru ~/.bashrc trvalou zkratku: alias mise='cat README.txt'.",
        "hint": "cd ~\necho \"alias mise='cat README.txt'\" >> ~/.bashrc",
        "commands": [
            "alias",
            ">>"
        ],
        "checks": [
            {
                "label": "~/.bashrc obsahuje zkratku 'mise'",
                "test": "grep -qF \"alias mise=\" \"$HOME/.bashrc\""
            }
        ]
    },
    {
        "id": 76,
        "set": 3,
        "tier": 1,
        "difficulty": "Sada 3 – 1. Fáze: Základy",
        "cmd_name": "date",
        "title": "Zaznamenej čas",
        "story": "Kolik je vlastně na stanici hodin?",
        "goal": "Zjisti aktuální datum a čas (date) a ulož výstup do 'cas1.txt'.",
        "hint": "cd ~\ndate > cas1.txt",
        "commands": [
            "date",
            ">"
        ],
        "checks": [
            {
                "label": "'cas1.txt' obsahuje rok (202x)",
                "test": "grep -qE \"20[0-9][0-9]\" \"$HOME/cas1.txt\""
            }
        ]
    },
    {
        "id": 77,
        "set": 3,
        "tier": 2,
        "difficulty": "Sada 3 – 2. Fáze: Posádka",
        "cmd_name": "date",
        "title": "Zaznamenej čas",
        "story": "Kolik je vlastně na stanici hodin?",
        "goal": "Zjisti aktuální datum a čas (date) a ulož výstup do 'cas2.txt'.",
        "hint": "cd ~\ndate > cas2.txt",
        "commands": [
            "date",
            ">"
        ],
        "checks": [
            {
                "label": "'cas2.txt' obsahuje rok (202x)",
                "test": "grep -qE \"20[0-9][0-9]\" \"$HOME/cas2.txt\""
            }
        ]
    },
    {
        "id": 78,
        "set": 3,
        "tier": 3,
        "difficulty": "Sada 3 – 3. Fáze: Mistr",
        "cmd_name": "date",
        "title": "Zaznamenej čas",
        "story": "Kolik je vlastně na stanici hodin?",
        "goal": "Zjisti aktuální datum a čas (date) a ulož výstup do 'cas3.txt'.",
        "hint": "cd ~\ndate > cas3.txt",
        "commands": [
            "date",
            ">"
        ],
        "checks": [
            {
                "label": "'cas3.txt' obsahuje rok (202x)",
                "test": "grep -qE \"20[0-9][0-9]\" \"$HOME/cas3.txt\""
            }
        ]
    },
    {
        "id": 79,
        "set": 3,
        "tier": 1,
        "difficulty": "Sada 3 – 1. Fáze: Základy",
        "cmd_name": "uname -a",
        "title": "Zjisti verzi jádra",
        "story": "Jaký systém vlastně pohání celou stanici?",
        "goal": "Zjisti informace o jádru (uname -a) a ulož výstup do 'system1.txt'.",
        "hint": "cd ~\nuname -a > system1.txt",
        "commands": [
            "uname -a",
            ">"
        ],
        "checks": [
            {
                "label": "'system1.txt' obsahuje slovo 'Linux'",
                "test": "grep -qF \"Linux\" \"$HOME/system1.txt\""
            }
        ]
    },
    {
        "id": 80,
        "set": 3,
        "tier": 2,
        "difficulty": "Sada 3 – 2. Fáze: Posádka",
        "cmd_name": "uname -a",
        "title": "Zjisti verzi jádra",
        "story": "Jaký systém vlastně pohání celou stanici?",
        "goal": "Zjisti informace o jádru (uname -a) a ulož výstup do 'system2.txt'.",
        "hint": "cd ~\nuname -a > system2.txt",
        "commands": [
            "uname -a",
            ">"
        ],
        "checks": [
            {
                "label": "'system2.txt' obsahuje slovo 'Linux'",
                "test": "grep -qF \"Linux\" \"$HOME/system2.txt\""
            }
        ]
    },
    {
        "id": 81,
        "set": 3,
        "tier": 3,
        "difficulty": "Sada 3 – 3. Fáze: Mistr",
        "cmd_name": "uname -a",
        "title": "Zjisti verzi jádra",
        "story": "Jaký systém vlastně pohání celou stanici?",
        "goal": "Zjisti informace o jádru (uname -a) a ulož výstup do 'system3.txt'.",
        "hint": "cd ~\nuname -a > system3.txt",
        "commands": [
            "uname -a",
            ">"
        ],
        "checks": [
            {
                "label": "'system3.txt' obsahuje slovo 'Linux'",
                "test": "grep -qF \"Linux\" \"$HOME/system3.txt\""
            }
        ]
    },
    {
        "id": 82,
        "set": 3,
        "tier": 1,
        "difficulty": "Sada 3 – 1. Fáze: Základy",
        "cmd_name": "uname -n",
        "title": "Zjisti jméno stanice",
        "story": "Každá stanice má svoje jméno v síti.",
        "goal": "Zjisti název stanice (uname -n) a ulož výstup do 'nazev1.txt'.",
        "hint": "cd ~\nuname -n > nazev1.txt",
        "commands": [
            "uname -n",
            ">"
        ],
        "checks": [
            {
                "label": "'nazev1.txt' není prázdný",
                "test": "test -s \"$HOME/nazev1.txt\""
            }
        ]
    },
    {
        "id": 83,
        "set": 3,
        "tier": 2,
        "difficulty": "Sada 3 – 2. Fáze: Posádka",
        "cmd_name": "uname -n",
        "title": "Zjisti jméno stanice",
        "story": "Každá stanice má svoje jméno v síti.",
        "goal": "Zjisti název stanice (uname -n) a ulož výstup do 'nazev2.txt'.",
        "hint": "cd ~\nuname -n > nazev2.txt",
        "commands": [
            "uname -n",
            ">"
        ],
        "checks": [
            {
                "label": "'nazev2.txt' není prázdný",
                "test": "test -s \"$HOME/nazev2.txt\""
            }
        ]
    },
    {
        "id": 84,
        "set": 3,
        "tier": 3,
        "difficulty": "Sada 3 – 3. Fáze: Mistr",
        "cmd_name": "uname -n",
        "title": "Zjisti jméno stanice",
        "story": "Každá stanice má svoje jméno v síti.",
        "goal": "Zjisti název stanice (uname -n) a ulož výstup do 'nazev3.txt'.",
        "hint": "cd ~\nuname -n > nazev3.txt",
        "commands": [
            "uname -n",
            ">"
        ],
        "checks": [
            {
                "label": "'nazev3.txt' není prázdný",
                "test": "test -s \"$HOME/nazev3.txt\""
            }
        ]
    },
    {
        "id": 85,
        "set": 3,
        "tier": 1,
        "difficulty": "Sada 3 – 1. Fáze: Základy",
        "cmd_name": "env",
        "title": "Zobraz systémové proměnné",
        "story": "Systém si pamatuje spoustu nastavení v proměnných prostředí.",
        "goal": "Vypiš proměnné prostředí (env) a ulož výstup do 'promenne1.txt'.",
        "hint": "cd ~\nenv > promenne1.txt",
        "commands": [
            "env",
            ">"
        ],
        "checks": [
            {
                "label": "'promenne1.txt' obsahuje 'HOME='",
                "test": "grep -qF \"HOME=\" \"$HOME/promenne1.txt\""
            }
        ]
    },
    {
        "id": 86,
        "set": 3,
        "tier": 2,
        "difficulty": "Sada 3 – 2. Fáze: Posádka",
        "cmd_name": "env",
        "title": "Zobraz systémové proměnné",
        "story": "Systém si pamatuje spoustu nastavení v proměnných prostředí.",
        "goal": "Vypiš proměnné prostředí (env) a ulož výstup do 'promenne2.txt'.",
        "hint": "cd ~\nenv > promenne2.txt",
        "commands": [
            "env",
            ">"
        ],
        "checks": [
            {
                "label": "'promenne2.txt' obsahuje 'HOME='",
                "test": "grep -qF \"HOME=\" \"$HOME/promenne2.txt\""
            }
        ]
    },
    {
        "id": 87,
        "set": 3,
        "tier": 3,
        "difficulty": "Sada 3 – 3. Fáze: Mistr",
        "cmd_name": "env",
        "title": "Zobraz systémové proměnné",
        "story": "Systém si pamatuje spoustu nastavení v proměnných prostředí.",
        "goal": "Vypiš proměnné prostředí (env) a ulož výstup do 'promenne3.txt'.",
        "hint": "cd ~\nenv > promenne3.txt",
        "commands": [
            "env",
            ">"
        ],
        "checks": [
            {
                "label": "'promenne3.txt' obsahuje 'HOME='",
                "test": "grep -qF \"HOME=\" \"$HOME/promenne3.txt\""
            }
        ]
    },
    {
        "id": 88,
        "set": 3,
        "tier": 1,
        "difficulty": "Sada 3 – 1. Fáze: Základy",
        "cmd_name": "pgrep",
        "title": "Najdi proces na pozadí",
        "story": "Spusť dlouho běžící proces a najdi jeho PID – ukončování procesů si necháme na jindy.",
        "goal": "Spusť na pozadí 'sleep 20 &' a najdi jeho PID příkazem pgrep; ulož ho do 'pid1.txt'.",
        "hint": "cd ~\nsleep 20 > /dev/null 2>&1 &\npgrep sleep > pid1.txt",
        "commands": [
            "sleep &",
            "pgrep"
        ],
        "checks": [
            {
                "label": "'pid1.txt' obsahuje nalezené PID",
                "test": "grep -qE \"^[0-9]+\" \"$HOME/pid1.txt\""
            }
        ]
    },
    {
        "id": 89,
        "set": 3,
        "tier": 2,
        "difficulty": "Sada 3 – 2. Fáze: Posádka",
        "cmd_name": "pgrep",
        "title": "Najdi proces na pozadí",
        "story": "Spusť dlouho běžící proces a najdi jeho PID – ukončování procesů si necháme na jindy.",
        "goal": "Spusť na pozadí 'sleep 25 &' a najdi jeho PID příkazem pgrep; ulož ho do 'pid2.txt'.",
        "hint": "cd ~\nsleep 25 > /dev/null 2>&1 &\npgrep sleep > pid2.txt",
        "commands": [
            "sleep &",
            "pgrep"
        ],
        "checks": [
            {
                "label": "'pid2.txt' obsahuje nalezené PID",
                "test": "grep -qE \"^[0-9]+\" \"$HOME/pid2.txt\""
            }
        ]
    },
    {
        "id": 90,
        "set": 3,
        "tier": 3,
        "difficulty": "Sada 3 – 3. Fáze: Mistr",
        "cmd_name": "pgrep",
        "title": "Najdi proces na pozadí",
        "story": "Spusť dlouho běžící proces a najdi jeho PID – ukončování procesů si necháme na jindy.",
        "goal": "Spusť na pozadí 'sleep 30 &' a najdi jeho PID příkazem pgrep; ulož ho do 'pid3.txt'.",
        "hint": "cd ~\nsleep 30 > /dev/null 2>&1 &\npgrep sleep > pid3.txt",
        "commands": [
            "sleep &",
            "pgrep"
        ],
        "checks": [
            {
                "label": "'pid3.txt' obsahuje nalezené PID",
                "test": "grep -qE \"^[0-9]+\" \"$HOME/pid3.txt\""
            }
        ]
    }
]

TASKS_BY_ID = {task["id"]: task for task in TASKS}
SET_SIZE = 30
TOTAL_SETS = 3

_OK = "LPD_OK"
_NO = "LPD_NO"


def public_tasks() -> List[dict]:
    """Verze úkolů pro prohlížeč – bez shellových testů."""
    return [
        {
            "id": t["id"],
            "set": t["set"],
            "tier": t["tier"],
            "difficulty": t["difficulty"],
            "title": t["title"],
            "story": t["story"],
            "goal": t["goal"],
            "hint": t["hint"],
            "commands": t["commands"],
            "checks": [c["label"] for c in t["checks"]],
        }
        for t in TASKS
    ]


def verify(user: auth.SandboxUser, task_id) -> dict:
    """Ověří úkol proti skutečnému souborovému systému / procesům v kontejneru."""
    task_id = int(task_id)
    task = TASKS_BY_ID.get(task_id)
    if task is None:
        raise engine.SandboxError("Takový úkol neznám.")

    lines = []
    for index, check in enumerate(task["checks"]):
        lines.append(
            f'if {check["test"]}; then echo "{_OK} {index}"; else echo "{_NO} {index}"; fi'
        )
    result = engine.run(user, "\n".join(lines))

    passed_indexes = {
        int(line.split()[1])
        for line in result.output.splitlines()
        if line.startswith(_OK) and len(line.split()) == 2
    }

    checks = [
        {"label": check["label"], "passed": index in passed_indexes}
        for index, check in enumerate(task["checks"])
    ]
    return {
        "task_id": task_id,
        "passed": all(c["passed"] for c in checks),
        "checks": checks,
    }
