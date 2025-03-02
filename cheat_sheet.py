import tkinter as tk
from tkinter import messagebox
import tkinter.font as tkfont


def main():
    root = tk.Tk()
    root.title("Penetration Testing Cheatsheet")
    root.geometry("800x600")
    
    # Testreszabené fonty
    header_font = tkfont.Font(family="Helvetica", size=16, weight="bold")
    command_font = tkfont.Font(family="Courier", size=12)
    description_font = tkfont.Font(family="Helvetica", size=12)
    
    # Ľavý sidebar
    sidebar = tk.Frame(root, width=200, bg="#2c3e50")
    sidebar.pack(side="left", fill="y")
    
    title_label = tk.Label(sidebar, text="Nástroje", bg="#2c3e50", fg="white", font=header_font)
    title_label.pack(pady=10)
    
    # Pravý panel – scrollovateľný obsah
    right_sidebar = tk.Frame(root, bg="#34495e", width=300)
    right_sidebar.pack(side="right", fill="both", expand=True, padx=10, pady=10)
    
    # Vytvorenie canvasu a scrollbar-u v pravom paneli
    canvas = tk.Canvas(right_sidebar, bg="white")
    scrollbar = tk.Scrollbar(right_sidebar, orient="vertical", command=canvas.yview)
    canvas.configure(yscrollcommand=scrollbar.set)
    scrollbar.pack(side="right", fill="y")
    canvas.pack(side="left", fill="both", expand=True)
    

    main_frame = tk.Frame(canvas, bg="white")
    canvas.create_window((0, 0), window=main_frame, anchor="nw")
    

    def on_configure(event):
        canvas.configure(scrollregion=canvas.bbox("all"))
    main_frame.bind("<Configure>", on_configure)
    

    def copy_to_clipboard(text):
        root.clipboard_clear()
        root.clipboard_append(text)
        #messagebox.showinfo("Kopírovanie", "Príkaz bol skopírovaný do schránky!")
    

    def clear_main_frame():
        for widget in main_frame.winfo_children():
            widget.destroy()
    
    # Funkcia: pridať sekciu s príkazom, popisom a tlačidlom na kopírovanie
    def add_command_section(command_text, description):
        section_frame = tk.Frame(main_frame, bg="white", pady=5)
        section_frame.pack(fill="x", padx=10, pady=5)
        command_label = tk.Label(section_frame, text=command_text, font=command_font, bg="#ecf0f1",
                                  anchor="w", justify="left", padx=5, pady=5)
        command_label.pack(fill="x")
        desc_label = tk.Label(section_frame, text=description, font=description_font, bg="white",
                               anchor="w", justify="left", wraplength=550)
        desc_label.pack(fill="x", pady=(2, 5))
        copy_button = tk.Button(section_frame, text="Kopírovať", command=lambda: copy_to_clipboard(command_text))
        copy_button.pack(anchor="e", padx=5, pady=2)
    
    # Funkcia: aktualizácia obsahu podľa vybraného nástroja
    def update_content(tool):
        clear_main_frame()
        tool_header = tk.Label(main_frame, text=tool, font=header_font, bg="white", anchor="w")
        tool_header.pack(fill="x", padx=10, pady=10)
        
        if tool == "Nmap":
            commands = [
                ("nmap -A target", "Úplné prehľadávanie: Detekcia operačného systému, služieb a ďalších informácií."),
                ("nmap -sS target", "Tichý SYN sken: Skener, ktorý môže obísť firewally a nevyvola podozrenie."),
                ("nmap -Pn target", "Vynechanie zisťovania hostov: Použitie v prípadoch, keď zisťovanie hostov zlyháva."),
                ("nmap target -p PORT", "Skenovanie konkrétneho portu: Nahraďte 'PORT' číslom portu, ktorý chcete skenovať."),
                ("nmap target -p START-END", "Skenovanie rozsahu portov: Nahraďte 'START' a 'END' číslami definujúcimi rozsah portov."),
                ("nmap target -p-", "Skenovanie všetkých portov: Prehľadá všetky porty od 1 do 65535."),
                ("nmap target -F", "Rýchly sken: Použitie preddefinovaného zoznamu najčastejšie používaných portov."),
                ("nmap target --top-ports NUMBER", "Skenovanie najpoužívanejších portov: Nahraďte 'NUMBER' počtom portov, ktoré chcete skenovať."),
                ("nmap -O target", "Detekcia operačného systému: Pokusí sa identifikovať operačný systém cieľa."),
                ("nmap target -sn", "Lokálny sken: Zistí aktívne hosty v lokálnej sieti.")
            ]
        elif tool == "Gobuster":
            commands = [
                ("gobuster dir -u http://target -w /path/to/wordlist.txt", "Vyhľadávanie adresárovej štruktúry webovej stránky pomocou slovníka."),
                ("gobuster dns -d target -w /path/to/subdomains.txt", "Enumerácia subdomén pre cieľovú doménu pomocou slovníka."),
                ("gobuster vhost -u http://target -w /path/to/wordlist.txt", "Enumerácia virtuálnych hostov na webovom serveri pomocou slovníka."),
                ("gobuster s3 -u target -w /path/to/wordlist.txt", "Vyhľadávanie verejných Amazon S3 bucketov pomocou slovníka."),
                ("gobuster fuzz -u http://target/FUZZ -w /path/to/wordlist.txt", "Fuzzovanie URL ciest na webovom serveri pomocou slovníka.")
            ]
        elif tool == "Hydra":
            commands = [
                ("hydra -L users.txt -P passwords.txt ftp://target", "Brute-force útok na FTP prihlásenie pomocou zoznamu používateľov a hesiel."),
                ("hydra -L users.txt -P passwords.txt ssh://target", "Brute-force útok na SSH prihlásenie s použitím zoznamu používateľov a hesiel."),
                ("hydra -L users.txt -P passwords.txt telnet://target", "Brute-force útok na Telnet prihlásenie pomocou zoznamu používateľov a hesiel."),
                ("hydra -L users.txt -P passwords.txt smtp://target", "Brute-force útok na SMTP autentifikáciu s použitím zoznamu používateľov a hesiel.")
            ]
        elif tool == "Macchanger":
            commands = [
                ("macchanger -r eth0", "Úplne náhodne zmení MAC adresu rozhrania eth0."),
                ("macchanger -s eth0", "Zobrazí aktuálnu MAC adresu rozhrania eth0."),
                ("macchanger -p eth0", "Zobrazí trvalú (originálnu) MAC adresu rozhrania eth0."),
                ("macchanger -m 00:11:22:33:44:55 eth0", "Nastaví konkrétnu MAC adresu (00:11:22:33:44:55) na rozhraní eth0."),
                ("macchanger -a eth0", "Vyberie náhodnú MAC adresu z rovnakého výrobcu pre rozhranie eth0.")
            ]
        elif tool == "Nikto":
            commands = [
                ("nikto -h http://domain.tld", 
                 "Základný scan: Spustí základnú kontrolu webovej aplikácie na porte 80."),

                ("nikto -h https://domain.tld -ssl", 
                 "Scan s povoleným protokolom SSL (HTTPS). Môžeš zadať aj konkrétny port, napr. -p 443."),

                ("nikto -h domain.tld -p 8080", 
                 "Scan na špecifickom porte (8080)."),

                ("nikto -h domain.tld -ask no", 
                 "Automatický režim: Nikto sa nespýta na potvrdenie (napr. pred prerušením testu)."),

                ("nikto -h domain.tld -Tuning 1,2,4", 
                 "Ladí sken tak, aby kontroloval len určité typy zraniteľností (1=konfiguračné chyby, 2=CGI, 4=verzie)."),

                ("nikto -h domain.tld -maxtime 60", 
                 "Obmedzí beh skenu na maximálne 60 sekúnd (užitočné na rýchle testy)."),

                ("nikto -h domain.tld -o scan.txt", 
                 "Uloží výsledok skenu do súboru scan.txt v textovom formáte."),

                ("nikto -h domain.tld -Format csv -o scan.csv", 
                 "Export výsledkov do CSV formátu, uložené v súbore scan.csv."),

                ("nikto -h domain.tld -C all", 
                 "Kompletný scan všetkých kontrol (podstatne dlhšie trvá, ale je detailný).")
            ]
        elif tool == "Linux":
            commands = [
                ("ls -l", "Zobrazí obsah aktuálneho adresára v detailnom (dlhom) formáte."),
                ("pwd", "Zobrazí absolútnu cestu (pracovný adresár), v ktorej sa práve nachádzaš."),
                ("cd /cesta", "Zmení aktuálny adresár na /cesta."),
                ("mkdir novy_priecinok", "Vytvorí nový priečinok s názvom 'novy_priecinok'."),
                ("rm subor.txt", "Zmaže súbor 'subor.txt'. Používaj opatrne, operácia je nevratná."),
                ("mv stary_nazov.txt novy_nazov.txt", "Premenuje alebo presunie 'stary_nazov.txt' na 'novy_nazov.txt'."),
                ("cp subor.txt /cielova/cesta", "Skopíruje súbor 'subor.txt' do priečinka '/cielova/cesta'."),
                ("grep 'hladany_text' subor.txt", "Vyhľadá riadky obsahujúce 'hladany_text' v súbore 'subor.txt'."),
                ("find /home -name '*.txt'", "Vyhľadá všetky súbory s príponou .txt v priečinku /home (rekurzívne)."),
                ("chmod +x skript.sh", "Pridá spúšťacie (execute) práva pre súbor 'skript.sh'."),
                ("chown user:group subor.txt", "Zmení vlastníka a skupinu súboru 'subor.txt' na 'user:group'."),
                ("nano subor.txt", "Otvára textový editor Nano so súborom 'subor.txt'."),
                ("vim subor.txt", "Otvára textový editor Vim so súborom 'subor.txt'."),
                ("wget http://example.com/subor.tar.gz", "Stiahne súbor 'subor.tar.gz' z adresy http://example.com."),
                ("ping -c 4 google.com", "Pošle 4 testovacie pakety na google.com, čím overí sieťové pripojenie."),
                ("top", "Zobrazí bežiace procesy, využitie CPU a pamäte v reálnom čase."),
            ]           
          
        else:
            commands = []
        
        for cmd, desc in commands:
            add_command_section(cmd, desc)

        canvas.yview_moveto(0)
    
    # Vytvorenie tlačidiel v ľavom sidebar-e
    tools_list = ["Nmap", "Gobuster", "Hydra", "Macchanger","Nikto", "Linux"]
    for t in tools_list:
        if t == "Exit":
            btn = tk.Button(sidebar, text=t, font=description_font, command=root.quit, bg="#e74c3c", fg="white")
        else:
            btn = tk.Button(sidebar, text=t, font=description_font, command=lambda tool=t: update_content(tool), bg="#3498db", fg="white")
        btn.pack(fill="x", padx=10, pady=5)
    
    # Na začiatok zobrazíme cheat sheet pre Nmap MACchanger macchanger
    update_content("Nmap")
    
    root.mainloop()

if __name__ == "__main__":
    main()
