import tkinter as tk
from tkinter import messagebox
import threading
import subprocess
import datetime
import logging

# Create a basic Tkinter window with an entry for the target and a button to start testing.
root = tk.Tk()
root.title("Penetration Testing Automation")

target_label = tk.Label(root, text="Target/IP:")
target_label.pack(padx=10, pady=5)

info = tk.Label(root, text="Target provide without www. and http or https in format domain.tld")
info.pack(padx=10, pady=5)

target_input = tk.Entry(root, width=40)
target_input.pack(padx=10, pady=5)

def run_command_live(command, description):
    """
    Futtat egy parancsot és valós időben logolja a stdout/stderr kimenetet.
    """
    logging.info("Starting %s with command: %s", description, command)
    process = subprocess.Popen(
        command,
        shell=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
        bufsize=1  # sorosítva olvassuk
    )

    def log_output(stream, log_func, stream_name):
        for line in iter(stream.readline, ''):
            log_func("%s %s: %s", description, stream_name, line.rstrip())
        stream.close()

    stdout_thread = threading.Thread(target=log_output, args=(process.stdout, logging.info, "STDOUT"))
    stderr_thread = threading.Thread(target=log_output, args=(process.stderr, logging.error, "STDERR"))
    stdout_thread.start()
    stderr_thread.start()

    process.wait()
    stdout_thread.join()
    stderr_thread.join()
    logging.info("%s completed", description)


def automatization_testing():
    # Set up logging with a custom log file name based on the current date and time.
    now = datetime.datetime.now()
    log_filename = f"{now.year}-{now.month:02d}-{now.day:02d}-{now.hour:02d}-{now.minute:02d}-{now.second:02d}-Automatizate_testing.log"
    # Note: logging.basicConfig() only works once per session. If you run this function multiple times,
    # you may need to reconfigure or restart the app.
    logging.basicConfig(
        filename=log_filename,
        level=logging.INFO,
        format="%(asctime)s - %(levelname)s - %(message)s"
    )
    logging.info("=== Starting full penetration test ===")

    # Get target from the input field.
    target = target_input.get().strip()
    if not target:
        messagebox.showerror("Missing target", "Please provide a target")
        logging.error("Missing target, quitting.")
        return

    nikto_command = f"nikto -h http://{target} -ask no -Tuning 1 -maxtime 10"
    run_command_live(nikto_command, "Nikto started")

# Button to start the penetration testing automation.
test_button = tk.Button(root, text="Start Penetration Test", command=automatization_testing)
test_button.pack(padx=10, pady=10)

root.mainloop()
