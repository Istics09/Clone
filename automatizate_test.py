import tkinter as tk
from tkinter import messagebox
from tkinter import ttk
import subprocess
import datetime
import logging

def run_command(command, description):
    logging.info("Starting %s with command: %s", description, command)
    try:
        result = subprocess.run(command, shell=True, capture_output=True, text=True)
        logging.info("%s completed successfully.", description)
        if result.stdout:
            for line in result.stdout.splitlines():
                logging.info("%s STDOUT: %s", description, line)
        if result.stderr:
            for line in result.stderr.splitlines():
                logging.error("%s STDERR: %s", description, line)
        return result.stdout
    except Exception as e:
        logging.error("Error during %s: %s", description, e)
        return ""

def run_command_live(command, description):
    logging.info("Starting %s with command: %s", description, command)
    output_lines = []
    try:
        proc = subprocess.Popen(command, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
        while True:
            line = proc.stdout.readline()
            if line:
                logging.info("%s STDOUT: %s", description, line.strip())
                output_lines.append(line)
            else:
                break
        for line in proc.stderr:
            if line:
                logging.error("%s STDERR: %s", description, line.strip())
                output_lines.append(line)
        proc.wait()
        logging.info("%s completed successfully.", description)
        return ''.join(output_lines)
    except Exception as e:
        logging.error("Error during %s: %s", description, e)
        return ""

def automatization_testing(target_input, root):
    now = datetime.datetime.now()
    log_filename = f"{now.year}-{now.month:02d}-{now.day:02d}-{now.hour:02d}-{now.minute:02d}-{now.second:02d}-Automatizate_testing.log"
    logging.basicConfig(
        filename=log_filename,
        level=logging.INFO,
        format="%(asctime)s - %(levelname)s - %(message)s"
    )
    logging.info("=== Starting full penetration test ===")
    
    target = target_input.get().strip()
    if not target:
        messagebox.showerror("Missing target", "Please provide a target")
        logging.error("Missing target, quitting.")
        return

    nmap_command = f"nmap -A {target}"
    nmap_output = run_command(nmap_command, "Nmap scan")

    gobuster_dir_command = f"gobuster dir -u {target} -w dir.txt"
    run_command(gobuster_dir_command, "Gobuster Directory scan")

    gobuster_dns_command = f"gobuster dns -d {target} -w subdomains.txt"
    run_command(gobuster_dns_command, "Gobuster DNS scan")

    if "21/tcp   open" in nmap_output:
        hydra_ftp_command = f"hydra -L users.txt -P passwords.txt ftp://{target}"
        run_command(hydra_ftp_command, "Hydra FTP scan")
    if "22/tcp   open" in nmap_output:
        hydra_ssh_command = f"hydra -L users.txt -P passwords.txt ssh://{target}"
        run_command(hydra_ssh_command, "Hydra SSH scan")
    
    nikto_command = f"nikto -h http://{target} -ask no -Tuning 1 -maxtime 10"
    run_command_live(nikto_command, "Nikto scan")

    logging.info("=== Penetration test completed ===")
    root.destroy()

def main():
    root = tk.Tk()
    root.title("Kraken - Automatizovaný skener")
    root.geometry("400x250")
    root.configure(bg="#2c3e50")
    
    style = ttk.Style()
    style.theme_use("clam")
    style.configure("TLabel", background="#2c3e50", foreground="white", font=("Helvetica", 12))
    style.configure("TEntry", font=("Helvetica", 12))
    style.configure("TButton", font=("Helvetica", 12), padding=6)
    
    main_frame = ttk.Frame(root, padding=20)
    main_frame.pack(expand=True, fill="both")
    
    title_label = ttk.Label(main_frame, text="Automatizovaný penetračný skener", font=("Helvetica", 16, "bold"))
    title_label.pack(pady=(0, 10))
    
    target_label = ttk.Label(main_frame, text="Cieľ/IP adresa")
    target_label.pack(pady=(5, 5))
    
    target_input = ttk.Entry(main_frame, width=40)
    target_input.pack(pady=(0, 10))
    
    info_label = ttk.Label(main_frame, text="Cieľ prosím uviesť bez www. http alebo https!")
    info_label.pack(pady=(0, 10))
    
    test_button = ttk.Button(main_frame, text="Spustiť",
                             command=lambda: automatization_testing(target_input, root))
    test_button.pack(pady=(10, 0))
    
    root.eval('tk::PlaceWindow . center')
    
    root.mainloop()

if __name__ == '__main__':
    main()
