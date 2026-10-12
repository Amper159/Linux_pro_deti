"""Úkoly SQL Labu: detektivní případ 'Zmizelý krystal' na stanici TUX-1.

Pyt (palubní počítač) po zkratu zapomněl, co se v noci stalo, ale archiv
(databáze) přežil. Kadet-detektiv z něj dotazy SELECT vytáhne, kdo vzal hlavní
energetický krystal. Každý splněný dotaz posune příběh o krok dál.

Pole úkolu:
  story    - děj (hlas Pyta), co se děje, než se dítě pustí do dotazu (max 170 znaků)
  tip      - výklad učiva (max 200 znaků)
  goal     - přesné zadání dotazu, musí stačit i bez nápovědy
  hint     - referenční řešení; zároveň slouží ke kontrole výsledku (viz sql_engine.check_result)
  victory  - reakce Pyta po splnění (max 110 znaků)
  ordered  - True, když záleží na pořadí řádků
  must     - [(regex, rada)] - klíčová slova, která dotaz musí obsahovat
"""
import re

SQL_TASKS = [
    # ------------------------------------------------------------ kapitola 1
    {
        "id": 1, "set": 1,
        "title": "Co je v archivu?",
        "tip": "SELECT říká, co chceš vidět, a hvězdička * znamená všechno. FROM říká, z které tabulky.",
        "story": "Hlavní krystal zmizel z reaktoru a já si nic nepamatuju. Jen archiv přežil. Začni tím, že mi ukážeš, kdo na stanici je.",
        "victory": "Dvanáct lidí na stanici. Jeden z nich ví, kam zmizel krystal.",
        "goal": "Vypiš všechno z tabulky posadka.",
        "starter": "SELECT * FROM posadka",
        "hint": "SELECT * FROM posadka",
        "must": [(r"\bfrom\s+posadka\b", "Čti z tabulky posadka: FROM posadka.")],
    },
    {
        "id": 2, "set": 1,
        "title": "Jen jména",
        "tip": "Místo hvězdičky můžeš napsat název sloupce. Pak se vypíše jen on.",
        "story": "Tabulka je plná čísel a nepřehledná. Pro začátek stačí jména, ať vím, koho se budeme ptát.",
        "victory": "Seznam jmen je čistý a přehledný. Jdeme dál.",
        "goal": "Vypiš jen sloupec jmeno z tabulky posadka.",
        "starter": "SELECT  FROM posadka",
        "hint": "SELECT jmeno FROM posadka",
    },
    {
        "id": 3, "set": 1,
        "title": "Jméno a role",
        "tip": "Víc sloupců odděl čárkou. Sloupce se vypíšou přesně v tom pořadí, v jakém je napíšeš.",
        "story": "Jména samotná nestačí. Potřebuju vědět, kdo co na stanici dělá, jestli je to technik, kuchař nebo vědec.",
        "victory": "Teď vím, kdo je kdo. Technici a vědci mě zajímají nejvíc.",
        "goal": "Vypiš sloupce jmeno a role (v tomhle pořadí) z tabulky posadka.",
        "starter": "SELECT  FROM posadka",
        "hint": "SELECT jmeno, role FROM posadka",
    },
    {
        "id": 4, "set": 1,
        "title": "Mapa stanice",
        "tip": "LIMIT na konci dotazu omezí počet řádků. LIMIT 3 vypíše jen první tři.",
        "story": "Taky potřebuju znát místnosti. Je jich ale hodně, tak si zatím ukaž jen první tři.",
        "victory": "Můstek, Reaktorová hala a Laboratoř. Reaktor je cílem celého případu.",
        "goal": "Vypiš sloupec nazev z tabulky mistnosti, ale jen první 3 řádky (použij LIMIT 3).",
        "starter": "SELECT  FROM mistnosti",
        "hint": "SELECT nazev FROM mistnosti LIMIT 3",
        "must": [(r"\blimit\s+3\b", "Počet řádků omezíš na konci dotazu: LIMIT 3.")],
    },
    # ------------------------------------------------------------ kapitola 2
    {
        "id": 5, "set": 2,
        "title": "Jen energetici",
        "tip": "WHERE filtruje řádky podle podmínky. Text se píše do apostrofů: oddeleni = 'energetika'.",
        "story": "Krystal je zdroj energie, takže první výslech patří energetikům. Z celé posádky potřebuju jen je.",
        "victory": "Čtyři energetici. Znají reaktor nejlíp, takže mají nejblíž k činu.",
        "goal": "Vypiš všechno z tabulky posadka, kde je oddeleni rovno 'energetika'.",
        "starter": "SELECT * FROM posadka WHERE ",
        "hint": "SELECT * FROM posadka WHERE oddeleni = 'energetika'",
        "must": [(r"\bwhere\b", "Na filtrování řádků se používá WHERE.")],
    },
    {
        "id": 6, "set": 2,
        "title": "Zkušení lidé",
        "tip": "V podmínce jde porovnávat i čísla: >, <, >= a <=. Čísla se píšou bez apostrofů.",
        "story": "Vypnout krystal bez poplachu umí jen zkušený člověk. Hledám ty, kdo na stanici pracují přes deset let.",
        "victory": "Šest zkušených lidí. Seznam podezřelých se pomalu zkracuje.",
        "goal": "Vypiš jméno (sloupec jmeno) všech lidí z tabulky posadka, kteří mají zkusenosti větší než 10.",
        "starter": "SELECT jmeno FROM posadka WHERE ",
        "hint": "SELECT jmeno FROM posadka WHERE zkusenosti > 10",
        "must": [(r"\bwhere\b", "Na filtrování řádků se používá WHERE.")],
    },
    {
        "id": 7, "set": 2,
        "title": "Zamčené místnosti",
        "tip": "Sloupec zamceno obsahuje 1 (zamčeno) nebo 0 (odemčeno). Podmínka zamceno = 1 najde zamčené.",
        "story": "Reaktorová hala byla zamčená, a přesto se krystal ztratil. Které místnosti mají zámek?",
        "victory": "Reaktor je zamčený, takže dveře si pamatují každého, kdo vešel.",
        "goal": "Vypiš sloupec nazev z tabulky mistnosti, kde je zamceno rovno 1.",
        "starter": "SELECT nazev FROM mistnosti WHERE ",
        "hint": "SELECT nazev FROM mistnosti WHERE zamceno = 1",
        "must": [(r"\bwhere\b", "Na filtrování řádků se používá WHERE.")],
    },
    {
        "id": 8, "set": 2,
        "title": "Technici z energetiky",
        "tip": "AND spojí dvě podmínky: řádek musí splnit obě. OR stačí, když splní aspoň jednu.",
        "story": "Hlavní krystal smí vyndat jen technik z energetiky. Hledám lidi, kteří jsou obojí.",
        "victory": "Bruno a Radek. Oba měli k reaktoru oprávnění.",
        "goal": "Vypiš jméno z tabulky posadka těch, kdo mají oddeleni 'energetika' A ZÁROVEŇ roli 'technik'.",
        "starter": "SELECT jmeno FROM posadka WHERE  AND ",
        "hint": "SELECT jmeno FROM posadka WHERE oddeleni = 'energetika' AND role = 'technik'",
        "must": [(r"\band\b", "Obě podmínky spoj slovem AND.")],
    },
    # ------------------------------------------------------------ kapitola 3
    {
        "id": 9, "set": 3,
        "title": "Kdo otvíral dveře reaktoru",
        "tip": "Tabulka vstupy zapisuje každé otevření dveří: kdo (osoba_id), kam (mistnost_id) a v kolik hodin (cas).",
        "story": "Dveře si pamatují každého, kdo vešel. Reaktorová hala má v tabulce místností číslo 2. Ukaž mi její záznamy.",
        "victory": "Šest vstupů do reaktoru za jednu noc. V čísle osoby je schovaná odpověď.",
        "goal": "Vypiš všechno z tabulky vstupy, kde je mistnost_id rovno 2.",
        "starter": "SELECT * FROM vstupy WHERE ",
        "hint": "SELECT * FROM vstupy WHERE mistnost_id = 2",
        "must": [(r"\bwhere\b", "Na filtrování řádků se používá WHERE.")],
    },
    {
        "id": 10, "set": 3,
        "title": "Seřaď podle času",
        "tip": "ORDER BY seřadí výsledek. Standardně od nejmenšího, s DESC od největšího.",
        "story": "Záznamy jsou pomíchané. Aby mělo vyšetřování smysl, musím je vidět tak, jak se opravdu stály, od nejstaršího.",
        "victory": "Teď vidím noc po hodinách. Nejzajímavější je čas těsně před výpadkem energie.",
        "goal": "Vypiš všechno z tabulky vstupy, kde je mistnost_id rovno 2, seřazené podle sloupce cas (ORDER BY cas).",
        "starter": "SELECT * FROM vstupy WHERE mistnost_id = 2 ",
        "hint": "SELECT * FROM vstupy WHERE mistnost_id = 2 ORDER BY cas",
        "ordered": True,
        "must": [(r"\border\s+by\b", "Řadí se příkazem ORDER BY a názvem sloupce.")],
    },
    {
        "id": 11, "set": 3,
        "title": "Podezřelá hodina",
        "tip": "BETWEEN a AND vybere hodnoty v rozsahu včetně krajů: cas BETWEEN '22:30' AND '22:50'.",
        "story": "Výkon reaktoru spadl na nulu krátce před 23:00. Zajímají mě jen vstupy do haly mezi 22:30 a 22:50.",
        "victory": "V tom okně vešla dovnitř jediná osoba. Číslo 8.",
        "goal": "Vypiš všechno z tabulky vstupy, kde je mistnost_id rovno 2 a cas je BETWEEN '22:30' AND '22:50'.",
        "starter": "SELECT * FROM vstupy WHERE mistnost_id = 2 AND ",
        "hint": "SELECT * FROM vstupy WHERE mistnost_id = 2 AND cas BETWEEN '22:30' AND '22:50'",
        "must": [(r"\bbetween\b", "Rozsah se zapisuje pomocí BETWEEN ... AND ...")],
    },
    {
        "id": 12, "set": 3,
        "title": "Hledání ve zprávách",
        "tip": "LIKE hledá text podle vzoru. Procento % znamená libovolný text: text LIKE '%reaktor%' najde slovo uprostřed.",
        "story": "Lidé o stanici psali zprávy. Chci všechny, ve kterých se mluví o reaktoru.",
        "victory": "Tři zprávy o reaktoru. Poslední z nich objevila prázdný stojan.",
        "goal": "Vypiš všechno z tabulky zpravy, kde sloupec text obsahuje slovo reaktor (text LIKE '%reaktor%').",
        "starter": "SELECT * FROM zpravy WHERE text ",
        "hint": "SELECT * FROM zpravy WHERE text LIKE '%reaktor%'",
        "must": [(r"\blike\b", "Hledání podle vzoru dělá LIKE a procenta kolem slova.")],
    },
    # ------------------------------------------------------------ kapitola 4
    {
        "id": 13, "set": 4,
        "title": "Kolik nás je",
        "tip": "COUNT(*) spočítá řádky. Místo seznamu dostaneš jedno číslo.",
        "story": "Detektiv nejdřív počítá. Kolik lidí je celkem na stanici? Nechci všechny vypisovat, stačí číslo.",
        "victory": "Dvanáct podezřelých, ale většina z nich má alibi.",
        "goal": "Spočítej, kolik řádků má tabulka posadka (použij COUNT(*)).",
        "starter": "SELECT  FROM posadka",
        "hint": "SELECT COUNT(*) FROM posadka",
        "must": [(r"\bcount\s*\(", "Počítá se funkcí COUNT(*).")],
    },
    {
        "id": 14, "set": 4,
        "title": "Kolikrát se otevřely dveře",
        "tip": "COUNT(*) jde spojit s WHERE. Spočítají se jen řádky, které podmínku splní.",
        "story": "Kolikrát se ta noc otevřely dveře reaktoru? Víc než obvykle by znamenalo čilý ruch.",
        "victory": "Šestkrát. Na zamčenou halu docela hodně.",
        "goal": "Spočítej řádky v tabulce vstupy, kde je mistnost_id rovno 2.",
        "starter": "SELECT COUNT(*) FROM vstupy WHERE ",
        "hint": "SELECT COUNT(*) FROM vstupy WHERE mistnost_id = 2",
        "must": [(r"\bcount\s*\(", "Počítá se funkcí COUNT(*)."), (r"\bwhere\b", "Přidej WHERE s podmínkou.")],
    },
    {
        "id": 15, "set": 4,
        "title": "Každý jen jednou",
        "tip": "DISTINCT odstraní opakující se hodnoty. Když někdo vešel dvakrát, objeví se ve výsledku jednou.",
        "story": "Někdo mohl vejít víckrát. Chci vědět, kolik různých lidí se v reaktoru vystřídalo, a každého jen jednou.",
        "victory": "Pět různých osob. Jedna z nich vešla dvakrát.",
        "goal": "Vypiš sloupec osoba_id z tabulky vstupy, kde je mistnost_id rovno 2, ale každou hodnotu jen jednou (DISTINCT).",
        "starter": "SELECT  osoba_id FROM vstupy WHERE mistnost_id = 2",
        "hint": "SELECT DISTINCT osoba_id FROM vstupy WHERE mistnost_id = 2",
        "must": [(r"\bdistinct\b", "Duplicity zahodíš slovem DISTINCT hned za SELECT.")],
    },
    {
        "id": 16, "set": 4,
        "title": "Kolik máme energie",
        "tip": "SUM sečte čísla ve sloupci. Podobně AVG udělá průměr, MIN najde nejmenší a MAX největší hodnotu.",
        "story": "Bez krystalu běžíme na zálohu. Sečti množství všeho, co je v tabulce zasoby v kategorii 'energie'.",
        "victory": "Energie je 21 jednotek. Na stanici dlouho nevydrží, pospíchej.",
        "goal": "Sečti sloupec mnozstvi v tabulce zasoby u řádků, kde je kategorie rovna 'energie' (SUM).",
        "starter": "SELECT  FROM zasoby WHERE ",
        "hint": "SELECT SUM(mnozstvi) FROM zasoby WHERE kategorie = 'energie'",
        "must": [(r"\bsum\s*\(", "Sčítá se funkcí SUM(sloupec).")],
    },
    # ------------------------------------------------------------ kapitola 5
    {
        "id": 17, "set": 5,
        "title": "Lidé podle oddělení",
        "tip": "GROUP BY slepí řádky se stejnou hodnotou do skupin. K tomu se hodí COUNT(*), kterým skupiny spočítáš.",
        "story": "Chci přehled po odděleních. Který tým je největší a který nejmenší? Potřebuju název oddělení a počet lidí.",
        "victory": "Energetika vede se čtyřmi lidmi. Nic překvapivého.",
        "goal": "Vypiš oddeleni a počet lidí v každém (COUNT(*)) z tabulky posadka, seskupeno podle oddeleni (GROUP BY).",
        "starter": "SELECT oddeleni,  FROM posadka ",
        "hint": "SELECT oddeleni, COUNT(*) FROM posadka GROUP BY oddeleni",
        "must": [(r"\bgroup\s+by\b", "Do skupin se seskupuje přes GROUP BY.")],
    },
    {
        "id": 18, "set": 5,
        "title": "Kdo chodí nejvíc",
        "tip": "Řazení DESC jde od největšího. LIMIT pak nechá jen první řádky, takže dostaneš žebříček.",
        "story": "Nejpodezřelejší je, kdo se té noci pohyboval nejvíc. Chci tři lidi s nejvíc záznamy ve vstupech.",
        "victory": "Osoba číslo 8 vede s náskokem. Zajímavé.",
        "goal": "Z tabulky vstupy vypiš osoba_id a COUNT(*) seskupené podle osoba_id, seřaď od největšího počtu (ORDER BY COUNT(*) DESC) a nech jen 3 řádky (LIMIT 3).",
        "starter": "SELECT osoba_id, COUNT(*) FROM vstupy GROUP BY osoba_id ",
        "hint": "SELECT osoba_id, COUNT(*) FROM vstupy GROUP BY osoba_id ORDER BY COUNT(*) DESC LIMIT 3",
        "ordered": True,
        "must": [(r"\bdesc\b", "Od největšího se řadí pomocí DESC."), (r"\blimit\s+3\b", "Nech jen tři řádky: LIMIT 3.")],
    },
    {
        "id": 19, "set": 5,
        "title": "Kdo se vracel",
        "tip": "WHERE filtruje řádky před seskupením, HAVING filtruje už hotové skupiny, třeba podle COUNT(*).",
        "story": "Kdo do reaktoru chodil opakovaně? Vyber z reaktoru jen ty, kdo tam byli víc než jednou.",
        "victory": "Bruno měl v reaktoru obchůzku dvakrát. Je to jeho práce a v kritický čas tam nebyl.",
        "goal": "Z tabulky vstupy vezmi řádky s mistnost_id rovno 2, seskup podle osoba_id a nech jen skupiny, kde je COUNT(*) větší než 1 (HAVING). Vypiš osoba_id.",
        "starter": "SELECT osoba_id FROM vstupy WHERE mistnost_id = 2 GROUP BY osoba_id ",
        "hint": "SELECT osoba_id FROM vstupy WHERE mistnost_id = 2 GROUP BY osoba_id HAVING COUNT(*) > 1",
        "must": [(r"\bhaving\b", "Filtr na hotové skupiny se píše za GROUP BY slovem HAVING.")],
    },
    # ------------------------------------------------------------ kapitola 6
    {
        "id": 20, "set": 6,
        "title": "Jména místo čísel",
        "tip": "JOIN spojí dvě tabulky podle společné hodnoty. ON říká, které sloupce se musí shodovat.",
        "story": "Čísla osob jsou k ničemu, chci jména. Jména jsou v posadka, vstupy mají jen číslo. Spoj tabulky přes osoba_id a id.",
        "victory": "Teď vidím jména a časy vedle sebe, tohle je opravdová detektivka.",
        "goal": "Vypiš posadka.jmeno a vstupy.cas z tabulky vstupy spojené s posadka (JOIN posadka ON vstupy.osoba_id = posadka.id), jen pro vstupy.mistnost_id rovno 2.",
        "starter": "SELECT posadka.jmeno, vstupy.cas FROM vstupy JOIN posadka ON  WHERE ",
        "hint": "SELECT posadka.jmeno, vstupy.cas FROM vstupy JOIN posadka ON vstupy.osoba_id = posadka.id WHERE vstupy.mistnost_id = 2",
        "must": [(r"\bjoin\b", "Spojení tabulek se dělá slovem JOIN.")],
    },
    {
        "id": 21, "set": 6,
        "title": "Kdo tam byl před výpadkem",
        "tip": "JOIN a WHERE se dají kombinovat. Nejdřív se tabulky spojí, potom se vyfiltrují řádky.",
        "story": "Teď to zpřesníme. Chci jen jméno člověka, který vešel do reaktoru v okně 22:30 až 22:50, těsně před výpadkem.",
        "victory": "Viktor, vědec z laboratoře. Nikdo jiný v tom okně do reaktoru nevešel.",
        "goal": "Vypiš posadka.jmeno všech, kdo mají vstup do mistnost_id 2 s casem BETWEEN '22:30' AND '22:50' (spoj vstupy a posadka přes JOIN).",
        "starter": "SELECT posadka.jmeno FROM vstupy JOIN posadka ON vstupy.osoba_id = posadka.id WHERE ",
        "hint": "SELECT posadka.jmeno FROM vstupy JOIN posadka ON vstupy.osoba_id = posadka.id WHERE vstupy.mistnost_id = 2 AND vstupy.cas BETWEEN '22:30' AND '22:50'",
        "must": [(r"\bjoin\b", "Spojení tabulek se dělá slovem JOIN."), (r"\bbetween\b", "Čas omez přes BETWEEN.")],
    },
    {
        "id": 22, "set": 6,
        "title": "Viktorovy zprávy",
        "tip": "Spojovat jde i jiné tabulky. Tady zpravy a posadka, aby se místo čísla osoby objevilo jméno autora.",
        "story": "Viktor mohl něco napsat. Přečti mi všechny jeho zprávy. Jejich text je ve zpravy, jméno v posadka.",
        "victory": "Přiznání mezi řádky: potřeboval energii pro pokus a vzal ji z reaktoru.",
        "goal": "Vypiš zpravy.text všech zpráv, jejichž autor má v posadka jmeno rovno 'Viktor' (spoj zpravy s posadka přes zpravy.osoba_id = posadka.id).",
        "starter": "SELECT zpravy.text FROM zpravy JOIN posadka ON  WHERE ",
        "hint": "SELECT zpravy.text FROM zpravy JOIN posadka ON zpravy.osoba_id = posadka.id WHERE posadka.jmeno = 'Viktor'",
        "must": [(r"\bjoin\b", "Spojení tabulek se dělá slovem JOIN.")],
    },
    {
        "id": 23, "set": 6,
        "title": "Kde je krystal",
        "tip": "Tabulka zasoby má sloupec mistnost_id, který odkazuje na mistnosti.id. Spojením zjistíš název místnosti.",
        "story": "Poslední krok případu. V archivu je u krystalu zapsané číslo místnosti. Zjisti mi její jméno a jdeme pro něj.",
        "victory": "Krystal leží v laboratoři. Případ je uzavřený a Tux už pro něj běží.",
        "goal": "Vypiš mistnosti.nazev místnosti, kde leží zasoby.nazev rovno 'Krystal' (spoj zasoby a mistnosti přes zasoby.mistnost_id = mistnosti.id).",
        "starter": "SELECT mistnosti.nazev FROM zasoby JOIN mistnosti ON  WHERE ",
        "hint": "SELECT mistnosti.nazev FROM zasoby JOIN mistnosti ON zasoby.mistnost_id = mistnosti.id WHERE zasoby.nazev = 'Krystal'",
        "must": [(r"\bjoin\b", "Spojení tabulek se dělá slovem JOIN.")],
    },
]

