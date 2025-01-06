import tkinter as tk
from tkinter import *
import subprocess
import threading
import os
import signal
import getpass

# Globális változó a futó folyamat tárolására
current_process = None
current_view = None
right_sidebar = None
console = False
processRunning = False
open_frame = None


def airmon_ng():
    """Ifconfig és airmon-ng parancs futtatása, kimenet megjelenítése."""
    try:
        # Ifconfig futtatása
        ifconfig_process = subprocess.run(
            "ifconfig",
            shell=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True
        )
        ifconfig_output = ifconfig_process.stdout

        # Kimenet megjelenítése az output mezőben
        output_text.config(state="normal")
        output_text.insert(tk.END, "=== =========================================== ===\n")
        output_text.insert(tk.END, ifconfig_output + "\n")
        output_text.insert(tk.END, "=== =========================================== ===\n")
        output_text.config(state="disabled")


        # Kimenet megjelenítése az output mezőben
        output_text.config(state="normal")
        output_text.insert(tk.END, "Please choose which is your WLAN device!\n")
        Run_Button_command("sudo airmon-ng start {device}")
        output_text.config(state="disabled")

    except Exception as e:
        # Hibaüzenet megjelenítése
        output_text.config(state="normal")
        output_text.insert(tk.END, f"Hiba történt: {str(e)}\n")
        output_text.config(state="disabled")


def Run_Command():
    """A beírt parancs végrehajtása külön szálban."""
    global current_process

    # Parancs beolvasása az input mezőből
    command = command_input.get()
    if not command.strip():
        return

    # Töröljük az input mezőt
    command_input.delete(0, tk.END)

    # Indítsuk el a subprocess-t külön szálban
    thread = threading.Thread(target=run_in_thread, args=(command,))
    thread.daemon = True
    thread.start()


def run_in_thread(command):
    """Parancs futtatása külön szálban, valós idejű kimenettel."""
    global current_process

    try:
        # Subprocess indítása új folyamatcsoportban
        current_process = subprocess.Popen(
            command,
            shell=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            preexec_fn=os.setsid  # Új folyamatcsoport indítása
        )

        # Valós idejű kimenet kiírása
        for line in iter(current_process.stdout.readline, ''):
            if line:
                output_text.config(state="normal")  # Állítsuk szerkeszthetőre
                output_text.insert(tk.END, line.strip() + "\n")  # Adjuk hozzá a sort
                output_text.see(tk.END)  # Görgessünk az aljára
                output_text.config(state="disabled")  # Állítsuk vissza readonly állapotba

        # Hibakimenet kezelése
        for line in iter(current_process.stderr.readline, ''):
            if line:
                output_text.config(state="normal")
                output_text.insert(tk.END, f"ERROR: {line.strip()}\n")
                output_text.see(tk.END)
                output_text.config(state="disabled")

        # Várjuk meg a folyamat végét
        current_process.wait()

    except Exception as e:
        output_text.config(state="normal")
        output_text.insert(tk.END, f"Hiba történt: {str(e)}\n")
        output_text.config(state="disabled")
    finally:
        current_process = None  # Folyamat vége



def interrupt_process(event=None):
    """Futó folyamat megszakítása Ctrl+C-vel."""
    global current_process
    if current_process and current_process.poll() is None:  # Ha folyamat fut
        # Teljes folyamatcsoport megszakítása
        os.killpg(os.getpgid(current_process.pid), signal.SIGTERM)
        output_text.config(state="normal")  # Állítsuk szerkeszthetőre
        output_text.insert(tk.END, "Folyamat megszakítva!\n")
        output_text.config(state="disabled")  # Állítsuk nem szerkezthetőre


def copy_to_clipboard(event=None):
    """Kijelölt szöveg másolása a vágólapra Ctrl+C használatával."""
    try:
        selected_text = output_text.selection_get()
        window.clipboard_clear()
        window.clipboard_append(selected_text)
        window.update()  # Vágólap frissítése
        #print("Szöveg másolva a vágólapra.")
    except tk.TclError:
        print("Nincs kijelölt szöveg.")

