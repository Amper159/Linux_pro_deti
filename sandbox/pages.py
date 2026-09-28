"""Samostatné výukové stránky (návody), které se mají dát najít ve vyhledávačích.

Každá stránka má vlastní adresu, titulek a popisek. Obsah stránek je v
sandbox/templates/articles/, sdílené rozvržení v articles/base.html.
Data, která se opakují (klávesy pro boot menu, srovnání distribucí, tabulka
příkazů, příklady v Pythonu), jsou tady - díky tomu jde jejich správnost
automaticky otestovat (viz tests v repozitáři / kontrola před nasazením).
"""
import json

from flask import Blueprint, render_template

SITE = "https://linuxhrou.cz"

bp = Blueprint("pages", __name__, template_folder="templates")

ARTICLES = [
    {
        "key": "instalace",
        "path": "/jak-nainstalovat-linux/",
        "template": "articles/instalace.html",
        "title": "Instalace Linuxu vedle Windows z USB – návod | Linuxhrou.cz",
        "h1": "Jak nainstalovat Linux vedle Windows z USB flashky",
        "crumb": "Instalace Linuxu",
        "description": "Krok za krokem: instalace Linuxu vedle Windows (dual boot) z USB. Příprava, Rufus, klávesy pro boot menu podle značky a řešení častých problémů.",
        "icon": "💿",
        "card_title": "Jak nainstalovat Linux vedle Windows",
        "card": "Krok za krokem od USB flashky po dual boot, včetně tabulky kláves pro boot menu.",
    },
    {
        "key": "distribuce",
        "path": "/ktery-linux-vybrat/",
        "template": "articles/distribuce.html",
        "title": "Který Linux vybrat? Distribuce pro začátečníky | Linuxhrou.cz",
        "h1": "Který Linux vybrat jako začátečník? Srovnání distribucí",
        "crumb": "Výběr distribuce",
        "description": "Který Linux zvolit jako první? Srovnání Linux Mint, Zorin OS, Ubuntu, Pop!_OS, Fedory a Manjara: pro koho se hodí a která je nejblíž Windows.",
        "icon": "🐧",
        "card_title": "Který Linux vybrat",
        "card": "Srovnání šesti distribucí pro začátečníky a rada, která je nejblíž Windows.",
    },
    {
        "key": "prikazy",
        "path": "/linux-prikazy/",
        "template": "articles/prikazy.html",
        "title": "Základní příkazy Linuxu – přehledný tahák | Linuxhrou.cz",
        "h1": "Základní příkazy Linuxu: přehledný tahák pro začátečníky",
        "crumb": "Příkazy Linuxu",
        "description": "Tahák nejdůležitějších příkazů Linuxu s příklady: ls, cd, cp, mv, rm, grep, find, chmod a další. Vysvětleno česky a vyzkoušitelné přímo v prohlížeči.",
        "icon": "⌨️",
        "card_title": "Základní příkazy Linuxu",
        "card": "Tahák více než třiceti příkazů s příklady, které si můžeš hned vyzkoušet v Pískovišti.",
    },
    {
        "key": "python",
        "path": "/python-zaklady/",
        "template": "articles/python_zaklady.html",
        "title": "Python pro začátečníky – základy s příklady | Linuxhrou.cz",
        "h1": "Python pro začátečníky: základy s příklady, které si můžeš hned vyzkoušet",
        "crumb": "Základy Pythonu",
        "description": "Základy Pythonu srozumitelně: proměnné, podmínky, smyčky, seznamy, funkce a časté chyby začátečníků. Každý příklad si můžeš vyzkoušet online.",
        "icon": "🐍",
        "card_title": "Python pro začátečníky",
        "card": "Proměnné, podmínky, smyčky a funkce s příklady a vysvětlením častých chyb.",
    },
]

# ---------------------------------------------------------------- instalace
# Stejné údaje jako v původní tabulce na hlavní stránce (ověřené dříve).
BOOT_KEYS = [
    ("Acer", "F12 / Esc", "F2 / Del"),
    ("Asus", "Esc / F8", "F2 / Del"),
    ("Dell", "F12", "F2"),
    ("HP", "Esc / F9", "F10"),
    ("Lenovo", "F12 (nebo tlačítko Novo)", "F1 / F2"),
    ("MSI", "F11", "Del"),
    ("Samsung", "Esc / F2", "F2"),
    ("Toshiba", "F12", "F2"),
]