CHAPTERS = [
    {"set": 1, "title": "Archiv se probouzí",
     "intro": "Krystal zmizel a já přišel o paměť. Archiv ale funguje. Naučíme se z něj číst: SELECT, FROM a LIMIT.",
     "outro": "Znáš archiv a umíš z něj číst. Teď začne pravý výslech."},
    {"set": 2, "title": "Výslech",
     "intro": "Z celé posádky potřebuju vybrat jen ty správné. K tomu slouží WHERE, porovnávání a AND.",
     "outro": "Okruh podezřelých je užší a víme, že krystal hlídaly zamčené dveře."},
    {"set": 3, "title": "Stopy v záznamech",
     "intro": "Dveře si pamatují každý vstup. Seřadíme je, omezíme na podezřelou hodinu a prohledáme zprávy.",
     "outro": "V podezřelou hodinu vešla do reaktoru jedna osoba, číslo 8."},
    {"set": 4, "title": "Počítání důkazů",
     "intro": "Detektiv spoléhá na čísla. COUNT, DISTINCT a SUM mi řeknou, kolik čeho a koho tu máme.",
     "outro": "Čísla sedí. V reaktoru se vystřídalo pět lidí a stanici dochází energie."},
    {"set": 5, "title": "Skupiny podezřelých",
     "intro": "Když záznamů přibývá, pomůže je seskupit. GROUP BY, ORDER BY a HAVING najdou ty, kdo vyčnívají.",
     "outro": "Číslo 8 vede v pohybu po stanici a s ním se nesmíme ztratit."},
    {"set": 6, "title": "Spojení stop",
     "intro": "Poslední kapitola. JOIN spojí tabulky, aby místo čísel byla jména. Teď případ uzavřeme.",
     "outro": "Případ uzavřen. Viktor krystal vrátí a dostane bezpečný zdroj energie pro svůj pokus."},
]