def create_console():
    global current_view
    global right_sidebar
    global console

    if console == True:
        return

    console = True

    right_sidebar = tk.Frame(window, width=180, bg="cornsilk4", relief="raised", borderwidth=0)
    right_sidebar.pack(side="right", fill="y")
    right_sidebar.pack_propagate(False)


    global output_text
    output_text = Text(window, height=31, width=60, font=('Arial', 15), bg="black", fg="green", state="disabled", wrap="word")
    output_text.pack(padx=10, pady=(10, 5), fill="x")

    global command_input
    command_input = tk.Entry(window, bg="black", fg="green", insertbackground="green", insertofftime=500, insertontime=500)
    command_input.pack(padx=10, pady=5, fill="x")

    Welcome_message = "Welcome in Kraken!\n"

    output_text.config(state="normal")
    output_text.insert(tk.END, Welcome_message)
    output_text.config(state="disabled")

    command_input.bind("<Return>", lambda event: Run_Command())

def Run_Button_command(command):
    global command_input
    
    command_input.delete(0, tk.END)
    command_input.insert(0, command)



def Clicked_button(Name):
    global current_view
    global right_sidebar
    global open_frame


    if Name == "Exit":
        window.destroy()
    elif Name == "Nmap":

        create_console()

        if open_frame != "Nmap":
            for widget in right_sidebar.winfo_children():
                widget.destroy()

            button1 = tk.Button(right_sidebar, text="Concrete port", width=150, activebackground="black", activeforeground="white", cursor="hand2", command=lambda: Run_Button_command("nmap {IP/Domain} -p {Port}"))
            button1.pack(pady=5)
            button2 = tk.Button(right_sidebar, text="Range port", width=150, activebackground="black", activeforeground="white", cursor="hand2", command=lambda: Run_Button_command("nmap {IP/Domain} -p {Starting port} - {Ending port}"))
            button2.pack(pady=5)
            button3 = tk.Button(right_sidebar, text="All ports", width=150, activebackground="black", activeforeground="white", cursor="hand2", command=lambda: Run_Button_command("nmap {IP/Domain} -p-"))
            button3.pack(pady=5)
            button4 = tk.Button(right_sidebar, text="Search for Service", width=150, activebackground="black", activeforeground="white", cursor="hand2", command=lambda: Run_Button_command("nmap {IP/Domain} -p {Service name}"))
            button4.pack(pady=5)
            button5 = tk.Button(right_sidebar, text="Fast scan", width=150, activebackground="black", activeforeground="white", cursor="hand2", command=lambda: Run_Button_command("nmap {IP/Domain} -F"))
            button5.pack(pady=5)
            button6 = tk.Button(right_sidebar, text="Top ports", width=150, activebackground="black", activeforeground="white", cursor="hand2", command=lambda: Run_Button_command("nmap {IP/Domain} --top-ports {Range of port}"))
            button6.pack(pady=5)
            button7 = tk.Button(right_sidebar, text="Try to OS detection", width=150, activebackground="black", activeforeground="white", cursor="hand2", command=lambda: Run_Button_command("nmap -O {IP/Domain}"))
            button7.pack(pady=5)
            button8 = tk.Button(right_sidebar, text="Local scan", width=150, activebackground="black", activeforeground="white", cursor="hand2", command=lambda: Run_Button_command("nmap {IP} -sn"))
            button8.pack(pady=5)
            button9 = tk.Button(right_sidebar, text="Decoy scan", width=150, activebackground="black", activeforeground="white", cursor="hand2", command=lambda: Run_Button_command("nmap -D {Sender IP} {Target}"))
            button9.pack(pady=5)
            button10 = tk.Button(right_sidebar, text="Source port set", width=150, activebackground="black", activeforeground="white", cursor="hand2", command=lambda: Run_Button_command("nmap -g {Port} {IP}"))
            button10.pack(pady=5)


        open_frame = "Nmap"
        current_process = "Nmap"
        right_sidebar.config(bg="green")



    elif Name == "Gobuster":
        current_process = "Gobuster"
        create_console()
        
        if open_frame != "Gobuster":
            for widget in right_sidebar.winfo_children():
                widget.destroy()
                
            button1 = tk.Button(right_sidebar, text="Folder Searcher", width=150, activebackground="black", activeforeground="white", cursor="hand2", command=lambda: Run_Button_command("gobuster dir -u {Url} -w dir.txt"))
            button1.pack(pady=5)
            button2 = tk.Button(right_sidebar, text="Subdomain Searcher", width=150, activebackground="black", activeforeground="white", cursor="hand2", command=lambda: Run_Button_command("gobuster dns -d {Url} -w subdomains.txt"))
            button2.pack(pady=5)




        open_frame = "Gobuster"
        current_process = "Gobuster"

        right_sidebar.config(bg="blue")


    elif Name == "Hydra":
        current_process = "Hydra"
        create_console()

        if open_frame != "Hydra":
            for widget in right_sidebar.winfo_children():
                widget.destroy()
        
            button1 = tk.Button(right_sidebar, text="Password cracker", width=150, activebackground="black", activeforeground="white", cursor="hand2", command=lambda: Run_Button_command("hydra -t 1 -l {Username} -P passwords.txt {IP} ftp"))
            button1.pack(pady=5)
            button2 = tk.Button(right_sidebar, text="SSH Login", width=150, activebackground="black", activeforeground="white", cursor="hand2", command=lambda: Run_Button_command("hydra -v -u -L users.txt -P passwords.txt -t 1 -u {IP} ssh"))
            button2.pack(pady=5)


        open_frame = "Hydra"
        current_process = "Hydra"

        right_sidebar.config(bg="red")

    elif Name == "Aircrack-ng":
        current_process = "Aircrack-ng"
        create_console()

        if open_frame != "Aircrack-ng":
            for widget in right_sidebar.winfo_children():
                widget.destroy()
        
            button1 = tk.Button(right_sidebar, text="Enable monitor mode", width=150, activebackground="black", activeforeground="white", cursor="hand2", command=airmon_ng)#command=lambda: Run_Button_command("airmon-ng start {device}")
            button1.pack(pady=5)
            button2 = tk.Button(right_sidebar, text="Scan avaliable networks", width=150, activebackground="black", activeforeground="white", cursor="hand2", command=lambda: Run_Button_command("airodump-ng wlan0mon"))#Device ID
            button2.pack(pady=5)
            button3 = tk.Button(right_sidebar, text="Listening to the network", width=150, activebackground="black", activeforeground="white", cursor="hand2", command=lambda: Run_Button_command("airodump-ng -c {Channel} --bssid {MAC} -w dump wlan0mon"))#Device ID
            button3.pack(pady=5)
            button4 = tk.Button(right_sidebar, text="Cracking the captured file", width=150, activebackground="black", activeforeground="white", cursor="hand2", command=lambda: Run_Button_command("aircrack-ng -b {MAC} {Filename}"))#Device ID
            button4.pack(pady=5)

        
        open_frame = "Aircrack-ng"
        current_process = "Aircrack-ng"

        right_sidebar.config(bg="grey")



window = tk.Tk()
window.title("Kraken - Penetration testing tool")
width = window.winfo_screenwidth()
height = window.winfo_screenheight()

window.geometry("%dx%d" % (width, height))
window['bg'] = 'black'
window.resizable(width=False, height=False)

# esemény kezelések
window.bind("<F2>", interrupt_process)

window.bind("<Control-c>", copy_to_clipboard)


sidebar = tk.Frame(window, width=150, bg="gray", relief="raised", borderwidth=2)
sidebar.pack(side="left", fill="y")

# Gombok a sidebaron
buttons = ["Nmap", "Gobuster", "Hydra", "Aircrack-ng", "Exit"]
for button_name in buttons:
    button = tk.Button(sidebar, text=button_name, command=lambda name=button_name: Clicked_button(name))
    button.pack(fill="x", padx=5, pady=5)

window.mainloop()
