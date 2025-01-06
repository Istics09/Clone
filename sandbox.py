import subprocess
import getpass

def run_sudo_command():
    """Interaktív jelszókérés csillaggal, majd sudo parancs futtatása."""
    try:
        # Jelszó bekérése csillaggal
        password = getpass.getpass("Sudo jelszó: ")

        # Példa parancs futtatása sudo-val
        command = "airmon-ng start wlan0"

        process = subprocess.run(
            f"echo {password} | sudo -S {command}",
            shell=True,
            text=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE
        )

        # Kimenet kiírása
        print("Kimenet:")
        print(process.stdout)
        print("Hibák:")
        print(process.stderr)
    except Exception as e:
        print(f"Hiba történt: {str(e)}")

# Használat
run_sudo_command()