# ---------------------------------------------------------------- distribuce
# Zdroj: DistroWatch Page Hit Ranking, posledních 6 měsíců, stav srpen 2026.
DISTROS = [
    {"name": "Linux Mint", "hits": 1790, "color": "#4ade80", "badge": "Nejčastější doporučení pro začátek",
     "base": "Ubuntu LTS", "desktop": "Cinnamon (také MATE a Xfce)",
     "text": "Nabídka Start, hodiny vpravo dole a panel s okny: ovládání je ze všech nejblíž Windows. "
             "Systém je konzervativní a stabilní a funguje dobře i na starších počítačích "
             "(existuje odlehčená edice Xfce).",
     "fit": "přechod z Windows, škola a běžná práce, starší počítače"},
    {"name": "Pop!_OS", "hits": 1206, "color": "#a78bfa", "badge": "",
     "base": "Ubuntu", "desktop": "vlastní prostředí od System76",
     "text": "Vyvíjí ji firma System76 na základě Ubuntu. Je oblíbená u hráčů a vývojářů, mimo jiné "
             "kvůli snadné podpoře grafických karet NVIDIA.",
     "fit": "hraní her, práce s grafikou, programování"},
    {"name": "Fedora", "hits": 1114, "color": "#fb7185", "badge": "",
     "base": "vlastní (sponzoruje Red Hat)", "desktop": "GNOME",
     "text": "Nové verze vycházejí zhruba jednou za půl roku a přinášejí nejnovější programy. "
             "Kvůli licencím v ní nejsou předinstalované multimediální kodeky, je potřeba je doplnit. "
             "Oblíbená mezi programátory.",
     "fit": "programování a zájem o nejnovější technologie"},
    {"name": "Zorin OS", "hits": 1112, "color": "#38bdf8", "badge": "",
     "base": "Ubuntu", "desktop": "upravené GNOME",
     "text": "Při prvním nastavení si můžeš vybrat rozložení podobné Windows. Existuje zdarma dostupná "
             "verze Core a placená verze Pro s přidanými funkcemi.",
     "fit": "co nejplynulejší přechod z Windows"},
    {"name": "Ubuntu", "hits": 914, "color": "#facc15", "badge": "",
     "base": "Debian", "desktop": "GNOME",
     "text": "Nejrozšířenější distribuce, takže k téměř čemukoliv najdeš návod. Verze LTS vycházejí jednou za "
             "dva roky a mají pět let standardní podpory. Vzhled se od Windows liší, ale zvykne se rychle.",
     "fit": "kdo chce nejvíc návodů a podpory na internetu"},
    {"name": "Manjaro", "hits": 837, "color": "#94a3b8", "badge": "",
     "base": "Arch Linux", "desktop": "Xfce, KDE Plasma nebo GNOME",
     "text": "Aktualizace přicházejí průběžně (rolling release). Instalace je pohodlná, ale běžný provoz "
             "vyžaduje víc péče a aktualizace mohou občas něco rozbít.",
     "fit": "pokročilejší uživatele, kteří chtějí mít vše po ruce"},
]

