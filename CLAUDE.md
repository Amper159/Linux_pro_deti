# Linuxhrou.cz (repo Linux_pro_deti)

Gamifikovaný web pro děti, kde se učí Linux (Pískoviště) a Python (Python Lab). Veřejně běží na https://linuxhrou.cz. Majitel komunikuje česky, texty na webu piš česky, bez emoji v příspěvcích (na webu pro děti emoji v UI používáme).

## Nasazení (majitel to dělá sám na serveru)
- `cd ~/projekty/Linux_pro_deti && make update` = `git pull` + `docker compose up -d --build`.
- Samotné `docker compose up -d` nebo `restart` NEPŘEBUILDUJE image ani nenačte nový `.env`. Změny kódu i `.env` vždy přes `make update`.
- Po každém pushi připomeň: nasadit přes `make update`.
- Push na `main` jde přes GitHub konektor session. Když proxy hlásí 403, zkus `add_repo` (push) a push znovu.

## Architektura
- Flask + Gunicorn za Caddy (HTTPS), Docker Compose, sandbox kontejnery (Alpine) pro Pískoviště.
- `app.py`: hlavní stránka (velká `render_template_string`, Tailwind z CDN), nav s hamburgerem, sekce `#python-hry`, `#navody`, `#pro-rodice` (formulář zpětné vazby), `/api/feedback`, sitemap, robots, `/soukromi`, tlačítko zpět nahoru.
- `sandbox/routes.py`, `engine.py`, `policy.py`: Pískoviště (terminál, filtr nebezpečných příkazů). Úkoly v `sandbox/tasks.py` (90 úkolů).
- `sandbox/python_lab.py` (blueprint `/python`), `python_tasks.py` (35 úkolů, 6 kapitol, prolog/epilog), `python_gamification.py`, `story_data.py` (příběh Iskra), `static_games/` (hry ke stažení: iskra, kobka, obesenec), `static_js/pyodide_worker.js`.
- Pyodide 0.26.4 běží ve Web Workeru (limit 5 s, pak terminate + restart). Pomocné funkce `_spust` a `_over` vrací srozumitelné chyby s číslem řádku, každé spuštění má čistý jmenný prostor.
- `sandbox/pages.py` + `templates/articles/`: články (SEO). Registr `ARTICLES`, sitemap se skládá z něj.
- `sandbox/auth.py`: uživatelé, progress v JSON souborech (`sandbox_data/progress/`, `sandbox_data/python_progress/`). Uživatelé jsou sdílení mezi Pískovištěm a Python Labem. Uživatelské jméno: `^[a-zA-Z0-9._-]{3,24}$`.
- Žebříčky: top 20 + vlastní pořadí hráče pod seznamem, když je mimo top (`gamification.leaderboard(me)`, `python_gamification.leaderboard(me)`). Čte soubory všech uživatelů při každém volání; při tisících hráčů přidat cache.
- `sandbox/feedback.py` (`sandbox_data/feedback.json`), `mailer.py` (Resend SMTP), `ratelimit.py`. Všechny zprávy z webu chodí na `FEEDBACK_NOTIFY_EMAIL` (lampart.m1305@gmail.com). Adresa info@linuxhrou.cz nefunguje.
- `sandbox/visits.py`: počítadlo návštěv (cookie `lpd_vid`). Počítá i boty. Nulovat `visits.json` zatím NEchce.
- SEO: JSON-LD, canonical, ověřovací meta tagy z env (`GOOGLE_SITE_VERIFICATION`, `BING_SITE_VERIFICATION`, `SEZNAM_WMT_VERIFICATION`).

## Kontrola před pushem
- `make check-tasks` zkontroluje všech 90 Linux úkolů (nápověda splní kontrolu, duplicity) i 35 Python úkolů (řešitelnost, délky textů: story 170, victory 110, tip 200 znaků). Musí vrátit 0 chyb. Úkoly 40-42 (ping) se přeskakují (síť).
- `python3 -m py_compile` na změněné soubory a načtení Jinja šablon.
- Změny UI ověř Playwrightem (Chromium v `/opt/pw-browsers`). Testovací prostředí nemá přístup na CDN: Tailwind zkompiluj z npm (`tailwindcss@3`) a CDN požadavky přesměruj přes `route`. Pyodide z npm balíčku `pyodide@0.26.4`.
- Při změně UI zkontroluj mobil (320-430 px): žádné vodorovné přetékání.

## Pravidla a rozhodnutí
- Autorská práva: jen vlastní postavy (Iskra, Pyt, Tux). Žádný Spider-Man, Tlapková patrola ani jiné cizí postavy.
- Pískoviště a Python Lab: XP, odznaky a žebříček jsou oddělené.
- Úkoly v `tasks.py` musí mít srozumitelné zadání bez nutnosti otevřít nápovědu; nápověda musí projít kontrolou. Pole `goal` u Python úkolů při práci na příběhu neměň.
- Ochrana dětí: žádné osobní údaje navíc, jména se vykreslují přes `textContent`.
- Commity piš česky, krátce, co a proč.

## Otevřené nápady (nerozhodnuto)
- Počítadlo ignorující boty; smazání testovacích účtů.
- Týdenní žebříček; cache žebříčku.
- Postupné nápovědy od Tuxe; skript, kde uživatelé u úkolů končí; bossové a levely.
- Odstranit `user-scalable=no` z viewportu (přístupnost).
