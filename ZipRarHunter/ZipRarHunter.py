
import pyzipper
import rarfile
import os
import sys
import subprocess
import shutil
import argparse
from concurrent.futures import ThreadPoolExecutor, as_completed, wait, FIRST_COMPLETED
import time

# ANSI color codes
RED = '\033[0;31m'
GREEN = '\033[0;32m'
BLUE = '\033[1;34m'
YELLOW = '\033[1;33m'
RESET = '\033[0m'

def banner():
    print("\033[0;36m")
    print(r"""


      _______       _____            _    _             _            
     |___  (_)     |  __ \          | |  | |           | |           
        / / _ _ __ | |__) |__ _ _ __| |__| |_   _ _ __ | |_ ___ _ __ 
       / / | | '_ \|  _  // _` | '__|  __  | | | | '_ \| __/ _ \ '__|
      / /__| | |_) | | \ \ (_| | |  | |  | | |_| | | | | ||  __/ |   
     /_____|_| .__/|_|  \_\__,_|_|  |_|  |_|\__,_|_| |_|\__\___|_|   
             | |                                                     
             |_|                               Developer: Sreeraj

     """)
    print(f"{YELLOW}   * GitHub : https://github.com/s-r-e-e-r-a-j{RESET}\n")
    

def install_7z_if_needed():
    if shutil.which("7z"):
        print("7z is already installed.")
        return

    print("7z is not installed. Installing with apt...")

    try:
        if os.geteuid() != 0:
           subprocess.run(["sudo", "apt", "update"], check=True)
           subprocess.run(["sudo", "apt", "install", "-y", "p7zip-full"], check=True)
        else:
             subprocess.run(["apt", "update"], check=True)
             subprocess.run(["apt", "install", "-y", "p7zip-full"], check=True)
        if shutil.which("7z"):
            print("7z installed successfully.")
        else:
            print("Installation completed, but 7z is still not found.")
    except subprocess.CalledProcessError as e:
        print(f"Command failed with error: {e}")
    except Exception as e:
        print(f"Unexpected error: {e}")
         
def detect_encryption(zip_path):
    try:
        output = subprocess.check_output(["7z", "l", "-slt", zip_path], stderr=subprocess.STDOUT).decode()
        if "Method = AES" in output:
            return "AES"
        elif "Method = ZipCrypto" in output:
            return "ZipCrypto"
        else:
            return "Not Encrypted"
    except Exception as e:
        print(f"{RED}Error detecting encryption: {e}{RESET}")
        return "Error"

def try_zip_password(zip_file, password, method):
    try:
        if method == "AES":
            with pyzipper.AESZipFile(zip_file, 'r') as zf:
                zf.pwd = password.encode()
                files = zf.namelist()
                if not files:
                    return False
                zf.read(files[0])
        elif method == "ZipCrypto":
            with pyzipper.ZipFile(zip_file, 'r') as zf:
                zf.setpassword(password.encode())
                files = zf.namelist()
                if not files:
                    return False
                zf.read(files[0])
        return True
    except Exception:
        return False

def crack_zip(zip_file, wordlist, max_threads=4):
    method = detect_encryption(zip_file)
    if method == "Not Encrypted":
        print(f"{GREEN}ZIP file is not encrypted.{RESET}")
        return
    elif method == "Error":
        print(f"{RED}Could not determine encryption method.{RESET}")
        return

    try:
        try:
            f = open(wordlist, 'r', encoding='utf-8')
            _ = f.readline()
            f.seek(0)
        except UnicodeDecodeError:
            f = open(wordlist, 'r', encoding='latin-1', errors='ignore')

        with f, ThreadPoolExecutor(max_workers=max_threads) as executor:
            futures = {}
            for line in f:
                password = line.strip()
                if not password:
                    continue

                # Submit new job
                future = executor.submit(try_zip_password, zip_file, password, method)
                futures[future] = password

                # Limit active futures to avoid overload
                if len(futures) >= max_threads:
                    done, _ = wait(futures, return_when=FIRST_COMPLETED)
                    for future in done:
                        pw = futures.pop(future)
                        try:
                            if future.result():
                                print(f"{GREEN}Password found: {pw}{RESET}")
                                executor.shutdown(wait=False)
                                return
                            else:
                                print(f"{BLUE}Tried: {pw}{RESET}")
                        except Exception:
                            continue

            # Final pending futures
            for future in as_completed(futures):
                pw = futures[future]
                try:
                    if future.result():
                        print(f"{GREEN}Password found: {pw}{RESET}")
                        return
                    else:
                        print(f"{BLUE}Tried: {pw}{RESET}")
                except Exception:
                    continue

        print(f"{RED}Password not found.{RESET}")
    except FileNotFoundError:
        print(f"{RED}Wordlist not found: {wordlist}{RESET}")


