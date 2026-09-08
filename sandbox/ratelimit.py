"""
Jednoduchý rate limiting pro přihlašovací endpoint - bez závislosti na Redis
nebo jiné externí službě, protože aplikace jede jako jeden kontejner s malým
provozem. Dvě nezávislé brzdy:

  1. Podle IP adresy - kolikrát se z jedné adresy zkusilo přihlásit/založit
     účet za posledních pár minut. Chrání hlavně proti skriptu, co by zkoušel
     zakládat pořád nové účty (= pořád nové Docker kontejnery).
  2. Podle jména účtu - kolikrát za sebou někdo zadal ŠPATNÉ heslo ke KONKRÉTNÍMU
     existujícímu účtu. Chrání proti hrubé síle na jeden konkrétní účet, i kdyby
     útočník střídal IP adresy.

Limity jsou schválně dost velkorysé (školní PC za NATem = jedna IP pro celou
třídu, co se přihlašuje ve stejnou minutu), ale znemožní smyčku ve skriptu.

POZOR na provozní omezení: čítače žijí jen v paměti procesu. Pokud gunicorn
běží s víc než jedním workerem (WEB_CONCURRENCY > 1), má každý worker svoji
vlastní kopii čítačů - limit se tak efektivně vydělí počtem workerů. Pořád je
to nesrovnatelně lepší než žádný limit, ale pro tvrdou garanci by bylo potřeba
sdílené úložiště (např. Redis).
"""
from __future__ import annotations

import time
from threading import Lock

# (max_pokusů, okno_v_sekundách)
IP_LIMIT = (20, 5 * 60)          # 20 pokusů o přihlášení/založení za 5 minut z jedné IP
USERNAME_LOCKOUT = (5, 15 * 60)  # 5 špatných hesel za sebou k jednomu jménu -> zámek na 15 minut

_lock = Lock()
_ip_hits: dict[str, list[float]] = {}
_username_fails: dict[str, list[float]] = {}


def _prune(hits: list[float], window: float, now: float) -> list[float]:
    return [t for t in hits if now - t < window]


def check_ip(ip: str) -> float | None:
    """Vrátí None, pokud je IP v pořádku, jinak počet sekund, než to má zkusit znovu."""
    limit, window = IP_LIMIT
    now = time.time()
    with _lock:
        hits = _prune(_ip_hits.get(ip, []), window, now)
        _ip_hits[ip] = hits
        if len(hits) >= limit:
            return window - (now - hits[0])
        hits.append(now)
    return None


def check_username_lock(username_key: str) -> float | None:
    """Vrátí None, pokud jméno není momentálně uzamčené, jinak počet sekund do konce zámku."""
    limit, window = USERNAME_LOCKOUT
    now = time.time()
    with _lock:
        fails = _prune(_username_fails.get(username_key, []), window, now)
        _username_fails[username_key] = fails
        if len(fails) >= limit:
            return window - (now - fails[0])
    return None


def record_failed_password(username_key: str) -> None:
    now = time.time()
    with _lock:
        fails = _username_fails.setdefault(username_key, [])
        fails.append(now)


def record_success(username_key: str) -> None:
    """Úspěšné přihlášení smaže historii špatných pokusů k danému jménu."""
    with _lock:
        _username_fails.pop(username_key, None)