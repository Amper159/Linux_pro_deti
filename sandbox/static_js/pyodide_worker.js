// Python Lab: Pyodide běží ve Web Workeru, mimo hlavní vlákno stránky.
// Díky tomu nekonečná smyčka v kódu dítěte nezamrzne záložku: hlavní vlákno
// po uplynutí limitu worker ukončí (terminate) a spustí nový.
// Každé spuštění má čistý jmenný prostor, takže nic nezůstává ze starých pokusů.
//
// Chyby v kódu dítěte i neúspěšné kontroly zachytává přímo Python (funkce _spust a _over
// níže), ne Pyodide. Důvod: když je stderr přesměrovaný do bufferu, PythonError z Pyodide
// má prázdnou zprávu a traceback (s interními soubory Pyodide) skončí ve výstupu programu.

const PYODIDE_BASE = "https://cdn.jsdelivr.net/pyodide/v0.26.4/full/";
const MAX_OUTPUT = 20000;   // kolik znaků výstupu se pošle do konzole

importScripts(PYODIDE_BASE + "pyodide.js");

let pyodide = null;
let lastNs = null;        // jmenný prostor posledního spuštění (použije ho kontrola)
let lastStdout = "";      // celý výstup posledního spuštění (kontrola vidí všechno)

const PY_SETUP = `
import sys, io, builtins

def _novy_vystup():
    sys.stdout = io.StringIO()
    sys.stderr = sys.stdout

def _vystup():
    return sys.stdout.getvalue()

def _input_nejde(prompt=""):
    raise RuntimeError("input() tady nejde použít, nemá se koho zeptat. Programy s input() si spusť u sebe, třeba stažené hry.")

builtins.input = _input_nejde

def _radek_v_kodu(tb):
    """Číslo posledního řádku z kódu dítěte (soubor <kod>) v tracebacku."""
    radek = None
    while tb is not None:
        if tb.tb_frame.f_code.co_filename == "<kod>":
            radek = tb.tb_lineno
        tb = tb.tb_next
    return radek

def _spust(zdroj, ns):
    """Spustí kód dítěte. Vrátí None, nebo srozumitelný popis chyby."""
    try:
        exec(compile(zdroj, "<kod>", "exec"), ns)
    except SystemExit:
        return None
    except SyntaxError as e:
        return (f"Řádek {e.lineno}: " if e.lineno else "") + f"{type(e).__name__}: {e.msg}"
    except BaseException as e:
        radek = _radek_v_kodu(e.__traceback__)
        return (f"Řádek {radek}: " if radek else "") + f"{type(e).__name__}: {e}"
    return None

def _over(kod, ns):
    """Spustí kontrolu úkolu. Vrátí None (splněno), nebo text, co dítěti řekne, co je špatně."""
    try:
        exec(compile(kod, "<kontrola>", "exec"), ns)
    except SystemExit:
        return None
    except AssertionError as e:
        return str(e) or "Výsledek ještě neodpovídá zadání."
    except NameError as e:
        return f"Nevidím tvoji proměnnou nebo funkci '{e.name}'. Je v kódu a jmenuje se přesně podle zadání?"
    except BaseException as e:
        radek = _radek_v_kodu(e.__traceback__)
        return f"{type(e).__name__}: {e}" + (f" (v tvém kódu na řádku {radek})" if radek else "")
    return None
`;

async function init() {
    pyodide = await loadPyodide({ indexURL: PYODIDE_BASE });
    pyodide.runPython(PY_SETUP);
    self.postMessage({ type: "ready" });
}

self.onmessage = (e) => {
    const m = e.data;
    if (!pyodide) { self.postMessage({ id: m.id, error: "Python se ještě nenačetl." }); return; }

    if (m.type === "run") {
        if (lastNs) { try { lastNs.destroy(); } catch (err) {} }
        lastNs = pyodide.globals.get("dict")();
        lastNs.set("__name__", "__main__");
        pyodide.globals.get("_novy_vystup")();
        const error = pyodide.globals.get("_spust")(m.code, lastNs) || null;
        lastStdout = pyodide.globals.get("_vystup")();
        let shown = lastStdout;
        if (shown.length > MAX_OUTPUT) shown = shown.slice(0, MAX_OUTPUT) + "\n… (výstup je moc dlouhý, zbytek jsem zkrátil)";
        self.postMessage({ id: m.id, stdout: shown, error: error });

    } else if (m.type === "check") {
        if (!lastNs) { self.postMessage({ id: m.id, ok: false, message: "Nejdřív spusť svůj kód." }); return; }
        lastNs.set("_stdout_capture", lastStdout);
        const problem = pyodide.globals.get("_over")(m.check, lastNs);
        if (problem) self.postMessage({ id: m.id, ok: false, message: problem });
        else self.postMessage({ id: m.id, ok: true });
    }
};

init().catch((err) => self.postMessage({ type: "init-error", message: String(err) }));
