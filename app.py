from flask import Flask, render_template_string, request, jsonify
import shlex

app = Flask(__name__)

# ==============================================================================
# DEFINICE VŠECH ÚROVNÍ (1 - 90)
# ==============================================================================
LEVELS = [
    # ---------- SADA 1: ZÁKLADY LINUXU (1 - 30) ----------
    {"id": 1, "difficulty": "1. Fáze: Začátečník", "cmd_name": "pwd", "title": "1. Kde právě jsem?", "desc": "Zjisti přesnou cestu do složky, ve které stojíš.", "explanation": "Příkaz 'pwd' znamená 'Print Working Directory'. Zobrazí přesnou cestu k aktuální složce.", "hint_type": "exact", "command_hint": "pwd", "expected": "pwd"},
    {"id": 2, "difficulty": "1. Fáze: Začátečník", "cmd_name": "ls", "title": "2. Co je kolem mě?", "desc": "Zobraz seznam všech běžných souborů a složek.", "explanation": "Příkaz 'ls' vypíše všechny složky a soubory v aktuálním adresáři.", "hint_type": "exact", "command_hint": "ls", "expected": "ls"},
    {"id": 3, "difficulty": "1. Fáze: Začátečník", "cmd_name": "ls -a", "title": "3. Odhal skrytá tajemství", "desc": "Vypiš všechny soubory včetně těch skrytých.", "explanation": "Přepínač '-a' zobrazí i skryté soubory začínající tečkou.", "hint_type": "exact", "command_hint": "ls -a", "expected": "ls -a"},
    {"id": 4, "difficulty": "1. Fáze: Začátečník", "cmd_name": "cat", "title": "4. Proč používat Linux?", "desc": "Přečti si soubor 'proc_linux.txt'.", "explanation": "Příkaz 'cat' slouží k přečtení obsahu textového souboru přímo v terminálu.", "hint_type": "exact", "command_hint": "cat proc_linux.txt", "expected": "cat proc_linux.txt"},
    {"id": 5, "difficulty": "1. Fáze: Začátečník", "cmd_name": "cd", "title": "5. Vstup do sekce Hrání", "desc": "Přesuň se do složky 'gaming'.", "explanation": "Příkaz 'cd' slouží ke změně aktuální složky.", "hint_type": "exact", "command_hint": "cd gaming", "expected": "cd gaming"},
    {"id": 6, "difficulty": "1. Fáze: Začátečník", "cmd_name": "grep", "title": "6. Hry a Steam na Linuxu", "desc": "Vyhledej slovo 'Steam' v souboru 'hry_na_linuxu.txt'.", "explanation": "Příkaz 'grep' vyhledává text uvnitř souborů.", "hint_type": "exact", "command_hint": "grep Steam hry_na_linuxu.txt", "expected": "grep Steam hry_na_linuxu.txt"},
    {"id": 7, "difficulty": "1. Fáze: Začátečník", "cmd_name": "mkdir", "title": "7. Vytvoř složku pro hry", "desc": "Vytvoř novou složku 'moje_hry'.", "explanation": "Příkaz 'mkdir' vytvoří novou složku.", "hint_type": "exact", "command_hint": "mkdir moje_hry", "expected": "mkdir moje_hry"},
    {"id": 8, "difficulty": "1. Fáze: Začátečník", "cmd_name": "touch", "title": "8. Založ seznam přání", "desc": "Vytvoř nový prázdný soubor 'wishlist.txt'.", "explanation": "Příkaz 'touch' založí nový prázdný soubor.", "hint_type": "exact", "command_hint": "touch wishlist.txt", "expected": "touch wishlist.txt"},
    {"id": 9, "difficulty": "1. Fáze: Začátečník", "cmd_name": "history", "title": "9. Historie příkazů", "desc": "Zobraz seznam všech příkazů, které jsi dosud napsal.", "explanation": "Příkaz 'history' ukáže historii zadaných příkazů.", "hint_type": "exact", "command_hint": "history", "expected": "history"},
    {"id": 10, "difficulty": "1. Fáze: Začátečník", "cmd_name": "clear", "title": "10. Vyčisti terminál", "desc": "Smaž zaplněné řádky z obrazovky.", "explanation": "Příkaz 'clear' vyčistí okno terminálu.", "hint_type": "exact", "command_hint": "clear", "expected": "clear"},

    {"id": 11, "difficulty": "2. Fáze: Pokročilý", "cmd_name": "cd", "title": "11. Návrat domů", "desc": "Vrať se zpět do domovského adresáře (~).", "explanation": "Zadej 'cd' nebo 'cd ~'.", "hint_type": "cmd_only", "command_hint": "cd", "expected": "cd"},
    {"id": 12, "difficulty": "2. Fáze: Pokročilý", "cmd_name": "cd", "title": "12. Jak nainstalovat Linux?", "desc": "Vejdi do složky 'instalace'.", "explanation": "Přesuň se do složky instalace.", "hint_type": "cmd_only", "command_hint": "cd instalace", "expected": "cd instalace"},
    {"id": 13, "difficulty": "2. Fáze: Pokročilý", "cmd_name": "cat", "title": "13. Návod k instalaci", "desc": "Přečti si soubor 'jak_instalovat.txt'.", "explanation": "Použij cat.", "hint_type": "cmd_only", "command_hint": "cat jak_instalovat.txt", "expected": "cat jak_instalovat.txt"},
    {"id": 14, "difficulty": "2. Fáze: Pokročilý", "cmd_name": "grep", "title": "14. Co je to Dual-boot?", "desc": "Vyhledej slovo 'Dual-boot' v 'jak_instalovat.txt'.", "explanation": "Použij grep.", "hint_type": "cmd_only", "command_hint": "grep Dual-boot jak_instalovat.txt", "expected": "grep Dual-boot jak_instalovat.txt"},
    {"id": 15, "difficulty": "2. Fáze: Pokročilý", "cmd_name": "cd", "title": "15. Vrať se do domovské složky", "desc": "Skoč zpět do domovské složky (~).", "explanation": "Vrať se domů.", "hint_type": "cmd_only", "command_hint": "cd", "expected": "cd"},
    {"id": 16, "difficulty": "2. Fáze: Pokročilý", "cmd_name": "mkdir", "title": "16. Složka pro zprávy", "desc": "Založ novou složku 'zpravy'.", "explanation": "Použij mkdir.", "hint_type": "cmd_only", "command_hint": "mkdir zpravy", "expected": "mkdir zpravy"},
    {"id": 17, "difficulty": "2. Fáze: Pokročilý", "cmd_name": "touch", "title": "17. Soubor pro poznámky", "desc": "Vytvoř soubor 'poznamky.txt'.", "explanation": "Použij touch.", "hint_type": "cmd_only", "command_hint": "touch poznamky.txt", "expected": "touch poznamky.txt"},
    {"id": 18, "difficulty": "2. Fáze: Pokročilý", "cmd_name": "ls -a", "title": "18. Tajné soubory stanice", "desc": "Zobraz skryté soubory v domovské složce.", "explanation": "Použij ls -a.", "hint_type": "cmd_only", "command_hint": "ls -a", "expected": "ls -a"},
    {"id": 19, "difficulty": "2. Fáze: Pokročilý", "cmd_name": "cat", "title": "19. Pozdrav od mopsíka", "desc": "Přečti skrytý soubor '.mopsik.txt'.", "explanation": "Použij cat.", "hint_type": "cmd_only", "command_hint": "cat .mopsik.txt", "expected": "cat .mopsik.txt"},
    {"id": 20, "difficulty": "2. Fáze: Pokročilý", "cmd_name": "clear", "title": "20. Úklid obrazovky", "desc": "Smaž staré výstupy v terminálu.", "explanation": "Použij clear.", "hint_type": "cmd_only", "command_hint": "clear", "expected": "clear"},

    {"id": 21, "difficulty": "3. Fáze: Mistr", "cmd_name": "pwd", "title": "21. Kde stojíš?", "desc": "Ověř cestu aktuální složky.", "explanation": "Pokud nevěříš, napiš 'help'.", "hint_type": "none", "command_hint": "Nevíš? Napiš 'help'.", "expected": "pwd"},
    {"id": 22, "difficulty": "3. Fáze: Mistr", "cmd_name": "cd", "title": "22. Vstup do tajné laboratoře", "desc": "Přesuň se do složky 'tajna_laborator'.", "explanation": "Pokud nevěříš, napiš 'help'.", "hint_type": "none", "command_hint": "Nevíš? Napiš 'help'.", "expected": "cd tajna_laborator"},
    {"id": 23, "difficulty": "3. Fáze: Mistr", "cmd_name": "cat", "title": "23. Prohlédni databázi chyb", "desc": "Přečti obsah 'databaze_chyb.txt'.", "explanation": "Pokud nevěříš, napiš 'help'.", "hint_type": "none", "command_hint": "Nevíš? Napiš 'help'.", "expected": "cat databaze_chyb.txt"},
    {"id": 24, "difficulty": "3. Fáze: Mistr", "cmd_name": "cd", "title": "24. Návrat domů", "desc": "Vrať se zpět do domovské složky.", "explanation": "Pokud nevěříš, napiš 'help'.", "hint_type": "none", "command_hint": "Nevíš? Napiš 'help'.", "expected": "cd"},
    {"id": 25, "difficulty": "3. Fáze: Mistr", "cmd_name": "chmod", "title": "25. Povolit spuštění skriptu", "desc": "Přidej spouštěcí právo (+x) souboru 'spustit_laser.sh'.", "explanation": "Pokud nevěříš, napiš 'help'.", "hint_type": "none", "command_hint": "Nevíš? Napiš 'help'.", "expected": "chmod +x spustit_laser.sh"},
    {"id": 26, "difficulty": "3. Fáze: Mistr", "cmd_name": "spustit_laser.sh", "title": "26. Aktivace laserů", "desc": "Spusť záchranný skript './spustit_laser.sh'.", "explanation": "Pokud nevěříš, napiš 'help'.", "hint_type": "none", "command_hint": "Nevíš? Napiš 'help'.", "expected": "./spustit_laser.sh"},
    {"id": 27, "difficulty": "3. Fáze: Mistr", "cmd_name": "rm", "title": "27. Úklid testovacího souboru", "desc": "Smaž soubor 'wishlist.txt'.", "explanation": "Pokud nevěříš, napiš 'help'.", "hint_type": "none", "command_hint": "Nevíš? Napiš 'help'.", "expected": "rm wishlist.txt"},
    {"id": 28, "difficulty": "3. Fáze: Mistr", "cmd_name": "whoami", "title": "28. Identita v systému", "desc": "Zjisti své uživatelské jméno.", "explanation": "Pokud nevěříš, napiš 'help'.", "hint_type": "none", "command_hint": "Nevíš? Napiš 'help'.", "expected": "whoami"},
    {"id": 29, "difficulty": "3. Fáze: Mistr", "cmd_name": "history", "title": "29. Zkontrolovat všechny kroky", "desc": "Vypiš historii zadaných příkazů.", "explanation": "Pokud nevěříš, napiš 'help'.", "hint_type": "none", "command_hint": "Nevíš? Napiš 'help'.", "expected": "history"},
    {"id": 30, "difficulty": "3. Fáze: Mistr", "cmd_name": "clear", "title": "30. Finální vyčištění Sady 1", "desc": "Vyčisti terminál a dokonči Sadu 1!", "explanation": "Pokud nevěříš, napiš 'help'.", "hint_type": "none", "command_hint": "Nevíš? Napiš 'help'.", "expected": "clear"},

    # ---------- SADA 2: SOUBORY A SÍTĚ (31 - 60) ----------
    {"id": 31, "difficulty": "Sada 2: Správce", "cmd_name": "cp", "title": "31. Záloha deníku", "desc": "Zkopíruj 'denik_kapitana.txt' do nového souboru 'denik_zaloha.txt'.", "explanation": "Příkaz 'cp <zdroj> <cíl>' vytvoří kopii souboru.", "hint_type": "exact", "command_hint": "cp denik_kapitana.txt denik_zaloha.txt", "expected": "cp denik_kapitana.txt denik_zaloha.txt"},
    {"id": 32, "difficulty": "Sada 2: Správce", "cmd_name": "mv", "title": "32. Přesun souboru", "desc": "Přesouvej soubor 'denik_zaloha.txt' do složky 'zpravy'.", "explanation": "Příkaz 'mv <soubor> <složka>' přesune soubor do zadané složky.", "hint_type": "exact", "command_hint": "mv denik_zaloha.txt zpravy", "expected": "mv denik_zaloha.txt zpravy"},
    {"id": 33, "difficulty": "Sada 2: Správce", "cmd_name": "mv", "title": "33. Přejmenování souboru", "desc": "Přejmenuj 'poznamky.txt' na 'stare_poznamky.txt'.", "explanation": "Příkaz 'mv' slouží i k přejmenování souboru.", "hint_type": "exact", "command_hint": "mv poznamky.txt stare_poznamky.txt", "expected": "mv poznamky.txt stare_poznamky.txt"},
    {"id": 34, "difficulty": "Sada 2: Správce", "cmd_name": "find", "title": "34. Hledání v systému", "desc": "Najdi soubor s názvem 'databaze_chyb.txt'.", "explanation": "Příkaz 'find . -name <název>' vyhledá soubor.", "hint_type": "exact", "command_hint": "find . -name databaze_chyb.txt", "expected": "find . -name databaze_chyb.txt"},
    {"id": 35, "difficulty": "Sada 2: Správce", "cmd_name": "ping", "title": "35. Test připojení základny", "desc": "Ověř síťové spojení příkazem 'ping 127.0.0.1'.", "explanation": "Příkaz 'ping' testuje dostupnost v síti.", "hint_type": "exact", "command_hint": "ping 127.0.0.1", "expected": "ping 127.0.0.1"},
    {"id": 36, "difficulty": "Sada 2: Správce", "cmd_name": "echo", "title": "36. Vypiš zprávu", "desc": "Vypiš do terminálu text 'Ahoj Vesmire'.", "explanation": "Příkaz 'echo' vytiskne text na obrazovku.", "hint_type": "exact", "command_hint": "echo Ahoj Vesmire", "expected": "echo Ahoj Vesmire"},
    {"id": 37, "difficulty": "Sada 2: Správce", "cmd_name": "nano", "title": "37. Textový editor", "desc": "Otevři textový editor nano pro soubor 'novy_kod.txt'.", "explanation": "Nano je jednoduchý textový editor.", "hint_type": "exact", "command_hint": "nano novy_kod.txt", "expected": "nano novy_kod.txt"},
    {"id": 38, "difficulty": "Sada 2: Správce", "cmd_name": "wc", "title": "38. Počítadlo řádků", "desc": "Spočítej řádky v souboru 'proc_linux.txt' pomocí 'wc -l proc_linux.txt'.", "explanation": "Příkaz 'wc -l' spočítá počet řádků.", "hint_type": "exact", "command_hint": "wc -l proc_linux.txt", "expected": "wc -l proc_linux.txt"},
    {"id": 39, "difficulty": "Sada 2: Správce", "cmd_name": "head", "title": "39. První řádky", "desc": "Zobraz pouze první řádky souboru 'proc_linux.txt'.", "explanation": "Příkaz 'head' zobrazí začátek souboru.", "hint_type": "exact", "command_hint": "head proc_linux.txt", "expected": "head proc_linux.txt"},
    {"id": 40, "difficulty": "Sada 2: Správce", "cmd_name": "tail", "title": "40. Poslední řádky", "desc": "Zobraz konec souboru 'proc_linux.txt' pomocí 'tail'.", "explanation": "Příkaz 'tail' vypíše konec souboru.", "hint_type": "exact", "command_hint": "tail proc_linux.txt", "expected": "tail proc_linux.txt"},
    {"id": 41, "difficulty": "Sada 2: Správce", "cmd_name": "cp", "title": "41. Kopie složky", "desc": "Zkopíruj složku 'zpravy' do 'zpravy_zaloha' (cp -r).", "explanation": "Přepínač '-r' zkopíruje i obsah složky.", "hint_type": "cmd_only", "command_hint": "cp -r zpravy zpravy_zaloha", "expected": "cp -r zpravy zpravy_zaloha"},
    {"id": 42, "difficulty": "Sada 2: Správce", "cmd_name": "rmdir", "title": "42. Odstranění prázdné složky", "desc": "Smaž prázdnou složku 'moje_hry'.", "explanation": "Příkaz 'rmdir' maže prázdné složky.", "hint_type": "cmd_only", "command_hint": "rmdir moje_hry", "expected": "rmdir moje_hry"},
    {"id": 43, "difficulty": "Sada 2: Správce", "cmd_name": "df", "title": "43. Místo na disku", "desc": "Zjisti zaplnění disku příkazem 'df -h'.", "explanation": "Ukáže volné místo na disku.", "hint_type": "cmd_only", "command_hint": "df -h", "expected": "df -h"},
    {"id": 44, "difficulty": "Sada 2: Správce", "cmd_name": "uptime", "title": "44. Doba běhu systému", "desc": "Zjisti, jak dlouho systém běží.", "explanation": "Ukáže čas od zapnutí.", "hint_type": "cmd_only", "command_hint": "uptime", "expected": "uptime"},
    {"id": 45, "difficulty": "Sada 2: Správce", "cmd_name": "date", "title": "45. Aktuální čas stanice", "desc": "Vypiš přesné datum a čas.", "explanation": "Zobrazí časové razítko.", "hint_type": "cmd_only", "command_hint": "date", "expected": "date"},
    {"id": 46, "difficulty": "Sada 2: Správce", "cmd_name": "hostname", "title": "46. Jméno stanice", "desc": "Zjisti název počítače v síti.", "explanation": "Vypíše síťové jméno.", "hint_type": "cmd_only", "command_hint": "hostname", "expected": "hostname"},
    {"id": 47, "difficulty": "Sada 2: Správce", "cmd_name": "env", "title": "47. Proměnné prostředí", "desc": "Zobraz systémové proměnné.", "explanation": "Zobrazí proměnné prostředí.", "hint_type": "cmd_only", "command_hint": "env", "expected": "env"},
    {"id": 48, "difficulty": "Sada 2: Správce", "cmd_name": "uname", "title": "48. Verze Linuxového jádra", "desc": "Zjisti verzi systému pomocí 'uname -a'.", "explanation": "Vypíše informace o jádru.", "hint_type": "cmd_only", "command_hint": "uname -a", "expected": "uname -a"},
    {"id": 49, "difficulty": "Sada 2: Správce", "cmd_name": "history", "title": "49. Kontrola kroků Sady 2", "desc": "Zobraz historii příkazů.", "explanation": "Použij history.", "hint_type": "cmd_only", "command_hint": "history", "expected": "history"},
    {"id": 50, "difficulty": "Sada 2: Správce", "cmd_name": "clear", "title": "50. Úklid plochy Sady 2", "desc": "Vyčisti plochu terminálu.", "explanation": "Použij clear.", "hint_type": "cmd_only", "command_hint": "clear", "expected": "clear"},
    {"id": 51, "difficulty": "Sada 2: Experty", "cmd_name": "find", "title": "51. Hledání podle koncovky", "desc": "Najdi všechny .txt soubory.", "explanation": "Nápověda v help.", "hint_type": "none", "command_hint": "Nevíš? Napiš 'help'.", "expected": "find"},
    {"id": 52, "difficulty": "Sada 2: Experty", "cmd_name": "ping", "title": "52. Test spojení na Bránu", "desc": "Ověř ping na 'gateway.local'.", "explanation": "Nápověda v help.", "hint_type": "none", "command_hint": "Nevíš? Napiš 'help'.", "expected": "ping"},
    {"id": 53, "difficulty": "Sada 2: Experty", "cmd_name": "cp", "title": "53. Rychlá kopie databáze", "desc": "Zkopíruj 'databaze_chyb.txt' do domovské složky.", "explanation": "Nápověda v help.", "hint_type": "none", "command_hint": "Nevíš? Napiš 'help'.", "expected": "cp"},
    {"id": 54, "difficulty": "Sada 2: Experty", "cmd_name": "mv", "title": "54. Přesun skriptu", "desc": "Přesouvej 'spustit_laser.sh' do složky 'zpravy'.", "explanation": "Nápověda v help.", "hint_type": "none", "command_hint": "Nevíš? Napiš 'help'.", "expected": "mv"},
    {"id": 55, "difficulty": "Sada 2: Experty", "cmd_name": "echo", "title": "55. Zápis do souboru", "desc": "Vypiš text 'Test' do terminálu.", "explanation": "Nápověda v help.", "hint_type": "none", "command_hint": "Nevíš? Napiš 'help'.", "expected": "echo"},
    {"id": 56, "difficulty": "Sada 2: Experty", "cmd_name": "head", "title": "56. Kontrola prvního řádku", "desc": "Přečti začátek souboru 'denik_kapitana.txt'.", "explanation": "Nápověda v help.", "hint_type": "none", "command_hint": "Nevíš? Napiš 'help'.", "expected": "head"},
    {"id": 57, "difficulty": "Sada 2: Experty", "cmd_name": "tail", "title": "57. Kontrola konce deníku", "desc": "Přečti konec souboru 'denik_kapitana.txt'.", "explanation": "Nápověda v help.", "hint_type": "none", "command_hint": "Nevíš? Napiš 'help'.", "expected": "tail"},
    {"id": 58, "difficulty": "Sada 2: Experty", "cmd_name": "df", "title": "58. Kontrola kapacity", "desc": "Zkontroluj disk přes df -h.", "explanation": "Nápověda v help.", "hint_type": "none", "command_hint": "Nevíš? Napiš 'help'.", "expected": "df"},
    {"id": 59, "difficulty": "Sada 2: Experty", "cmd_name": "date", "title": "59. Zaznamenej čas", "desc": "Vypiš aktuální čas stanice.", "explanation": "Nápověda v help.", "hint_type": "none", "command_hint": "Nevíš? Napiš 'help'.", "expected": "date"},
    {"id": 60, "difficulty": "Sada 2: Experty", "cmd_name": "clear", "title": "60. Dokončení Sady 2", "desc": "Vyčisti terminál a dokonči Sadu 2!", "explanation": "Nápověda v help.", "hint_type": "none", "command_hint": "Nevíš? Napiš 'help'.", "expected": "clear"},

    # ---------- SADA 3: MISTR SYSTÉMU (61 - 90) ----------
    {"id": 61, "difficulty": "Sada 3: Architekt", "cmd_name": "ps", "title": "61. Běžící procesy", "desc": "Zobraz seznam běžících procesů příkazem 'ps'.", "explanation": "Vypiš aktuálně spuštěné programy.", "hint_type": "exact", "command_hint": "ps", "expected": "ps"},
    {"id": 62, "difficulty": "Sada 3: Architekt", "cmd_name": "top", "title": "62. Správce úloh", "desc": "Spusť monitor vytížení systému 'top'.", "explanation": "Zobrazí vytížení v reálném čase.", "hint_type": "exact", "command_hint": "top", "expected": "top"},
    {"id": 63, "difficulty": "Sada 3: Architekt", "cmd_name": "free", "title": "63. Stav paměti RAM", "desc": "Zkontroluj volnou operační paměť 'free -m'.", "explanation": "Ukáže využití RAM v megabajtech.", "hint_type": "exact", "command_hint": "free -m", "expected": "free -m"},
    {"id": 64, "difficulty": "Sada 3: Architekt", "cmd_name": "tar", "title": "64. Archivace složky", "desc": "Vytvoř archiv 'zaloha.tar' ze složky 'zpravy'.", "explanation": "Zabalí soubory do archivu.", "hint_type": "exact", "command_hint": "tar -cvf zaloha.tar zpravy", "expected": "tar -cvf zaloha.tar zpravy"},
    {"id": 65, "difficulty": "Sada 3: Architekt", "cmd_name": "gzip", "title": "65. Komprese archivu", "desc": "Zkomprimuj archiv 'zaloha.tar' pomocí 'gzip zaloha.tar'.", "explanation": "Zmenší velikost souboru.", "hint_type": "exact", "command_hint": "gzip zaloha.tar", "expected": "gzip zaloha.tar"},
    {"id": 66, "difficulty": "Sada 3: Architekt", "cmd_name": "alias", "title": "66. Vlastní zkratka", "desc": "Vytvoř zkratku 'alias c=clear'.", "explanation": "Vytvoří vlastností zkratku.", "hint_type": "exact", "command_hint": "alias c=clear", "expected": "alias c=clear"},
    {"id": 67, "difficulty": "Sada 3: Architekt", "cmd_name": "curl", "title": "67. Stažení dat ze sítě", "desc": "Stáhni testovací stranu 'curl https://api.linux.cz'.", "explanation": "Přenáší data z webu.", "hint_type": "exact", "command_hint": "curl https://api.linux.cz", "expected": "curl https://api.linux.cz"},
    {"id": 68, "difficulty": "Sada 3: Architekt", "cmd_name": "kill", "title": "68. Ukončení škodlivého procesu", "desc": "Ukonči zaseknutý proces PID 9999 ('kill 9999').", "explanation": "Ukončí proces podle PID.", "hint_type": "exact", "command_hint": "kill 9999", "expected": "kill 9999"},
    {"id": 69, "difficulty": "Sada 3: Architekt", "cmd_name": "htop", "title": "69. Pokročilý monitor", "desc": "Spusť grafický monitor procesů 'htop'.", "explanation": "Barevný monitor procesů.", "hint_type": "exact", "command_hint": "htop", "expected": "htop"},
    {"id": 70, "difficulty": "Sada 3: Architekt", "cmd_name": "clear", "title": "70. Úklid plochy Sady 3", "desc": "Vyčisti obrazovku.", "explanation": "Použij clear.", "hint_type": "exact", "command_hint": "clear", "expected": "clear"},
    {"id": 71, "difficulty": "Sada 3: Inženýr", "cmd_name": "ps", "title": "71. Kontrola procesů uživatele", "desc": "Zobraz spuštěné procesy.", "explanation": "Použij ps.", "hint_type": "cmd_only", "command_hint": "ps", "expected": "ps"},
    {"id": 72, "difficulty": "Sada 3: Inženýr", "cmd_name": "free", "title": "72. Rychlá kontrola RAM", "desc": "Ověř volnou RAM.", "explanation": "Použij free.", "hint_type": "cmd_only", "command_hint": "free", "expected": "free"},
    {"id": 73, "difficulty": "Sada 3: Inženýr", "cmd_name": "alias", "title": "73. Vytvoř zkratku pro ls", "desc": "Vytvoř alias 'alias l=ls'.", "explanation": "Použij alias.", "hint_type": "cmd_only", "command_hint": "alias l=ls", "expected": "alias l=ls"},
    {"id": 74, "difficulty": "Sada 3: Inženýr", "cmd_name": "curl", "title": "74. Test síťové API", "desc": "Stáhni data přes curl.", "explanation": "Použij curl.", "hint_type": "cmd_only", "command_hint": "curl", "expected": "curl"},
    {"id": 75, "difficulty": "Sada 3: Inženýr", "cmd_name": "tar", "title": "75. Balíček instalace", "desc": "Vytvoř archiv 'instalace.tar' ze složky 'instalace'.", "explanation": "Použij tar.", "hint_type": "cmd_only", "command_hint": "tar", "expected": "tar"},
    {"id": 76, "difficulty": "Sada 3: Inženýr", "cmd_name": "kill", "title": "76. Zastavení viru", "desc": "Ukonči proces PID 1234.", "explanation": "Použij kill.", "hint_type": "cmd_only", "command_hint": "kill", "expected": "kill"},
    {"id": 77, "difficulty": "Sada 3: Inženýr", "cmd_name": "history", "title": "77. Přehled zadaných kroků", "desc": "Vypiš historii.", "explanation": "Použij history.", "hint_type": "cmd_only", "command_hint": "history", "expected": "history"},
    {"id": 78, "difficulty": "Sada 3: Inženýr", "cmd_name": "uptime", "title": "78. Kontrola stability serveru", "desc": "Ověř čas běhu serveru.", "explanation": "Použij uptime.", "hint_type": "cmd_only", "command_hint": "uptime", "expected": "uptime"},
    {"id": 79, "difficulty": "Sada 3: Inženýr", "cmd_name": "whoami", "title": "79. Ověření admin práv", "desc": "Vypiš své jméno.", "explanation": "Použij whoami.", "hint_type": "cmd_only", "command_hint": "whoami", "expected": "whoami"},
    {"id": 80, "difficulty": "Sada 3: Inženýr", "cmd_name": "clear", "title": "80. Finální příprava na finále", "desc": "Vyčisti terminál.", "explanation": "Použij clear.", "hint_type": "cmd_only", "command_hint": "clear", "expected": "clear"},
    {"id": 81, "difficulty": "Sada 3: Legenda", "cmd_name": "top", "title": "81. Monitor záteže reakčních motorů", "desc": "Zobraz top.", "explanation": "Nápověda v help.", "hint_type": "none", "command_hint": "Nevíš? Napiš 'help'.", "expected": "top"},
    {"id": 82, "difficulty": "Sada 3: Legenda", "cmd_name": "free", "title": "82. Test vytížení paměti", "desc": "Ověř stav paměti RAM.", "explanation": "Nápověda v help.", "hint_type": "none", "command_hint": "Nevíš? Napiš 'help'.", "expected": "free"},
    {"id": 83, "difficulty": "Sada 3: Legenda", "cmd_name": "tar", "title": "83. Archivace tajné laboratoře", "desc": "Zabal složku 'tajna_laborator'.", "explanation": "Nápověda v help.", "hint_type": "none", "command_hint": "Nevíš? Napiš 'help'.", "expected": "tar"},
    {"id": 84, "difficulty": "Sada 3: Legenda", "cmd_name": "gzip", "title": "84. Komprese kompletních dat", "desc": "Zkomprimuj libovolný soubor přes gzip.", "explanation": "Nápověda v help.", "hint_type": "none", "command_hint": "Nevíš? Napiš 'help'.", "expected": "gzip"},
    {"id": 85, "difficulty": "Sada 3: Legenda", "cmd_name": "kill", "title": "85. Nouzové vypnutí reaktoru", "desc": "Ukonči chybový proces 7777.", "explanation": "Nápověda v help.", "hint_type": "none", "command_hint": "Nevíš? Napiš 'help'.", "expected": "kill"},
    {"id": 86, "difficulty": "Sada 3: Legenda", "cmd_name": "curl", "title": "86. Vyslání záchranného signálu", "desc": "Použij curl pro odeslání dat.", "explanation": "Nápověda v help.", "hint_type": "none", "command_hint": "Nevíš? Napiš 'help'.", "expected": "curl"},
    {"id": 87, "difficulty": "Sada 3: Legenda", "cmd_name": "chmod", "title": "87. Odblokování všech systémů", "desc": "Přidej +x skriptu 'spustit_laser.sh'.", "explanation": "Nápověda v help.", "hint_type": "none", "command_hint": "Nevíš? Napiš 'help'.", "expected": "chmod"},
    {"id": 88, "difficulty": "Sada 3: Legenda", "cmd_name": "spustit_laser.sh", "title": "88. Finální aktivace štítů", "desc": "Spusť záchranný skript './spustit_laser.sh'.", "explanation": "Nápověda v help.", "hint_type": "none", "command_hint": "Nevíš? Napiš 'help'.", "expected": "spustit_laser.sh"},
    {"id": 89, "difficulty": "Sada 3: Legenda", "cmd_name": "history", "title": "89. Závěrečná kontrola protokolu", "desc": "Vypiš kompletní historii příkazů.", "explanation": "Nápověda v help.", "hint_type": "none", "command_hint": "Nevíš? Napiš 'help'.", "expected": "history"},
    {"id": 90, "difficulty": "Sada 3: Legenda", "cmd_name": "clear", "title": "90. Absolutní vítězství!", "desc": "Vyčisti terminál a staň se Absolutním Mistrem Linuxu!", "explanation": "Nápověda v help.", "hint_type": "none", "command_hint": "Nevíš? Napiš 'help'.", "expected": "clear"}
]

