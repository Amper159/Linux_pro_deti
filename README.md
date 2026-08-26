<div align="center">

# 🐧 MISE: LINUXOVÝ PRŮZKUMNÍK
**Interaktivní kampaňová hra pro výuku terminálu Linuxu**

![Python](https://img.shields.io/badge/Python-3.10+-3776AB?style=for-the-badge&logo=python&logoColor=white)
![Flask](https://img.shields.io/badge/Flask-3.0+-000000?style=for-the-badge&logo=flask&logoColor=white)
![TailwindCSS](https://img.shields.io/badge/Tailwind_CSS-3.0+-38B2AC?style=for-the-badge&logo=tailwind-css&logoColor=white)
![Licence](https://img.shields.io/badge/Licence-MIT-green?style=for-the-badge)

</div>

---

## 📖 O projektu

**Mise: Linuxový Průzkumník** je webová výuková aplikace navržená pro zábavné osvojování práce v Linuxové příkazové řádce (CLI). Hráč prochází jednotlivými úrovněmi na vesmírné stanici **TUX-1**, kde plní praktické úkoly pomocí simulovaného bash terminálu.

Projekt je ideální pro děti, začátečníky i pokročilejší zájemce o administraci systému.

---

## ✨ Hlavní funkce

* 🎮 **90 interaktivních úrovní** rozdělených do 3 tematických kampaňových sad:
  * **1. Základy Linuxu** (*pwd, ls, cd, cat, grep, mkdir, touch, rm, chmod...*)
  * **2. Soubory a sítě** (*cp, mv, find, ping, echo, nano, wc, head, tail, df...*)
  * **3. Mistr Systému** (*ps, top, free, tar, gzip, alias, curl, kill...*)
* 🎯 **Striktní validace příkazů** – hra vyžaduje přesné zadání správného příkazu a hlásí okamžitou zpětnou vazbu při chybě.
* 👤 **Profil hráče & ukládání pokroku** – podpora více uživatelů přes lokální úložiště (`localStorage`).
* 🏆 **Gamifikace** – systém XP bodů, streaks, žebříček kadetů a získávání tématických odznaků.
* ⌨️ **Historie příkazů** – možnost procházení dříve zadaných příkazů pomocí šipek `↑` a `↓`.
* 🐧 **Pískoviště `/piskoviste`** – volné hřiště se **skutečným Linuxem** v kontejneru (viz níže).

---

## 🛠️ Použité technologie

* **Backend**: Python, Flask, `shlex`
* **Frontend**: HTML5, JavaScript (ES6+), Tailwind CSS (via CDN)
* **Ikony & Písma**: FontAwesome 6, Google Fonts (*Quicksand*, *Fira Code*)

---

## 🚀 Jak hru spustit lokálně

### 1. Klonování repozitáře
```bash
git clone [https://github.com/Amper159/Linux_pro_deti.git](https://github.com/Amper159/Linux_pro_deti.git)
cd Linux_pro_deti

---

## 🐧 Pískoviště: opravdový Linux (`/piskoviste`)

Hra příkazy jen simuluje. Pískoviště je opak – běží v něm **skutečný minimální
Linux** (Alpine, ~22 MB) v izolovaném kontejneru, takže výstupy jsou reálné
a splnění úkolů se ověřuje proti opravdovému souborovému systému.

### Jak to funguje

1. **Přihlášení jménem a heslem.** Heslo se nikam neukládá – počítá se z něj
   ověřovač (`scrypt` se solí) a **otisk účtu**. Z otisku vzniká uživatel
   (`kadet_<8 znaků hashe>`) a jeho domovská složka.
2. **Mount vlastního filesystému.** Složka `sandbox_data/homes/<otisk>` se
   do kontejneru připojí jako `/home/kadet_<…>`. Soubory tak přežijí odhlášení
   i restart serveru.
3. **Kontejner na uživatele.** Startuje se při prvním příkazu, po 20 minutách
   nečinnosti ho uklidí reaper. Data zůstávají na disku.
4. **Tři úkoly** – vytvoř složku a soubor, zapiš text do souboru, přidej právo
   ke spuštění a spusť skript. Kontrola spouští reálné `test` a `grep`
   v kontejneru; je jedno, jakým příkazem se k výsledku dostaneš.

### Bezpečnost (dvě vrstvy)

**Kontejner** – `--network none` (žádný internet), běh pod UID hostitele místo
roota, `--cap-drop ALL`, `--security-opt no-new-privileges`, read-only rootfs
(zapisovatelný je jen domov a `/tmp` jako tmpfs), 128 MB paměti, 0.5 CPU,
max 64 procesů, časový limit 10 s na příkaz.

**Filtr příkazů** (`sandbox/policy.py`) – nebezpečné příkazy se zachytí ještě
před spuštěním a uživatel dostane česky vysvětlené proč: `sudo`, `su`, `mount`,
`dd`, `mkfs`, `chown`, `chroot`, `reboot`, `shutdown`, `systemctl`, `kill`,
`curl`, `wget`, `ssh`, `apk`/`apt`, `crontab` a další. Navíc se hlídají vzory
jako fork bomba `:(){ :|:& };:`, `rm -rf /`, zápis do `/etc` nebo na `/dev/sda`
a nekonečné smyčky.

Bez Dockeru se automaticky použije záložní `bubblewrap` (`bwrap`).
Když není ani jeden, stránka to poctivě oznámí.

### Struktura

```
sandbox/
├── auth.py         účty, scrypt hash, odvození uživatele a domova
├── config.py       cesty a limity (dá se přepsat proměnnými prostředí)
├── engine.py       start kontejneru, spouštění příkazů, úklid
├── policy.py       filtr nebezpečných příkazů
├── tasks.py        tři úkoly + ověření proti reálnému systému
├── routes.py       stránka a API (/piskoviste)
├── docker/         Dockerfile minimálního Linuxu
├── skel/           obsah domovské složky nového uživatele
└── templates/      piskoviste.html
```

### Nastavení

| Proměnná | Výchozí | K čemu |
|---|---|---|
| `SECRET_KEY` | vygeneruje se do `sandbox_data/.flask_secret` | podpis session cookie |
| `SANDBOX_DATA` | `sandbox_data/` | kam se ukládají domovy a účty |
| `SANDBOX_MAX_CONTAINERS` | `12` | kolik kontejnerů smí běžet naráz |
| `SANDBOX_IDLE_TIMEOUT` | `1200` | po kolika sekundách nečinnosti se kontejner zastaví |

Obraz se postaví sám při prvním použití, nebo předem:

```bash
docker build -t linux-pro-deti-sandbox:1 sandbox/docker
```

---

## 🐳 Nasazení na VPS (Docker Compose)

Aplikace běží v kontejneru pod `gunicorn`, ale pískoviště startuje **sourozenecké**
kontejnery přes Docker socket hostitele. Proto se `sandbox_data` mountuje dovnitř
na **stejnou absolutní cestu** jako na hostiteli – domovy uživatelů připojuje
démon hostitele a jinak by našel jinou složku.

```bash
make init            # vytvoří .env a sám doplní SECRET_KEY, APP_UID/GID, DOCKER_GID
nano .env            # zbývá vyplnit SANDBOX_DATA, SITE_ADDRESS, ACME_EMAIL
make deploy          # preflight, datová složka, obrazy, start, kontrola běhu
```

`make deploy` udělá celý postup sám: ověří prostředí (Docker, skupina `docker`,
absolutní `SANDBOX_DATA`, vyplněný `SECRET_KEY`), založí datovou složku
(v případě potřeby přes `sudo` a s `chown` na `APP_UID:APP_GID`), předpostaví
obraz pískoviště, spustí stack s Caddym a počká, až aplikace odpovídá.

Aktualizace nasazené instance je pak jen `make update` (git pull + rebuild +
restart + kontrola).

### Vývojové prostředí: `make dev`

Jeden příkaz postaví kompletní lokální stack – nic se nevyplňuje ručně:

```bash
make dev
```

* vygeneruje `.env.dev` (detekuje UID/GID i GID skupiny `docker`, nastaví
  vlastní `SECRET_KEY`, data do `./test_data`, port `8099`, jeden worker),
* nastartuje stack pod **odděleným compose projektem** `linux-pro-deti-dev`,
  takže může běžet současně s produkčním,
* přimountuje `app.py` a `sandbox/` do kontejneru a zapne `gunicorn --reload`
  → uložení souboru rovnou restartuje workera,
* počká na naběhnutí a spustí smoke test (přihlášení + reálný příkaz v pískovišti).

`make dev-logs`, `make dev-shell`, `make dev-down`, `make dev-clean`
(smaže `test_data/` i `.env.dev`).

### Přehled cílů

`make` bez argumentů vypíše nápovědu.

| Cíl | Co dělá |
|---|---|
| `make init` | vytvoří `.env` a doplní, co jde detekovat |
| `make preflight` | kontrola prostředí a `.env` před nasazením |
| `make deploy` | kompletní nasazení včetně Caddyho a kontroly běhu |
| `make update` | `git pull` + rebuild + restart |
| `make dev` | kompletní lokální vývojové prostředí |
| `make smoke` | end-to-end test běžící instance (založí testovací účet) |
| `make up` / `up-proxy` / `down` / `restart` / `ps` | ruční ovládání stacku |
| `make logs`, `logs-web`, `logs-caddy` | sledování logů |
| `make shell` | shell uvnitř běžícího kontejneru |
| `make sandbox-image` | předběžné postavení obrazu pískoviště |
| `make sandboxes` / `clean-sandboxes` | výpis / smazání kontejnerů hráčů |
| `make backup` | záloha `SANDBOX_DATA` do `backups/` |

Všechny cíle jdou přepnout na jiný env soubor: `make ENV_FILE=.env.staging up`.

Aplikace poslouchá na `127.0.0.1:8000` (viz `APP_BIND`/`APP_PORT`).

### HTTPS přes Caddy (volitelný profil)

V compose je připravená služba `caddy`, která se spouští jen s profilem `proxy`.
Certifikát od Let's Encrypt si vyřídí i obnovuje sama – stačí, aby doména
mířila na VPS a porty 80 + 443 byly otevřené:

```bash
# v .env:  SITE_ADDRESS=linuxhrou.cz   ACME_EMAIL=admin@linuxhrou.cz
make up-proxy        # `make deploy` ho spouští automaticky
make logs-caddy
```

* `SITE_ADDRESS=:80` = běh bez TLS (lokální test nebo cizí proxy před tím).
* `ACME_EMAIL` může zůstat prázdné – jen nepřijdou upozornění na expiraci.
* Certifikáty žijí ve volume `caddy_data`; **nemazat** (`docker compose down -v`
  je smaže a nové vydávání naráží na limity Let's Encrypt).
* Konfigurace je v `Caddyfile` (gzip/zstd, bezpečnostní hlavičky, HTTP→HTTPS).
* S Caddym už `APP_BIND`/`APP_PORT` nepotřebuješ – klidně řádek `ports:`
  ve službě `web` zakomentuj, aplikace bude dostupná jen přes proxy.

Bez profilu `proxy` se spustí jen `web` a proxy si postavíš vlastní
(nginx, Traefik) proti `127.0.0.1:8000`.

| Proměnná | Výchozí | K čemu |
|---|---|---|
| `SECRET_KEY` | – | podpis session cookie (nastav, jinak restart odhlásí všechny) |
| `SANDBOX_DATA` | `/srv/linux-pro-deti/sandbox_data` | absolutní cesta k datům (stejná uvnitř i venku) |
| `APP_UID` / `APP_GID` | `1000` | vlastník dat; pod tímto UID běží i pískoviště |
| `DOCKER_GID` | `999` | GID skupiny `docker` (`getent group docker \| cut -d: -f3`) |
| `APP_BIND` / `APP_PORT` | `127.0.0.1` / `8000` | kde se publikuje gunicorn |
| `WEB_CONCURRENCY` | `2` | počet workerů gunicornu |
| `SITE_ADDRESS` | `linuxhrou.cz` | doména pro Caddy (`:80` = bez TLS) |
| `ACME_EMAIL` | – | e-mail pro Let's Encrypt (může být prázdný) |
| `SANDBOX_MAX_CONTAINERS` | `12` | strop běžících pískovišť (128 MB / 0.5 CPU každé) |

> ⚠️ Kontejner `web` má připojený `/var/run/docker.sock`, což je na hostiteli
> ekvivalent roota. Dětské kontejnery zůstávají neprivilegované, ale samotnou
> aplikaci provozuj jen z důvěryhodného kódu.