# ---------------------------------------------------------------- příkazy
# Každý příklad: (příkaz, vysvětlení) nebo (příkaz, vysvětlení, příkaz_pro_test).
# Test = spustit v dočasné složce se vzorovými soubory; "SKIP" = netestovat
# (síť, běh donekonečna apod.).
COMMAND_GROUPS = [
    {"id": "orientace", "title": "Kde jsem a co tu je",
     "intro": "První tři příkazy se používají pořád: kde stojíš, co je kolem a jak se přesunout jinam.",
     "items": [
        {"cmd": "pwd", "label": "kde právě jsem",
         "what": "Vypíše úplnou cestu ke složce, ve které se právě nacházíš. Hodí se, když se v terminálu ztratíš.",
         "examples": [("pwd", "vypíše např. /home/kadet")]},
        {"cmd": "ls", "label": "výpis souborů a složek",
         "what": "Ukáže, co je v aktuální složce. Bez parametrů vypíše jen názvy.",
         "examples": [("ls", "názvy souborů a složek"),
                      ("ls -l", "podrobný výpis: práva, vlastník, velikost, datum"),
                      ("ls -a", "včetně skrytých souborů (jejich název začíná tečkou)"),
                      ("ls -la", "podrobně a se skrytými soubory")]},
        {"cmd": "cd", "label": "přechod do jiné složky",
         "what": "Změní aktuální složku. Zkratka ~ znamená tvoji domovskou složku.",
         "examples": [("cd slozka", "vstoupí do podsložky"),
                      ("cd ..", "o úroveň výš"),
                      ("cd ~", "do domovské složky (stejně funguje samotné cd)"),
                      ("cd -", "zpět do předchozí složky", "cd slozka && cd -")]},
     ]},
    {"id": "soubory", "title": "Práce se soubory a složkami",
     "intro": "Vytváření, kopírování, přesouvání a mazání. Pozor na mazání: v terminálu neexistuje koš.",
     "items": [
        {"cmd": "mkdir", "label": "vytvoření složky",
         "what": "Vytvoří novou složku.",
         "examples": [("mkdir projekty", "vytvoří složku projekty"),
                      ("mkdir -p a/b/c", "vytvoří celou cestu, i s chybějícími nadřazenými složkami")]},
        {"cmd": "touch", "label": "vytvoření prázdného souboru",
         "what": "Když soubor neexistuje, vytvoří ho prázdný. Když existuje, jen mu aktualizuje čas poslední změny.",
         "examples": [("touch novy.txt", "vytvoří prázdný soubor novy.txt")]},
        {"cmd": "cp", "label": "kopírování",
         "what": "Zkopíruje soubor nebo složku.",
         "examples": [("cp soubor.txt kopie.txt", "zkopíruje soubor"),
                      ("cp -r slozka zaloha", "zkopíruje celou složku i s obsahem (-r = rekurzivně)")]},
        {"cmd": "mv", "label": "přesun a přejmenování",
         "what": "Přesune soubor nebo složku. V Linuxu je přejmenování totéž co přesun na nový název.",
         "examples": [("mv soubor.txt slozka/", "přesune soubor do složky"),
                      ("mv soubor.txt novy_nazev.txt", "přejmenuje soubor")]},
        {"cmd": "rm", "label": "smazání souboru",
         "what": "Smaže soubor. Smazané soubory se neposílají do koše, zmizí natrvalo.",
         "warn": "Před stisknutím Enteru si přečti, co mažeš. Zvlášť opatrně s parametrem -r, který maže složky "
                 "i s celým obsahem. Kombinaci rm -rf nikdy nespouštěj, pokud přesně nevíš, co dělá.",
         "examples": [("rm soubor.txt", "smaže soubor"),
                      ("rm -r slozka", "smaže složku i s celým obsahem")]},
        {"cmd": "rmdir", "label": "smazání prázdné složky",
         "what": "Funguje jen na prázdné složky, proto je bezpečnější než rm -r.",
         "examples": [("rmdir prazdna", "smaže prázdnou složku")]},
     ]},
    {"id": "cteni", "title": "Čtení a zápis textu",
     "intro": "Jak se podívat do souboru, aniž bys ho otevíral v editoru, a jak do něj něco rychle zapsat.",
     "items": [
        {"cmd": "cat", "label": "vypsání obsahu souboru",
         "what": "Vypíše celý soubor na obrazovku.",
         "examples": [("cat soubor.txt", "vypíše obsah souboru")]},
        {"cmd": "head", "label": "začátek souboru",
         "what": "Vypíše začátek souboru. Bez parametrů prvních deset řádků.",
         "examples": [("head -n 3 poznamky.txt", "prvních 3 řádky")]},
        {"cmd": "tail", "label": "konec souboru",
         "what": "Vypíše konec souboru. Hodí se na logy, kde nejnovější záznamy přibývají dole.",
         "examples": [("tail -n 3 poznamky.txt", "posledních 3 řádky"),
                      ("tail -f log.txt", "průběžně sleduje nově přibývající řádky (ukončíš klávesami Ctrl+C)", "SKIP")]},
        {"cmd": "wc", "label": "počítání řádků a slov",
         "what": "Spočítá řádky, slova a znaky. S parametrem -l vypíše jen počet řádků.",
         "examples": [("wc -l poznamky.txt", "počet řádků v souboru")]},
        {"cmd": "echo", "label": "vypsání textu",
         "what": "Vypíše text. Ve spojení s přesměrováním se hodí k rychlému zápisu do souboru.",
         "examples": [("echo Ahoj", "vypíše Ahoj"),
                      ('echo "Ahoj" > soubor.txt', "zapíše text do souboru (starý obsah přepíše)"),
                      ('echo "další řádek" >> soubor.txt', "přidá řádek na konec souboru")]},
     ]},
    {"id": "hledani", "title": "Hledání",
     "intro": "Najít text uvnitř souborů a najít soubory podle názvu.",
     "items": [
        {"cmd": "grep", "label": "hledání textu v souborech",
         "what": "Vypíše řádky, které obsahují hledaný text.",
         "examples": [("grep chyba log.txt", "řádky obsahující slovo chyba"),
                      ("grep -i chyba log.txt", "hledá bez ohledu na velká a malá písmena"),
                      ('grep -r "Ahoj" .', "hledá ve všech souborech ve složce i v podsložkách")]},
        {"cmd": "find", "label": "hledání souborů podle názvu",
         "what": "Prohledá složku a všechny její podsložky.",
         "examples": [('find . -name "*.txt"', "najde všechny soubory končící na .txt od aktuální složky níž")]},
     ]},
    {"id": "komprese", "title": "Balení a komprese",
     "intro": "Jak zabalit více souborů do jednoho archivu a zmenšit je.",
     "items": [
        {"cmd": "tar", "label": "balení a rozbalování archivů",
         "what": "Spojí více souborů do jednoho archivu (přípona .tar). S parametrem z je navíc zkomprimuje (.tar.gz).",
         "examples": [("tar -czf archiv2.tar.gz slozka", "zabalí složku (c = vytvořit, z = komprimovat, f = název souboru)"),
                      ("tar -xzf archiv.tar.gz", "rozbalí archiv (x = rozbalit)")]},
        {"cmd": "gzip", "label": "komprese souboru",
         "what": "Zkomprimuje jeden soubor. Původní soubor se nahradí komprimovaným.",
         "examples": [("gzip soubor.txt", "vytvoří soubor.txt.gz a původní soubor zmizí"),
                      ("gunzip stary.txt.gz", "rozbalí komprimovaný soubor zpět")]},
     ]},
    {"id": "system", "title": "Systém a procesy",
     "intro": "Jak zjistit, co se v počítači děje: místo na disku, paměť, běžící programy.",
     "items": [
        {"cmd": "df", "label": "volné místo na discích",
         "what": "Ukáže využití disků. Parametr -h přepíše velikosti do čitelných jednotek (MB, GB).",
         "examples": [("df -h", "místo na discích v čitelných jednotkách")]},
        {"cmd": "free", "label": "využití paměti",
         "what": "Ukáže, kolik operační paměti (RAM) je obsazené a kolik volné.",
         "examples": [("free -h", "paměť v čitelných jednotkách")]},
        {"cmd": "ps", "label": "běžící procesy",
         "what": "Vypíše procesy (běžící programy).",
         "examples": [("ps", "procesy spuštěné z tvého terminálu"),
                      ("ps aux", "všechny procesy v systému")]},
        {"cmd": "pgrep", "label": "číslo procesu podle názvu",
         "what": "Najde proces podle jména a vypíše jeho číslo (PID).",
         "examples": [("pgrep firefox", "vypíše čísla procesů, které se jmenují firefox", "sleep 2 & pgrep sleep")]},
        {"cmd": "date", "label": "datum a čas",
         "what": "Vypíše aktuální datum a čas.",
         "examples": [("date", "aktuální datum a čas")]},
        {"cmd": "uname", "label": "informace o systému",
         "what": "Vypíše základní údaje o systému a jádru.",
         "examples": [("uname -a", "všechny informace: jádro, název počítače, architektura"),
                      ("uname -n", "jen název počítače")]},
        {"cmd": "env", "label": "proměnné prostředí",
         "what": "Vypíše proměnné prostředí, například HOME (domovská složka) nebo PATH (kde se hledají programy).",
         "examples": [("env", "všechny proměnné prostředí")]},
        {"cmd": "alias", "label": "vlastní zkratky",
         "what": "Vytvoří zkratku pro delší příkaz. Platí jen v aktuálním terminálu, dokud ji nezapíšeš do "
                 "konfiguračního souboru ~/.bashrc.",
         "examples": [("alias ll='ls -la'", "po zadání stačí psát ll")]},
     ]},
    {"id": "sit", "title": "Síť",
     "intro": "Základní zjištění, jestli je server dostupný.",
     "items": [
        {"cmd": "ping", "label": "test spojení",
         "what": "Pošle dotazy na zadanou adresu a změří, jestli a jak rychle odpovídá. Na Linuxu běží donekonečna, "
                 "dokud ho nezastavíš klávesami Ctrl+C, proto se hodí parametr -c s počtem dotazů.",
         "examples": [("ping -c 4 example.com", "pošle čtyři dotazy a skončí", "SKIP")]},
     ]},
    {"id": "skripty", "title": "Skripty a práva",
     "intro": "Aby šel soubor spustit jako program, musí k tomu mít právo.",
     "items": [
        {"cmd": "chmod", "label": "změna práv k souboru",
         "what": "Mění, kdo smí soubor číst, zapisovat do něj nebo ho spouštět. Nejčastěji se používá k přidání "
                 "práva ke spuštění skriptu.",
         "examples": [("chmod +x skript.sh", "přidá právo ke spuštění"),
                      ("./skript.sh", "spustí skript ve složce, kde stojíš (tečka a lomítko znamenají „tady“)",
                       "chmod +x skript.sh && ./skript.sh")]},
     ]},
    {"id": "kombinace", "title": "Kombinování příkazů",
     "intro": "Síla terminálu je v tom, že se jednoduché příkazy dají spojovat.",
     "items": [
        {"cmd": "|", "slug": "roura", "label": "roura (pipe)",
         "what": "Výstup jednoho příkazu pošle jako vstup dalšímu.",
         "examples": [("ls | wc -l", "spočítá soubory ve složce: výpis z ls se předá příkazu wc")]},
        {"cmd": ">", "slug": "presmerovani", "label": "přesměrování do souboru",
         "what": "Uloží výstup příkazu do souboru. Jedno > starý obsah přepíše, dvě >> přidávají na konec.",
         "examples": [("ls > seznam.txt", "uloží výpis složky do souboru seznam.txt")]},
        {"cmd": "*", "slug": "zastupny-znak", "label": "zástupný znak",
         "what": "Hvězdička nahradí libovolný text v názvu souboru.",
         "examples": [("ls *.txt", "vypíše všechny soubory končící na .txt")]},
     ]},
]