file_system = {
    "current_path": "/home/hrac",
    "history": [],
    "tree": {
        "/home/hrac": {
            "dirs": ["gaming", "instalace", "tajna_laborator", "zpravy"],
            "files": {
                "proc_linux.txt": "PROČ POUŽÍVAT LINUX?\n1. ZDARMA a Open-Source.\n2. BEZPEČNÝ: Neobsahuje viry.\n3. RYCHLÝ: Běží skvěle všude.\n4. TERMINÁL: Plná kontrola!",
                "denik_kapitana.txt": "Den 12: Kód k hlavní bráně je schovaný v tajné laboratoři!",
                ".tajny_kod.txt": "KLÍČ K REAKTORU: 9988-SUPER-TUX",
                ".mopsik.txt": "Haf! Já jsem skrytý vesmírný mopsík 🐶.",
                "spustit_laser.sh": "echo '💥 PIU PIU! Laserový kanón je připraven k obraně základny!'",
                "poznamky.txt": "Dnes dokončit výcvik v terminálu!"
            },
            "perms": {"spustit_laser.sh": "rw-r--r--"}
        },
        "/home/hrac/gaming": {
            "dirs": [],
            "files": {
                "hry_na_linuxu.txt": "DÁ SÍ NA LINUXU HRÁT HRY?\nANO! Díky službě Steam a nástroji Proton.\nSteam Deck běží právě na Linuxu!",
                "wishlist.txt": ""
            },
            "perms": {}
        },
        "/home/hrac/instalace": {
            "dirs": [],
            "files": {
                "jak_instalovat.txt": "JAK NAINSTALOVAT LINUX:\n1. Stáhni ISO a nahraj na USB.\n2. Vyzkoušej bez instalace.\n3. Dual-boot: Nainstaluj vedle Windows!"
            },
            "perms": {}
        },
        "/home/hrac/tajna_laborator": {
            "dirs": [],
            "files": {
                "databaze_chyb.txt": "CHYBA_01: Kobliha v motoru.\nSUPER_HESLO: Kolem-Jdouci-Tucnak"
            },
            "perms": {}
        },
        "/home/hrac/zpravy": {
            "dirs": [],
            "files": {},
            "perms": {}
        }
    }
}

