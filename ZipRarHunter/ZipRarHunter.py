#!/usr/bin/env python3

import pyzipper
import rarfile
import os
import sys
import subprocess
import shutil
import argparse
import multiprocessing
import threading
from concurrent.futures import ThreadPoolExecutor, ProcessPoolExecutor, as_completed, wait, FIRST_COMPLETED
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

def check_root():
    if os.geteuid() != 0:
        print(f"{RED} please run this tool as root or with sudo{RESET}")
        sys.exit(1)
        
def detect_linux_distribution():
    try:
        if not os.path.exists("/etc/os-release"):
            return "Unknown"

        with open("/etc/os-release", "r") as f:
            content = f.read().lower()

        if any(distro in content for distro in ["debian", "ubuntu", "kali", "linuxmint", "raspbian", "parrot"]):
            return "Debian"
        elif any(distro in content for distro in ["rhel", "red hat", "centos", "fedora", "rocky", "alma", "redhat"]):
            return "RedHat"
        elif any(distro in content for distro in ["arch", "manjaro", "endeavouros", "blackarch"]):
            return "Arch"
        else:
            return "Unknown"

    except Exception as e:
        return f"{RED}Error: {e}{RESET}"


def install_7z_if_needed():
    if shutil.which("7z"):
        return True

    distro = detect_linux_distribution()
    print(f"Detected distribution family: {distro}")
    try:
        if distro == "Debian":
            print("Updating package list and installing 7z with apt-get...")
            subprocess.run(["apt-get", "update"], check=True)
            subprocess.run(["apt-get", "install", "-y", "p7zip-full"], check=True)

        elif distro == "RedHat":
            print("Updating system and installing 7z with yum/dnf...")
            if shutil.which("dnf"):
                subprocess.run(["dnf", "-y", "update"], check=True)
                subprocess.run(["dnf", "install", "-y", "p7zip"], check=True)
            elif shutil.which("yum"):
                subprocess.run(["yum", "install", "-y", "p7zip"], check=True)
            else:
                print("Neither dnf nor yum found. Please install 7z manually.")
                time.sleep(2)
                return False

        elif distro == "Arch":
            print("Updating package database and installing 7z with pacman...")
            subprocess.run(["pacman", "-Sy"], check=True)
            subprocess.run(["pacman", "-S", "--noconfirm", "p7zip"], check=True)

        else:
            print("Unsupported or unknown distribution. Please install 7z manually.")
            time.sleep(2)
            return False

        if shutil.which("7z"):
            print("7z installed successfully.")
            time.sleep(2)
            return True
        else:
            print("Installation completed, but 7z is still not found.")
            time.sleep(2)
            return False

    except subprocess.CalledProcessError as e:
        print(f"Command failed with error: {e}")
        time.sleep(2)
        sys.exit(1)
    except Exception as e:
        print(f"Unexpected error: {e}")
        time.sleep(2)
        sys.exit(1)

         
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

def try_zip_password(zip_file, password, method, stop_event=None):

    if stop_event is not None:
        try:
            if stop_event.is_set():
                return False
        except Exception:
            pass
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

def crack_zip(zip_file, wordlist, max_threads=4, ExecutorClass=None, stop_event=None):
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

        Executor = ExecutorClass or ThreadPoolExecutor
        
        with f, Executor(max_workers=max_threads) as executor:
            futures = {}
            for line in f:
                password = line.strip()
                if not password:
                    continue

                # Submit new job
                future = executor.submit(try_zip_password, zip_file, password, method, stop_event)
                futures[future] = password

                # Limit active futures to avoid overload
                if len(futures) >= max_threads:
                    done, _ = wait(set(futures.keys()), return_when=FIRST_COMPLETED)
                    for future in done:
                        pw = futures.pop(future, None)
                        try:
                            if future.result():
                               print(f"{GREEN}Password found: {pw}{RESET}")
                               # signal other workers to stop
                               try:
                                   stop_event.set()
                               except Exception:
                                      pass
                              # cancel remaining futures
                               for fut in list(futures.keys()):
                                   try:
                                       fut.cancel()
                                   except Exception:
                                          pass
                               return
                            else:
                                   pass
                        except Exception:
                               continue

            # Final pending futures
            for future in as_completed(list(futures.keys())):
                 pw = futures.get(future)
                 try:
                     if future.result():
                        print(f"{GREEN}Password found: {pw}{RESET}")
                        try:
                            stop_event.set()
                        except Exception:
                               pass
                        return
                     else:
                          pass
                 except Exception:
                        continue

        print(f"{RED}Password not found.{RESET}")
    except FileNotFoundError:
        print(f"{RED}Wordlist not found: {wordlist}{RESET}")

