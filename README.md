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
