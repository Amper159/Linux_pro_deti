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
    <link href="https://fonts.googleapis.com/css2?family=Fira+Code:wght@600&family=Quicksand:wght@500;700;800&display=swap" rel="stylesheet">
    <style>
        body { font-family: 'Quicksand', sans-serif; background-color: #0f172a; color: #f8fafc; }
        .font-mono { font-family: 'Fira Code', monospace; }
        .card-hover { transition: transform 0.2s, box-shadow 0.2s; }
        .card-hover:hover { transform: translateY(-4px); }
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
                <div class="hidden md:flex space-x-6 text-sm font-bold">
                    <a href="#o-linuxu" class="text-slate-300 hover:text-amber-400 transition">Co je Linux?</a>
                    <a href="#kde-bezi" class="text-slate-300 hover:text-sky-400 transition">Kde všude běží?</a>
                    <a href="#instalace" class="text-slate-300 hover:text-emerald-400 transition">Instalace aplikací</a>
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

    <header class="relative overflow-hidden bg-gradient-to-b from-slate-900 to-slate-950 py-16 px-4 text-center border-b border-slate-800">
        <div class="max-w-4xl mx-auto space-y-6">
            <span class="bg-sky-500/10 text-sky-400 text-xs font-bold px-3 py-1 rounded-full border border-sky-500/20 uppercase tracking-widest">
                🚀 Vzdělávací portál pro malé i velké SysAdminy
            </span>
            <h1 class="text-4xl md:text-6xl font-black text-slate-100 leading-tight">
                Ovládni počítač jako superfrajer pomocí <span class="text-transparent bg-clip-text bg-gradient-to-r from-amber-400 via-sky-400 to-emerald-400">Příkazové Řádky!</span>
            </h1>
            <p class="text-slate-400 text-base md:text-lg max-w-2xl mx-auto font-medium">
                Zjisti, jak funguje operační systém, na kterém běží rakety SpaceX, Android v mobilu i nejrychlejší superpočítače světa.
            </p>
            <div class="pt-4 flex flex-wrap justify-center gap-4">
                <a href="/piskoviste" class="bg-amber-400 hover:bg-amber-300 text-slate-950 font-black px-8 py-4 rounded-2xl border-b-4 border-amber-600 active:translate-y-1 transition text-lg flex items-center space-x-3 shadow-lg shadow-amber-400/10">
                    <i class="fa-solid fa-rocket"></i>
                    <span>Vstoupit do skutečného terminálu</span>
                </a>
            </div>
        </div>
    </header>

    <main class="max-w-7xl mx-auto px-4 py-12 space-y-16">

        <section id="o-linuxu" class="space-y-6">
            <div class="flex items-center space-x-3">
                <div class="p-2 bg-amber-500/10 rounded-lg text-amber-400 text-xl"><i class="fa-solid fa-book-open"></i></div>
                <h2 class="text-2xl font-bold text-slate-100">Příběh Tučňáka Tuxe a Linuse</h2>
            </div>
            
            <div class="grid md:grid-cols-2 gap-6">
                <div class="bg-slate-900 p-6 rounded-2xl border border-slate-800 card-hover space-y-3">
                    <div class="w-12 h-12 bg-sky-500/20 text-sky-400 rounded-xl flex items-center justify-center text-2xl font-bold">👤</div>
                    <h3 class="text-xl font-bold text-sky-300">Kdo to vymyslel?</h3>
                    <p class="text-slate-300 text-sm leading-relaxed">
                        V roce 1991 se finský student **Linus Torvalds** nudil a chtěl si vytvořit vlastní operační systém pro svůj počítač. Napsal základní kód a zdarma ho nabídl celému světu. Dnes na jeho kód přispívají tisíce programátorů z celého světu!
                    </p>
                </div>

                <div class="bg-slate-900 p-6 rounded-2xl border border-slate-800 card-hover space-y-3">
                    <div class="w-12 h-12 bg-amber-500/20 text-amber-400 rounded-xl flex items-center justify-center text-2xl font-bold">🐧</div>
                    <h3 class="text-xl font-bold text-amber-300">Proč právě Tučňák?</h3>
                    <p class="text-slate-300 text-sm leading-relaxed">
                        Maskotem Linuxu je tučňák **Tux**. Linus Torvalds miluje tučňáky – při návštěvě zoo v Austrálii ho dokonce jeden malý tučňák kousnul do prstu! Od té doby se Tux stal symbolem přátelského a svobodného systému.
                    </p>
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
                    <p class="text-xs text-slate-400">Systém **Android** je postavený přímo na jádře Linuxu!</p>
                </div>

                <div class="bg-slate-900 p-5 rounded-xl border border-slate-800 text-center space-y-2 card-hover">
                    <i class="fa-solid fa-gamepad text-3xl text-purple-400 mb-2"></i>
                    <h4 class="font-bold text-slate-200">Herní konzole</h4>
                    <p class="text-xs text-slate-400">Populární handheld **Steam Deck** běží na vysoce vyladěném Linuxu (SteamOS).</p>
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
                    Na Windows musíš hledat webové stránky, stahovat `.exe` soubory a proklikávat instalátory. V Linuxu stačí otevřít terminál a napsat jediný příkaz:
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

        <section id="prikazy" class="space-y-6">
            <div class="flex items-center justify-between">
                <div class="flex items-center space-x-3">
                    <div class="p-2 bg-purple-500/10 rounded-lg text-purple-400 text-xl"><i class="fa-solid fa-code"></i></div>
                    <h2 class="text-2xl font-bold text-slate-100">Rychlý příkazový tahák</h2>
                </div>
                <a href="/piskoviste" class="text-xs font-bold text-sky-400 hover:underline">Vyzkoušet ve skutečném terminálu →</a>
            </div>

            <div class="grid sm:grid-cols-2 md:grid-cols-3 gap-3 font-mono text-xs">
                <div class="bg-slate-900 p-3 rounded-lg border border-slate-800 flex justify-between items-center">
                    <span class="text-amber-300 font-bold">pwd</span>
                    <span class="text-slate-400 text-[11px]">Kde právě jsem?</span>
                </div>
                <div class="bg-slate-900 p-3 rounded-lg border border-slate-800 flex justify-between items-center">
                    <span class="text-amber-300 font-bold">ls</span>
                    <span class="text-slate-400 text-[11px]">Vypiš soubory a složky</span>
                </div>
                <div class="bg-slate-900 p-3 rounded-lg border border-slate-800 flex justify-between items-center">
                    <span class="text-amber-300 font-bold">cd &lt;složka&gt;</span>
                    <span class="text-slate-400 text-[11px]">Otevři složku</span>
                </div>
                <div class="bg-slate-900 p-3 rounded-lg border border-slate-800 flex justify-between items-center">
                    <span class="text-amber-300 font-bold">cat &lt;soubor&gt;</span>
                    <span class="text-slate-400 text-[11px]">Přečti obsah souboru</span>
                </div>
                <div class="bg-slate-900 p-3 rounded-lg border border-slate-800 flex justify-between items-center">
                    <span class="text-amber-300 font-bold">mkdir &lt;název&gt;</span>
                    <span class="text-slate-400 text-[11px]">Vytvoř novou složku</span>
                </div>
                <div class="bg-slate-900 p-3 rounded-lg border border-slate-800 flex justify-between items-center">
                    <span class="text-amber-300 font-bold">clear</span>
                    <span class="text-slate-400 text-[11px]">Vyčisti terminál</span>
                </div>
            </div>
        </section>

    </main>

    <footer class="bg-slate-900 border-t border-slate-800 py-8 px-4 text-center text-xs text-slate-500 space-y-2">
        <p class="font-bold text-slate-400">Linuxhrou.cz – Výuková platforma pro malé i velké průzkumníky</p>
        <p>Vytvořeno s ❤️ pro podporu výuky IT a Open-Source technologií.</p>
    </footer>

</body>
</html>
"""

@app.route("/")
def home():
    """Úvodní vzdělávací portál Linuxhrou.cz"""
    return render_template_string(PORTAL_HTML_TEMPLATE)


if __name__ == "__main__":
    app.run(debug=True, port=5000)