def install_unrar_if_needed():
    if shutil.which("unrar"):
        return True  # Already installed

    distro = detect_linux_distribution()
    print(f"Detected distribution family: {distro}")
    print("[*] 'unrar' not found. Attempting installation...")

    try:
        if distro == "Debian":
            subprocess.run(["apt-get", "update"], check=True)
            subprocess.run(["apt-get", "install", "-y", "unrar"], check=True)

        elif distro == "RedHat":
            if shutil.which("dnf"):
                subprocess.run(["dnf", "-y", "update"], check=True)
                subprocess.run(["dnf", "install", "-y", "unrar"], check=True)
            elif shutil.which("yum"):
                subprocess.run(["yum", "install", "-y", "unrar"], check=True)
            else:
                print("[!] Neither dnf nor yum found. Please install unrar manually.")
                time.sleep(2)
                return False

        elif distro == "Arch":
            subprocess.run(["pacman", "-Sy"], check=True)
            subprocess.run(["pacman", "-S", "--noconfirm", "unrar"], check=True)

        else:
            print("[!] Unsupported or unknown distribution. Please install unrar manually.")
            time.sleep(2)
            return False

        if shutil.which("unrar"):
            print("unrar installed successfully.")
            time.sleep(2)
            return True
        else:
            print("Installation completed, but unrar is still not found.")
            time.sleep(2)
            return False

    except subprocess.CalledProcessError as e:
        print(f"[!] Failed to install unrar: {e}")
        time.sleep(2)
        sys.exit(1)
    except Exception as e:
        print(f"Unexpected error: {e}")
        time.sleep(2)
        sys.exit(1)

        
def try_rar_password(rar_file, password, stop_event=None):

    if stop_event is not None:
        try:
            if stop_event.is_set():
                return False
        except Exception:
            pass
    
    try:
        with rarfile.RarFile(rar_file) as rf:
            rf.setpassword(password)
            rf.testrar()
            return True
  # except (rarfile.BadRarFile, rarfile.PasswordRequired, rarfile.BadPassword):
      # return False
    except Exception:
        return False


def crack_rar(rar_file, wordlist, max_threads=4, ExecutorClass=None, stop_event=None):
    try:
        try:
            f = open(wordlist, 'r', encoding='utf-8')
            _ = f.readline()  # quick test to catch decoding error
            f.seek(0)
        except UnicodeDecodeError:
            f = open(wordlist, 'r', encoding='latin-1', errors='ignore')

        Executor = ExecutorClass or ThreadPoolExecutor
        
        with f, Executor(max_workers=max_threads) as executor:
            futures = {}
            for line in f:
                password = line.strip()
                if not password:
                    continue

                future = executor.submit(try_rar_password, rar_file, password, stop_event)
                futures[future] = password

                if len(futures) >= max_threads:
                    done, _ = wait(set(futures.keys()), return_when=FIRST_COMPLETED)
                    for future in done:
                        pw = futures.pop(future, None)
                        try:
                            if future.result():
                               print(f"{GREEN}Password found: {pw}{RESET}")
                               # signal other workers to stop
                               try:
                                   stop_event.set()
                               except Exception:
                                      pass
                               # cancel remaining futures
                               for fut in list(futures.keys()):
                                   try:
                                       fut.cancel()
                                   except Exception:
                                          pass
                               return
                            else:
                                 pass
                        except Exception:
                               continue

            # Finish remaining futures
            for future in as_completed(list(futures.keys())):
                pw = futures.get(future)
                try:
                    if future.result():
                       print(f"{GREEN}Password found: {pw}{RESET}")
                       try:
                           stop_event.set()
                       except Exception:
                              pass
                       return
                    else:
                         pass
                except Exception:
                       continue

        print(f"{RED}Password not found for RAR file.{RESET}")
    except FileNotFoundError:
        print(f"{RED}Wordlist not found: {wordlist}{RESET}")


def main():
    check_root()
    parser = argparse.ArgumentParser(description="Crack password for ZIP or RAR files.")
    parser.add_argument("-f", "--file", required=True, help="Path to the ZIP or RAR file.")
    parser.add_argument("-w", "--wordlist", required=True, help="Path to the wordlist file.")
    parser.add_argument("-t", "--type", choices=["zip", "rar"], required=True, help="Type of archive (zip or rar).")
    parser.add_argument("--threads", nargs="?", const=4, type=int, default=None, help="Number of threads to use (ThreadPoolExecutor).")
    parser.add_argument("--cores", nargs="?", const=os.cpu_count(), type=int, default=None, help="Number of cores to use (ProcessPoolExecutor).")

    args = parser.parse_args()

    file = args.file
    wordlist = args.wordlist
    filetype = args.type
    max_threads = args.threads

    if args.threads and args.cores:
       print(f"{RED}Error: cannot use both --threads and --cores{RESET}")
       sys.exit(1)

    if args.cores:
       ExecutorClass = ProcessPoolExecutor
       max_workers = min(args.cores, os.cpu_count())
       mode = "process"
    elif args.threads:
       ExecutorClass = ThreadPoolExecutor
       max_workers = args.threads
       mode = "thread"
    else:
       ExecutorClass = ThreadPoolExecutor
       max_workers = 4
       mode = "thread"

    # create a stop event that works in processes or threads
    if mode == "process":
        manager = multiprocessing.Manager()
        stop_event = manager.Event()
    else:
        stop_event = threading.Event()
    max_threads = max_workers
    
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
        crack_zip(file, wordlist, max_threads, ExecutorClass=ExecutorClass, stop_event=stop_event)
    elif filetype == "rar":
        os.system("clear")
        banner()
        install_unrar_if_needed()
        os.system("clear")
        banner()
        crack_rar(file, wordlist, max_threads, ExecutorClass=ExecutorClass, stop_event=stop_event)
    else:
        print(f"{RED}Invalid file type. Use 'zip' or 'rar'.{RESET}")
        sys.exit(1)

if __name__ == "__main__":
    main()