def install_unrar_if_needed():
    if shutil.which("unrar"):
        return  # Already installed

    print("[*] 'unrar' not found. Attempting installation using apt...")

    try:
        if os.geteuid() != 0:
            # Not running as root, use sudo
            subprocess.run(["sudo", "apt", "update"], check=True)
            subprocess.run(["sudo", "apt", "install", "-y", "unrar"], check=True)
        else:
            # Already root
            subprocess.run(["apt", "update"], check=True)
            subprocess.run(["apt", "install", "-y", "unrar"], check=True)

        print("[+] 'unrar' installed successfully.")

    except subprocess.CalledProcessError as e:
        print(f"[!] Failed to install unrar: {e}")
        sys.exit(1)

def try_rar_password(rar_file, password):
    try:
        with rarfile.RarFile(rar_file) as rf:
            rf.setpassword(password)
            rf.testrar();
            return True
  # except (rarfile.BadRarFile, rarfile.PasswordRequired, rarfile.BadPassword):
      # return False
    except Exception:
        return False


def crack_rar(rar_file, wordlist, max_threads=4):
    try:
        try:
            f = open(wordlist, 'r', encoding='utf-8')
            _ = f.readline()  # quick test to catch decoding error
            f.seek(0)
        except UnicodeDecodeError:
            f = open(wordlist, 'r', encoding='latin-1', errors='ignore')

        with f, ThreadPoolExecutor(max_workers=max_threads) as executor:
            futures = {}
            for line in f:
                password = line.strip()
                if not password:
                    continue

                future = executor.submit(try_rar_password, rar_file, password)
                futures[future] = password

                if len(futures) >= max_threads:
                    done, _ = wait(futures, return_when=FIRST_COMPLETED)
                    for future in done:
                        pw = futures.pop(future)
                        try:
                            if future.result():
                                print(f"{GREEN}Password found for RAR file: {pw}{RESET}")
                                executor.shutdown(wait=False)
                                return
                            else:
                                print(f"{BLUE}Tried password: {pw}{RESET}")
                        except Exception:
                            continue

            # Finish remaining futures
            for future in as_completed(futures):
                pw = futures[future]
                try:
                    if future.result():
                        print(f"{GREEN}Password found for RAR file: {pw}{RESET}")
                        return
                    else:
                        print(f"{BLUE}Tried password: {pw}{RESET}")
                except Exception:
                    continue

        print(f"{RED}Password not found for RAR file.{RESET}")
    except FileNotFoundError:
        print(f"{RED}Wordlist not found: {wordlist}{RESET}")


def main():
    parser = argparse.ArgumentParser(description="Crack password for ZIP or RAR files.")
    parser.add_argument("-f", "--file", required=True, help="Path to the ZIP or RAR file.")
    parser.add_argument("-w", "--wordlist", required=True, help="Path to the wordlist file.")
    parser.add_argument("-t", "--type", choices=["zip", "rar"], required=True, help="Type of archive (zip or rar).")
    parser.add_argument("--threads", type=int, default=4, help="Number of threads to use (default: 4).")


    args = parser.parse_args()

    file = args.file
    wordlist = args.wordlist
    filetype = args.type
    max_threads = args.threads

    if not os.path.isfile(file):
        print(f"{RED}File {file} not found.{RESET}")
        sys.exit(1)

    if not os.path.isfile(wordlist):
        print(f"{RED}Wordlist {wordlist} not found.{RESET}")
        sys.exit(1)

    if max_threads < 1:
        print(f"{RED}Number of threads must be at least 1.{RESET}")
        sys.exit(1)

    if filetype == "zip":
        os.system("clear")
        banner()
        install_7z_if_needed()
        os.system("clear")
        banner()
        crack_zip(file, wordlist, max_threads)
    elif filetype == "rar":
        os.system("clear")
        banner()
        install_unrar_if_needed()
        os.system("clear")
        banner()
        crack_rar(file, wordlist, max_threads)
    else:
        print(f"{RED}Invalid file type. Use 'zip' or 'rar'.{RESET}")
        sys.exit(1)

if __name__ == "__main__":
    main()
