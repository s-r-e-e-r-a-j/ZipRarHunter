import pyzipper
import rarfile
import os
import sys
import subprocess
import shutil
import argparse

# ANSI color codes
RED = '\033[0;31m'
GREEN = '\033[0;32m'
BLUE = '\033[1;34m'
YELLOW = '\033[1;33m'
RESET = '\033[0m'

def banner():

     print("""\033[0;36m


      _______       _____            _    _             _            
     |___  (_)     |  __ \          | |  | |           | |           
        / / _ _ __ | |__) |__ _ _ __| |__| |_   _ _ __ | |_ ___ _ __ 
       / / | | '_ \|  _  // _` | '__|  __  | | | | '_ \| __/ _ \ '__|
      / /__| | |_) | | \ \ (_| | |  | |  | | |_| | | | | ||  __/ |   
     /_____|_| .__/|_|  \_\__,_|_|  |_|  |_|\__,_|_| |_|\__\___|_|   
             | |                                                     
             |_|                               Developer: Sreeraj
         
     \033[0m
     \033[1;33m* GitHub: https://github.com/s-r-e-e-r-a-j \n
     \033[0m""")

# Function to crack ZIP password
def crack_zip(zip_file, wordlist, color_output):
    with open(wordlist, 'r', encoding='utf-8') as f:
        for password in f:
            password = password.strip()
            if not password:
                continue

            if color_output:
                print(f"{BLUE}Trying password: {password}{RESET}")
            else:
                print(f"Trying password: {password}")

            try:
                with pyzipper.AESZipFile(zip_file) as zf:
                    zf.pwd = password.encode()
                    # Try to read a file to verify password
                    test_file = zf.namelist()[0]
                    zf.read(test_file)

                    if color_output:
                        print(f"{GREEN}Password found for ZIP file: {password}{RESET}")
                    else:
                        print(f"Password found for ZIP file: {password}")
                    return
            except (RuntimeError, pyzipper.BadZipFile, pyzipper.LargeZipFile, Exception):
                continue

    if color_output:
        print(f"{RED}Password not found for ZIP file.{RESET}")
    else:
        print(f"Password not found for ZIP file.")

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

# Function to crack RAR password
def crack_rar(rar_file, wordlist, color_output):
    with open(wordlist, 'r', encoding='utf-8') as f:
        for password in f:
            password = password.strip()  # Remove trailing newlines and spaces
            if not password:
                continue  # Skip empty lines

            # Display current password attempt
            if color_output:
                print(f"{BLUE}Trying password: {password}{RESET}")
            else:
                print(f"Trying password: {password}")

            try:
                with rarfile.RarFile(rar_file) as rf:
                    rf.setpassword(password)  # Set the password for the RAR file
                    # Try extracting a file to verify the password
                    test_file = rf.infolist()[0]  # Get the first file in the archive
                    rf.extract(test_file.filename)  # Attempt to extract the first file
                    if color_output:
                        print(f"{GREEN}Password found for RAR file: {password}{RESET}")
                    else:
                        print(f"Password found for RAR file: {password}")
                    return
            except rarfile.BadRarFile:
                continue
            except rarfile.PasswordRequired:
                continue

    if color_output:
        print(f"{RED}Password not found for RAR file.{RESET}")
    else:
        print(f"Password not found for RAR file.")

# Main function to handle user input and call appropriate crack functions
def main():
    # Set up argument parsing
    parser = argparse.ArgumentParser(description="Crack password for ZIP or RAR files.")
    parser.add_argument("-f", "--file", required=True, help="Path to the ZIP or RAR file.")
    parser.add_argument("-w", "--wordlist", required=True, help="Path to the wordlist file.")
    parser.add_argument("-t", "--type", choices=["zip", "rar"], required=True, help="Type of archive (zip or rar).")
    parser.add_argument("--no-color", action="store_true", help="Disable colored output.")

    # Parse command-line arguments
    args = parser.parse_args()

    file = args.file
    wordlist = args.wordlist
    filetype = args.type
    color_output = not args.no_color  # Default is to use color, unless --no-color is specified

    if not os.path.isfile(file):
        print(f"{RED}File {file} not found.{RESET}")
        sys.exit(1)

    if not os.path.isfile(wordlist):
        print(f"{RED}Wordlist {wordlist} not found.{RESET}")
        sys.exit(1)

    if filetype == "zip":
        os.system("clear")
        banner()
        crack_zip(file, wordlist, color_output)
    elif filetype == "rar":
        banner()
        install_unrar_if_needed();
        os.system("clear")
        banner()
        crack_rar(file, wordlist, color_output)
    else:
        print(f"{RED}Invalid file type. Use 'zip' or 'rar'.{RESET}")
        sys.exit(1)

if __name__ == "__main__":
    main()
