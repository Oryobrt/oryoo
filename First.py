#!/usr/bin/env python3
# loader.py

import os
import sys
import uuid
import time
import random
import platform
import tkinter as tk
from tkinter import messagebox
from datetime import datetime, timedelta
from colorama import Fore, init as colorama_init
import aiohttp
import requests
import threading
import asyncio
import django
from asgiref.sync import sync_to_async


BASE_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.append(os.path.join(BASE_DIR, 'keissho'))

# Set up Django environment
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "keissho.settings")
django.setup()

# Now you can import your Django models
from licenses.models import License
from django.utils import timezone

colorama_init(autoreset=True)

# === CONFIG ===
LICENSE_DIR = r"C:\Users\mark\Desktop\Python\Licenses"
LICENSE_FILE = os.path.join(LICENSE_DIR, "License.json")

# === SPAMMER LOGIC ===
TOKENS = [
    "your_token_1",  # Replace with your actual tokens
    "your_token_2",  # Replace with your actual tokens
    "your_token_3",  # Replace with your actual tokens
    # Add more tokens as needed
]

PROXY_POOL = [
    # Add your proxy pool here
]

use_proxy = False  # Set later

def proxy_url(row: str) -> str:
    host, port, user, pwd = row.split(":")
    return f"http://{user}:{pwd}@{host}:{port}"

def headers(tok):
    return {"Authorization": f"Bot {tok}", "Content-Type": "application/json"}

async def new_session():
    if not use_proxy:
        return aiohttp.ClientSession()
    return aiohttp.ClientSession(
        proxy=proxy_url(random.choice(PROXY_POOL)),
        connector=aiohttp.TCPConnector(limit=0, ssl=False)
    )

session = requests.Session()

# === UTILITIES ===
def clear_screen():
    os.system('cls' if os.name == 'nt' else 'clear')

if os.name == 'nt':
    os.system('title KEiSSHO LAUNCHER')
else:
    sys.stdout.write("\x1b]2;KSH LAUNCHER\x07")

# === HELPER FUNCTIONS ===
def show_messagebox(type_, title, message):
    root = tk.Tk()
    root.withdraw()
    if type_ == "info":
        messagebox.showinfo(title, message)
    elif type_ == "error":
        messagebox.showerror(title, message)
    root.destroy()

def get_hwid():
    return str(uuid.getnode())

# === LICENSE HANDLING ===
async def check_license_online(license_key):
    try:
        API_URL = "http://keishooz.duckdns.org/api/verify-license/"  # Replace with your actual API URL
        async with aiohttp.ClientSession() as session:
            async with session.get(API_URL, params={"license_key": license_key}) as response:
                if response.status == 200:
                    return await response.json()  # License data if found
                else:
                    return None  # Invalid or not found
    except Exception as e:
        print(f"Error checking license: {e}")
        return None

@sync_to_async
def check_license_and_hwid_local(license_key, hwid):
    try:
        license = License.objects.get(license_key=license_key)
        now = timezone.now()

        # Debugging output
        print(f"License found in DB: {license}")
        print(f"License HWID: {license.hwid}, Provided HWID: {hwid}")

        if license.hwid == hwid:
            if license.expiry_date > now:
                return 'matched', license
            else:
                return 'expired', license
        else:
            return 'mismatch', license
    except License.DoesNotExist:
        return 'invalid', None