PROLOGUE = ("Ahoj, detektive! Jsem Pyt, palubní počítač stanice TUX-1. V noci zmizel hlavní energetický krystal "
            "a po výpadku jsem zapomněl, co se stalo. Archiv s daty ale přežil. Tux už čeká u reaktoru "
            "a já potřebuju, abys v archivu pomocí příkazu SELECT našel stopy.")

EPILOGUE = ("Případ je vyřešený. Díky tvým dotazům víme, kdo krystal vzal a kde leží. Tux ho právě nese zpátky do reaktoru "
            "a stanice zase svítí. Z tebe je opravdový datový detektiv.")


def all_tasks():
    return SQL_TASKS


def get_task(task_id):
    for t in SQL_TASKS:
        if t["id"] == task_id:
            return t
    return None


_BETWEEN_AND = re.compile(r"(\bBETWEEN\s+(?:'[^']*'|\S+))\s+AND\b", re.IGNORECASE)
_NEW_LINE = re.compile(r"\s+(FROM|WHERE|GROUP\s+BY|HAVING|ORDER\s+BY|LIMIT|JOIN)\b", re.IGNORECASE)
_NEW_LINE_INDENT = re.compile(r"\s+(AND|OR)\b", re.IGNORECASE)


def format_sql(query: str) -> str:
    """Každou část dotazu (FROM, WHERE, ORDER BY...) dá na nový řádek, AND a OR odsadí.
    Slouží jen pro zobrazení dětem, aby se učily psát dotazy přehledně. AND uvnitř BETWEEN zůstává na řádku."""
    q = _BETWEEN_AND.sub(lambda m: m.group(1) + " \x00", query.strip("\n"))
    q = _NEW_LINE.sub(lambda m: "\n" + m.group(1), q)
    q = _NEW_LINE_INDENT.sub(lambda m: "\n  " + m.group(1), q)
    q = q.replace("\x00", "AND")
    q = re.sub(r"[ \t]+\n", "\n", q)
    # řádek končící klíčovým slovem je prázdné místo k doplnění, nech za ním mezeru
    return re.sub(r"(?m)\b(SELECT|WHERE|ON|AND|OR|BY)$", r"\1 ", q)
