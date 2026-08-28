from datetime import timedelta
from flask import Flask, render_template_string
import os

from sandbox import engine as sandbox_engine
from sandbox import sandbox_bp
from sandbox.config import SECRET_FILE, ensure_dirs

app = Flask(__name__)


def _secret_key() -> bytes:
    """Klíč pro session cookie – z proměnné prostředí, jinak jednou vygenerovaný."""
    env = os.environ.get("SECRET_KEY")
    if env:
        return env.encode("utf-8")
    ensure_dirs()
    if not SECRET_FILE.exists():
        SECRET_FILE.write_bytes(os.urandom(32))
        SECRET_FILE.chmod(0o600)
    return SECRET_FILE.read_bytes()


app.secret_key = _secret_key()
app.permanent_session_lifetime = timedelta(days=7)

# Nová stránka: /piskoviste – opravdový Linux v kontejneru.
app.register_blueprint(sandbox_bp)
sandbox_engine.start_reaper()

PORTAL_HTML_TEMPLATE = """<!DOCTYPE html>
<html lang="cs">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Linuxhrou.cz – Objevuj svět Linuxu zábavně!</title>
    <script src="https://cdn.tailwindcss.com"></script>
    <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.0/css/all.min.css">
    <link href="https://fonts.googleapis.com/css2?family=Fira+Code:wght@500;600&family=Quicksand:wght@500;600;700;800&display=swap" rel="stylesheet">
    <script src="https://cdnjs.cloudflare.com/ajax/libs/Chart.js/4.4.0/chart.umd.min.js"></script>
    <style>
        body { font-family: 'Quicksand', sans-serif; background-color: #0f172a; color: #f8fafc; }
        .font-mono { font-family: 'Fira Code', monospace; }
        .card-hover { transition: transform 0.2s, box-shadow 0.2s; }
        .card-hover:hover { transform: translateY(-4px); }

    body { font-family: 'Quicksand', sans-serif; background-color: #0f172a; color: #f8fafc; }
    .font-mono { font-family: 'Fira Code', monospace; }
    .card-hover { transition: transform 0.2s, box-shadow 0.2s; }
    .card-hover:hover { transform: translateY(-4px); }
    .lego-card-yellow { border: 3px solid #facc15; box-shadow: 0 5px 0 #ca8a04; }
    .speech-bubble { position: relative; }
    .speech-bubble::before {
        content: "";
        position: absolute;
        left: -8px;
        top: 22px;
        border-width: 8px 10px 8px 0;
        border-style: solid;
        border-color: transparent #1e293b transparent transparent;
    }
    @keyframes tux-bounce {
        0%, 100% { transform: translateY(0) rotate(-2deg); }
        50% { transform: translateY(-6px) rotate(2deg); }
    }
    .tux-idle { animation: tux-bounce 2.4s ease-in-out infinite; display:inline-block; }
    @keyframes pulse-dot { 0%,100%{opacity:1} 50%{opacity:.3} }
    .live-dot { animation: pulse-dot 1.6s ease-in-out infinite; }
    .fade-fact { transition: opacity .35s ease; }
    .station-line { background: linear-gradient(90deg,#38bdf8,#4ade80,#facc15); }

    </style>
</head>
<body class="min-h-screen flex flex-col justify-between bg-slate-950">

    <nav class="bg-slate-900 border-b border-slate-800 sticky top-0 z-50">
        <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
            <div class="flex items-center justify-between h-16">
                <div class="flex items-center space-x-3">
                    <div class="bg-amber-400 text-slate-950 p-2 rounded-xl font-bold text-xl">
                        <i class="fa-solid fa-terminal"></i>
                    </div>
                    <span class="text-2xl font-black tracking-wider text-amber-400">Linux<span class="text-sky-400">hrou.cz</span></span>
                </div>
                <div class="hidden xl:flex space-x-4 text-[13px] font-bold">
                    <a href="#o-linuxu" class="text-slate-300 hover:text-amber-400 transition">Co je Linux?</a>
                    <a href="#mapa" class="text-slate-300 hover:text-emerald-400 transition">Mapa kampaní</a>
                    <a href="#kde-bezi" class="text-slate-300 hover:text-sky-400 transition">Kde všude běží?</a>
                    <a href="#distribuce" class="text-slate-300 hover:text-purple-400 transition">Vyber si distribuci</a>
                    <a href="#odznaky" class="text-slate-300 hover:text-amber-400 transition">Odznaky</a>
                    <a href="#pro-rodice" class="text-slate-300 hover:text-rose-400 transition">Pro rodiče</a>
                    <a href="#prikazy" class="text-slate-300 hover:text-purple-400 transition">Slovník příkazů</a>
                </div>
                <div>
                    <a href="/piskoviste" class="bg-emerald-500 hover:bg-emerald-400 text-slate-950 font-extrabold px-5 py-2.5 rounded-xl border-b-4 border-emerald-700 active:translate-y-0.5 transition flex items-center space-x-2">
                        <i class="fa-solid fa-terminal text-lg"></i>
                        <span>SPUSTIT TERMINÁL</span>
                    </a>
                </div>
            </div>
        </div>
    </nav>

    <!-- ============ HERO + ŽIVÁ STATISTIKA + MINI TERMINÁL ============ -->
    <header class="relative overflow-hidden bg-gradient-to-b from-slate-900 to-slate-950 py-14 px-4 border-b border-slate-800">
        <div class="max-w-6xl mx-auto">

            <div class="text-center space-y-6 max-w-3xl mx-auto">
                <span class="bg-sky-500/10 text-sky-400 text-xs font-bold px-3 py-1 rounded-full border border-sky-500/20 uppercase tracking-widest">
                    🚀 Vzdělávací portál pro malé i velké SysAdminy
                </span>
                <h1 class="text-4xl md:text-6xl font-black text-slate-100 leading-tight">
                    Ovládni počítač jako superfrajer pomocí <span class="text-transparent bg-clip-text bg-gradient-to-r from-amber-400 via-sky-400 to-emerald-400">Příkazové Řádky!</span>
                </h1>
                <p class="text-slate-400 text-base md:text-lg font-medium">
                    Zjisti, jak funguje operační systém, na kterém běží rakety SpaceX, Android v mobilu i nejrychlejší superpočítače světa.
                </p>
            </div>

            <div class="mt-8 flex flex-wrap justify-center gap-3 text-xs font-bold">
                <div class="bg-slate-900 border border-slate-800 rounded-xl px-4 py-2 flex items-center gap-2">
                    <span class="w-2 h-2 rounded-full bg-emerald-400 live-dot"></span>
                    <span class="text-slate-300"><span id="stat-online" class="text-emerald-300">0</span> kadetů právě online</span>
                </div>
                <div class="bg-slate-900 border border-slate-800 rounded-xl px-4 py-2 text-slate-300">
                    <i class="fa-solid fa-list-check text-sky-400"></i>
                    Splněno <span id="stat-tasks" class="text-sky-300">0</span> úkolů dohromady
                </div>
                <div class="bg-slate-900 border border-slate-800 rounded-xl px-4 py-2 text-slate-300">
                    <i class="fa-solid fa-star text-amber-400"></i>
                    Nasbíráno <span id="stat-xp" class="text-amber-300">0</span> XP
                </div>
            </div>

            <div class="mt-10 max-w-2xl mx-auto bg-slate-900 rounded-2xl border-2 border-sky-500/40 shadow-lg shadow-sky-500/5 overflow-hidden">
                <div class="bg-slate-800 px-4 py-2 flex items-center justify-between border-b-2 border-slate-700">
                    <div class="flex items-center space-x-2">
                        <span class="w-3 h-3 rounded-full bg-rose-500"></span>
                        <span class="w-3 h-3 rounded-full bg-amber-400"></span>
                        <span class="w-3 h-3 rounded-full bg-emerald-400"></span>
                        <span class="text-[11px] font-bold text-slate-400 ml-2 font-mono">ukázka – zkus to na nečisto</span>
                    </div>
                    <span class="text-[10px] font-bold text-sky-400 uppercase tracking-wide">bez přihlášení</span>
                </div>
                <div id="demo-output" class="p-4 font-mono text-[12px] text-left text-slate-300 min-h-[92px] leading-relaxed"></div>
                <div class="flex items-center px-4 py-3 bg-slate-950 border-t-2 border-slate-700">
                    <span class="font-mono text-emerald-400 font-bold mr-2">~$</span>
                    <input id="demo-input" type="text" autocomplete="off" spellcheck="false"
                        class="flex-1 bg-transparent font-mono text-[12px] text-slate-100 focus:outline-none"
                        placeholder="zkus třeba: ls, pwd, whoami nebo help">
                </div>
            </div>

            <div class="pt-8 flex flex-wrap justify-center gap-4">
                <a href="/piskoviste" class="bg-amber-400 hover:bg-amber-300 text-slate-950 font-black px-8 py-4 rounded-2xl border-b-4 border-amber-600 active:translate-y-1 transition text-lg flex items-center space-x-3 shadow-lg shadow-amber-400/10">
                    <i class="fa-solid fa-rocket"></i>
                    <span>Vstoupit do skutečného terminálu</span>
                </a>
            </div>
        </div>
    </header>

<main class="max-w-7xl mx-auto px-4 py-12 space-y-16">

    <!-- bod 6: Tux mluví i na homepage -->
    <section id="o-linuxu" class="space-y-6">
        <div class="flex items-center space-x-3">
            <div class="p-2 bg-amber-500/10 rounded-lg text-amber-400 text-xl"><i class="fa-solid fa-book-open"></i></div>
            <h2 class="text-2xl font-bold text-slate-100">Příběh Tučňáka Tuxe a Linuse</h2>
        </div>

        <div class="bg-slate-900 rounded-2xl p-5 border-2 border-slate-800 flex items-start gap-4">
            <div class="text-4xl tux-idle shrink-0">🐧</div>
            <div class="bg-slate-800 rounded-xl px-4 py-3 speech-bubble border-2 border-slate-700">
                <p class="text-sm font-semibold text-slate-100" id="tux-homepage-msg">
                    Ahoj! Já jsem Tux a provedu tě celým Linuxhrou.cz. Klidně si nejdřív zkus terminál nahoře – nic tím nerozbiješ!
                </p>
            </div>
        </div>

        <div class="grid md:grid-cols-2 gap-6">
            <div class="bg-slate-900 p-6 rounded-2xl border border-slate-800 card-hover space-y-3">
                <div class="w-12 h-12 bg-sky-500/20 text-sky-400 rounded-xl flex items-center justify-center text-2xl font-bold">👤</div>
                <h3 class="text-xl font-bold text-sky-300">Kdo to vymyslel?</h3>
                <p class="text-slate-300 text-sm leading-relaxed">
                    V roce 1991 se finský student <b>Linus Torvalds</b> nudil a chtěl si vytvořit vlastní operační systém pro svůj počítač. Napsal základní kód a zdarma ho nabídl celému světu. Dnes na jeho kód přispívají tisíce programátorů z celého světa!
                </p>
            </div>
            <div class="bg-slate-900 p-6 rounded-2xl border border-slate-800 card-hover space-y-3">
                <div class="w-12 h-12 bg-amber-500/20 text-amber-400 rounded-xl flex items-center justify-center text-2xl font-bold">🐧</div>
                <h3 class="text-xl font-bold text-amber-300">Proč právě Tučňák?</h3>
                <p class="text-slate-300 text-sm leading-relaxed">
                    Maskotem Linuxu je tučňák <b>Tux</b>. Linus Torvalds miluje tučňáky – při návštěvě zoo v Austrálii ho dokonce jeden malý tučňák kousnul do prstu! Od té doby se Tux stal symbolem přátelského a svobodného systému.
                </p>
            </div>
        </div>
    </section>

    <!-- bod 3: náhled mapy tří kampaní -->
    <section id="mapa" class="space-y-6">
        <div class="flex items-center space-x-3">
            <div class="p-2 bg-emerald-500/10 rounded-lg text-emerald-400 text-xl"><i class="fa-solid fa-map"></i></div>
            <h2 class="text-2xl font-bold text-slate-100">Tvoje cesta vesmírnou stanicí TUX-1</h2>
        </div>
        <p class="text-slate-400 text-sm max-w-2xl">Tři kampaně, 90 úkolů – tady je náhled, co tě v pískovišti čeká.</p>

        <div class="relative">
            <div class="hidden md:block absolute top-10 left-[16%] right-[16%] h-1 station-line rounded-full opacity-40"></div>
            <div class="grid md:grid-cols-3 gap-6 relative">
                <div class="bg-slate-900 rounded-2xl border-2 border-sky-400 p-5 card-hover">
                    <div class="w-14 h-14 rounded-full bg-sky-500/20 flex items-center justify-center text-2xl mb-3 mx-auto border-2 border-sky-400">🛰️</div>
                    <h3 class="text-center font-bold text-sky-300">1. Základy Linuxu</h3>
                    <p class="text-center text-[11px] text-slate-400 mt-1">30 úkolů</p>
                    <p class="text-xs text-slate-300 mt-3 text-center">Procházení příkazové řádky, první soubory a složky, orientace v lodi.</p>
                </div>
                <div class="bg-slate-900 rounded-2xl border-2 border-slate-700 p-5 card-hover opacity-90">
                    <div class="w-14 h-14 rounded-full bg-emerald-500/20 flex items-center justify-center text-2xl mb-3 mx-auto border-2 border-slate-700">📡</div>
                    <h3 class="text-center font-bold text-emerald-300">2. Soubory a sítě</h3>
                    <p class="text-center text-[11px] text-slate-400 mt-1">30 úkolů</p>
                    <p class="text-xs text-slate-300 mt-3 text-center">Práva k souborům, hledání textu, propojování příkazů dohromady.</p>
                </div>
                <div class="bg-slate-900 rounded-2xl border-2 border-slate-700 p-5 card-hover opacity-90">
                    <div class="w-14 h-14 rounded-full bg-amber-500/20 flex items-center justify-center text-2xl mb-3 mx-auto border-2 border-slate-700">🚀</div>
                    <h3 class="text-center font-bold text-amber-300">3. Mistr systému</h3>
                    <p class="text-center text-[11px] text-slate-400 mt-1">30 úkolů</p>
                    <p class="text-xs text-slate-300 mt-3 text-center">Procesy, pokročilá správa – staneš se kapitánem stanice TUX-1.</p>
                </div>
            </div>
        </div>
    </section>

    <section id="kde-bezi" class="space-y-6">
        <div class="flex items-center space-x-3">
            <div class="p-2 bg-sky-500/10 rounded-lg text-sky-400 text-xl"><i class="fa-solid fa-globe"></i></div>
            <h2 class="text-2xl font-bold text-slate-100">Kde všude se Linux ukrývá?</h2>
        </div>
        <div class="grid sm:grid-cols-2 lg:grid-cols-4 gap-4">
            <div class="bg-slate-900 p-5 rounded-xl border border-slate-800 text-center space-y-2 card-hover">
                <i class="fa-solid fa-mobile-screen text-3xl text-emerald-400 mb-2"></i>
                <h4 class="font-bold text-slate-200">V tvém mobilu</h4>
                <p class="text-xs text-slate-400">Systém <b>Android</b> je postavený přímo na jádře Linuxu!</p>
            </div>
            <div class="bg-slate-900 p-5 rounded-xl border border-slate-800 text-center space-y-2 card-hover">
                <i class="fa-solid fa-gamepad text-3xl text-purple-400 mb-2"></i>
                <h4 class="font-bold text-slate-200">Herní konzole</h4>
                <p class="text-xs text-slate-400">Populární handheld <b>Steam Deck</b> běží na vysoce vyladěném Linuxu (SteamOS).</p>
            </div>
            <div class="bg-slate-900 p-5 rounded-xl border border-slate-800 text-center space-y-2 card-hover">
                <i class="fa-solid fa-shuttle-space text-3xl text-rose-400 mb-2"></i>
                <h4 class="font-bold text-slate-200">Vesmírné rakety</h4>
                <p class="text-xs text-slate-400">Rakety SpaceX i stanice ISS spoléhají na rychlost a bezpečnost Linuxu.</p>
            </div>
            <div class="bg-slate-900 p-5 rounded-xl border border-slate-800 text-center space-y-2 card-hover">
                <i class="fa-solid fa-server text-3xl text-amber-400 mb-2"></i>
                <h4 class="font-bold text-slate-200">Superpočítače & Internet</h4>
                <p class="text-xs text-slate-400">100 % z 500 nejrychlejších superpočítačů světa používá Linux.</p>
            </div>
        </div>
    </section>

    <section id="instalace" class="bg-gradient-to-r from-slate-900 via-slate-900 to-indigo-950/40 p-8 rounded-3xl border border-slate-800 space-y-6">
        <div class="max-w-3xl space-y-3">
            <span class="text-xs font-bold text-emerald-400 uppercase tracking-wider">Kouzlo Terminálu</span>
            <h2 class="text-3xl font-black text-slate-100">Instalace aplikací během 2 sekund</h2>
            <p class="text-slate-300 text-sm leading-relaxed">
                Na Windows musíš hledat webové stránky, stahovat .exe soubory a proklikávat instalátory. V Linuxu stačí otevřít terminál a napsat jediný příkaz:
            </p>
        </div>
        <div class="grid md:grid-cols-2 gap-4">
            <div class="bg-slate-950 p-4 rounded-xl border border-slate-800 font-mono text-xs space-y-2">
                <div class="text-slate-500">// Ubuntu / Debian (Apt)</div>
                <div class="text-emerald-400"><span class="text-sky-400">sudo apt</span> install vlc discord steam</div>
                <div class="text-slate-400 text-[11px]">--> Nainstaluje VLC prehrávač, Discord a Steam najednou!</div>
            </div>
            <div class="bg-slate-950 p-4 rounded-xl border border-slate-800 font-mono text-xs space-y-2">
                <div class="text-slate-500">// Aktualizace celého systému</div>
                <div class="text-emerald-400"><span class="text-sky-400">sudo apt</span> update && <span class="text-sky-400">sudo apt</span> upgrade</div>
                <div class="text-slate-400 text-[11px]">--> Zaktualizuje všechny programy v počítači 1 kliknutím!</div>
            </div>
        </div>
    </section>



    <!-- ============ GRAF A SROVNÁNÍ DISTRIBUCÍ ============ -->
    <section id="distribuce" class="space-y-6">
        <div class="flex items-center space-x-3">
            <div class="p-2 bg-sky-500/10 rounded-lg text-sky-400 text-xl"><i class="fa-solid fa-layer-group"></i></div>
            <h2 class="text-2xl font-bold text-slate-100">Který Linux je pro tebe ten pravý?</h2>
        </div>
        <p class="text-slate-400 text-sm max-w-2xl">
            "Linux" není jeden systém, ale rodina desítek <b class="text-slate-200">distribucí</b> – různě poskládaný stejný základ.
            Tady je srovnání těch nejoblíbenějších pro úplné začátečníky.
        </p>

        <div class="bg-slate-900 rounded-2xl border border-slate-800 p-5">
            <canvas id="distro-chart" height="110"></canvas>
            <p class="text-[10px] text-slate-500 mt-3 text-center">
                Zdroj: <a href="https://distrowatch.com/dwres.php?resource=popularity" class="text-sky-400 hover:underline" target="_blank">DistroWatch.com – Page Hit Ranking</a>,
                posledních 6 měsíců (stav srpen 2026). Číslo ukazuje zájem návštěvníků webu, ne skutečný podíl uživatelů –
                DistroWatch sám upozorňuje, že se nejedná o měřítko tržního podílu.
            </p>
        </div>

        <div class="grid md:grid-cols-3 gap-4">
            <div class="bg-slate-900 rounded-2xl border-2 border-emerald-500 p-5 card-hover space-y-2">
                <div class="flex items-center justify-between">
                    <h3 class="font-bold text-emerald-300 text-lg">Linux Mint</h3>
                    <span class="text-[10px] font-bold bg-emerald-500/20 text-emerald-300 px-2 py-1 rounded-lg border border-emerald-500/40">DOPORUČENO PRO ZAČÁTEK</span>
                </div>
                <p class="text-xs text-slate-300 leading-relaxed">
                    Nabídka Start, hodiny vpravo dole, ikony v liště – vypadá a chová se nejpodobněji Windows ze všech.
                    Nastavuje se skoro sám, funguje spolehlivě i na starších počítačích.
                </p>
                <p class="text-[11px] text-slate-500">Hodí se na: běžnou práci, školu, přechod z Windows</p>
            </div>
            <div class="bg-slate-900 rounded-2xl border border-slate-800 p-5 card-hover space-y-2">
                <h3 class="font-bold text-sky-300 text-lg">Zorin OS</h3>
                <p class="text-xs text-slate-300 leading-relaxed">
                    Přímo nabízí vzhled "jako Windows" nebo "jako macOS" na výběr při instalaci. Skvělá volba,
                    když se s vzhledem nechceš vůbec trápit.
                </p>
                <p class="text-[11px] text-slate-500">Hodí se na: co nejplynulejší přechod z Windows</p>
            </div>
            <div class="bg-slate-900 rounded-2xl border border-slate-800 p-5 card-hover space-y-2">
                <h3 class="font-bold text-amber-300 text-lg">Ubuntu</h3>
                <p class="text-xs text-slate-300 leading-relaxed">
                    Nejrozšířenější a nejlépe zdokumentovaná distribuce – na cokoliv se zeptáš, najdeš návod.
                    Vzhled je jinačí než Windows, ale zvykneš si rychle.
                </p>
                <p class="text-[11px] text-slate-500">Hodí se na: kdo chce nejvíc návodů a podpory na internetu</p>
            </div>
            <div class="bg-slate-900 rounded-2xl border border-slate-800 p-5 card-hover space-y-2">
                <h3 class="font-bold text-purple-300 text-lg">Pop!_OS</h3>
                <p class="text-xs text-slate-300 leading-relaxed">
                    Postavené na Ubuntu, ale vyladěné pro hraní her a grafické karty. Skvělá volba, pokud
                    chceš na Linuxu i hrát.
                </p>
                <p class="text-[11px] text-slate-500">Hodí se na: hraní her, grafické práce</p>
            </div>
            <div class="bg-slate-900 rounded-2xl border border-slate-800 p-5 card-hover space-y-2">
                <h3 class="font-bold text-rose-300 text-lg">Fedora</h3>
                <p class="text-xs text-slate-300 leading-relaxed">
                    Vždy jedna z nejnovějších verzí softwaru, používají ji i profesionální vývojáři.
                    O něco náročnější na začátek než Mint nebo Zorin.
                </p>
                <p class="text-[11px] text-slate-500">Hodí se na: programátory, nejnovější technologie</p>
            </div>
            <div class="bg-slate-900 rounded-2xl border border-slate-800 p-5 card-hover space-y-2">
                <h3 class="font-bold text-slate-300 text-lg">Manjaro</h3>
                <p class="text-xs text-slate-300 leading-relaxed">
                    Umožňuje systém doslova poskládat podle sebe – obrovská volnost, ale i o dost víc věcí,
                    které si musíš nastavit sám.
                </p>
                <p class="text-[11px] text-slate-500">Hodí se na: pokročilé uživatele, co chtějí vše na míru</p>
            </div>
        </div>
    </section>

    <!-- ============ NÁVOD NA INSTALACI Z USB ============ -->
    <section id="instalace-navod" class="space-y-6">
        <div class="flex items-center space-x-3">
            <div class="p-2 bg-emerald-500/10 rounded-lg text-emerald-400 text-xl"><i class="fa-solid fa-download"></i></div>
            <h2 class="text-2xl font-bold text-slate-100">Jak nainstalovat Linux z USB flashdisku</h2>
        </div>
        <p class="text-slate-400 text-sm max-w-2xl">
            Budeš potřebovat prázdný USB flashdisk (aspoň 8 GB – jeho obsah se při přípravě smaže) a asi hodinu času.
        </p>

        <div class="space-y-3">
            <div class="bg-slate-900 rounded-xl border border-slate-800 p-4 flex gap-4 items-start card-hover">
                <div class="step-num bg-sky-500/20 text-sky-300 border-2 border-sky-500">1</div>
                <div>
                    <h4 class="font-bold text-slate-100 text-sm">Stáhni si instalační soubor (ISO)</h4>
                    <p class="text-xs text-slate-400 mt-1">Jdi na oficiální stránky zvolené distribuce (např. linuxmint.com) a stáhni si soubor s příponou <span class="font-mono text-sky-300">.iso</span>. Je to celý systém zabalený v jednom souboru, obvykle 2–4 GB.</p>
                </div>
            </div>
            <div class="bg-slate-900 rounded-xl border border-slate-800 p-4 flex gap-4 items-start card-hover">
                <div class="step-num bg-sky-500/20 text-sky-300 border-2 border-sky-500">2</div>
                <div>
                    <h4 class="font-bold text-slate-100 text-sm">Vytvoř si bootovací USB</h4>
                    <p class="text-xs text-slate-400 mt-1">Stáhni si zdarma program <span class="font-mono text-sky-300">Rufus</span> (rufus.ie) nebo <span class="font-mono text-sky-300">balenaEtcher</span>, vlož flashdisk do počítače, v programu vyber stažené ISO a klikni na vytvoření. Flashdisk se stane "spouštěcím" pro instalaci.</p>
                </div>
            </div>
            <div class="bg-slate-900 rounded-xl border border-slate-800 p-4 flex gap-4 items-start card-hover">
                <div class="step-num bg-sky-500/20 text-sky-300 border-2 border-sky-500">3</div>
                <div class="flex-1">
                    <h4 class="font-bold text-slate-100 text-sm">Restartuj počítač do boot menu</h4>
                    <p class="text-xs text-slate-400 mt-1">Nech flashdisk zasunutý, restartuj počítač a hned na začátku několikrát zmáčkni klávesu pro boot menu — liší se podle výrobce, viz tabulka níže. Vyber odtud USB flashdisk.</p>

                    <div class="mt-3 overflow-x-auto rounded-lg border border-slate-800">
                        <table class="w-full text-[11px] text-left">
                            <thead>
                                <tr class="bg-slate-800 text-slate-300">
                                    <th class="px-3 py-2 font-bold">Výrobce</th>
                                    <th class="px-3 py-2 font-bold">Klávesa pro boot menu</th>
                                    <th class="px-3 py-2 font-bold">Klávesa do BIOS/UEFI</th>
                                </tr>
                            </thead>
                            <tbody class="text-slate-400">
                                <tr class="border-t border-slate-800"><td class="px-3 py-1.5 font-semibold text-slate-300">Acer</td><td class="px-3 py-1.5 font-mono">F12 / Esc</td><td class="px-3 py-1.5 font-mono">F2 / Del</td></tr>
                                <tr class="border-t border-slate-800"><td class="px-3 py-1.5 font-semibold text-slate-300">Asus</td><td class="px-3 py-1.5 font-mono">Esc / F8</td><td class="px-3 py-1.5 font-mono">F2 / Del</td></tr>
                                <tr class="border-t border-slate-800"><td class="px-3 py-1.5 font-semibold text-slate-300">Dell</td><td class="px-3 py-1.5 font-mono">F12</td><td class="px-3 py-1.5 font-mono">F2</td></tr>
                                <tr class="border-t border-slate-800"><td class="px-3 py-1.5 font-semibold text-slate-300">HP</td><td class="px-3 py-1.5 font-mono">Esc / F9</td><td class="px-3 py-1.5 font-mono">F10</td></tr>
                                <tr class="border-t border-slate-800"><td class="px-3 py-1.5 font-semibold text-slate-300">Lenovo</td><td class="px-3 py-1.5 font-mono">F12 (nebo tlačítko Novo)</td><td class="px-3 py-1.5 font-mono">F1 / F2</td></tr>
                                <tr class="border-t border-slate-800"><td class="px-3 py-1.5 font-semibold text-slate-300">MSI</td><td class="px-3 py-1.5 font-mono">F11</td><td class="px-3 py-1.5 font-mono">Del</td></tr>
                                <tr class="border-t border-slate-800"><td class="px-3 py-1.5 font-semibold text-slate-300">Samsung</td><td class="px-3 py-1.5 font-mono">Esc / F2</td><td class="px-3 py-1.5 font-mono">F2</td></tr>
                                <tr class="border-t border-slate-800"><td class="px-3 py-1.5 font-semibold text-slate-300">Toshiba</td><td class="px-3 py-1.5 font-mono">F12</td><td class="px-3 py-1.5 font-mono">F2</td></tr>
                            </tbody>
                        </table>
                    </div>
                    <p class="text-[10px] text-slate-500 mt-2">Přesná klávesa se může lišit podle konkrétního modelu — pokud žádná nezabere, zkus vyhledat "boot menu" spolu s modelem svého počítače.</p>
                </div>
            </div>
            <div class="bg-slate-900 rounded-xl border border-slate-800 p-4 flex gap-4 items-start card-hover">
                <div class="step-num bg-sky-500/20 text-sky-300 border-2 border-sky-500">4</div>
                <div>
                    <h4 class="font-bold text-slate-100 text-sm">Vyzkoušej si Linux nanečisto</h4>
                    <p class="text-xs text-slate-400 mt-1">Naběhne nabídka – zvol <span class="font-mono text-sky-300">"Try/Zkusit"</span>. Linux se spustí přímo z flashky, aniž by se čehokoliv na disku dotkl. Klidně si to takhle jen prohlédni a nic neinstaluj.</p>
                </div>
            </div>
            <div class="bg-slate-900 rounded-xl border border-slate-800 p-4 flex gap-4 items-start card-hover">
                <div class="step-num bg-emerald-500/20 text-emerald-300 border-2 border-emerald-500">5</div>
                <div>
                    <h4 class="font-bold text-slate-100 text-sm">Spusť instalaci "vedle Windows"</h4>
                    <p class="text-xs text-slate-400 mt-1">Pokud se ti líbí, klikni na ikonu instalace a zvol možnost <span class="font-mono text-emerald-300">"Instalovat vedle Windows"</span> (Install alongside Windows). Instalátor sám bezpečně zmenší místo pro Windows a vedle něj vytvoří místo pro Linux – Windows se nesmaže ani nijak nepoškodí.</p>
                </div>
            </div>
            <div class="bg-slate-900 rounded-xl border border-slate-800 p-4 flex gap-4 items-start card-hover">
                <div class="step-num bg-emerald-500/20 text-emerald-300 border-2 border-emerald-500">6</div>
                <div>
                    <h4 class="font-bold text-slate-100 text-sm">Vyber si systém při každém zapnutí</h4>
                    <p class="text-xs text-slate-400 mt-1">Po dokončení a restartu se objeví jednoduchá nabídka (tzv. <span class="font-mono text-emerald-300">GRUB</span>), kde si šipkami při každém zapnutí zvolíš, jestli chceš Windows, nebo svůj nový Linux.</p>
                </div>
            </div>
        </div>

        <div class="bg-amber-500/10 border border-amber-500/30 rounded-xl p-4 flex items-start gap-3">
            <i class="fa-solid fa-circle-info text-amber-400 mt-0.5"></i>
            <p class="text-xs text-amber-200">
                <b>Dobrá rada navíc:</b> i když instalátor Windows nemaže, před jakoukoliv instalací je vždycky rozumné
                zálohovat si důležité soubory (fotky, dokumenty) na flashdisk nebo cloud – pro jistotu, ne proto, že by se něco muselo pokazit.
            </p>
        </div>
    </section>

    <!-- ============ LINUX VEDLE WINDOWS (DUAL-BOOT) ============ -->
    <section id="dual-boot" class="bg-gradient-to-r from-slate-900 via-slate-900 to-emerald-950/30 rounded-3xl border border-slate-800 p-8 space-y-4">
        <div class="flex items-center space-x-3">
            <div class="p-2 bg-emerald-500/10 rounded-lg text-emerald-400 text-xl"><i class="fa-solid fa-window-restore"></i></div>
            <h2 class="text-2xl font-bold text-slate-100">Linux a Windows na jednom počítači? Žádný problém.</h2>
        </div>
        <p class="text-slate-300 text-sm max-w-2xl leading-relaxed">
            Tomuhle uspořádání se říká <b class="text-emerald-300">dual-boot</b> – oba systémy si "rozdělí" pevný disk mezi sebe
            a žijí vedle sebe, aniž by se navzájem ovlivňovaly. Windows zůstane přesně tak, jak ho znáš, se všemi
            soubory a programy – Linux dostane jen svoji vlastní, oddělenou část disku.
        </p>
        <div class="grid sm:grid-cols-3 gap-4 pt-2">
            <div class="bg-slate-950/60 rounded-xl p-4 border border-slate-800 text-center">
                <i class="fa-solid fa-hard-drive text-2xl text-sky-400 mb-2"></i>
                <p class="text-xs text-slate-300">Disk se jen <b class="text-slate-100">rozdělí</b> na dvě části, nic se nemaže.</p>
            </div>
            <div class="bg-slate-950/60 rounded-xl p-4 border border-slate-800 text-center">
                <i class="fa-solid fa-list-check text-2xl text-emerald-400 mb-2"></i>
                <p class="text-xs text-slate-300">Při startu si vždy <b class="text-slate-100">vybereš</b>, který systém chceš spustit.</p>
            </div>
            <div class="bg-slate-950/60 rounded-xl p-4 border border-slate-800 text-center">
                <i class="fa-solid fa-rotate-left text-2xl text-amber-400 mb-2"></i>
                <p class="text-xs text-slate-300">Linux <b class="text-slate-100">jde kdykoliv odinstalovat</b> a vrátit disku plné místo Windows.</p>
            </div>
        </div>
    </section>


    <!-- bod 5: rotující vtipná fakta -->
    <section class="space-y-6">
        <div class="flex items-center space-x-3">
            <div class="p-2 bg-rose-500/10 rounded-lg text-rose-400 text-xl"><i class="fa-solid fa-lightbulb"></i></div>
            <h2 class="text-2xl font-bold text-slate-100">Věděl jsi, že...?</h2>
        </div>
        <div class="bg-slate-900 border-2 border-slate-800 rounded-2xl p-6 flex items-center justify-between gap-4 min-h-[92px]">
            <p id="fun-fact" class="fade-fact text-slate-200 text-sm md:text-base font-semibold"></p>
            <div class="flex gap-1.5 shrink-0" id="fact-dots"></div>
        </div>
    </section>

    <section id="prikazy" class="space-y-6">
        <div class="flex items-center justify-between flex-wrap gap-3">
            <div class="flex items-center space-x-3">
                <div class="p-2 bg-purple-500/10 rounded-lg text-purple-400 text-xl"><i class="fa-solid fa-code"></i></div>
                <h2 class="text-2xl font-bold text-slate-100">Rychlý příkazový tahák</h2>
            </div>
            <a href="/piskoviste" class="text-xs font-bold text-sky-400 hover:underline">Vyzkoušet ve skutečném terminálu →</a>
        </div>
        <div class="grid sm:grid-cols-2 md:grid-cols-3 gap-3 font-mono text-xs">
            <div class="bg-slate-900 p-3 rounded-lg border border-slate-800 flex justify-between items-center">
                <span class="text-amber-300 font-bold">pwd</span><span class="text-slate-400 text-[11px]">Kde právě jsem?</span>
            </div>
            <div class="bg-slate-900 p-3 rounded-lg border border-slate-800 flex justify-between items-center">
                <span class="text-amber-300 font-bold">ls</span><span class="text-slate-400 text-[11px]">Vypiš soubory a složky</span>
            </div>
            <div class="bg-slate-900 p-3 rounded-lg border border-slate-800 flex justify-between items-center">
                <span class="text-amber-300 font-bold">cd &lt;složka&gt;</span><span class="text-slate-400 text-[11px]">Otevři složku</span>
            </div>
            <div class="bg-slate-900 p-3 rounded-lg border border-slate-800 flex justify-between items-center">
                <span class="text-amber-300 font-bold">cat &lt;soubor&gt;</span><span class="text-slate-400 text-[11px]">Přečti obsah souboru</span>
            </div>
            <div class="bg-slate-900 p-3 rounded-lg border border-slate-800 flex justify-between items-center">
                <span class="text-amber-300 font-bold">mkdir &lt;název&gt;</span><span class="text-slate-400 text-[11px]">Vytvoř novou složku</span>
            </div>
            <div class="bg-slate-900 p-3 rounded-lg border border-slate-800 flex justify-between items-center">
                <span class="text-amber-300 font-bold">clear</span><span class="text-slate-400 text-[11px]">Vyčisti terminál</span>
            </div>
        </div>
    </section>

    <!-- bod 7: odznaky jako lákadlo -->
    <section id="odznaky" class="space-y-6">
        <div class="flex items-center space-x-3">
            <div class="p-2 bg-amber-500/10 rounded-lg text-amber-400 text-xl"><i class="fa-solid fa-award"></i></div>
            <h2 class="text-2xl font-bold text-slate-100">Tohle všechno můžeš vysbírat</h2>
        </div>
        <div class="grid grid-cols-3 sm:grid-cols-6 gap-3">
            <div class="bg-slate-900 rounded-xl p-3 border-2 border-amber-400 text-center card-hover">
                <i class="fa-solid fa-terminal text-xl text-amber-300 mb-1"></i>
                <p class="text-[10px] font-bold text-amber-200">První kroky</p>
            </div>
            <div class="bg-slate-900 rounded-xl p-3 border-2 border-amber-400 text-center card-hover">
                <i class="fa-solid fa-folder-tree text-xl text-amber-300 mb-1"></i>
                <p class="text-[10px] font-bold text-amber-200">Mistr složek</p>
            </div>
            <div class="bg-slate-900 rounded-xl p-3 border-2 border-amber-400 text-center card-hover">
                <i class="fa-solid fa-magnifying-glass text-xl text-amber-300 mb-1"></i>
                <p class="text-[10px] font-bold text-amber-200">Lovec textu</p>
            </div>
            <div class="bg-slate-900 rounded-xl p-3 border-2 border-slate-700 text-center opacity-50">
                <i class="fa-solid fa-lock text-xl text-slate-500 mb-1"></i>
                <p class="text-[10px] font-bold text-slate-400">Síťový expert</p>
            </div>
            <div class="bg-slate-900 rounded-xl p-3 border-2 border-slate-700 text-center opacity-50">
                <i class="fa-solid fa-lock text-xl text-slate-500 mb-1"></i>
                <p class="text-[10px] font-bold text-slate-400">Kapitán procesů</p>
            </div>
            <div class="bg-slate-900 rounded-xl p-3 border-2 border-slate-700 text-center opacity-50">
                <i class="fa-solid fa-lock text-xl text-slate-500 mb-1"></i>
                <p class="text-[10px] font-bold text-slate-400">Mistr Linuxu</p>
            </div>
        </div>
    </section>

    <!-- bod 4: sekce pro rodiče a učitele -->
    <section id="pro-rodice" class="bg-slate-900 rounded-3xl border-2 border-rose-500/30 p-8 space-y-6">
        <div class="flex items-center space-x-3">
            <div class="p-2 bg-rose-500/10 rounded-lg text-rose-400 text-xl"><i class="fa-solid fa-shield-heart"></i></div>
            <h2 class="text-2xl font-bold text-slate-100">Pro rodiče a učitele</h2>
        </div>
        <div class="grid md:grid-cols-3 gap-4 text-sm">
            <div class="bg-slate-950 p-4 rounded-xl border border-slate-800">
                <p class="font-bold text-emerald-300 mb-1"><i class="fa-solid fa-wifi-slash"></i> Bez internetu v pískovišti</p>
                <p class="text-slate-400 text-xs">Kontejner dítěte nemá přístup k síti – nejde z něj nic stáhnout ani se kamkoliv připojit.</p>
            </div>
            <div class="bg-slate-950 p-4 rounded-xl border border-slate-800">
                <p class="font-bold text-emerald-300 mb-1"><i class="fa-solid fa-box"></i> Plně izolované</p>
                <p class="text-slate-400 text-xs">Vše běží v odděleném kontejneru bez práv správce – domácí počítač nijak neovlivní.</p>
            </div>
            <div class="bg-slate-950 p-4 rounded-xl border border-slate-800">
                <p class="font-bold text-emerald-300 mb-1"><i class="fa-solid fa-comment-slash"></i> Žádný volný chat s cizími lidmi</p>
                <p class="text-slate-400 text-xs">Sociální prvky jsou omezené na odznaky a žebříček – žádná otevřená komunikace s neznámými.</p>
            </div>
        </div>
        <div class="flex flex-wrap items-center justify-between gap-4 bg-slate-950/60 rounded-xl p-4 border border-slate-800">
            <p class="text-sm text-slate-300">Učíte třídu nebo kroužek? Založte si skupinu a sledujte pokrok všech dětí na jednom místě.</p>
            <a href="#" class="bg-rose-500 hover:bg-rose-400 text-white font-bold px-5 py-2.5 rounded-xl border-b-4 border-rose-700 active:translate-y-1 transition text-sm whitespace-nowrap">
                Chci to použít ve třídě →
            </a>
        </div>
    </section>

</main>

<footer class="bg-slate-900 border-t border-slate-800 py-8 px-4 text-center text-xs text-slate-500 space-y-2">
    <p class="font-bold text-slate-400">Linuxhrou.cz – Výuková platforma pro malé i velké průzkumníky</p>
    <p>Vytvořeno s ❤️ pro podporu výuky IT a Open-Source technologií.</p>
</footer>

<script>

// ---- bod 1: živá statistika (nasimulovaná, jen pro náhled) ----
function animateCount(id, target, suffix) {
    const el = document.getElementById(id);
    let cur = 0;
    const step = Math.max(1, Math.round(target / 60));
    const timer = setInterval(() => {
        cur += step;
        if (cur >= target) { cur = target; clearInterval(timer); }
        el.textContent = cur.toLocaleString('cs-CZ') + (suffix || '');
    }, 20);
}
animateCount('stat-online', 37);
animateCount('stat-tasks', 148920);
animateCount('stat-xp', 2456000);

// ---- bod 2: mini terminál nanečisto ----
const demoOut = document.getElementById('demo-output');
const demoIn = document.getElementById('demo-input');
const DEMO_RESPONSES = {
    'ls': 'ukoly.txt  hesla_TAJNE.txt  poznamky/  lod_TUX1/',
    'pwd': '/domov/kadet',
    'whoami': 'kadet_na_zkousku',
    'help': 'Zkus: ls, pwd, whoami. Plnou verzi s desítkami příkazů najdeš po vstupu do pískoviště →',
};
function demoWrite(text, cls) {
    const line = document.createElement('div');
    if (cls) line.className = cls;
    line.textContent = text;
    demoOut.appendChild(line);
    demoOut.scrollTop = demoOut.scrollHeight;
}
demoWrite('Tohle je ukázka nanečisto – zkus si napsat příkaz 👇', 'text-slate-500');
demoIn.addEventListener('keydown', (e) => {
    if (e.key !== 'Enter') return;
    const cmd = demoIn.value.trim();
    demoIn.value = '';
    if (!cmd) return;
    const echo = document.createElement('div');
    echo.innerHTML = '<span class="text-emerald-400 font-bold">~$</span> ' + cmd.replace(/[&<>]/g, c => ({'&':'&amp;','<':'&lt;','>':'&gt;'}[c]));
    demoOut.appendChild(echo);
    const resp = DEMO_RESPONSES[cmd.toLowerCase()];
    demoWrite(resp || `Tenhle příkaz zkus rovnou ve skutečném pískovišti →`, resp ? 'text-slate-300' : 'text-amber-400');
    demoOut.scrollTop = demoOut.scrollHeight;
});

// ---- bod 5: rotující fakta ----
const FACTS = [
    'Slovo „Linux" vzniklo náhodou – Linus Torvalds chtěl svůj projekt pojmenovat „Freax", ale správce serveru mu tam založil složku „linux" a název se ujal.',
    'Maskota Tuxe navrhl Larry Ewing v roce 1996 v programu GIMP – tedy v programu, který sám běží na Linuxu.',
    'Mezinárodní vesmírná stanice ISS přešla v roce 2013 z Windows na Linux kvůli stabilitě.',
    '100 % z 500 nejvýkonnějších superpočítačů světa běží na Linuxu.',
    'Android, nejrozšířenější mobilní systém světa, staví přímo na jádře Linuxu.',
];
let factIdx = 0;
const factEl = document.getElementById('fun-fact');
const dotsEl = document.getElementById('fact-dots');
FACTS.forEach((_, i) => {
    const dot = document.createElement('span');
    dot.className = 'w-2 h-2 rounded-full ' + (i === 0 ? 'bg-rose-400' : 'bg-slate-700');
    dotsEl.appendChild(dot);
});
function showFact(i) {
    factEl.style.opacity = 0;
    setTimeout(() => {
        factEl.textContent = FACTS[i];
        factEl.style.opacity = 1;
        [...dotsEl.children].forEach((d, j) => d.className = 'w-2 h-2 rounded-full ' + (j === i ? 'bg-rose-400' : 'bg-slate-700'));
    }, 350);
}
showFact(0);
setInterval(() => { factIdx = (factIdx + 1) % FACTS.length; showFact(factIdx); }, 4500);

// ---- bod 6: Tux hláška se mění při načtení ----
const TUX_GREETINGS = [
    'Ahoj! Já jsem Tux a provedu tě celým Linuxhrou.cz. Klidně si nejdřív zkus terminál nahoře – nic tím nerozbiješ!',
    'Vítej na palubě, kadete! Nejdřív se mrkni na mapu kampaní, ať víš, co tě čeká.',
    'Psst, věděl jsi, že dole najdeš i vtipná fakta o Linuxu? Podívej se na ně!',
];
document.getElementById('tux-homepage-msg').textContent = TUX_GREETINGS[Math.floor(Math.random() * TUX_GREETINGS.length)];



const ctx = document.getElementById('distro-chart').getContext('2d');
new Chart(ctx, {
    type: 'bar',
    data: {
        // Reálná data: DistroWatch Page Hit Ranking (hitů/den, posledních 6 měsíců, srpen 2026)
        labels: ['Linux Mint', "Pop!_OS", 'Fedora', 'Zorin OS', 'Ubuntu', 'Manjaro'],
        datasets: [
            {
                label: 'Zájem na DistroWatch (hitů/den, posl. 6 měsíců)',
                data: [1790, 1206, 1114, 1112, 914, 837],
                backgroundColor: ['#4ade80', '#a78bfa', '#fb7185', '#38bdf8', '#facc15', '#94a3b8'],
                borderRadius: 6,
            },
        ],
    },
    options: {
        indexAxis: 'y',
        responsive: true,
        scales: {
            x: { beginAtZero: true, ticks: { color: '#cbd5e1' }, grid: { color: '#1e293b' } },
            y: { ticks: { color: '#e2e8f0', font: { family: 'Quicksand', weight: '600' } }, grid: { display: false } },
        },
        plugins: {
            legend: { display: false },
            title: {
                display: true,
                text: 'Kolik zájmu weboví návštěvníci projevují o jednotlivé distribuce',
                color: '#94a3b8',
                font: { size: 12, family: 'Quicksand' },
            },
        },
    },
});

</script>
</body>
</html>
"""

@app.route("/")
def home():
    """Úvodní vzdělávací portál Linuxhrou.cz"""
    return render_template_string(PORTAL_HTML_TEMPLATE)


if __name__ == "__main__":
    app.run(debug=True, port=5000)