# ---------------------------------------------------------------- Python
# Každý příklad je otestovaný skutečným spuštěním (viz kontrola před nasazením).
# "out" = očekávaný výstup, "error" = očekávaná chyba ve tvaru Typ: zpráva.
PY_EXAMPLES = {
    "print": {"code": 'print("Ahoj, světe!")', "out": "Ahoj, světe!"},
    "promenne": {"code": 'jmeno = "Ema"\nvek = 12\nprint(jmeno)\nprint(vek)', "out": "Ema\n12"},
    "typy": {"code": 'print(type("text"))\nprint(type(12))\nprint(type(3.14))\nprint(type(True))',
             "out": "<class 'str'>\n<class 'int'>\n<class 'float'>\n<class 'bool'>"},
    "pocitani": {"code": "print(7 + 3)\nprint(7 - 3)\nprint(7 * 3)\nprint(7 / 2)\nprint(7 // 2)\nprint(7 % 2)\nprint(2 ** 10)",
                 "out": "10\n4\n21\n3.5\n3\n1\n1024"},
    "fstring": {"code": 'jmeno = "Ema"\nvek = 12\nprint(f"{jmeno} je {vek} let.")', "out": "Ema je 12 let."},
    "input": {"code": 'jmeno = input("Jak se jmenuješ? ")\nprint("Ahoj,", jmeno)', "stdin": "Ema",
              "shown": "Jak se jmenuješ? Ema\nAhoj, Ema", "out_contains": "Ahoj, Ema"},
    "podminky": {"code": 'vek = 15\nif vek >= 18:\n    print("Jsi dospělý.")\nelif vek >= 13:\n    print("Jsi teenager.")\nelse:\n    print("Jsi dítě.")',
                 "out": "Jsi teenager."},
    "logika": {"code": 'teplota = 22\nslunecno = True\nif teplota > 20 and slunecno:\n    print("Jdeme ven!")',
               "out": "Jdeme ven!"},
    "for": {"code": 'for i in range(1, 4):\n    print("Kolo", i)', "out": "Kolo 1\nKolo 2\nKolo 3"},
    "while": {"code": 'zivoty = 3\nwhile zivoty > 0:\n    print("Životů:", zivoty)\n    zivoty -= 1\nprint("Konec hry")',
              "out": "Životů: 3\nŽivotů: 2\nŽivotů: 1\nKonec hry"},
    "seznam": {"code": 'zvirata = ["pes", "kočka", "papoušek"]\nzvirata.append("křeček")\nprint(zvirata[0])\nprint(len(zvirata))\nfor z in zvirata:\n    print(z)',
               "out": "pes\n4\npes\nkočka\npapoušek\nkřeček"},
    "slovnik": {"code": 'hrdina = {"jmeno": "Iskra", "zivoty": 20}\nprint(hrdina["jmeno"])\nhrdina["zivoty"] = hrdina["zivoty"] - 5\nprint(hrdina["zivoty"])',
                "out": "Iskra\n15"},
    "funkce": {"code": 'def pozdrav(jmeno):\n    return f"Ahoj, {jmeno}!"\n\nprint(pozdrav("Ema"))\nprint(pozdrav("Tomáš"))',
               "out": "Ahoj, Ema!\nAhoj, Tomáš!"},
    "return": {"code": "def dvojnasobek(x):\n    return x * 2\n\nvysledek = dvojnasobek(21)\nprint(vysledek)", "out": "42"},
    "err_syntax": {"code": 'if 5 > 3\n    print("ano")', "error": "SyntaxError: expected ':'"},
    "err_indent": {"code": 'if 5 > 3:\nprint("ano")',
                   "error": "IndentationError: expected an indented block after 'if' statement on line 1"},
    "err_name": {"code": 'jmeno = "Ema"\nprint(jmneo)', "error": "NameError: name 'jmneo' is not defined"},
    "err_type": {"code": 'vek = 12\nprint("Je mi " + vek)', "error": 'TypeError: can only concatenate str (not "int") to str'},
    "err_zero": {"code": "print(10 / 0)", "error": "ZeroDivisionError: division by zero"},
}


