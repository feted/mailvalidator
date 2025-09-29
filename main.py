#!/usr/bin/env python3
"""
email_checker.py

Run:
    python email_checker.py
"""

import concurrent.futures
import requests
import sys
import time
from urllib.parse import quote
from colorama import Fore, Style, init as colorama_init
import threading

# Initialize colorama
colorama_init(autoreset=True)

# ASCII banner
BANNER = Fore.CYAN + Style.BRIGHT + r"""
  _____                 _ _     _____ _               _             
 | ____|_   _____ _ __ (_) |_  | ____| | _____      _| | _____ _ __ 
 |  _| \ \ / / _ \ '_ \| | __| |  _| | |/ _ \ \ /\ / / |/ / _ \ '__|
 | |___ \ V /  __/ | | | | |_  | |___| |  __/\ V  V /|   <  __/ |   
 |_____| \_/ \___|_| |_|_|\__| |_____|_|\___| \_/\_/ |_|\_\___|_|   

 Multi-threaded Skrapp open email verifier
"""

# Skrapp open verify base endpoint
BASE_URL = "https://api.skrapp.io/v3/open/verify?email={email}"

# Full headers copied from your capture
DEFAULT_HEADERS = {
    ":authority": "api.skrapp.io",
    ":method": "GET",
    ":path": "/v3/open/verify",
    ":scheme": "https",
    "accept": "*/*",
    "accept-encoding": "gzip, deflate, br, zstd",
    "accept-language": "en-GB,en;q=0.9,id;q=0.8",
    "content-type": "application/json",
    "dnt": "1",
    "origin": "https://skrapp.io",
    "priority": "u=1, i",
    "referer": "https://skrapp.io/",
    "sec-ch-ua": '"Chromium";v="140", "Not=A?Brand";v="24", "Google Chrome";v="140"',
    "sec-ch-ua-mobile": "?0",
    "sec-ch-ua-platform": '"Windows"',
    "sec-fetch-dest": "empty",
    "sec-fetch-mode": "cors",
    "sec-fetch-site": "same-site",
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                  "AppleWebKit/537.36 (KHTML, like Gecko) "
                  "Chrome/140.0.0.0 Safari/537.36"
}

print_lock = threading.Lock()
file_lock = threading.Lock()  # for writing valid.txt safely


def banner():
    print(BANNER)


def check_email(session: requests.Session, email: str, retries: int = 2, timeout: int = 10):
    url = BASE_URL.format(email=quote(email.strip()))
    last_exc = None
    for attempt in range(1, retries + 2):
        try:
            resp = session.get(url, headers=DEFAULT_HEADERS, timeout=timeout)
            if resp.status_code != 200:
                with print_lock:
                    print(Fore.YELLOW + f"[?] HTTP {resp.status_code} for {email} -> DEAD")
                return False

            try:
                j = resp.json()
            except ValueError:
                with print_lock:
                    print(Fore.YELLOW + f"[?] Non-JSON response for {email} -> DEAD")
                return False

            # ✅ Main logic:
            mailbox_status = j.get("mailbox_status", "").lower()
            if mailbox_status == "valid":
                with print_lock:
                    print(Fore.GREEN + Style.BRIGHT + f"[+] LIVE => {email}")
                with file_lock:
                    with open("valid.txt", "a", encoding="utf-8") as vf:
                        vf.write(email + "\n")
                return True
            else:
                with print_lock:
                    print(Fore.RED + f"[-] DEAD => {email}")
                return False

        except requests.RequestException as e:
            last_exc = e
            time.sleep(0.5 * attempt)  # small backoff
            continue

    with print_lock:
        print(Fore.MAGENTA + f"[!] ERROR checking {email}: {last_exc} (DEAD)")
    return False


def load_emails_from_file(path):
    with open(path, "r", encoding="utf-8", errors="ignore") as f:
        return [line.strip() for line in f if line.strip()]


def main():
    banner()

    # 🔹 Prompt user for file name
    input_file = input(Fore.CYAN + Style.BRIGHT +
                       "Enter the file name containing the email list: ").strip()

    try:
        emails = load_emails_from_file(input_file)
    except Exception as e:
        print(Fore.RED + f"Failed to load input file: {e}")
        sys.exit(1)

    if not emails:
        print(Fore.YELLOW + "No emails found in input file.")
        sys.exit(0)

    # Ask for thread count
    try:
        threads = int(input(Fore.CYAN + Style.BRIGHT +
                            "Enter number of threads (default 50): ") or "50")
    except ValueError:
        threads = 50

    # Clear previous valid.txt
    open("valid.txt", "w").close()

    session = requests.Session()
    adapter = requests.adapters.HTTPAdapter(pool_connections=threads * 2,
                                            pool_maxsize=threads * 2)
    session.mount("https://", adapter)
    session.mount("http://", adapter)

    with concurrent.futures.ThreadPoolExecutor(max_workers=threads) as executor:
        futures = [executor.submit(check_email, session, email) for email in emails]
        for fut in concurrent.futures.as_completed(futures):
            try:
                _ = fut.result()
            except Exception as e:
                with print_lock:
                    print(Fore.MAGENTA + f"[!] Unexpected error: {e}")

    print(Fore.CYAN + Style.BRIGHT + "\n[✓] Done! Valid emails saved to valid.txt")


if __name__ == "__main__":
    main()
