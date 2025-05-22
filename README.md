## ZipRarHunter
ZipRarHunter is a powerful command-line ethical hacking tool designed to crack passwords of ZIP and RAR archive files using a wordlist.It automates the process of password recovery from encrypted archives

## Features
- Cracking ZIP files encrypted with both **ZipCrypto** and **AES-256** encryption

- Cracking RAR4 archives using multithreaded brute-force attacks
*(Also supports RAR5 if the paid version of UnRAR is installed)*

- Improve cracking speed by specifying the number of threads with `--threads` option (default is 4)

- Efficient memory usage by reading wordlists line-by-line (streaming)

- Automatic detection of ZIP encryption methods

- Encoding fallback support (**UTF-8 and Latin-1**) for various wordlists
  
## Requirements
- **Linux distributions:** `Debian`, `RedHat`, `Arch` 
- **Python 3.x:** Ensure that Python 3 is installed on your system.
- **Dependencies:**
- `pyzipper` (for handling ZIP files)
- `rarfile` (for handling RAR files)
  
**You can install the required Python packages using**:`pip3`
```bash
pip3 install pyzipper
```
```bash
pip3 install rarfile
```
## Installation

1. **Clone the repository:**

```bash
git clone https://github.com/s-r-e-e-r-a-j/ZipRarHunter.git
```
2. **Navigate to the ZipRarHunter directory:**

```bash
cd ZipRarHunter
```
3. **Ensure all dependencies are installed. If not, run:**

``` bash
pip3 install -r requirements.txt
```

4. **Navigate to the ZipRarHunter directory**
   
```bash
cd ZipRarHunter
```
5. **Install the tool**
   
   *Run the install.py script*
```bash
sudo python3 install.py
```
**then enter `y` for install**
## Usage
ZipRarHunter uses command-line arguments to specify the target file, wordlist, file type (ZIP or RAR) and the number of threads.

## Basic Usage
```bash
ziprarhunter -f /path/to/archive.zip -w /path/to/wordlist.txt -t zip
ziprarhunter -f /path/to/archive.rar -w /path/to/wordlist.txt -t rar
```
## Command-line Arguments
- `-f` or `--file`: The path to the ZIP or RAR file you want to crack.
- `-w` or `--wordlist`: The path to the wordlist file that contains potential passwords.
- `-t` or `--type`: The type of archive. Acceptable values are zip or rar.
- `--threads`: Number of threads to use (default:4).
## Example Commands
1. **Crack a ZIP file with a wordlist:**

``` bash
ziprarhunter -f /path/to/archive.zip -w /path/to/wordlist.txt -t zip
```
2. **Crack a RAR file with a wordlist:**

```bash
ziprarhunter -f /path/to/archive.rar -w /path/to/wordlist.txt -t rar
```
3. **Crack a zip file with 20 threads:**

```bash
ziprarhunter -f /path/to/archive.zip -w /path/to/wordlist.txt -t zip --threads 20
```
## Output Example
```bash
Tried: password
Password found : password123
```

## uninstallation
**Run the install.py script**
```bash
sudo python3 install.py
```
**Then Enter `n` for uninstall**

## License
This project is licensed under the MIT License - see the LICENSE file for details.

## Disclaimer
This tool is intended for educational purposes only. It should be used responsibly and legally. Unauthorized use of this tool to crack passwords without permission is illegal and unethical.