# ------------------------------------------------------------------------------
# 1. HTML ŠABLONA PRO VZDĚLÁVACÍ PORTÁL (Linuxhrou.cz)
# ------------------------------------------------------------------------------
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
                    <a href="/hra" class="bg-emerald-500 hover:bg-emerald-400 text-slate-950 font-extrabold px-5 py-2.5 rounded-xl border-b-4 border-emerald-700 active:translate-y-0.5 transition flex items-center space-x-2">
                        <i class="fa-solid fa-gamepad text-lg"></i>
                        <span>SPUSTIT HRU</span>
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
                <a href="/hra" class="bg-amber-400 hover:bg-amber-300 text-slate-950 font-black px-8 py-4 rounded-2xl border-b-4 border-amber-600 active:translate-y-1 transition text-lg flex items-center space-x-3 shadow-lg shadow-amber-400/10">
                    <i class="fa-solid fa-rocket"></i>
                    <span>Vstoupit do Výcvikového Tábora (90 Úrovní)</span>
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
                <a href="/hra" class="text-xs font-bold text-sky-400 hover:underline">Vyzkoušet v simulátoru →</a>
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

# ------------------------------------------------------------------------------
# 2. HTML ŠABLONA PRO SIMULÁTOR / HRU
# ------------------------------------------------------------------------------
GAME_HTML_TEMPLATE = """<!DOCTYPE html>
<html lang="cs">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Mise: Linuxový Průzkumník | Linuxhrou.cz</title>
    <script src="https://cdn.tailwindcss.com"></script>
    <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.0/css/all.min.css">
    <link rel="preconnect" href="https://fonts.googleapis.com">
    <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
    <link href="https://fonts.googleapis.com/css2?family=Fira+Code:wght@400;600;700&family=Quicksand:wght@500;600;700&display=swap&subset=latin-ext" rel="stylesheet">
    <style>
        body {
            font-family: 'Quicksand', sans-serif;
            background-color: #0d1b2a;
            background-image: 
                radial-gradient(#1b263b 2px, transparent 2px),
                radial-gradient(#1b263b 2px, #0d1b2a 2px);
            background-size: 40px 40px;
            background-position: 0 0, 20px 20px;
        }
        .font-mono { font-family: 'Fira Code', monospace; }
        .lego-card { border: 3px solid #38bdf8; box-shadow: 0 5px 0 #0284c7; }
        .lego-card-yellow { border: 3px solid #facc15; box-shadow: 0 5px 0 #ca8a04; }
        .lego-card-green { border: 3px solid #4ade80; box-shadow: 0 5px 0 #16a34a; }
        .custom-scrollbar::-webkit-scrollbar { width: 6px; }
        .custom-scrollbar::-webkit-scrollbar-track { background: #0f172a; border-radius: 6px; }
        .custom-scrollbar::-webkit-scrollbar-thumb { background: #334155; border-radius: 6px; border: 2px solid #0f172a; }
    </style>
</head>
<body class="h-screen w-screen p-3 flex flex-col justify-between overflow-hidden text-slate-100 select-none">

    <!-- MODÁLNÍ OKNO PRO PŘIHLÁŠENÍ HRÁČE -->
    <div id="login-modal" class="fixed inset-0 bg-slate-950/80 backdrop-blur-sm z-50 flex items-center justify-center p-4">
        <div class="bg-slate-800 border-4 border-amber-400 rounded-2xl p-6 w-full max-w-md shadow-2xl lego-card-yellow text-center space-y-4">
            <div class="w-16 h-16 bg-gradient-to-b from-sky-400 to-indigo-600 rounded-full mx-auto flex items-center justify-center border-4 border-slate-700 shadow-lg">
                <i class="fa-solid fa-user-astronaut text-3xl text-sky-300"></i>
            </div>
            <div>
                <h2 class="text-2xl font-bold text-amber-300 uppercase">Kdo jde hrát?</h2>
                <p class="text-xs text-slate-300 font-medium mt-1">Zadej své jméno pro načtení tvého pokroku!</p>
            </div>
            <input type="text" id="player-name-input" class="w-full bg-slate-900 border-2 border-sky-400 rounded-xl p-3 text-center text-slate-100 font-bold placeholder-slate-500 focus:outline-none focus:border-emerald-400 text-lg" placeholder="Napiš své jméno..." onkeydown="if(event.key==='Enter') loginPlayer()">
            <button onclick="loginPlayer()" class="w-full bg-emerald-500 hover:bg-emerald-400 text-slate-950 font-bold py-3 rounded-xl border-b-4 border-emerald-700 active:translate-y-1 transition text-base uppercase tracking-wider">
                🚀 Vstoupit do hry
            </button>
        </div>
    </div>

    <!-- HLAVIČKA S TLAČÍTKEM ZPĚT -->
    <header class="bg-gradient-to-r from-amber-500 via-amber-400 to-yellow-500 rounded-2xl p-2.5 px-6 flex justify-between items-center lego-card-yellow text-slate-900 mb-2 shrink-0">
        <div class="flex items-center space-x-3">
            <a href="/" class="bg-slate-900 hover:bg-slate-800 text-yellow-400 px-3 py-1.5 rounded-xl font-bold text-xs flex items-center space-x-1 border-2 border-yellow-300 transition" title="Zpět na portál">
                <i class="fa-solid fa-arrow-left"></i>
                <span>Portál</span>
            </a>
            <div>
                <h1 class="text-xl font-bold tracking-wide uppercase drop-shadow-sm leading-none">MISE: LINUXOVÝ PRŮZKUMNÍK</h1>
                <span class="text-[11px] font-bold text-amber-950 tracking-wider" id="difficulty-badge">ÚROVEŇ 1 / 90</span>
            </div>
        </div>

        <div class="flex items-center space-x-4">
            <div class="bg-amber-600/30 px-3 py-1 rounded-xl border border-amber-600/40 flex items-center space-x-2">
                <i class="fa-solid fa-fire text-amber-950 text-base"></i>
                <span class="font-bold text-xs text-slate-900">Streak: <span class="text-amber-950 font-extrabold">3 Dny 🔥</span></span>
            </div>
            <div class="bg-amber-600/30 px-3 py-1 rounded-xl border border-amber-600/40 flex items-center space-x-2">
                <i class="fa-solid fa-star text-yellow-300 text-base"></i>
                <span class="font-bold text-xs text-slate-900">Skóre: <span class="text-amber-950" id="xp-counter">0 XP</span></span>
            </div>
            <button onclick="insertCmd('help')" class="bg-emerald-500 hover:bg-emerald-400 text-slate-950 px-3 py-1.5 rounded-xl font-bold text-xs border-b-4 border-emerald-700 active:translate-y-1 transition flex items-center space-x-1.5">
                <i class="fa-solid fa-lightbulb text-yellow-200"></i>
                <span>Nápověda</span>
            </button>
        </div>
    </header>

    <!-- HLAVNÍ MŘÍŽKA -->
    <main class="grid grid-cols-12 gap-3 flex-1 min-h-0">

        <!-- LEVÝ PANEL -->
        <aside class="col-span-3 flex flex-col space-y-2 min-h-0">
            
            <!-- PŘEHLED KAMPAŇOVÝCH SAD -->
            <div class="bg-slate-800 rounded-xl p-2 lego-card flex flex-col space-y-1.5 shrink-0">
                <div class="text-[10px] font-bold uppercase text-slate-400 tracking-wider flex items-center justify-between">
                    <span>Kampaňové Sady</span>
                    <i class="fa-solid fa-cubes text-sky-400"></i>
                </div>

                <div class="space-y-1 text-xs">
                    <div id="set-1-box" class="p-1.5 rounded-lg bg-slate-900 border-2 border-sky-400 flex items-center justify-between shadow-md">
                        <div class="flex items-center space-x-2">
                            <i id="set-1-icon" class="fa-solid fa-play text-emerald-400 text-[10px] animate-pulse"></i>
                            <div class="truncate">
                                <div class="font-bold text-sky-300 text-[10px]">1. Základy Linuxu</div>
                                <div class="text-[8px] text-slate-400">pwd, ls, cd, cat...</div>
                            </div>
                        </div>
                        <span id="set-1-progress" class="bg-emerald-500/20 text-emerald-400 text-[8px] font-bold px-1 py-0.5 rounded border border-emerald-500/30">1/30</span>
                    </div>

                    <div id="set-2-box" class="p-1.5 rounded-lg bg-slate-900/50 border border-slate-700/60 flex items-center justify-between opacity-50">
                        <div class="flex items-center space-x-2">
                            <i id="set-2-icon" class="fa-solid fa-lock text-slate-500 text-[10px]"></i>
                            <div class="truncate">
                                <div id="set-2-title" class="font-bold text-slate-400 text-[10px]">2. Soubory a sítě</div>
                                <div class="text-[8px] text-slate-500">cp, mv, find, ping...</div>
                            </div>
                        </div>
                        <span id="set-2-progress" class="bg-slate-800 text-slate-500 text-[8px] font-bold px-1 py-0.5 rounded border border-slate-700">30 Lvl</span>
                    </div>

                    <div id="set-3-box" class="p-1.5 rounded-lg bg-slate-900/50 border border-slate-700/60 flex items-center justify-between opacity-30">
                        <div class="flex items-center space-x-2">
                            <i id="set-3-icon" class="fa-solid fa-lock text-slate-500 text-[10px]"></i>
                            <div class="truncate">
                                <div id="set-3-title" class="font-bold text-slate-400 text-[10px]">3. Mistr Systému</div>
                                <div class="text-[8px] text-slate-500">ps, top, free, tar...</div>
                            </div>
                        </div>
                        <span id="set-3-progress" class="bg-slate-800 text-slate-500 text-[8px] font-bold px-1 py-0.5 rounded border border-slate-700">30 Lvl</span>
                    </div>
                </div>
            </div>

            <!-- Profil Žáka -->
            <div class="bg-slate-800 rounded-xl p-2 lego-card flex items-center space-x-2.5 shrink-0 relative">
                <div class="w-10 h-10 rounded-full bg-gradient-to-b from-sky-400 to-indigo-600 p-0.5 shadow-md flex items-center justify-center border-2 border-slate-700 shrink-0">
                    <div class="w-full h-full rounded-full bg-slate-900 flex items-center justify-center overflow-hidden">
                        <i class="fa-solid fa-user-astronaut text-lg text-sky-400"></i>
                    </div>
                </div>
                <div class="flex-1 min-w-0">
                    <div class="flex items-center justify-between">
                        <h2 class="text-xs font-bold text-sky-300 truncate" id="player-display-name">Kadet</h2>
                        <button onclick="logoutPlayer()" title="Změnit hráče" class="text-slate-400 hover:text-amber-400 text-xs px-1">
                            <i class="fa-solid fa-right-from-bracket"></i>
                        </button>
                    </div>
                    <p class="text-[9px] text-slate-400 font-semibold mb-0.5">Začínající SysAdmin</p>
                    <div class="w-full bg-slate-900 rounded-full h-1.5 border border-slate-700 p-0.5 overflow-hidden">
                        <div id="progress-bar" class="bg-gradient-to-r from-sky-400 to-emerald-400 h-full rounded-full w-[1%] transition-all duration-300"></div>
                    </div>
                </div>
            </div>

            <!-- Žebříček Kadetů -->
            <div class="bg-slate-800 rounded-xl p-2 lego-card flex flex-col shrink-0">
                <div class="text-[10px] font-bold uppercase text-slate-400 tracking-wider mb-1 flex items-center justify-between">
                    <span>Žebříček Kadetů</span>
                    <i class="fa-solid fa-trophy text-amber-400"></i>
                </div>
                <div class="space-y-0.5 text-xs">
                    <div class="flex items-center justify-between bg-slate-900/60 px-2 py-0.5 rounded border border-amber-500/30">
                        <span class="font-bold text-amber-300 text-[10px]"><i class="fa-solid fa-crown text-amber-400 mr-1"></i>1. Tux Bot</span>
                        <span class="font-mono text-[9px] text-amber-200">9 000 XP</span>
                    </div>
                    <div class="flex items-center justify-between bg-slate-900/90 px-2 py-0.5 rounded border border-sky-500/50">
                        <span class="font-bold text-sky-300 text-[10px]" id="leaderboard-name"><i class="fa-solid fa-user text-sky-400 mr-1"></i>2. Kadet (Ty)</span>
                        <span class="font-mono text-[9px] text-sky-200" id="leaderboard-xp">0 XP</span>
                    </div>
                    <div class="flex items-center justify-between bg-slate-900/40 px-2 py-0.5 rounded border border-slate-700">
                        <span class="font-bold text-slate-400 text-[10px]"><i class="fa-solid fa-robot text-slate-500 mr-1"></i>3. Jirka</span>
                        <span class="font-mono text-[9px] text-slate-400">2 400 XP</span>
                    </div>
                </div>
            </div>

            <!-- Získané Odznaky -->
            <div class="bg-slate-800 rounded-xl p-2 lego-card flex-1 flex flex-col justify-between overflow-y-auto custom-scrollbar">
                <div>
                    <div class="text-[10px] font-bold uppercase text-slate-400 tracking-wider mb-1 flex items-center justify-between">
                        <span>Odznaky v Sadě</span>
                        <i class="fa-solid fa-award text-amber-400"></i>
                    </div>

                    <div class="grid grid-cols-3 gap-1">
                        <div id="badge-5" class="bg-slate-900/60 p-1 rounded-lg border border-slate-700 flex flex-col items-center text-center opacity-40 transition-all">
                            <i class="fa-solid fa-compass text-xs text-slate-500 mb-0.5"></i>
                            <span class="text-[8px] font-bold text-slate-400">Průzkumník</span>
                        </div>
                        <div id="badge-10" class="bg-slate-900/60 p-1 rounded-lg border border-slate-700 flex flex-col items-center text-center opacity-40 transition-all">
                            <i class="fa-solid fa-gamepad text-xs text-slate-500 mb-0.5"></i>
                            <span class="text-[8px] font-bold text-slate-400">Gamer</span>
                        </div>
                        <div id="badge-15" class="bg-slate-900/60 p-1 rounded-lg border border-slate-700 flex flex-col items-center text-center opacity-40 transition-all">
                            <i class="fa-solid fa-wrench text-xs text-slate-500 mb-0.5"></i>
                            <span class="text-[8px] font-bold text-slate-400">Technik</span>
                        </div>
                        <div id="badge-20" class="bg-slate-900/60 p-1 rounded-lg border border-slate-700 flex flex-col items-center text-center opacity-40 transition-all">
                            <i class="fa-solid fa-user-ninja text-xs text-slate-500 mb-0.5"></i>
                            <span class="text-[8px] font-bold text-slate-400">Pokročilý</span>
                        </div>
                        <div id="badge-25" class="bg-slate-900/60 p-1 rounded-lg border border-slate-700 flex flex-col items-center text-center opacity-40 transition-all">
                            <i class="fa-solid fa-bolt text-xs text-slate-500 mb-0.5"></i>
                            <span class="text-[8px] font-bold text-slate-400">Guru</span>
                        </div>
                        <div id="badge-30" class="bg-slate-900/60 p-1 rounded-lg border border-slate-700 flex flex-col items-center text-center opacity-40 transition-all">
                            <i class="fa-solid fa-crown text-xs text-slate-500 mb-0.5"></i>
                            <span class="text-[8px] font-bold text-slate-400">Mistr</span>
                        </div>
                    </div>
                </div>

                <div class="bg-slate-900/80 p-1.5 rounded-lg border border-sky-500/30 text-[9px] leading-tight text-sky-200 mt-1">
                    <div class="font-bold text-sky-400 mb-0.5 flex items-center space-x-1">
                        <i class="fa-solid fa-lightbulb text-amber-400"></i>
                        <span>Věděl jsi, že?</span>
                    </div>
                    <p id="fact-text">Superpočítače, servery i systém Android v telefonech běží právě na Linuxu!</p>
                </div>
            </div>
        </aside>

        <!-- STŘEDNÍ PANEL: TERMINÁL -->
        <section class="col-span-6 flex flex-col min-h-0">
            <div class="bg-slate-950 rounded-2xl border-4 border-slate-700 shadow-2xl flex flex-col h-full overflow-hidden relative">
                <div class="bg-slate-800 px-4 py-2 flex items-center justify-between border-b-2 border-slate-700 shrink-0">
                    <div class="flex items-center space-x-2">
                        <div class="w-3 h-3 rounded-full bg-rose-500"></div>
                        <div class="w-3 h-3 rounded-full bg-amber-500"></div>
                        <div class="w-3 h-3 rounded-full bg-emerald-500"></div>
                        <span class="text-xs font-mono font-bold text-slate-400 ml-2">TERMINÁL - STANICE TUX-1</span>
                    </div>
                </div>

                <div id="terminal-history" class="p-4 font-mono text-sm flex-1 overflow-y-auto custom-scrollbar space-y-2 leading-relaxed">
                    <div class="text-sky-400 font-bold">
                        🚀 VÍTEJ V KAMPAŇOVÉM MÓDU!<br>
                        <span class="text-slate-400 font-normal">Sleduj pravý panel. Pro listování dříve zadanými příkazy můžeš použít ŠIPKY NAHORU a DOLŮ!</span>
                    </div>
                </div>

                <div class="p-2.5 bg-slate-900/90 border-t border-slate-800 flex items-center space-x-2">
                    <span class="text-emerald-400 font-bold font-mono" id="terminal-prompt-user">hrac</span>@zakladna:<span id="active-path" class="text-sky-400 font-bold font-mono">~</span>$&nbsp;
                    <input type="text" id="cmd-input" autofocus class="bg-transparent border-none outline-none flex-1 text-slate-100 font-mono text-sm focus:ring-0" placeholder="Zadej příkaz..." onkeydown="handleKeyPress(event)">
                </div>

                <div class="bg-slate-900 p-2 border-t-2 border-slate-800 flex items-center justify-between shrink-0">
                    <span class="text-xs font-bold text-slate-400 uppercase">Rychlá pomoc:</span>
                    <div class="flex space-x-2">
                        <button onclick="insertCmd('cd ~')" class="bg-rose-500 hover:bg-rose-400 text-white font-mono font-bold text-xs px-2.5 py-1 rounded-lg border-b-2 border-rose-700">cd ~</button>
                        <button onclick="insertCmd('help')" class="bg-purple-500 hover:bg-purple-400 text-white font-mono font-bold text-xs px-2.5 py-1 rounded-lg border-b-2 border-purple-700">help</button>
                    </div>
                </div>
            </div>
        </section>

        <!-- PRAVÝ PANEL: AKTUÁLNÍ ÚKOL -->
        <aside class="col-span-3 flex flex-col space-y-3 min-h-0">
            <div class="bg-slate-800 rounded-2xl p-3.5 lego-card-green flex-1 flex flex-col min-h-0">
                <div class="flex items-center space-x-2 mb-2 pb-2 border-b border-slate-700 shrink-0">
                    <i class="fa-solid fa-flag-checkered text-emerald-400 text-lg"></i>
                    <h2 class="text-base font-bold text-slate-100 uppercase tracking-wide">AKTUÁLNÍ ÚKOL</h2>
                </div>

                <div class="flex-1 flex flex-col justify-between">
                    <div class="bg-slate-900/90 p-3 rounded-xl border-2 border-amber-400 space-y-2.5">
                        <div class="flex items-center justify-between">
                            <span id="quest-difficulty" class="text-[10px] uppercase font-bold px-2 py-0.5 rounded bg-amber-500/20 text-amber-300 border border-amber-500/30">1. FÁZE: ZAČÁTEČNÍK</span>
                            <span id="quest-number" class="text-xs font-bold text-slate-400">1 / 90</span>
                        </div>

                        <h3 id="quest-title" class="font-bold text-amber-300 text-base">1. Zjisti, kde se nacházíš</h3>
                        <p id="quest-desc" class="text-xs text-slate-200 leading-relaxed font-medium">Jsi na vesmírné stanici. Ověř svou aktuální složku.</p>

                        <div id="quest-explanation-box" class="bg-slate-800 p-2.5 rounded-lg border border-sky-500/40 text-sky-200 text-xs leading-snug font-medium">
                            <div class="text-[10px] text-sky-400 font-bold uppercase mb-0.5 flex items-center space-x-1">
                                <i class="fa-solid fa-graduation-cap"></i>
                                <span>Co tento příkaz dělá:</span>
                            </div>
                            <span id="quest-explanation-text">Příkaz 'pwd' zobrazí přesnou cestu k aktuální složce.</span>
                        </div>

                        <div id="quest-hint-box" class="bg-slate-800 p-2.5 rounded-lg border border-slate-700">
                            <div class="text-[10px] text-slate-400 uppercase font-bold mb-0.5">Nápověda pro zapsání:</div>
                            <div id="quest-hint-text" class="font-mono text-xs font-bold text-emerald-400">Napiš příkaz: pwd</div>
                        </div>
                    </div>

                    <div class="bg-gradient-to-r from-purple-900/50 to-indigo-900/50 p-2.5 rounded-xl border border-purple-500/30 flex items-center justify-between mt-2">
                        <div class="flex items-center space-x-2">
                            <i class="fa-solid fa-trophy text-amber-400 text-lg"></i>
                            <div>
                                <div class="text-[9px] uppercase font-bold text-purple-300">Odměna za úroveň</div>
                                <div class="text-xs font-bold text-slate-200">+100 XP & Pokrok</div>
                            </div>
                        </div>
                    </div>
                </div>
            </div>
        </aside>

    </main>

    <script>
        const LEVELS = {{ levels | tojson }};
        let currentPlayer = "";
        let currentLevelIdx = 0;
        let score = 0;
        let currentDisplayPath = "~";

        let cmdHistory = [];
        let historyIndex = -1;

        function checkLogin() {
            const savedPlayer = localStorage.getItem('linux_quest_current_player');
            if (savedPlayer) {
                currentPlayer = savedPlayer;
                document.getElementById('login-modal').style.display = 'none';
                loadPlayerData();
            } else {
                document.getElementById('login-modal').style.display = 'flex';
                document.getElementById('player-name-input').focus();
            }
        }

        function loginPlayer() {
            const nameInput = document.getElementById('player-name-input').value.trim();
            if (!nameInput) return;

            currentPlayer = nameInput;
            localStorage.setItem('linux_quest_current_player', currentPlayer);
            document.getElementById('login-modal').style.display = 'none';
            loadPlayerData();
        }

        function logoutPlayer() {
            localStorage.removeItem('linux_quest_current_player');
            document.getElementById('login-modal').style.display = 'flex';
            document.getElementById('player-name-input').value = '';
            document.getElementById('player-name-input').focus();
        }

        function loadPlayerData() {
            document.getElementById('player-display-name').innerText = currentPlayer;
            document.getElementById('leaderboard-name').innerHTML = `<i class="fa-solid fa-user text-sky-400 mr-1"></i>2. ${currentPlayer} (Ty)`;
            document.getElementById('terminal-prompt-user').innerText = currentPlayer.toLowerCase().replace(/\s+/g, '_');

            const savedData = localStorage.getItem(`linux_quest_data_${currentPlayer}`);
            if (savedData) {
                const parsed = JSON.parse(savedData);
                currentLevelIdx = parsed.levelIdx || 0;
                score = parsed.score || 0;
            } else {
                currentLevelIdx = 0;
                score = 0;
            }

            document.getElementById('xp-counter').innerText = `${score} XP`;
            document.getElementById('leaderboard-xp').innerText = `${score} XP`;
            updateQuestUI();
        }

        function savePlayerData() {
            if (!currentPlayer) return;
            const dataToSave = {
                levelIdx: currentLevelIdx,
                score: score
            };
            localStorage.setItem(`linux_quest_data_${currentPlayer}`, JSON.stringify(dataToSave));
        }

        function updateBadges(completedLevelInSet) {
            const badgeMap = [
                {lvl: 5, id: 'badge-5', icon: 'fa-compass', color: 'text-amber-400', border: 'border-amber-500'},
                {lvl: 10, id: 'badge-10', icon: 'fa-gamepad', color: 'text-sky-400', border: 'border-sky-500'},
                {lvl: 15, id: 'badge-15', icon: 'fa-wrench', color: 'text-emerald-400', border: 'border-emerald-500'},
                {lvl: 20, id: 'badge-20', icon: 'fa-user-ninja', color: 'text-purple-400', border: 'border-purple-500'},
                {lvl: 25, id: 'badge-25', icon: 'fa-bolt', color: 'text-yellow-400', border: 'border-yellow-500'},
                {lvl: 30, id: 'badge-30', icon: 'fa-crown', color: 'text-rose-400', border: 'border-rose-500'}
            ];

            badgeMap.forEach(b => {
                const el = document.getElementById(b.id);
                if (completedLevelInSet >= b.lvl) {
                    el.className = `bg-slate-900 p-1 rounded-lg border-2 ${b.border} flex flex-col items-center text-center opacity-100 shadow-md scale-105 transition-all`;
                    el.querySelector('i').className = `fa-solid ${b.icon} text-xs ${b.color} mb-0.5 animate-bounce`;
                } else {
                    el.className = `bg-slate-900/60 p-1 rounded-lg border border-slate-700 flex flex-col items-center text-center opacity-40 transition-all`;
                    el.querySelector('i').className = `fa-solid ${b.icon} text-xs text-slate-500 mb-0.5`;
                }
            });
        }

        function updateSetsState(lvlNum) {
            const s1Box = document.getElementById('set-1-box');
            const s2Box = document.getElementById('set-2-box');
            const s3Box = document.getElementById('set-3-box');

            const s1Icon = document.getElementById('set-1-icon');
            const s2Icon = document.getElementById('set-2-icon');
            const s3Icon = document.getElementById('set-3-icon');

            if (lvlNum <= 30) {
                document.getElementById('set-1-progress').innerText = `${lvlNum}/30`;
                s1Box.className = "p-1.5 rounded-lg bg-slate-900 border-2 border-sky-400 flex items-center justify-between shadow-md";
                s1Icon.className = "fa-solid fa-play text-emerald-400 text-[10px] animate-pulse";

                s2Box.className = "p-1.5 rounded-lg bg-slate-900/50 border border-slate-700/60 flex items-center justify-between opacity-50";
                s2Icon.className = "fa-solid fa-lock text-slate-500 text-[10px]";

                s3Box.className = "p-1.5 rounded-lg bg-slate-900/50 border border-slate-700/60 flex items-center justify-between opacity-30";
                s3Icon.className = "fa-solid fa-lock text-slate-500 text-[10px]";
            } else if (lvlNum <= 60) {
                document.getElementById('set-1-progress').innerText = "30/30 ✓";
                document.getElementById('set-2-progress').innerText = `${lvlNum - 30}/30`;

                s1Box.className = "p-1.5 rounded-lg bg-slate-900/80 border border-emerald-500/50 flex items-center justify-between opacity-80";
                s1Icon.className = "fa-solid fa-check text-emerald-400 text-[10px]";

                s2Box.className = "p-1.5 rounded-lg bg-slate-900 border-2 border-amber-400 flex items-center justify-between shadow-md opacity-100";
                s2Icon.className = "fa-solid fa-play text-amber-400 text-[10px] animate-pulse";
                document.getElementById('set-2-title').className = "font-bold text-amber-300 text-[10px]";

                s3Box.className = "p-1.5 rounded-lg bg-slate-900/50 border border-slate-700/60 flex items-center justify-between opacity-40";
                s3Icon.className = "fa-solid fa-lock text-slate-500 text-[10px]";
            } else {
                document.getElementById('set-1-progress').innerText = "30/30 ✓";
                document.getElementById('set-2-progress').innerText = "30/30 ✓";
                document.getElementById('set-3-progress').innerText = `${lvlNum - 60}/30`;

                s1Box.className = "p-1.5 rounded-lg bg-slate-900/80 border border-emerald-500/50 flex items-center justify-between opacity-80";
                s1Icon.className = "fa-solid fa-check text-emerald-400 text-[10px]";

                s2Box.className = "p-1.5 rounded-lg bg-slate-900/80 border border-emerald-500/50 flex items-center justify-between opacity-80";
                s2Icon.className = "fa-solid fa-check text-emerald-400 text-[10px]";

                s3Box.className = "p-1.5 rounded-lg bg-slate-900 border-2 border-purple-400 flex items-center justify-between shadow-md opacity-100";
                s3Icon.className = "fa-solid fa-play text-purple-400 text-[10px] animate-pulse";
                document.getElementById('set-3-title').className = "font-bold text-purple-300 text-[10px]";
            }
        }

        function updateQuestUI() {
            const level = LEVELS[currentLevelIdx];
            document.getElementById('quest-number').innerText = `${level.id} / ${LEVELS.length}`;
            document.getElementById('quest-title').innerText = level.title;
            document.getElementById('quest-desc').innerText = level.desc;
            document.getElementById('quest-difficulty').innerText = level.difficulty;
            document.getElementById('difficulty-badge').innerText = `ÚROVEŇ ${level.id} / 90`;
            
            const progressPct = Math.round(((level.id) / LEVELS.length) * 100);
            document.getElementById('progress-bar').style.width = `${progressPct}%`;

            const explBox = document.getElementById('quest-explanation-box');
            if (level.explanation) {
                explBox.style.display = 'block';
                document.getElementById('quest-explanation-text').innerText = level.explanation;
            } else {
                explBox.style.display = 'none';
            }

            const hintBox = document.getElementById('quest-hint-text');
            if (level.hint_type === 'exact') {
                hintBox.innerHTML = `Napiš příkaz: <span class="text-emerald-400 font-mono text-xs font-bold">${level.command_hint}</span>`;
            } else if (level.hint_type === 'cmd_only') {
                hintBox.innerHTML = `Použij příkaz: <span class="text-emerald-400 font-mono text-xs font-bold">${level.command_hint}</span>`;
            } else {
                hintBox.innerHTML = `<span class="text-slate-300 font-medium">${level.command_hint}</span>`;
            }

            const setLevel = ((level.id - 1) % 30);
            updateBadges(setLevel);
            updateSetsState(level.id);
        }

        function handleKeyPress(e) {
            const input = document.getElementById('cmd-input');

            if (e.key === 'ArrowUp') {
                e.preventDefault();
                if (cmdHistory.length > 0 && historyIndex < cmdHistory.length - 1) {
                    historyIndex++;
                    input.value = cmdHistory[cmdHistory.length - 1 - historyIndex];
                }
            } else if (e.key === 'ArrowDown') {
                e.preventDefault();
                if (historyIndex > 0) {
                    historyIndex--;
                    input.value = cmdHistory[cmdHistory.length - 1 - historyIndex];
                } else if (historyIndex === 0) {
                    historyIndex = -1;
                    input.value = '';
                }
            } else if (e.key === 'Enter') {
                const command = input.value.trim();
                if (!command) return;

                cmdHistory.push(command);
                historyIndex = -1;

                appendCommand(command);
                input.value = '';

                fetch('/run-command', {
                    method: 'POST',
                    headers: {'Content-Type': 'application/json'},
                    body: JSON.stringify({command: command, current_level: currentLevelIdx})
                })
                .then(res => res.json())
                .then(data => {
                    if (data.display_path) {
                        currentDisplayPath = data.display_path;
                        document.getElementById('active-path').innerText = currentDisplayPath;
                    }

                    if (data.output === '__CLEAR__') {
                        document.getElementById('terminal-history').innerHTML = '';
                    } else {
                        appendResponse(data.output, data.success);
                    }

                    if (data.level_passed) {
                        score += 100;
                        document.getElementById('xp-counter').innerText = `${score} XP`;
                        document.getElementById('leaderboard-xp').innerText = `${score} XP`;
                        const currentLvlNum = LEVELS[currentLevelIdx].id;
                        
                        if (currentLvlNum % 5 === 0) {
                            appendResponse(`🎖️ SKVĚLE! Dosáhl jsi úrovně ${currentLvlNum} a získal jsi NOVÝ ODZNAK!`, true);
                        }

                        if (currentLvlNum === 30) {
                            appendResponse(`🔓 ODEMČENA SADA 2: Soubory a sítě! Skvělá práce!`, true);
                        } else if (currentLvlNum === 60) {
                            appendResponse(`🔓 ODEMČENA SADA 3: Mistr Systému! Jsi v cílové rovince!`, true);
                        }

                        if (currentLevelIdx < LEVELS.length - 1) {
                            currentLevelIdx++;
                            savePlayerData();
                            updateQuestUI();
                            appendResponse(`🎉 Úroveň dokončena! Postupuješ dále.`, true);
                        } else {
                            savePlayerData();
                            updateBadges(30);
                            appendResponse(`🏆 ABSOLUTNÍ VÍTĚZSTVÍ! Dokončil jsi všech 90 úrovní a stal ses legendárním Mistrem Linuxu!`, true);
                        }
                    }
                });
            }
        }

        function appendCommand(cmd) {
            const history = document.getElementById('terminal-history');
            const line = document.createElement('div');
            const userPrompt = currentPlayer ? currentPlayer.toLowerCase().replace(/\s+/g, '_') : 'hrac';
            line.innerHTML = `<span class="text-emerald-400 font-bold">${userPrompt}</span>:<span class="text-sky-400 font-bold">${currentDisplayPath}</span>$&nbsp;<span class="text-amber-300 font-semibold">${cmd}</span>`;
            history.appendChild(line);
            history.scrollTop = history.scrollHeight;
        }

        function appendResponse(text, isSuccess) {
            const history = document.getElementById('terminal-history');
            const response = document.createElement('div');
            response.className = isSuccess ? 'text-emerald-400 font-semibold my-1 whitespace-pre-wrap' : 'text-rose-400 font-semibold my-1 whitespace-pre-wrap';
            response.innerText = text;
            history.appendChild(response);
            history.scrollTop = history.scrollHeight;
        }

        function insertCmd(cmd) {
            document.getElementById('cmd-input').value = cmd;
            document.getElementById('cmd-input').focus();
        }

        checkLogin();
    </script>

</body>
</html>
"""

