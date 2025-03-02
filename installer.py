import tkinter as tk
from tkinter import scrolledtext, messagebox
import subprocess
import threading
import os
import sys

def log(message):
    output_text.config(state="normal")
    output_text.insert(tk.END, message)
    output_text.see(tk.END)
    output_text.config(state="disabled")

def install_tools():
    # Zoznam inštalovateľných nástrojov: kľúč je názov (pre informáciu), hodnota je balík pre apt-get
    tools = {
        "Nmap": "nmap",
        "Gobuster": "gobuster",
        "Nikto": "nikto",
        "Hydra": "hydra",
        "Macchanger": "macchanger",
        "Aircrack-ng": "aircrack-ng",
        "Seclists (wordlist)": "seclists"
    }

    log("Spúšťam inštaláciu...\n\n")
    
    # Najprv vykonáme update repozitárov
    update_cmd = "apt-get update"
    log(f"Spúšťam: {update_cmd}\n")
    try:
        result = subprocess.run(update_cmd, shell=True, capture_output=True, text=True)
        log(result.stdout)
        if result.returncode != 0:
            log(result.stderr)
            log("Chyba počas aktualizácie repozitárov.\n")
            return
    except Exception as e:
        log(f"Výnimka počas apt-get update: {e}\n")
        return

    # Inštalácia jednotlivých nástrojov
    for tool_name, package in tools.items():
        cmd = f"apt-get install -y {package}"
        log(f"\nInštalujem {tool_name} príkazom: {cmd}\n")
        try:
            result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
            log(result.stdout)
            if result.returncode != 0:
                log(result.stderr)
                log(f"Inštalácia {tool_name} zlyhala (návratový kód {result.returncode}).\n")
            else:
                log(f"{tool_name} bol úspešne nainštalovaný.\n")
        except Exception as e:
            log(f"Výnimka pri inštalácii {tool_name}: {e}\n")
    
    log("\nInštalácia dokončená.\n")

def start_installation():
    threading.Thread(target=install_tools, daemon=True).start()

def check_root():
    if os.geteuid() != 0:
        messagebox.showerror("Chyba", "Tento skript musí byť spustený s oprávneniami root (sudo).")
        sys.exit(1)

check_root()


root = tk.Tk()
root.title("Inštalačný skript pre penetračné nástroje")
root.geometry("800x500")
root.configure(bg="#2c3e50")

install_button = tk.Button(root, text="Spustiť inštaláciu", font=('Helvetica', 14),
                           command=start_installation, bg="#16a085", fg="white")
install_button.pack(padx=10, pady=10)

output_text = scrolledtext.ScrolledText(root, wrap=tk.WORD, width=100, height=25, font=('Helvetica', 10), bg="black", fg="lime")
output_text.pack(padx=10, pady=10)
output_text.config(state="disabled")

root.mainloop()
