"""SQL Lab: bezpečné spouštění dotazů nad vymyšlenou databází stanice TUX-1.

Databáze žije jen v paměti a vzniká znovu pro každý dotaz (je malá), takže
nic nejde rozbít ani trvale změnit. Povolený je výhradně SELECT - dohlíží na to
authorizer SQLite, takže to platí i pro triky typu PRAGMA, ATTACH nebo INSERT.
Dotaz má časový limit a výsledek se ořezává na MAX_ROWS řádků.
"""
import re
import sqlite3
import time

from .sql_data import SCHEMA_SQL

MAX_QUERY_LENGTH = 600
MAX_ROWS = 100
TIME_LIMIT_SECONDS = 1.0

_ALLOWED_ACTIONS = {
    sqlite3.SQLITE_SELECT,
    sqlite3.SQLITE_READ,
    sqlite3.SQLITE_FUNCTION,
    sqlite3.SQLITE_RECURSIVE,
}
# Funkce, které nikdo v hodinách SQL nepotřebuje a mohly by sežrat paměť.
_DENIED_FUNCTIONS = {"randomblob", "zeroblob", "load_extension", "readfile", "writefile"}


class QueryError(Exception):
    """Chyba dotazu s českou, dětem srozumitelnou zprávou."""


def _connect() -> sqlite3.Connection:
    conn = sqlite3.connect(":memory:")
    conn.executescript(SCHEMA_SQL)
    conn.commit()
    return conn


def _make_authorizer(state: dict):
    def authorizer(action, arg1, arg2, db_name, source):
        if action == sqlite3.SQLITE_READ:
            state["reads"] += 1
            return sqlite3.SQLITE_OK
        if action == sqlite3.SQLITE_FUNCTION:
            if (arg2 or "").lower() in _DENIED_FUNCTIONS:
                return sqlite3.SQLITE_DENY
            return sqlite3.SQLITE_OK
        if action in _ALLOWED_ACTIONS:
            return sqlite3.SQLITE_OK
        return sqlite3.SQLITE_DENY
    return authorizer


def _translate_error(exc: Exception, query: str) -> str:
    text = str(exc)
    low = text.lower()
    if "no such table" in low:
        name = text.split(":")[-1].strip()
        return f"Tabulka „{name}“ v archivu neexistuje. Zkontroluj název tabulky."
    if "no such column" in low:
        name = text.split(":")[-1].strip()
        return f"Sloupec „{name}“ jsem nenašel. Zkontroluj název sloupce a u textu nezapomeň na apostrofy."
    if "ambiguous column" in low:
        name = text.split(":")[-1].strip()
        return f"Sloupec „{name}“ je ve více tabulkách. Napiš před něj název tabulky, třeba posadka.id."
    if "unrecognized token" in low or "unterminated" in low:
        return "Někde chybí uvozovka nebo je tam divný znak. Texty se píšou do apostrofů, třeba 'energetika'."
    if "incomplete input" in low:
        return "Dotaz vypadá nedokončený. Chybí třeba část za FROM nebo uzavírací závorka."
    if "syntax error" in low:
        near = re.search(r'near "(.*?)"', text)
        kde = f" Podívej se na místo kolem „{near.group(1)}“." if near else ""
        return "Něco je špatně napsané." + kde + " Pozor na čárky mezi sloupci a na pořadí SELECT, FROM, WHERE."
    if "not authorized" in low or "prohibited" in low:
        return "Tady se jen ptáme a čteme. Povolený je jen příkaz SELECT, nic se nemění ani nemaže."
    if "interrupted" in low:
        return "Dotaz trval moc dlouho a archiv ho zastavil. Zkus ho zjednodušit."
    if "only execute one statement" in low:
        return "Najednou se dá poslat jen jeden příkaz. Smaž všechno za středníkem."
    if "no tables specified" in low:
        return "Chybí část FROM. Řekni, ze které tabulky se má číst."
    return "Archiv tomu nerozumí: " + text


def run_query(query: str) -> dict:
    """Spustí dotaz. Vrátí {'columns', 'rows', 'truncated', 'reads'}; při chybě QueryError."""
    query = (query or "").strip()
    if not query:
        raise QueryError("Nejdřív napiš dotaz.")
    if len(query) > MAX_QUERY_LENGTH:
        raise QueryError(f"Dotaz je moc dlouhý (nejvýš {MAX_QUERY_LENGTH} znaků).")
    first = query.lstrip("( \n\t").split(None, 1)
    if not first or first[0].lower() not in ("select", "with"):
        raise QueryError("Dotaz musí začínat slovem SELECT.")

    conn = _connect()
    state = {"reads": 0}
    deadline = time.monotonic() + TIME_LIMIT_SECONDS
    try:
        conn.set_authorizer(_make_authorizer(state))
        conn.set_progress_handler(lambda: 1 if time.monotonic() > deadline else 0, 20000)
        try:
            conn.setlimit(sqlite3.SQLITE_LIMIT_LENGTH, 100000)
        except (AttributeError, sqlite3.Error):
            pass
        try:
            cur = conn.execute(query.rstrip().rstrip(";"))
            columns = [d[0] for d in (cur.description or [])]
            fetched = cur.fetchmany(MAX_ROWS + 1)
        except (sqlite3.Error, ValueError, OverflowError) as exc:
            raise QueryError(_translate_error(exc, query)) from exc
    finally:
        conn.close()

    truncated = len(fetched) > MAX_ROWS
    rows = [list(r) for r in fetched[:MAX_ROWS]]
    for row in rows:
        for i, value in enumerate(row):
            if isinstance(value, (bytes, bytearray)):
                row[i] = "<binární data>"
    return {"columns": columns, "rows": rows, "truncated": truncated, "reads": state["reads"]}


def _norm_value(v):
    if isinstance(v, float):
        return round(v, 4)
    return v


def _norm_rows(rows, ordered: bool):
    out = [tuple(_norm_value(v) for v in r) for r in rows]
    return out if ordered else sorted(out, key=repr)


def check_result(task: dict, query: str, result: dict) -> str:
    """Porovná výsledek dítěte s výsledkem referenčního řešení. Vrací '' když je OK, jinak radu."""
    for pattern, rada in task.get("must", []):
        if not re.search(pattern, query, re.IGNORECASE):
            return rada
    if result["reads"] == 0:
        return "Data se musí číst z tabulky. Opisování hotové odpovědi se nepočítá."

    expected = run_query(task["hint"])
    ordered = bool(task.get("ordered"))
    got = _norm_rows(result["rows"], ordered)
    want = _norm_rows(expected["rows"], ordered)
    if len(result["columns"]) != len(expected["columns"]):
        return (f"Chtěli jsme {len(expected['columns'])} sloupců, ty jich vracíš {len(result['columns'])}. "
                "Přečti si zadání, které sloupce se mají vypsat.")
    if len(got) != len(want):
        if len(got) > len(want):
            return f"Vrací se {len(got)} řádků, ale mělo by jich být {len(want)}. Přidej nebo uprav podmínku."
        return f"Vrací se jen {len(got)} řádků, ale mělo by jich být {len(want)}. Podmínka je asi moc přísná."
    if got != want:
        if ordered and sorted(got, key=repr) == sorted(want, key=repr):
            return "Řádky tam jsou, ale ve špatném pořadí. Zkontroluj ORDER BY."
        return "Počet řádků sedí, ale hodnoty ne. Zkontroluj sloupce a podmínku v zadání."
    return ""
