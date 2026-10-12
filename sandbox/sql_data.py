"""Vymyšlená databáze stanice TUX-1 pro SQL Lab (případ zmizelého krystalu).

Data jsou pevná a hlídá je 'make check-tasks' - kdo je mění, musí zkontrolovat,
že referenční řešení úkolů (sql_tasks.py) pořád vracejí to, co mají.
Názvy tabulek a sloupců jsou schválně bez diakritiky, aby se daly snadno psát.
"""

SCHEMA_SQL = """
CREATE TABLE posadka (
    id INTEGER PRIMARY KEY,
    jmeno TEXT,
    role TEXT,
    oddeleni TEXT,
    vek INTEGER,
    zkusenosti INTEGER
);
INSERT INTO posadka VALUES
    (1,  'Mira',   'inženýrka', 'energetika', 34, 9),
    (2,  'Bruno',  'technik',   'energetika', 41, 15),
    (3,  'Dana',   'lékařka',   'zdravi',     29, 5),
    (4,  'Ondra',  'kuchař',    'zazemi',     52, 20),
    (5,  'Eliška', 'pilotka',   'navigace',   27, 4),
    (6,  'Radek',  'technik',   'energetika', 38, 11),
    (7,  'Nela',   'vědkyně',   'laborator',  31, 6),
    (8,  'Viktor', 'vědec',     'laborator',  45, 18),
    (9,  'Sofie',  'kadetka',   'navigace',   17, 1),
    (10, 'Jarda',  'údržbář',   'zazemi',     58, 30),
    (11, 'Lenka',  'inženýrka', 'energetika', 36, 12),
    (12, 'Pavel',  'pilot',     'navigace',   33, 8);

CREATE TABLE mistnosti (
    id INTEGER PRIMARY KEY,
    nazev TEXT,
    patro INTEGER,
    zamceno INTEGER
);
INSERT INTO mistnosti VALUES
    (1, 'Můstek',          3, 0),
    (2, 'Reaktorová hala', 0, 1),
    (3, 'Laboratoř',       1, 0),
    (4, 'Jídelna',         1, 0),
    (5, 'Ošetřovna',       1, 0),
    (6, 'Sklad',           0, 1),
    (7, 'Hangár',          0, 0),
    (8, 'Kajuty',          2, 0);

CREATE TABLE vstupy (
    id INTEGER PRIMARY KEY,
    osoba_id INTEGER,
    mistnost_id INTEGER,
    cas TEXT
);
INSERT INTO vstupy VALUES
    (1,  2,  2, '21:05'),
    (2,  11, 2, '21:40'),
    (3,  2,  2, '22:10'),
    (4,  6,  2, '22:25'),
    (5,  8,  2, '22:47'),
    (6,  10, 2, '23:15'),
    (7,  8,  3, '20:30'),
    (8,  8,  4, '19:45'),
    (9,  8,  3, '22:58'),
    (10, 8,  8, '23:50'),
    (11, 2,  6, '20:15'),
    (12, 2,  7, '22:30'),
    (13, 4,  4, '17:30'),
    (14, 4,  4, '21:15'),
    (15, 4,  8, '22:20'),
    (16, 10, 6, '21:50'),
    (17, 1,  1, '22:00'),
    (18, 1,  1, '22:50'),
    (19, 3,  5, '21:00');

CREATE TABLE zasoby (
    id INTEGER PRIMARY KEY,
    nazev TEXT,
    kategorie TEXT,
    mnozstvi INTEGER,
    mistnost_id INTEGER
);
INSERT INTO zasoby VALUES
    (1, 'Krystal',          'energie', 1,   3),
    (2, 'Záložní baterie',  'energie', 6,   6),
    (3, 'Solární článek',   'energie', 14,  7),
    (4, 'Konzervy',         'jidlo',   120, 4),
    (5, 'Chléb',            'jidlo',   40,  4),
    (6, 'Lékárnička',       'lekarna', 8,   5),
    (7, 'Šroubovák',        'naradi',  15,  6),
    (8, 'Kladivo',          'naradi',  5,   6),
    (9, 'Kyslíková láhev',  'kyslik',  30,  7);

CREATE TABLE zpravy (
    id INTEGER PRIMARY KEY,
    osoba_id INTEGER,
    cas TEXT,
    text TEXT
);
INSERT INTO zpravy VALUES
    (1, 1,  '22:52', 'Výkon reaktoru spadl na nulu! Někdo vypnul hlavní krystal.'),
    (2, 2,  '22:12', 'Hotovo, v reaktorové hale je všechno v pořádku.'),
    (3, 4,  '21:20', 'Večeře je hotová, kdo chce přídavek?'),
    (4, 8,  '20:40', 'Můj pokus v laboratoři potřebuje hodně energie. Moc hodně.'),
    (5, 8,  '23:10', 'Pokus běží. Nikdo se nesmí dozvědět, odkud jsem energii vzal.'),
    (6, 10, '23:17', 'V reaktorové hale je prázdný stojan! Krystal tam není!'),
    (7, 7,  '21:55', 'Viktor je dnes nějak nervózní.'),
    (8, 3,  '21:05', 'Ošetřovna zavírá, dobrou noc.');
"""

# Popis tabulek pro panel vpravo (název, popis, sloupce).
TABLES_INFO = [
    {"name": "posadka", "desc": "lidé na stanici", "columns": ["id", "jmeno", "role", "oddeleni", "vek", "zkusenosti"]},
    {"name": "mistnosti", "desc": "místnosti stanice", "columns": ["id", "nazev", "patro", "zamceno"]},
    {"name": "vstupy", "desc": "záznamy z dveří", "columns": ["id", "osoba_id", "mistnost_id", "cas"]},
    {"name": "zasoby", "desc": "věci ve skladech", "columns": ["id", "nazev", "kategorie", "mnozstvi", "mistnost_id"]},
    {"name": "zpravy", "desc": "zprávy posádky", "columns": ["id", "osoba_id", "cas", "text"]},
]
