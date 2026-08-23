"""Tři úkoly pískoviště.

Splnění se **neporovnává s očekávaným příkazem** – kontroluje se skutečný stav
souborového systému v kontejneru (`test`, `grep`). Je jedno, jestli k výsledku
dojdeš jedním příkazem nebo deseti oklikami; důležité je, jak to dopadlo.
"""

from typing import List

from . import auth, engine

TASKS = [
    {
        "id": "tabor",
        "title": "1. Postav základní tábor",
        "story": "Přistál jsi na cizí planetě. Nejdřív potřebuješ složku na výbavu a prázdný deník.",
        "goal": "Vytvoř složku 'mise' a v ní prázdný soubor 'denik.txt'.",
        "hint": "mkdir mise\ntouch mise/denik.txt",
        "commands": ["mkdir", "touch", "ls"],
        "checks": [
            {"label": "existuje složka 'mise'", "test": 'test -d "$HOME/mise"'},
            {"label": "ve složce je soubor 'denik.txt'", "test": 'test -f "$HOME/mise/denik.txt"'},
        ],
    },
    {
        "id": "denik",
        "title": "2. Zapiš první záznam",
        "story": "Velitelství chce hlášení. Do deníku musí přijít text, ve kterém se objeví slovo TUX.",
        "goal": "Do souboru 'mise/denik.txt' zapiš větu, která obsahuje slovo 'TUX'.",
        "hint": 'echo "Potkal jsem tučňáka TUX" > mise/denik.txt\ncat mise/denik.txt',
        "commands": ["echo", "cat", "grep"],
        "checks": [
            {"label": "soubor 'denik.txt' není prázdný", "test": 'test -s "$HOME/mise/denik.txt"'},
            {"label": "v deníku je slovo 'TUX'", "test": 'grep -qi tux "$HOME/mise/denik.txt"'},
        ],
    },
    {
        "id": "start",
        "title": "3. Odstartuj raketu",
        "story": "V domovské složce leží skript 'start.sh'. Zatím ho nejde spustit – chybí mu právo 'x'.",
        "goal": "Přidej souboru 'start.sh' právo ke spuštění a spusť ho.",
        "hint": "ls -l start.sh\nchmod +x start.sh\n./start.sh",
        "commands": ["ls -l", "chmod", "./start.sh"],
        "checks": [
            {"label": "'start.sh' má právo ke spuštění (x)", "test": 'test -x "$HOME/start.sh"'},
            {"label": "skript byl opravdu spuštěn (vznikl 'starty.log')", "test": 'test -s "$HOME/starty.log"'},
        ],
    },
]

TASKS_BY_ID = {task["id"]: task for task in TASKS}

_OK = "LPD_OK"
_NO = "LPD_NO"


def public_tasks() -> List[dict]:
    """Verze úkolů pro prohlížeč – bez shellových testů."""
    return [
        {
            "id": t["id"],
            "title": t["title"],
            "story": t["story"],
            "goal": t["goal"],
            "hint": t["hint"],
            "commands": t["commands"],
            "checks": [c["label"] for c in t["checks"]],
        }
        for t in TASKS
    ]


def verify(user: auth.SandboxUser, task_id: str) -> dict:
    """Ověří úkol proti skutečnému souborovému systému v kontejneru."""
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