# === MAIN EXECUTION ===
def simulate_loader():
    print("[loader] Version checking...")
    time.sleep(0.5)
    print("[loader] Downloading update...", flush=True)
    progress = 0
    while progress < 100:
        step = random.randint(5, 15)
        progress = min(progress + step, 100)
        bar = '■' * (progress // 10) + '□' * (10 - progress // 10)
        print(f"\r[{bar}] {progress}%", end='', flush=True)
        time.sleep(0.2)
    print("\n[loader] Latest patch updated.")
    time.sleep(0.5)
    clear_screen()

@sync_to_async
def get_license_by_key(license_key):
    try:
        return License.objects.get(license_key=license_key)
    except License.DoesNotExist:
        return None

async def main():
    simulate_loader()
    user_hwid = get_hwid()
    license_key = input("Enter your license key: ").strip()

    # Check license from the server
    license_data = await check_license_online(license_key)

    if not license_data:
        print(f"License with key {license_key} not found.")
        show_messagebox("error", "INVALID LICENSE", "The provided license key is invalid. Access denied.")
        sys.exit(1)

    print(f"License found: {license_data}")

    # Now we need to check the HWID from the license data.
    if 'hwid' in license_data and license_data['hwid']:
        if license_data['hwid'] == user_hwid:
            print("HWID matched!")
        else:
            print("HWID mismatch.")
            show_messagebox("error", "WRONG HWID", "The HWID does not match the registered one. Access denied.")
            sys.exit(1)
    else:
        print("HWID not set. Binding new HWID...")

        # Send a POST request to bind HWID through the API
        try:
            async with aiohttp.ClientSession() as session:
                async with session.post("http://127.0.0.1:8000/api/bind-hwid/", json={
                    "license_key": license_key,
                    "hwid": user_hwid
                }) as response:
                    result = await response.json()
                    if response.status == 200:
                        print(result.get('message', 'HWID bound successfully.'))
                    else:
                        show_messagebox("error", "BIND HWID ERROR", result.get('error', 'Error binding HWID.'))
                        sys.exit(1)
        except Exception as e:
            print(f"Error binding HWID: {e}")
            show_messagebox("error", "ERROR", "Could not contact the server to bind HWID.")
            sys.exit(1)

        # Small delay to ensure the server has updated the HWID before proceeding
        await asyncio.sleep(1)

    # Recheck the license and HWID locally to ensure it's updated
    status, rec = await check_license_and_hwid_local(license_key, user_hwid)

    if status == 'invalid':
        show_messagebox("error", "INVALID LICENSE", "The provided license key is invalid. Access denied.")
        sys.exit(1)
    elif status == 'mismatch':
        show_messagebox("error", "WRONG HWID", "The HWID does not match the registered one. Access denied.")
        sys.exit(1)
    elif status == 'expired':
        show_messagebox("error", "LICENSE EXPIRED", "Your license has expired. Please renew.")
        sys.exit(1)
    elif status == 'matched':
        show_messagebox("info", "LICENSE VALID", "License and HWID matched successfully!")

    expiration_message = f"Your license will expire on: {calculate_expiration(rec)}"
    show_messagebox("info", "LICENSE EXPIRATION", expiration_message)

    print(Fore.CYAN + f"[i] {len(TOKENS)} tokens loaded.")
    print(Fore.CYAN + f"[i] Proxy mode: {'ON' if use_proxy else 'OFF'}")
    await menu()



# === EXPIRATION ===
def calculate_expiration(rec):
    activated_on = rec.activated_on.timestamp()  # Make sure 'activated_on' is a DateTime object
    exp_date = datetime.fromtimestamp(activated_on) + timedelta(days=30)
    return exp_date.strftime('%B %d, %Y')

async def menu():
    global use_proxy
    use_proxy = input("Use proxies? (y/n): ").lower().startswith("y")

    while True:
        print("\n1) Send DM\n2) Exit")
        choice = input("> ").strip()
        if choice == "1":
            await run_dm_tool()  # Make it async if you're using async operations in run_dm_tool
        elif choice == "2":
            break
        else:
            print("Bad choice.")

async def run_dm_tool():
    clear_screen()
    uid = input("Target user ID: ")
    txt = input("Message text: ")
    if input("Ping user? y/n: ").lower().startswith("y"):
        txt = f"<@{uid}> {txt}"
    loops = int(input("Repeat count: "))
    delay = float(input("Delay between rounds: "))

    if delay == 0:
        for _ in range(loops):
            for tok in TOKENS:
                threading.Thread(target=run_dm_tool, args=(tok, uid, txt), daemon=True).start()
                time.sleep(0.01)  # Optional: tune/remove for max speed
    else:
        for _ in range(loops):
            for tok in TOKENS:
                run_dm_tool(tok, uid, txt)
                time.sleep(delay)

    print(Fore.GREEN + "\nStarted flooding (no join, running in background)!")

# ── ENTRY ────────────────────────────────────────────────────────────────
if __name__ == "__main__":
    asyncio.run(main())
