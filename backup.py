import tkinter as tk
from tkinter import messagebox
import tkinter.font as tkfont
import subprocess, threading, os, signal, datetime, logging, getpass, automatizate_test
import cheat_sheet

# Globálne premenné
current_process = None
open_frame = None
target = "{Domain/IP}"
port = "{Port/Služba}"

# Inicializácia logovania
x = datetime.datetime.now()
if not os.path.exists("logs"):
    os.makedirs("logs")
log_filename = f'logs/{x.year}-{x.month:02d}-{x.day:02d}-{x.hour:02d}-{x.minute:02d}-{x.second:02d}.log'
logging.basicConfig(
    filename=log_filename,
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

# Funkcia na spustenie automatizovaného testu
def auto_testing():
    automatizate_test.main()

def airmon_ng(Name):
    """Spustí príkazy ifconfig a airmon-ng/ifconfig podľa potreby a zobrazí ich výstup."""
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

def Run_Command():
    """Spustí príkaz zadaný do vstupného poľa v samostatnom vlákne."""
    global current_process
    command = command_input.get()
    if not command.strip():
        return
    command_input.delete(0, tk.END)
    thread = threading.Thread(target=run_in_thread, args=(command,))
    thread.daemon = True
    thread.start()

def run_in_thread(command):
    """Spustí príkaz v samostatnom vlákne s reálnym výstupom."""
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
    """Vytvorí konzolu v strednom paneli, ak ešte neexistuje."""
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

def Run_Button_command(command):
    """Nastaví príkaz do vstupného poľa konzoly."""
    global command_input
    if logging_enabled.get():
        logging.info("Spúšťam príkaz: %s", command)
    command_input.delete(0, tk.END)
    command_input.insert(0, command)

def clear_right_sidebar():
    """Vymaže obsah pravého panela."""
    for widget in right_sidebar.winfo_children():
        widget.destroy()

def update_target():
    """Aktualizuje globálne premenné pre cieľ a port zo vstupov."""
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

def add_right_button(text, command):
    """Pridá tlačidlo do pravého panela s daným textom a príkazom."""
    btn = tk.Button(right_sidebar, text=text, font=('Helvetica', 12), bg="#2980b9", fg="white",
                    activebackground="black", activeforeground="white", cursor="hand2",
                    command=lambda: Run_Button_command(command) if isinstance(command, str) else command())
    btn.pack(pady=5, padx=5, fill="x")


def Clicked_button(Name):
    """Spracováva kliknutia na tlačidlá v ľavom paneli a aktualizuje pravý panel podľa vybraného nástroja."""
    global open_frame, current_process

    if Name == "Exit":
        window.destroy()
    elif Name == "Nmap":
        create_console()
        clear_right_sidebar()
        add_right_button("Konkretný port", f"nmap {target} -p {port}")
        add_right_button("Rozsah portov", f"nmap {target} -p (Začiatočný port)-(Koncový port)")
        add_right_button("Všetky porty", f"nmap {target} -p-")
        add_right_button("Vyhľadať službu", f"nmap {target} -p {port}")
        add_right_button("Rýchly sken", f"nmap {target} -F")
        add_right_button("Najpoužívanejšie porty", f"nmap {target} --top-ports (Počet portov)")
        add_right_button("Detekcia OS", f"nmap -O {target}")
        add_right_button("Lokálny sken", f"nmap {target} -sn")
        add_right_button("Decoy sken", "nmap -D {Sender IP} {Target}")
        add_right_button("Nastaviť zdrojový port", f"nmap -g {port} {target}")
        open_frame = "Nmap"
        right_sidebar.config(bg="#34495e")
    elif Name == "Gobuster":
        current_process = "Gobuster"
        create_console()
        clear_right_sidebar()
        add_right_button("Hľadanie adresárov", f"gobuster dir -u {target} -w dir.txt")
        add_right_button("Hľadanie subdomén", f"gobuster dns -d {target} -w subdomains.txt")
        add_right_button("Hľadanie virtuálnych hostov", f"gobuster vhost -u http://{target} -w /path/to/wordlist.txt")
        add_right_button("Vyhľadávanie S3 bucketov", f"gobuster s3 -u {target} -w /path/to/wordlist.txt")
        add_right_button("Fuzzovanie URL ciest", f"gobuster fuzz -u http://{target}/FUZZ -w /path/to/wordlist.txt")
        open_frame = "Gobuster"
        right_sidebar.config(bg="#34495e")
    elif Name == "Hydra":
        current_process = "Hydra"
        create_console()
        clear_right_sidebar()
        add_right_button("Lámač hesiel (FTP)", f"hydra -t 1 -l {getpass.getuser()} -P passwords.txt {target} ftp")
        add_right_button("Prihlásenie SSH", f"hydra -v -u -L users.txt -P passwords.txt -t 1 {target} ssh")
        add_right_button("Lámač hesiel (Telnet)", f"hydra -L users.txt -P passwords.txt {target} telnet")
        add_right_button("Lámač hesiel (SMTP)", f"hydra -L users.txt -P passwords.txt {target} smtp")
        open_frame = "Hydra"
        right_sidebar.config(bg="#34495e")
    elif Name == "Aircrack-ng":
        current_process = "Aircrack-ng"
        create_console()
        clear_right_sidebar()
        add_right_button("Povoliť monitorovací režim", lambda: airmon_ng("Aircrack-ng"))
        add_right_button("Skenovať dostupné siete", "airodump-ng {Zariadenie}")
        add_right_button("Počúvať sieť", "airodump-ng -c {Kanál} --bssid {MAC} -w dump {Zariadenie}")
        add_right_button("Lámať zachytený súbor", "aircrack-ng -b {MAC} {Súbor}")
        open_frame = "Aircrack-ng"
        right_sidebar.config(bg="#34495e")
    elif Name == "Macchanger":
        current_process = "Macchanger"
        create_console()
        clear_right_sidebar()
        add_right_button("Náhodná zmena MAC", "macchanger -r eth0")
        add_right_button("Zobraziť aktuálnu MAC", "macchanger -s eth0")
        add_right_button("Zobraziť originálnu MAC", "macchanger -p eth0")
        add_right_button("Nastaviť konkrétnu MAC", "macchanger -m 00:11:22:33:44:55 eth0")
        add_right_button("Výber náhodnej MAC od výrobcu", "macchanger -a eth0")
        open_frame = "Macchanger"
        right_sidebar.config(bg="#34495e")
    elif Name == "Cheat Sheet":
        current_process = "Cheat Sheet"
        cheat_sheet.main()

# Vytvorenie hlavného okna (fullscreen)
window = tk.Tk()
window.title("Kraken - Nástroj na penetračné testovanie")
window.config(bg="#1e1e1e")
window.geometry("1280x720")
window.bind("<F2>", interrupt_process)
window.bind("<Control-c>", copy_to_clipboard)
window.bind("<Escape>", lambda event: window.destroy())
window.eval('tk::PlaceWindow . center')

# Rozloženie do troch hlavných rámcov
left_sidebar = tk.Frame(window, width=200, bg="#2c3e50", relief="raised", borderwidth=2)
left_sidebar.pack(side="left", fill="y")

center_frame = tk.Frame(window, bg="#1e1e1e")
center_frame.pack(side="left", fill="both", expand=True)

right_sidebar = tk.Frame(window, width=250, bg="#34495e", relief="raised", borderwidth=2)
right_sidebar.pack(side="right", fill="y")

# Tlačidlá v ľavom paneli
nav_buttons = ["Nmap", "Gobuster", "Hydra", "Aircrack-ng", "Macchanger","Cheat Sheet", "Exit"]
for btn_name in nav_buttons:
    btn = tk.Button(left_sidebar, text=btn_name, font=('Helvetica', 14), bg="#3498db", fg="white",
                    command=lambda name=btn_name: Clicked_button(name))
    btn.pack(fill="x", padx=10, pady=5)

# Vstupy pre cieľ a port v ľavom paneli
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
logging_checkbox = tk.Checkbutton(left_sidebar, text="Povoliť logovanie", font=('Helvetica', 12), variable=logging_enabled, bg="#2c3e50", fg="white")
logging_checkbox.pack(padx=5, pady=5)

auto_test = tk.Button(left_sidebar, text="Automatizovaný test", font=('Helvetica', 12), bg="#27ae60", fg="white", command=auto_testing)
auto_test.pack(fill="x", padx=5, pady=5)

window.mainloop()