def _jsonld(a):
    url = SITE + a["path"]
    org = {"@type": "Organization", "name": "Linuxhrou.cz", "url": SITE + "/"}
    return json.dumps({
        "@context": "https://schema.org",
        "@graph": [
            {"@type": "Article", "headline": a["h1"], "description": a["description"],
             "inLanguage": "cs", "mainEntityOfPage": url, "image": SITE + "/og-image.png",
             "author": org, "publisher": org},
            {"@type": "BreadcrumbList", "itemListElement": [
                {"@type": "ListItem", "position": 1, "name": "Linuxhrou.cz", "item": SITE + "/"},
                {"@type": "ListItem", "position": 2, "name": a["crumb"], "item": url},
            ]},
        ],
    }, ensure_ascii=False)


def _extra_context(key):
    if key == "instalace":
        return {"boot_keys": BOOT_KEYS}
    if key == "distribuce":
        return {"distros": DISTROS,
                "chart": {"labels": [d["name"] for d in DISTROS],
                          "data": [d["hits"] for d in DISTROS],
                          "colors": [d["color"] for d in DISTROS]}}
    if key == "prikazy":
        return {"groups": COMMAND_GROUPS}
    if key == "python":
        return {"ex": PY_EXAMPLES}
    return {}


def _make_view(article):
    def view():
        return render_template(
            article["template"], page=article, jsonld=_jsonld(article),
            articles=ARTICLES, **_extra_context(article["key"]),
        )
    view.__name__ = f"view_{article['key']}"
    return view


for _a in ARTICLES:
    bp.add_url_rule(_a["path"], endpoint=_a["key"], view_func=_make_view(_a))
