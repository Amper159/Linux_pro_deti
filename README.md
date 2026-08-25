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
