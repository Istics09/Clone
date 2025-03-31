import tkinter as tk
from tkinter import messagebox
import tkinter.font as tkfont
import subprocess, threading, os, signal, datetime, logging, getpass, automatizate_test
import cheat_sheet
import tkinter.font as tkFont
import base64


current_process = None
open_frame = None
target = "{Domain/IP}"
port = "{Port/Služba}"


x = datetime.datetime.now()
if not os.path.exists("logs"):
    os.makedirs("logs")
log_filename = f'logs/{x.year}-{x.month:02d}-{x.day:02d}-{x.hour:02d}-{x.minute:02d}-{x.second:02d}.log'
logging.basicConfig(
    filename=log_filename,
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

def auto_testing():
    automatizate_test.main()

def airmon_ng(Name):
    
    try:
        result = subprocess.run("ifconfig", shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
        output = result.stdout
        output_text.config(state="normal")
        output_text.insert(tk.END, "=== Výstup ifconfig ===\n")
        output_text.insert(tk.END, output + "\n")
        output_text.insert(tk.END, "=== Prosím, vyberte svoje WLAN/LAN zariadenie! ===\n")
        output_text.config(state="disabled")
        
        if Name == "Aircrack-ng":
            Run_Button_command("sudo airmon-ng start {device}")
        else:
            Run_Button_command("sudo ifconfig {device} down")
    except Exception as e:
        output_text.config(state="normal")
        output_text.insert(tk.END, f"Chyba: {str(e)}\n")
        output_text.config(state="disabled")
        
def clear_console(event=None):
    if 'output_text' in globals() and output_text.winfo_exists():
        output_text.config(state="normal")
        output_text.delete("1.0", tk.END)
        output_text.config(state="disabled")
    return "break"

def Run_Command():

    global current_process
    command = command_input.get()
    if not command.strip():
        return
    command_input.delete(0, tk.END)
    
        # Ellenőrizzük, hogy a parancs a speciális decode64 -s parancs-e
    if command.startswith("decode64 "):
        encoded = command[len("decode64 "):].strip()
        try:
            decoded = base64.b64decode(encoded).decode('utf-8')
            output_text.config(state="normal")
            output_text.insert(tk.END, "Decoded output: " + decoded + "\n")
            output_text.config(state="disabled")
            if logging_enabled.get():
                logging.info("Decoded output: %s", decoded)
        except Exception as e:
            output_text.config(state="normal")
            output_text.insert(tk.END, "Error decoding: " + str(e) + "\n")
            output_text.config(state="disabled")
            if logging_enabled.get():
                logging.error("Error decoding: %s", str(e))
        return
    
    thread = threading.Thread(target=run_in_thread, args=(command,))
    thread.daemon = True
    thread.start()

def run_in_thread(command):

    global current_process
    try:
        current_process = subprocess.Popen(
            command, shell=True,
            stdout=subprocess.PIPE, stderr=subprocess.PIPE,
            text=True, preexec_fn=os.setsid
        )
        for line in iter(current_process.stdout.readline, ''):
            if line:
                output_text.config(state="normal")
                output_text.insert(tk.END, line.strip() + "\n")
                if logging_enabled.get():
                    logging.info("STDOUT: %s", line.strip())
                output_text.see(tk.END)
                output_text.config(state="disabled")
        for line in iter(current_process.stderr.readline, ''):
            if line:
                output_text.config(state="normal")
                output_text.insert(tk.END, f"ERROR: {line.strip()}\n")
                if logging_enabled.get():
                    logging.error("STDERR: %s", line.strip())
                output_text.see(tk.END)
                output_text.config(state="disabled")
        current_process.wait()
    except Exception as e:
        output_text.config(state="normal")
        output_text.insert(tk.END, f"Chyba: {str(e)}\n")
        output_text.config(state="disabled")
    finally:
        current_process = None

def interrupt_process(event=None):
    """Preruší bežiaci proces (Ctrl+F2)."""
    global current_process
    if logging_enabled.get():
        logging.info("Proces prerušený!")
    if current_process and current_process.poll() is None:
        os.killpg(os.getpgid(current_process.pid), signal.SIGTERM)
        output_text.config(state="normal")
        output_text.insert(tk.END, "Proces prerušený!\n")
        output_text.config(state="disabled")

def copy_to_clipboard(event=None):
    """Skopíruje vybraný text do schránky (Ctrl+C)."""
    try:
        selected_text = output_text.selection_get()
        window.clipboard_clear()
        window.clipboard_append(selected_text)
        window.update()
    except tk.TclError:
        print("Žiadny vybraný text.")

def create_console():
    global output_text, command_input, center_frame
    if 'output_text' in globals() and output_text.winfo_exists():
        return
    output_text = tk.Text(center_frame, font=('Consolas', 14), bg="black", fg="lime", state="disabled", wrap="word")
    output_text.pack(padx=10, pady=(10, 5), fill="both", expand=True)
    command_input = tk.Entry(center_frame, bg="black", fg="lime", insertbackground="lime", font=('Consolas', 14))
    command_input.pack(padx=10, pady=5, fill="x")
    welcome_message = "Vitajte v Kraken!\n"
    output_text.config(state="normal")
    output_text.insert(tk.END, welcome_message)
    output_text.config(state="disabled")
    command_input.bind("<Return>", lambda event: Run_Command())
    command_input.bind("<Tab>", autocomplete)
    window.bind("<Control-l>", clear_console)

def Run_Button_command(command):
    global command_input, target
    command_input.delete(0, tk.END)

    needle = "{target}"
    index = command.find(needle)
    if not index == -1:
        cmd1 = command[:index] 
        cmd2 = command[index + len(needle):] 
        command = cmd1 + target + cmd2

    needle = "{port}"
    index = command.find(needle)
    if not index == -1:
        cmd1 = command[:index]
        cmd2 = command[index + len(needle):]
        command = cmd1 + port + cmd2
    print(command)

    command_input.insert(0, command)

def clear_right_sidebar():
    for widget in right_sidebar.winfo_children():
        widget.destroy()
        
def autocomplete(event):
    """
    Autocomplete pre file system cesty.
    Ak je aktuálny text v command_input napr. "cd Seclists" alebo "cd /home/us",
    funkcia zistí, ktoré položky v príslušnom adresári začínajú na zadaný prefix a:
      - ak je iba jedna, automaticky doplní celú cestu;
      - ak je viacero, vypíše ich do output_text.
    """
    # Získame aktuálny text
    text = command_input.get()
    # Rozdelíme text na tokeny (predpokladáme oddelenie medzerou)
    tokens = text.split()
    if not tokens:
        return "break"
    last_token = tokens[-1]
    
    sep = os.sep
    if sep in last_token:
        # Ak už je zadaná cesta (obsahuje /), rozdelíme ju na adresár a prefix
        dir_part = os.path.dirname(last_token)
        prefix = os.path.basename(last_token)
        if not dir_part:
            dir_part = "."
    else:
        # Ak token neobsahuje lomítko, predpokladáme, že ide o názov v aktuálnom adresári.
        dir_part = os.getcwd()  # Alebo môžete nastaviť iný predvolený adresár
        prefix = last_token
    
    # Rozšírenie user (ak je použitý ~)
    dir_part = os.path.expanduser(dir_part)
    
    try:
        candidates = [f for f in os.listdir(dir_part) if f.startswith(prefix)]
    except Exception as e:
        output_text.config(state="normal")
        output_text.insert(tk.END, f"Chyba pri čítaní adresára {dir_part}: {str(e)}\n")
        output_text.config(state="disabled")
        return "break"
    
    candidates.sort()
    
    if not candidates:
        return "break"
    elif len(candidates) == 1:
        # Ak je iba jeden kandidát, doplníme ho automaticky
        candidate = candidates[0]
        # Ak candidate obsahuje medzeru a ešte nie je v úvodzovkách, obalíme ho úvodzovkami
        if " " in candidate and not (candidate.startswith('"') and candidate.endswith('"')):
            candidate = f'"{candidate}"'
        completed = os.path.join(dir_part, candidate)
        # Zostavíme nový text s doplneným tokenom
        new_tokens = tokens[:-1] + [completed]
        new_text = " ".join(new_tokens)
        command_input.delete(0, tk.END)
        command_input.insert(0, new_text)
    else:
        # Viacero kandidátov – vypíšeme ich do output_text
        output_text.config(state="normal")
        output_text.insert(tk.END, "Možnosti: " + "    ".join(candidates) + "\n")
        output_text.config(state="disabled")
    return "break"


def update_target():
    global target, port, open_frame
    if target_input.get().strip() != '':
        target = target_input.get()
    else:
        target = "(Cieľ/Doména)"
    if port_input.get().strip() != '':
        port = port_input.get()
    else:
        port = "(Port/Služba)"

    print(f"Cieľ: {target}, Port: {port}, openframe: {open_frame}")


def add_right_button(text, command, tooltip_text):
    btn = tk.Button(right_sidebar, text=text, font=('Helvetica', 12), bg="#2980b9", fg="white",
                    activebackground="black", activeforeground="white", cursor="hand2",
                    command=lambda: Run_Button_command(command))
    btn.pack(pady=5, padx=5, fill="x")
    CreateToolTip(btn, tooltip_text)

class CreateToolTip:
    """
    Tooltip létrehozása egy widgethez. A tooltip pozíciója a widget elhelyezkedésétől függ:
    - Bal oldali widget esetén a tooltip jobbra jelenik meg.
    - Jobb oldali widget esetén a tooltip balra jelenik meg.
    """
    def __init__(self, widget, text="widget info"):
        self.waittime = 500  # késleltetés ms-ban
        self.wraplength = 180  # alapértelmezett tördelési hossz (pixelben)
        self.widget = widget
        self.text = text
        self.widget.bind("<Enter>", self.enter)
        self.widget.bind("<Leave>", self.leave)
        self.widget.bind("<ButtonPress>", self.leave)
        self.id = None
        self.tw = None

    def enter(self, event=None):
        self.schedule()

    def leave(self, event=None):
        self.unschedule()
        self.hidetip()

    def schedule(self):
        self.unschedule()
        self.id = self.widget.after(self.waittime, self.showtip)

    def unschedule(self):
        id_ = self.id
        self.id = None
        if id_:
            self.widget.after_cancel(id_)

    def showtip(self, event=None):
        # Lekérjük a widget relatív pozícióját
        bbox = self.widget.bbox("insert")
        if bbox:
            x_rel, y_rel, cx, cy = bbox
        else:
            # Ha nincs 'insert', akkor alapértelmezett értékek
            x_rel, y_rel = 0, 0

        # Widget abszolút koordinátái
        abs_x = self.widget.winfo_rootx()
        abs_y = self.widget.winfo_rooty()

        # Képernyő szélessége
        screen_width = self.widget.winfo_screenwidth()

        # Döntés: ha a widget a képernyő bal felén van, a tooltip jobbra, ha jobb felén, akkor balra.
        if abs_x < screen_width / 2:
            x_offset = 150   # bal oldali widget => tooltip jobbra
        else:
            x_offset = -200  # jobb oldali widget => tooltip balra; ezt az értéket igény szerint módosíthatod

        tooltip_x = abs_x + x_rel + x_offset
        tooltip_y = abs_y + y_rel + 30

        self.tw = tk.Toplevel(self.widget)
        self.tw.wm_overrideredirect(True)
        self.tw.wm_geometry(f"+{tooltip_x}+{tooltip_y}")

        # Dinamikus wraplength beállítás a szöveg szélessége alapján
        font = tkFont.Font(font=self.widget.cget("font"))
        text_width = font.measure(self.text)
        max_width = 200  # Maximum szélesség
        if text_width > max_width:
            wraplength = max_width
        else:
            wraplength = text_width + 10

        label = tk.Label(self.tw, text=self.text, justify='left',
                         background="#ffffe0", relief='solid', borderwidth=1,
                         wraplength=wraplength)
        label.pack(ipadx=1)

    def hidetip(self):
        if self.tw:
            self.tw.destroy()
        self.tw = None

def Clicked_button(Name):
    global open_frame, current_process

    if Name == "Exit":
        window.destroy()
    elif Name == "Nmap":
        create_console()
        clear_right_sidebar()
        add_right_button(
            "Konkretný port",
            "nmap {target} -p {port}",
            "Skontroluje zadaný port na cieľovom zariadení. Použite na overenie dostupnosti konkrétnej služby na danom porte."
        )
        add_right_button(
            "Verzia aplikácii",
            "nmap -sV {target}",
            "Spraví obyčajný sken avšak snaží zistiť bežiacé procesy a ich verziu"
        )
        add_right_button(
            "Rozsah portov",
            "nmap {target} -p (Začiatočný)-(Koncový)",
            "Prehľadá zadaný rozsah portov na cieľovom zariadení a zisťuje, ktoré porty sú otvorené v danom intervale."
        )
        add_right_button(
            "Všetky porty",
            "nmap {target} -p-",
            "Skenuje všetky porty na cieľovom zariadení. Poskytne úplný prehľad o otvorených portoch, avšak môže trvať dlhšie."
        )
        add_right_button(
            "Vyhľadať službu",
            "nmap {target} -p {port}",
            "Skontroluje konkrétny port a pokúsi sa identifikovať bežiacu službu, ktorá na ňom komunikuje."
        )
        add_right_button(
            "Rýchly sken",
            "nmap {target} -F",
            "Vykoná rýchly sken s preddefinovaným zoznamom najčastejšie používaných portov. Vhodné pre rýchle získanie prehľadu."
        )
        add_right_button(
            "Najpoužívanejšie porty",
            "nmap {target} --top-ports (Počet portov)",
            "Skenuje najčastejšie používané porty. Môžeš zadať počet portov, ktoré majú byť skenované, a získať tak rýchly prehľad."
        )
        add_right_button(
            "Detekcia OS",
            "nmap -O {target}",
            "Vykoná detekciu operačného systému na cieľovom zariadení na základe odpovedí portov. Pomáha určiť, aký systém beží na cieľovom hoste."
        )
        add_right_button(
            "Lokálny sken",
            "nmap {target} -sn",
            "Vykoná ping scan, ktorý zisťuje, či je cieľové zariadenie online, bez hlbšieho portového skenovania."
        )
        add_right_button(
            "Nastaviť zdrojový port",
            "nmap -g {port} {target}",
            "Umožní nastaviť zdrojový port pre skenovanie, čo môže pomôcť obísť niektoré bezpečnostné mechanizmy alebo firewally."
        )
        open_frame = "Nmap"
        right_sidebar.config(bg="#34495e")
    elif Name == "Gobuster":
        current_process = "Gobuster"
        create_console()
        clear_right_sidebar()
        add_right_button(
            "Hľadanie adresárov",
            "gobuster dir -u {target} -w dir.txt",
            "Vyhľadáva dostupné adresáre na webovom serveri pomocou zoznamu slov (wordlist)."
        )
        add_right_button(
            "Hľadanie subdomén",
            "gobuster dns -d {target} -w subdomains.txt",
            "Skúma subdomény cieľovej domény na základe slovníka subdomén."
        )
        add_right_button(
            "Virtuálé hosty",
            "gobuster vhost -u http://{target} -w /path/to/wordlist.txt",
            "Detekuje virtuálne hosty na webovom serveri podľa zadaného zoznamu hostov."
        )
        open_frame = "Gobuster"
        right_sidebar.config(bg="#34495e")
    elif Name == "Hydra":
        current_process = "Hydra"
        create_console()
        clear_right_sidebar()
        add_right_button(
            "Lámač(FTP)",
            "hydra -L users.txt -P passwords.txt {target} ftp",
            "Spúšťa útok hrubou silou na FTP službu pomocou zoznamu hesiel."
        )
        add_right_button(
            "Prihlásenie SSH",
            "hydra -L users.txt -P passwords.txt {target} ssh",
            "Skúša prihlásenie do SSH pomocou kombinácií používateľov a hesiel zo zoznamov."
        )
        open_frame = "Hydra"
        right_sidebar.config(bg="#34495e")
    elif Name == "Hashcat":
        current_process = "Hashcat"
        create_console()
        clear_right_sidebar()
        
        add_right_button(
            "Dictionary Attack",
            "hashcat -m {typ šifrovania} -a 0 hash.txt passwords.txt",
            "Spustí útok pomocou preddefinovaného zoznamu hesiel (slovníkový útok). Heslá sú načítané zo súboru password.txt."
        )

        add_right_button(
            "Brute-Force Attack",
            "hashcat -m {typ šifrovania} -a 3 hash.txt passwords.txt",
            "Vykoná brute-force útok s maskou, pričom testuje všetky možné kombinácie znakov na prelomenie hesla."
        )

        add_right_button(
            "Hybrid Attack",
            "hashcat -m {typ šifrovania} -a 6 hash.txt passwords.txt",
            "Kombinuje slovníkový útok s brute-force metódou, čím rozširuje možnosti prelomenia hesla o maskové variácie."
        )

        add_right_button(
            "Combinator Attack",
            "hashcat -m {typ šifrovania} -a 1 hash.txt passwords.txt",
            "Spustí kombinatorický útok, kde sa spájajú dve sady hesiel za účelom vytvorenia nových kombinácií a zvýšenia úspešnosti prelomenia."
        )
        
        add_right_button(
        "Zobraziť prelomené hashe",
        "hashcat --show -m {typ šifrovania} hash.txt passwords.txt",
        "Odborne zobrazuje prelomené heslá uložené v potfile. Parameter {typ šifrovania} určuje typ šifrovania pre správnu interpretáciu výsledkov."
        )
        
        
        open_frame = "Hashcat"
        right_sidebar.config(bg="#34495e")
    elif Name == "MACchanger":
        current_process = "MACchanger"
        create_console()
        clear_right_sidebar()
        add_right_button(
            "Náhodný MAC",
            "macchanger -r {Zariadenie}",
            "Náhodne zmení MAC adresu zariadenia, čo môže pomôcť pri zachovaní anonymity."
        )
        add_right_button(
            "aktuálny MAC",
            "macchanger -s {Zariadenie}",
            "Zobrazí aktuálnu MAC adresu zvoleného sieťového rozhrania."
        )
        add_right_button(
            "Originálnu MAC",
            "macchanger -p {Zariadenie}",
            "Obnoví pôvodnú (fabrické) MAC adresu zariadenia."
        )
        add_right_button(
            "Konkrétnu MAC",
            "macchanger -m 00:11:22:33:44:55 {Zariadenie}",
            "Nastaví zvolenú MAC adresu (v tomto prípade 00:11:22:33:44:55) na zariadení."
        )
        add_right_button(
            "Náhodný MAC výrobcu",
            "macchanger -a {Zariadenie}",
            "Zmení MAC adresu na náhodnú adresu výrobcu, čo môže pomôcť s imitáciou konkrétneho zariadenia."
        )
        open_frame = "MACchanger"
        right_sidebar.config(bg="#34495e")
    elif Name == "Cheat Sheet":
        current_process = "Cheat Sheet"
        cheat_sheet.main()
    elif Name == "Nikto":
        current_process = "Nikto"
        create_console()
        clear_right_sidebar()
        add_right_button(
            "Základný scan",
            "nikto -h {target}",
            "Spustí základný sken webového servera a vyhľadá bežné zraniteľnosti."
        )
        add_right_button(
            "Scan s tuning",
            "nikto -h {target} -ask no -Tuning 1",
            "Vykoná sken s jemnejším ladením, kde sú niektoré otázky automaticky odmietnuté pre rýchlejší prehľad."
        )
        add_right_button(
            "Agresívny Full scan",
            "nikto -h {target} -C all",
            "Spustí kompletný, agresívny sken webového servera, ktorý preverí čo najviac možných zraniteľností."
        )
        open_frame = "Nikto"
        right_sidebar.config(bg="#34495e")
        


window = tk.Tk()
window.title("Kraken - Nástroj na penetračné testovanie")
window.config(bg="#1e1e1e")
#window.geometry("1380x920")
window.attributes('-fullscreen', True)
window.bind("<F2>", interrupt_process)
window.bind("<Control-c>", copy_to_clipboard)
#window.bind("<Escape>", lambda event: window.destroy())
window.eval('tk::PlaceWindow . center')


left_sidebar = tk.Frame(window, width=200, bg="#2c3e50", relief="raised", borderwidth=2)
left_sidebar.pack(side="left", fill="y")

center_frame = tk.Frame(window, bg="#1e1e1e")
center_frame.pack(side="left", fill="both", expand=True)

right_sidebar = tk.Frame(window, width=250, bg="#34495e", relief="raised", borderwidth=2)
right_sidebar.pack(side="right", fill="y")


tooltip_texts = {
    "Nmap": "Tento nástroj vám pomôže zistiť, ktoré " +
            "porty na cieľovom počítači sú otvorené a aké služby bežia.",
    "Gobuster": "Gobuster pomáha objaviť skryté adresáre a poddomény na webovej stránke.",
    "Hydra": "Hydra skúša rôzne kombinácie hesiel pre pripojenie, aby otestovala bezpečnosť " +
             "hesiel na rôznych službách.",
    "Aircrack-ng": "Aircrack-ng vám umožní sledovať WiFi siete a zistiť, aké sú ich bezpečnostné nastavenia.",
    "MACchanger": "MACchanger umožňuje zmeniť identifikačné číslo sieťového adaptéra, čo môže pomôcť " +
                   "pri zachovaní vašej anonymity.",
    "Nikto": "Nikto prehľadá webový server a nájde bežné bezpečnostné chyby, čím pomáha zabezpečiť web.",
    "Cheat Sheet": "Cheat Sheet obsahuje prehľad základných príkazov a tipov, ktoré vám uľahčia prácu s nástrojmi.",
    "Exit": "Opustiť program"
}

nav_buttons = ["Nmap", "Gobuster", "Hydra", "Hashcat", "MACchanger","Nikto","Cheat Sheet", "Exit"]
for btn_name in nav_buttons:
    btn = tk.Button(left_sidebar, text=btn_name, font=('Helvetica', 14), bg="#3498db", fg="white",
                    command=lambda name=btn_name: Clicked_button(name))
    btn.pack(fill="x", padx=10, pady=5)
    CreateToolTip(btn, tooltip_texts.get(btn_name, ""))




def toggle_logging():
    global logging_enabled, logging_button
    logging_enabled.set(not logging_enabled.get())
    if logging_enabled.get():
        logging_button.config(text="Zakázat logovanie")
    else:
        logging_button.config(text="Povolit logovanie")
    print("Login status:", logging_enabled.get())

target_label = tk.Label(left_sidebar, text="Cieľ/Doména:", font=('Helvetica', 12), bg="#2c3e50", fg="white")
target_label.pack(fill="x", padx=5, pady=5)
target_input = tk.Entry(left_sidebar, font=('Helvetica', 12))
target_input.pack(fill="x", padx=5, pady=5)

port_label = tk.Label(left_sidebar, text="Port/Služba:", font=('Helvetica', 12), bg="#2c3e50", fg="white")
port_label.pack(fill="x", padx=5, pady=5)
port_input = tk.Entry(left_sidebar, font=('Helvetica', 12))
port_input.pack(fill="x", padx=5, pady=5)

update_button = tk.Button(left_sidebar, text="Aktualizovať cieľ/port", font=('Helvetica', 12), bg="#e67e22", fg="white", command=update_target)
update_button.pack(fill="x", padx=5, pady=5)

logging_enabled = tk.BooleanVar(value=False)
logging_button = tk.Button(left_sidebar, text="Povoliť logovanie",font=('Helvetica', 12),command=toggle_logging,bg="#2c3e50",fg="white")
logging_button.pack(padx=5, pady=5)

auto_test = tk.Button(left_sidebar, text="Automatizovaný test", font=('Helvetica', 12), bg="#27ae60", fg="white", command=auto_testing)
auto_test.pack(fill="x", padx=5, pady=5)

window.mainloop()