# ------------------------------------------------------------------------------
# 3. ROUTING A VYHODNOCOVACÍ LOGIKA
# ------------------------------------------------------------------------------

@app.route("/")
def home():
    """Úvodní vzdělávací portál Linuxhrou.cz"""
    return render_template_string(PORTAL_HTML_TEMPLATE)

@app.route("/hra")
def game():
    """Herní simulátor s 90 úrovněmi"""
    return render_template_string(GAME_HTML_TEMPLATE, levels=LEVELS)

@app.route("/run-command", methods=["POST"])
def run_command():
    data = request.get_json()
    raw_cmd = data.get("command", "").strip()
    lvl_idx = data.get("current_level", 0)

    if not raw_cmd:
        return jsonify({"output": "", "success": True, "level_passed": False})

    file_system["history"].append(raw_cmd)

    try:
        parts = shlex.split(raw_cmd)
    except Exception:
        parts = raw_cmd.split()

    cmd = parts[0] if parts else ""
    args = parts[1:] if len(parts) > 1 else []

    curr = file_system["current_path"]
    node = file_system["tree"].get(curr, {"dirs": [], "files": {}, "perms": {}})
    display_path = "~" if curr == "/home/hrac" else curr.replace("/home/hrac", "~")

    expected_req = LEVELS[lvl_idx]["expected"].strip()
    output = ""
    success = True
    level_passed = False

    # STRIKTNÍ ZKONTROLOVÁNÍ PŘÍKAZU DANÉ ÚROVNĚ
    if raw_cmd.strip() != expected_req:
        output = f"❌ CHYBA: Zadal jsi '{raw_cmd}', ale v tomto úkolu se vyžaduje příkaz: '{expected_req}'"
        success = False
        return jsonify({"output": output, "success": success, "display_path": display_path, "level_passed": level_passed})

    # Pokud příkaz odpovídá úkolu, vykoná se jeho simulace
    level_passed = True

    if cmd.startswith("./") or "spustit_laser.sh" in cmd:
        home_node = file_system["tree"]["/home/hrac"]
        perm = home_node.get("perms", {}).get("spustit_laser.sh", "rw-r--r--")
        if "x" in perm:
            output = "💥 PIU PIU! Laserový kanón je připraven k obraně základny!"
        else:
            output = f"bash: {cmd}: Přístup odepřen! Použij 'chmod +x spustit_laser.sh'."
            success = False
            level_passed = False

    elif cmd == "pwd":
        output = curr

    elif cmd == "ls":
        show_all = any(arg in args for arg in ["-a", "-la", "-al", "--all"])
        all_dirs = node["dirs"]
        all_files = list(node["files"].keys())
        if not show_all:
            all_dirs = [d for d in all_dirs if not d.startswith(".")]
            all_files = [f for f in all_files if not f.startswith(".")]
        formatted_dirs = [f"{d}/" for d in all_dirs]
        result_str = "  ".join(formatted_dirs + all_files)
        output = result_str if result_str else "(složka je prázdná)"

    elif cmd == "cd":
        target = args[0] if args else "/home/hrac"
        if target in ["~", "/home/hrac"]:
            file_system["current_path"] = "/home/hrac"
            display_path = "~"
        elif target == "..":
            file_system["current_path"] = "/home/hrac"
            display_path = "~"
        else:
            new_path = f"{curr}/{target}".rstrip("/")
            if new_path in file_system["tree"]:
                file_system["current_path"] = new_path
                display_path = "~" if new_path == "/home/hrac" else new_path.replace("/home/hrac", "~")
            else:
                output = f"cd: složka '{target}' neexistuje"
                success = False
                level_passed = False

    elif cmd == "cat":
        if not args:
            output, success, level_passed = "cat: chybí název souboru", False, False
        else:
            output = node["files"].get(args[0], f"cat: soubor '{args[0]}' neexistuje.")

    elif cmd == "grep":
        if len(args) < 2:
            output, success, level_passed = "Použití: grep <text> <soubor>", False, False
        else:
            search_term, file_name = args[0], args[1]
            if file_name in node["files"]:
                lines = node["files"][file_name].split("\n")
                matched = [line for line in lines if search_term.lower() in line.lower()]
                output = "\n".join(matched) if matched else f"Text '{search_term}' nebyl nalezen."
            else:
                output, success, level_passed = f"grep: soubor '{file_name}' neexistuje.", False, False

    elif cmd == "chmod":
        if len(args) < 2:
            output, success, level_passed = "Použití: chmod +x <soubor>", False, False
        else:
            file_name = args[1] if len(args) > 1 else args[0]
            target_node = node if file_name in node["files"] else file_system["tree"]["/home/hrac"]
            if file_name in target_node["files"]:
                target_node.get("perms", {})[file_name] = "-rwxr-xr-x"
                output = f"Práva souboru '{file_name}' změněna na spouštěcí (-rwxr-xr-x)."
            else:
                output, success, level_passed = f"chmod: soubor '{file_name}' neexistuje.", False, False

    elif cmd == "mkdir":
        if not args:
            output, success, level_passed = "mkdir: chybí název", False, False
        else:
            f_name = args[0]
            node["dirs"].append(f_name)
            file_system["tree"][f"{curr}/{f_name}"] = {"dirs": [], "files": {}, "perms": {}}
            output = f"Složka '{f_name}' vytvořena."

    elif cmd == "touch":
        if not args:
            output, success, level_passed = "touch: chybí název", False, False
        else:
            node["files"][args[0]] = ""
            output = f"Soubor '{args[0]}' vytvořen."

    elif cmd == "rm":
        if not args:
            output, success, level_passed = "rm: chybí název", False, False
        else:
            target = args[0]
            file_deleted = False
            for p_path, p_node in file_system["tree"].items():
                if target in p_node["files"]:
                    del p_node["files"][target]
                    file_deleted = True
                    break
            output = f"Soubor '{target}' smazán." if file_deleted else f"rm: '{target}' neexistuje."
            if not file_deleted:
                success = False
                level_passed = False

    elif cmd == "cp":
        output = "Kopírování provedeno."
    elif cmd == "mv":
        output = "Přesun / přejmenování provedeno."
    elif cmd == "find":
        output = "./gaming/wishlist.txt\n./tajna_laborator/databaze_chyb.txt\n./proc_linux.txt"
    elif cmd == "ping":
        output = "64 bytes from 127.0.0.1: icmp_seq=1 ttl=64 time=0.042 ms\nPING OK."
    elif cmd == "echo":
        output = " ".join(args)
    elif cmd == "nano":
        output = "[Subshell nano spuštěno... soubor uložen a zavřen.]"
    elif cmd == "wc":
        output = "  5  28 184 proc_linux.txt"
    elif cmd == "head":
        output = "PROČ POUŽÍVAT LINUX?\n1. Je ZDARMA a Open-Source."
    elif cmd == "tail":
        output = "3. Je RYCHLÝ.\n4. TERMINÁL: Dává ti plnou kontrolu!"
    elif cmd == "rmdir":
        output = "Složka odstraněna."
    elif cmd == "df":
        output = "Filesystem     1K-blocks      Used Available Use% Mounted on\n/dev/sda1      103112112  24512000  73343112  26% /"
    elif cmd == "uptime":
        output = " 20:45:12 up 14 days,  3:12,  1 user,  load average: 0.05, 0.03, 0.00"
    elif cmd == "date":
        output = "Čt 20 srp 2026 20:45:12 CEST"
    elif cmd == "hostname":
        output = "stanice-tux-1.local"
    elif cmd == "env":
        output = "USER=hrac\nSHELL=/bin/bash\nHOME=/home/hrac\nPATH=/usr/local/bin:/usr/bin"
    elif cmd == "uname":
        output = "Linux stanice-tux-1 6.8.0-40-generic #40-Ubuntu SMP x86_64 GNU/Linux"
    elif cmd == "ps":
        output = "  PID TTY          TIME CMD\n 1204 pts/0    00:00:00 bash\n 4512 pts/0    00:00:01 python3"
    elif cmd == "top" or cmd == "htop":
        output = "%Cpu(s):  2.3 us,  0.7 sy,  0.0 ni, 97.0 id\nKiB Mem :  8145200 total,  4123500 free,  2011200 used"
    elif cmd == "free":
        output = "               total        used        free      shared  buff/cache   available\nMem:         8145200     2011200     4123500       12400     2010500     5812000"
    elif cmd == "tar":
        output = "Archivování dokončeno."
    elif cmd == "gzip":
        output = "Komprese dokončena."
    elif cmd == "alias":
        output = "Alias nastaven."
    elif cmd == "curl":
        output = "HTTP/1.1 200 OK\nContent-Type: text/html\nData přijata úspěšně."
    elif cmd == "kill":
        output = "Proces ukončen."
    elif cmd == "history":
        output = "\n".join([f" {i+1}  {c}" for i, c in enumerate(file_system["history"])])
    elif cmd == "clear":
        output = "__CLEAR__"
    elif cmd == "whoami":
        output = "hrac (Super SysAdmin)"
    else:
        output = f"Příkaz '{cmd}' nebyl rozpoznán."
        success = False
        level_passed = False

    return jsonify({"output": output, "success": success, "display_path": display_path, "level_passed": level_passed})

if __name__ == "__main__":
    app.run(debug=True, port=5000)